import streamlit as st
import pandas as pd
import random
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- CONFIG ----------
st.set_page_config(page_title="📚 Chat-Style Book Recommender", layout="wide", initial_sidebar_state="expanded")

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items_improved_image2.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    return recs, items, interactions

recs_df, items_df, interactions_df = load_data()

# ---------- TF-IDF SETUP ----------
@st.cache_data
def compute_tfidf_matrix(items):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
    tfidf_matrix = vectorizer.fit_transform(items['content'].fillna(""))
    return vectorizer, tfidf_matrix

vectorizer, tfidf_matrix = compute_tfidf_matrix(items_df)

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ---------- SIDEBAR ----------
st.sidebar.title("🔧 Settings")
st.sidebar.markdown("Chat with the system to get personalized book recommendations based on content similarity.")

# ---------- CHAT INTERFACE ----------
st.title("💬 Book Chat Recommender")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "books" in msg:
            cols = st.columns(5)
            for i, book in enumerate(msg["books"]):
                with cols[i % 5]:
                    st.image(book["cover"], width=100)
                    st.markdown(f"**{book['title']}**")
                    st.caption(book["author"])

if prompt := st.chat_input("What kind of book are you looking for?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Vectorize user query and compute cosine similarity
    query_vec = vectorizer.transform([prompt])
    similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarity.argsort()[-5:][::-1]
    recommended_books = items_df.iloc[top_indices]

    books_info = []
    for _, row in recommended_books.iterrows():
        books_info.append({
            "title": row['Title'],
            "author": row['Author'],
            "cover": row.get('cover_url', "https://via.placeholder.com/128x195.png?text=No+Image")
        })

    assistant_msg = f"Here are some great book suggestions for you based on your interest in '{prompt}':"
    with st.chat_message("assistant"):
        st.markdown(assistant_msg)
        cols = st.columns(5)
        for i, book in enumerate(books_info):
            with cols[i % 5]:
                st.image(book["cover"], width=100)
                st.markdown(f"**{book['title']}**")
                st.caption(book['author'])

    st.session_state.messages.append({"role": "assistant", "content": assistant_msg, "books": books_info})
