import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
INDEX_DIR = os.path.join(BASE_DIR, "index")
FAISS_PATH = os.path.join(INDEX_DIR, "vectors.faiss")
METADATA_PATH = os.path.join(INDEX_DIR, "metadata.json")
MODEL_NAME = "BAAI/bge-small-en-v1.5"
