import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Book Recommender", layout="wide")

# ------------------ Load Data ------------------
@st.cache_data
def load_data():
    items = pd.read_csv("items.csv")
    return items

items_df = load_data()

# ------------------ Cover Retrieval ------------------
def get_cover_url(isbn):
    if pd.isna(isbn):
        return "https://via.placeholder.com/128x195.png?text=No+ISBN"
    isbn_clean = str(isbn).split(";")[0].strip()
    return f"https://covers.openlibrary.org/b/isbn/{isbn_clean}-L.jpg"

# ------------------ Sidebar ------------------
st.sidebar.title("📘 Book Recommender System")
top_n = st.sidebar.slider("Top N Books to Show", 5, 50, 20)

genre = st.sidebar.text_input("Filter by subject:")
author = st.sidebar.text_input("Filter by author:")

# ------------------ Filter Books ------------------
books = items_df.copy()
if genre:
    books = books[books['Subjects'].str.contains(genre, case=False, na=False)]
if author:
    books = books[books['Author'].str.contains(author, case=False, na=False)]

books = books.head(top_n)

# ------------------ Display Cards ------------------
st.title("🎬 Recommended Books")

cols = st.columns(5)

for i, (_, row) in enumerate(books.iterrows()):
    with cols[i % 5]:
        st.image(get_cover_url(row['ISBN Valid']), width=120)
        st.markdown(f"**{row['Title']}**")
        st.caption(f"{row['Author']}")
