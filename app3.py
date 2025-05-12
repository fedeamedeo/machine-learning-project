import streamlit as st
import pandas as pd
import requests

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    return recs, items, interactions

recs_df, items_df, interactions_df = load_data()

# ------------------ GET BOOK COVER ------------------
@st.cache_data
def get_cover_image(isbn):
    try:
        query = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(query)
        data = response.json()
        image_url = data['items'][0]['volumeInfo']['imageLinks']['thumbnail']
        return image_url
    except:
        return "https://via.placeholder.com/128x195.png?text=No+Cover"

# ------------------ MOST POPULAR ------------------
st.title("📚 Book Recommendation System")
st.header("🔥 Most Popular Books")

popular_ids = interactions_df['i'].value_counts().head(10).index.tolist()
popular_books = items_df[items_df['i'].isin(popular_ids)]

cols = st.columns(5)
for i, (_, row) in enumerate(popular_books.iterrows()):
    with cols[i % 5]:
        isbn = str(row['ISBN Valid']).split(";")[0].strip()
        img_url = get_cover_image(isbn)
        st.image(img_url, width=100)
        st.markdown(f"**{row['Title']}**")
        st.caption(row['Author'])

# ------------------ PERSONALIZED RECOMMENDATIONS ------------------
st.header("🎯 Recommended for You")

user_ids = recs_df['user_id'].unique()
selected_user = st.selectbox("Select a User ID", sorted(user_ids))

if st.button("Show Recommendations"):
    user_row = recs_df[recs_df['user_id'] == selected_user]

    if not user_row.empty:
        book_ids = list(map(int, user_row.iloc[0]['recommendation'].split()))
        recommended_books = items_df[items_df['i'].isin(book_ids)]

        st.subheader("📖 Top Book Picks for You")
        cols = st.columns(5)
        for i, (_, row) in enumerate(recommended_books.iterrows()):
            with cols[i % 5]:
                isbn = str(row['ISBN Valid']).split(";")[0].strip()
                img_url = get_cover_image(isbn)
                st.image(img_url, width=100)
                st.markdown(f"**{row['Title']}**")
                st.caption(row['Author'])
    else:
        st.warning("No recommendations found for this user.")

# ------------------ BROWSE BY GENRE ------------------
st.header("📚 Browse by Genre")

top_subjects = ["Mangas", "Roman", "Sciences", "Fantasy", "Histoire"]

for subject in top_subjects:
    st.subheader(f"📖 {subject}")
    subject_books = items_df[
        items_df['Subjects'].str.contains(subject, case=False, na=False)
    ].head(5)

    cols = st.columns(5)
    for i, (_, row) in enumerate(subject_books.iterrows()):
        with cols[i % 5]:
            isbn = str(row['ISBN Valid']).split(";")[0].strip()
            img_url = get_cover_image(isbn)
            st.image(img_url, width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
