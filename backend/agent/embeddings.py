# agent/embeddings.py
from sentence_transformers import SentenceTransformer

# Load once, reuse across requests
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_query(text: str) -> list[float]:
    """Embed a single query string locally using sentence-transformers."""
    model = get_model()
    embedding = model.encode(text)
    return embedding.tolist()