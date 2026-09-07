import os
import json
import pymupdf
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import RESOURCES_DIR, INDEX_DIR, FAISS_PATH, METADATA_PATH, MODEL_NAME

def get_chunks(text, max_chars=1000, overlap_chars=200):
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < max_chars:
            current_chunk += p + "\n\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            if len(current_chunk) > overlap_chars:
                current_chunk = current_chunk[-overlap_chars:] + "\n\n" + p + "\n\n"
            else:
                current_chunk = p + "\n\n"
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    return chunks

def ingest():
    if not os.path.exists(RESOURCES_DIR):
        os.makedirs(RESOURCES_DIR)
        print(f"Created {RESOURCES_DIR}. Please add PDFs and re-run.")
        return

    os.makedirs(INDEX_DIR, exist_ok=True)
    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)
    
    metadata = []
    texts = []
    
    for filename in os.listdir(RESOURCES_DIR):
        if not filename.lower().endswith(".pdf"):
            continue
        
        path = os.path.join(RESOURCES_DIR, filename)
        doc = pymupdf.open(path)
        print(f"Processing {filename} ({len(doc)} pages)...")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if not text:
                continue
            
            chunks = get_chunks(text, max_chars=1000, overlap_chars=200)
            
            for chunk in chunks:
                if not chunk.strip():
                    continue
                texts.append(chunk)
                metadata.append({
                    "document": filename,
                    "page": page_num + 1,
                    "content": chunk
                })
                
    if not texts:
        print("No text found in PDFs.")
        return

    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    faiss.write_index(index, FAISS_PATH)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully indexed {len(metadata)} chunks from PDFs.")

if __name__ == "__main__":
    ingest()
