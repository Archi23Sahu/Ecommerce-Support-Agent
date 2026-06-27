# agent/tools.py
import os
import random
from langchain_core.tools import tool
from pinecone import Pinecone
from dotenv import load_dotenv
from agent.embeddings import embed_query

load_dotenv()

def get_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return pc.Index(os.getenv("PINECONE_INDEX_NAME"))

@tool
def search_products(query: str, category: str = None, min_rating: float = None) -> str:
    """Search the product catalog by description, features, or use case."""
    index = get_index()
    vector = embed_query(query)
    filter_dict = {}
    if category:
        filter_dict["categories"] = {"$eq": category}
    if min_rating:
        filter_dict["avg_rating"] = {"$gte": min_rating}

    results = index.query(
        vector=vector,
        top_k=5,
        include_metadata=True,
        filter=filter_dict if filter_dict else None
    )

    if not results["matches"]:
        return "No products found matching your criteria."

    output = []
    for match in results["matches"]:
        m = match["metadata"]
        output.append(
            f"- {m.get('product_name', 'Unknown')} | "
            f"Brand: {m.get('brand', 'Unknown')} | "
            f"Rating: {m.get('avg_rating', '?')}/5 | "
            f"Reviews: {m.get('num_reviews', 0)} | "
            f"Category: {m.get('categories', 'General')}"
        )
    return "\n".join(output)

@tool
def get_reviews(product_name: str, sentiment: str = None) -> str:
    """Fetch customer reviews for a specific product. Sentiment: 'positive' or 'negative'."""
    index = get_index()
    query = f"review of {product_name}"
    if sentiment == "negative":
        query += " problems complaints issues"
    elif sentiment == "positive":
        query += " great excellent loved"

    vector = embed_query(query)
    results = index.query(
        vector=vector,
        top_k=3,
        include_metadata=True,
    )

    if not results["matches"]:
        return f"No reviews found for '{product_name}'."

    chunks = [
        m["metadata"].get("product_name", "") + ": " + m["metadata"].get("text", "")
        for m in results["matches"]
    ]
    return "\n---\n".join(chunks[:3])

@tool
def check_order_status(order_id: str) -> str:
    """Check the status of a customer order by order ID."""
    statuses = ["Processing", "Shipped", "Out for delivery", "Delivered"]
    fake_status = random.choice(statuses)
    fake_eta = "2–3 business days" if fake_status != "Delivered" else "Delivered on June 20"
    return (
        f"Order #{order_id}: {fake_status}. "
        f"Estimated delivery: {fake_eta}."
    )

@tool
def escalate_to_human(reason: str) -> str:
    """Escalate the conversation to a human support agent."""
    return (
        f"I've flagged this conversation for a human agent. "
        f"Reason: {reason}. "
        f"A support representative will contact you within 24 hours."
    )