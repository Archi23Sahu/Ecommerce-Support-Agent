# ingestion/embed_and_upload.py
import json
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

load_dotenv()

CHUNKS_PATH = "data/processed/chunks.json"
BATCH_SIZE  = 100

def upload():
    # Load chunks
    with open(CHUNKS_PATH) as f:
        chunks = json.load(f)

    # Embed locally with sentence-transformers 
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print(f"Embedding {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

    # Connect to Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")

    # Create index if it doesn't exist (dimension=384 for MiniLM)
    if index_name not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    index = pc.Index(index_name)

    # Upsert in batches
    vectors = [
        (c["id"], emb.tolist(), c["metadata"])
        for c, emb in zip(chunks, embeddings)
    ]

    for i in range(0, len(vectors), BATCH_SIZE):
        batch = vectors[i:i + BATCH_SIZE]
        index.upsert(vectors=batch)
        print(f"Uploaded batch {i // BATCH_SIZE + 1}")

    print("Done! All chunks in Pinecone.")

if __name__ == "__main__":
    upload()