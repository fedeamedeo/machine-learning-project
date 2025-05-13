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
    items = pd.read_csv("items_improved_image2.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    return recs, items, interactions

recs_df, items_df, interactions_df = load_data()

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ---------- SIDEBAR ----------
st.sidebar.title("🔧 Settings")
st.sidebar.markdown("Chat with the system to get personalized book recommendations.")

user_ids = recs_df['user_id'].unique()
selected_user = st.sidebar.selectbox("Select a User ID", sorted(user_ids))

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

    # Simulated interpretation (we just fetch the user recommendations)
    user_row = recs_df[recs_df['user_id'] == selected_user]
    if not user_row.empty:
        book_ids = list(map(int, user_row.iloc[0]['recommendation'].split()))
        recommended_books = items_df[items_df['i'].isin(book_ids)].sample(n=5)

        books_info = []
        for _, row in recommended_books.iterrows():
            books_info.append({
                "title": row['Title'],
                "author": row['Author'],
                "cover": row['cover_url']
            })

        assistant_msg = f"Here are some great book suggestions for you based on your interest in '{prompt}':"
        with st.chat_message("assistant"):
            st.markdown(assistant_msg)
            cols = st.columns(5)
            for i, book in enumerate(books_info):
                with cols[i % 5]:
                    st.image(book["cover"], width=100)
                    st.markdown(f"**{book['title']}**")
                    st.caption(book["author"])

        st.session_state.messages.append({"role": "assistant", "content": assistant_msg, "books": books_info})
    else:
        msg = "Sorry, I couldn't find recommendations for this user."
        st.chat_message("assistant").markdown(msg)
        st.session_state.messages.append({"role": "assistant", "content": msg})
