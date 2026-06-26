# ui/app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="ShopBot",
    page_icon="🛍️",
    layout="centered"
)

st.title("🛍️ ShopBot — AI Shopping Assistant")
st.caption("Ask me about products, reviews, or your order status.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Suggested questions
if not st.session_state.messages:
    st.markdown("**Try asking:**")
    cols = st.columns(3)
    suggestions = [
        "Recommend a good Kindle",
        "What's the best Fire tablet?",
        "Check order #12345",
    ]
    for col, suggestion in zip(cols, suggestions):
        if col.button(suggestion):
            st.session_state.messages.append({"role": "user", "content": suggestion})
            st.rerun()

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(
                    f"{API_URL}/chat",
                    json={"message": prompt},
                    timeout=60
                )
                if res.status_code == 200:
                    reply = res.json()["reply"]
                else:
                    reply = f"Error {res.status_code}: {res.text}"
            except requests.exceptions.Timeout:
                reply = "Sorry, the request timed out. Please try again."
            except Exception as e:
                reply = f"Connection error: {e}. Make sure the backend is running."

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# Clear chat button
if st.session_state.messages:
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()