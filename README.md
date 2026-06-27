# ShopBot — AI E-commerce Support Agent

An AI-powered customer support agent built with RAG (Retrieval-Augmented Generation) and LangChain ReAct architecture. ShopBot answers product queries, retrieves customer reviews, and handles order status tracking using semantic search over Amazon product data.

---


## Features

- **Semantic product search** — finds relevant products using vector similarity, not just keywords
- **Review analysis** — retrieves and summarizes customer reviews with sentiment filtering
- **Order tracking** — checks order status by order ID
- **Human escalation** — detects complex issues and escalates to a human agent
- **Conversation memory** — remembers the last 5 turns of the conversation
- **React chat UI** — clean, responsive chat interface with typing indicators

---

## Architecture

```
User → React UI 
          ↓
      FastAPI backend 
          ↓
      LangChain ReAct Agent (Llama 3.3 70B via Groq)
          ↓ picks a tool
    ┌─────────────────────────────────────┐
    │  search_products  │  get_reviews    │
    │  check_order      │  escalate       │
    └─────────────────────────────────────┘
          ↓ search_products / get_reviews
      embed query (sentence-transformers)
          ↓
      Pinecone vector search
          ↓
      top-5 similar product chunks
          ↓
      LLM synthesizes Final Answer
```

### Ingestion pipeline (runs once locally)

```
Kaggle CSV (5,000 rows)
    → clean_data.py       (clean, group by product, chunk)
    → chunks.json         (237 chunks across 23 products)
    → embed_and_upload.py (embed with sentence-transformers, upsert to Pinecone)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Llama 3.3 70B via Groq |
| Agent framework | LangChain + LangGraph |
| Vector database | Pinecone|
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| Backend | FastAPI + Uvicorn |
| Frontend | React |
| Dataset | Amazon Consumer Reviews (Kaggle) |
| Deployment | Render (API) + Vercel (UI) |

---

## Getting Started

### Prerequisites

- Python 3.10+
- React
- Accounts on: [Pinecone](https://pinecone.io), [Groq](https://console.groq.com), [Hugging Face](https://huggingface.co)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/ecommerce-support-agent.git
cd ecommerce-support-agent
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=ecommerce-agent
HF_API_TOKEN=your_huggingface_token
GROQ_API_KEY=your_groq_key
API_BASE_URL=http://127.0.0.1:8000
```

### 3. Download the dataset

Download the Amazon Consumer Reviews dataset from Kaggle and place the CSV in:

https://www.kaggle.com/datasets/datafiniti/consumer-reviews-of-amazon-products/code
```
backend/data/raw/amazon_products.csv
```

Dataset columns used: `id`, `name`, `asins`, `brand`, `categories`, `manufacturer`, `reviews.rating`, `reviews.text`, `reviews.title`, `reviews.doRecommend`, `reviews.numHelpful`, `reviews.username`

### 4. Run the ingestion pipeline

```bash
# Step 1 — clean and chunk the data
python ingestion/clean_data.py

# Step 2 — embed and upload to Pinecone 
python ingestion/embed_and_upload.py
```


### 5. Start the backend

```bash
uvicorn api.main:app --reload
```

API running at `http://127.0.0.1:8000`
Swagger docs at `http://127.0.0.1:8000/docs`

### 6. Set up and start the frontend

```bash
cd ../frontend
npm install
cp .env.example .env   # set REACT_APP_API_URL=http://127.0.0.1:8000
npm start
```

UI running at `http://localhost:3000`

---

## API Reference

### POST /chat

```json
// Request
{
  "message": "recommend me a good kindle",
  "session_id": "default"
}

// Response
{
  "reply": "Based on our catalog, I recommend the Kindle Oasis (4.8/5, 39 reviews)..."
}
```

### GET /health

```json
{ "status": "ok" }
```

---

## How RAG Works in This Project

1. **Ingestion** — 5,000 Amazon reviews are grouped by product (23 products), chunked into 237 text segments, and embedded into 384-dimensional vectors using `all-MiniLM-L6-v2`
2. **Storage** — vectors + metadata (product name, brand, rating, category) uploaded to Pinecone
3. **Query** — user's question is embedded using the same model
4. **Retrieval** — Pinecone finds the 5 most semantically similar chunks using cosine similarity
5. **Generation** — Llama 3.3 70B reads the retrieved chunks and writes a natural language answer

---

