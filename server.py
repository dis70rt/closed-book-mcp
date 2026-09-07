import os
import json
import pymupdf
import faiss
from mcp.server import MCPServer
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

from config import RESOURCES_DIR, INDEX_DIR, FAISS_PATH, METADATA_PATH, MODEL_NAME

mcp = MCPServer("MCP Closed-Book")

_model = None
_index = None
_metadata = None
_bm25 = None

def load_resources():
    global _model, _index, _metadata, _bm25
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    if _index is None and os.path.exists(FAISS_PATH):
        _index = faiss.read_index(FAISS_PATH)
    if _metadata is None and os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            _metadata = json.load(f)
        import re
        def tokenize(text):
            return re.findall(r'\b\w+\b', text.lower())
        tokenized_corpus = [tokenize(doc['content']) for doc in _metadata]
        _bm25 = BM25Okapi(tokenized_corpus)

@mcp.tool()
def closed_book_search(query: str, top_k: int = 5) -> str:
    """
    Search the authoritative study materials using Hybrid Search.
    The returned content comes directly from the user's PDFs.
    This is the primary knowledge retrieval tool for closed-book questions.
    """
    load_resources()
    if not _index or not _metadata or not _bm25:
        return "Error: Index not found. Please run ingest.py first."

    # Vector search
    query_embedding = _model.encode([query], convert_to_numpy=True)
    distances, indices = _index.search(query_embedding, top_k)
    
    # BM25 search
    import re
    tokenized_query = re.findall(r'\b\w+\b', query.lower())
    bm25_scores = _bm25.get_scores(tokenized_query)
    
    # Combine results
    results_map = {}
    
    for i, idx in enumerate(indices[0]):
        if idx == -1 or idx >= len(_metadata):
            continue
        score = 1.0 / (1.0 + float(distances[0][i]))
        results_map[idx] = {'item': _metadata[idx], 'v_score': score, 'b_score': 0}
        
    top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
    for idx in top_bm25_indices:
        if bm25_scores[idx] <= 0: continue
        if idx not in results_map:
            results_map[idx] = {'item': _metadata[idx], 'v_score': 0, 'b_score': bm25_scores[idx]}
        else:
            results_map[idx]['b_score'] = bm25_scores[idx]
            
    final_results = []
    for idx, data in results_map.items():
        # pseudo combined score
        combined_score = data['v_score'] + (data['b_score'] * 0.1) 
        final_results.append((combined_score, data['item']))
        
    final_results.sort(key=lambda x: x[0], reverse=True)
    final_results = final_results[:top_k]
    
    results_strings = []
    for score, item in final_results:
        result_str = f"SOURCE: {item['document']} (p. {item['page']})\nRELEVANCE: {score:.4f}\nCONTENT: {item['content']}\n"
        results_strings.append(result_str)
        
    if not results_strings:
        return "No relevant information found in the exam materials."
        
    return "\n---\n".join(results_strings)

@mcp.tool()
def read_document_page(document: str, page: int) -> str:
    """
    Return the complete extracted text of a specific page from a document.
    """
    import pymupdf
    path = os.path.join(RESOURCES_DIR, document)
    if not os.path.exists(path):
        return f"Error: Document {document} not found."
        
    try:
        doc = pymupdf.open(path)
        if page < 1 or page > len(doc):
            return f"Error: Page {page} out of bounds (1-{len(doc)})."
            
        page_obj = doc[page - 1]
        text = page_obj.get_text("text").strip()
        return f"SOURCE: {document}\nPAGE: {page}\n\n{text}"
    except Exception as e:
        return f"Error reading page: {str(e)}"

@mcp.tool()
def list_indexed_documents() -> str:
    """
    Return all indexed PDFs and their page counts.
    """
    if not os.path.exists(RESOURCES_DIR):
        return "Resources directory does not exist."
        
    files = [f for f in os.listdir(RESOURCES_DIR) if f.lower().endswith(".pdf")]
    if not files:
        return "No exam materials found."
        
    import pymupdf
    result = "Available exam materials:\n\n"
    for f in files:
        path = os.path.join(RESOURCES_DIR, f)
        try:
            doc = pymupdf.open(path)
            result += f"- {f} ({len(doc)} pages)\n"
        except:
            result += f"- {f} (Error reading pages)\n"
            
    return result

if __name__ == "__main__":
    load_resources()
    mcp.run()
