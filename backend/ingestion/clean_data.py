import pandas as pd
import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

RAW_PATH = "data/raw/amazon_products_3.csv"
OUT_PATH  = "data/processed/chunks.json"

def clean_and_chunk():
    # Load the raw data
    df = pd.read_csv(RAW_PATH,low_memory=False)

    print(f"Loaded {len(df)} rows, columns: {list(df.columns)}")

    keep = [
        "id", "name", "asins", "brand", "categories",
        "manufacturer",
        "reviews.rating", "reviews.text", "reviews.title",
        "reviews.doRecommend", "reviews.numHelpful", "reviews.username"
    ]

    df = df[[c for c in keep if c in df.columns]].copy()

    # ── 2. Basic cleaning ────────────────────────────────────────────────
    df["name"]  = df["name"].fillna("Unknown Product").str.strip()
    df["brand"] = df["brand"].fillna("Unknown Brand").str.strip()
    df["manufacturer"] = df["manufacturer"].fillna(df["brand"])
    df["categories"] = df["categories"].fillna("General").str.strip()

    # Rating: keep numeric, fill missing with 0
    df["reviews.rating"] = pd.to_numeric(df["reviews.rating"], errors="coerce").fillna(0)

    # Review text: drop rows where both title and text are empty
    df["reviews.text"]  = df["reviews.text"].fillna("").str.strip()
    df["reviews.title"] = df["reviews.title"].fillna("").str.strip()
    df = df[~((df["reviews.text"] == "") & (df["reviews.title"] == ""))]

    df["reviews.doRecommend"] = df["reviews.doRecommend"].fillna("").astype(str)
    df["reviews.numHelpful"]  = pd.to_numeric(df["reviews.numHelpful"], errors="coerce").fillna(0).astype(int)
    df["reviews.username"]    = df["reviews.username"].fillna("Anonymous")

    print(f"After cleaning: {len(df)} rows")
    
    # ── 3. Aggregate reviews per product ─────────────────────────────────
    # Each unique product (by name + brand) gets its reviews grouped together
    product_groups = df.groupby(["name", "brand"], sort=False)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    )

    chunks = []
    product_idx = 0

    for (product_name, brand), group in product_groups:
        product_idx += 1
        avg_rating   = round(group["reviews.rating"].mean(), 1)
        num_reviews  = len(group)
        categories   = group["categories"].iloc[0]
        manufacturer = group["manufacturer"].iloc[0]
        asins        = group["asins"].iloc[0] if "asins" in group.columns else ""

        # Build top reviews block (up to 5 most helpful)
        top_reviews = (
            group.sort_values("reviews.numHelpful", ascending=False)
                 .head(5)
        )

        reviews_text_parts = []
        for _, row in top_reviews.iterrows():
            stars   = int(row["reviews.rating"]) if row["reviews.rating"] else "?"
            helpful = row["reviews.numHelpful"]
            title   = row["reviews.title"]
            body    = row["reviews.text"]
            recommend = "Recommends" if str(row["reviews.doRecommend"]).lower() == "true" else ""

            review_line = f"[{stars}★ {recommend}] {title}: {body}"
            if helpful > 0:
                review_line += f" ({helpful} found helpful)"
            reviews_text_parts.append(review_line)

        reviews_block = "\n".join(reviews_text_parts)

        # Build the full document text for this product
        doc_text = (
            f"Product: {product_name}\n"
            f"Brand: {brand}\n"
            f"Manufacturer: {manufacturer}\n"
            f"Category: {categories}\n"
            f"Average Rating: {avg_rating}/5 ({num_reviews} reviews)\n"
            f"ASIN: {asins}\n\n"
            f"Customer Reviews:\n{reviews_block}"
        )

        # Split into chunks (long review lists get split, metadata stays attached)
        splits = splitter.split_text(doc_text)

        for chunk_idx, text in enumerate(splits):
            chunks.append({
                "id": f"product_{product_idx}_chunk{chunk_idx}",
                "text": text,
                "metadata": {
                    "product_name": product_name,
                    "brand":        brand,
                    "manufacturer": manufacturer,
                    "categories":   categories,
                    "avg_rating":   avg_rating,
                    "num_reviews":  num_reviews,
                    "asins":        str(asins),
                }
            })

   # ── 4. Save ──────────────────────────────────────────────────────────
    os.makedirs("data/processed", exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(chunks, f, indent=2)

    print(f"\nDone! {product_idx} products → {len(chunks)} chunks saved to {OUT_PATH}")
    print(f"Sample chunk:\n{chunks[0]['text'][:300]}...")

if __name__ == "__main__":
    clean_and_chunk()