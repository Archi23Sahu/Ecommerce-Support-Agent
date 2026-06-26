pip install -r requirements.txt
pip install pandas langchain langchain-community
pip install langchain-text-splitters
python ingestion/clean_data.py

pip install sentence-transformers pinecone python-dotenv
python ingestion/embed_and_upload.py

pip install fastapi uvicorn python-dotenv langchain-groq

pip install langchain-classic
uvicorn api.main:app --reload

pip install streamlit


https://www.kaggle.com/datasets/datafiniti/consumer-reviews-of-amazon-products/code