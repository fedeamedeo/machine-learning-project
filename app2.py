import streamlit as st
import pandas as pd
import requests

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="📚 Book Recommender", layout="wide")

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    items = pd.read_csv("items.csv")
    return items

items_df = load_data()

# ---------- GET COVER IMAGE ----------
def get_cover_url(isbn):
    if pd.isna(isbn):
        return "https://via.placeholder.com/128x195.png?text=No+ISBN"
    isbn_clean = str(isbn).split(";")[0].strip()
    return f"https://covers.openlibrary.org/b/isbn/{isbn_clean}-L.jpg"

# ---------- SIDEBAR ----------
st.sidebar.title("🎯 Book Recommender System")
st.sidebar.markdown("### 🎬 Explore top books visually!")

# Filters
top_n = st.sidebar.slider("Number of books to display", min_value=5, max_value=50, value=20)
subject_filter = st.sidebar.text_input("Filter by subject keyword:")
author_filter = st.sidebar.text_input("Filter by author keyword:")

# ---------- FILTER BOOKS ----------
filtered_books = items_df.copy()

if subject_filter:
    filtered_books = filtered_books[filtered_books['Subjects'].str.contains(subject_filter, case=False, na=False)]

if author_filter:
    filtered_books = filtered_books[filtered_books['Author'].str.contains(author_filter, case=False, na=False)]

filtered_books = filtered_books.head(top_n)

# ---------- MAIN DISPLAY ----------
st.title("📚 Recommended Books for You")

cols = st.columns(5)

for i, (_, row) in enumerate(filtered_books.iterrows()):
    with cols[i % 5]:
        st.image(get_cover_url(row['ISBN Valid']), width=120)
        st.markdown(f"**{row['Title']}**")
        st.caption(f"{row['Author']}")
        if not pd.isna(row['Subjects']):
            st.markdown(f"<small style='color:gray'>{row['Subjects'].split(';')[0]}</small>", unsafe_allow_html=True)
