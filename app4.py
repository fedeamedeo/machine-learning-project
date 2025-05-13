import streamlit as st
import pandas as pd
import random
import os

# ---------- CONFIG ----------
st.set_page_config(page_title="📚 Chat-Style Book Recommender", layout="wide", initial_sidebar_state="expanded")

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items_improved.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    rec_lookup = pd.read_csv("tfidf_recommendations.csv")
    return recs, items, interactions, rec_lookup

recs_df, items_df, interactions_df, rec_lookup = load_data()

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ---------- SIDEBAR ----------
st.sidebar.title("🔧 Settings")
st.sidebar.markdown("Chat with the system to get personalized book recommendations using precomputed TF-IDF matches.")

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

    # Match query to book metadata
    matched = items_df[
        items_df['Title'].str.lower().str.contains(prompt.lower(), na=False) |
        items_df['Subjects'].str.lower().str.contains(prompt.lower(), na=False)
    ]

    if matched.empty:
        recommended_books = items_df.sample(5)
    else:
        best_match_id = matched.iloc[0]['i']
        rec_row = rec_lookup[rec_lookup['i'] == best_match_id]

        if not rec_row.empty:
            rec_ids = list(map(int, rec_row.iloc[0]['tfidf_recs'].split()))
            recommended_books = items_df[items_df['i'].isin(rec_ids)].head(5)
        else:
            recommended_books = matched.head(5)

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
