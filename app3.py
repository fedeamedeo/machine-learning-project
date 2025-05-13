import streamlit as st
import pandas as pd
import requests
import os
st.set_page_config(
    page_title="📚 Book Recommender",
    layout="wide",
    initial_sidebar_state="expanded"  # 👈 this keeps the sidebar open
)

# ---------- CONFIG ----------
st.set_page_config(page_title="📚 Book Recommender", layout="wide")
st.write("Python version:", os.sys.version)
# ---------- SIDEBAR CONTROLS ----------
st.sidebar.title("🔧 Controls")

lang_code = st.sidebar.selectbox(
    "🌍 Choose cover image language",
    options=["en", "fr", "de", "es", "it"],
    format_func=lambda x: {
        "en": "English", "fr": "French", "de": "German", "es": "Spanish", "it": "Italian"
    }[x]
)

selected_user = st.sidebar.selectbox("👤 Select User ID", sorted(recs_df['user_id'].unique()))
recommend_btn = st.sidebar.button("🎯 Show Recommendations")

# ---------- SESSION STATE ----------
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items_enriched_openlibrary.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    return recs, items, interactions

recs_df, items_df, interactions_df = load_data()



# ---------- COVER FETCH FUNCTION ----------
@st.cache_data
def get_cover_image_google(isbn, lang='en'):
    if not isbn:
        return "https://via.placeholder.com/128x195.png?text=No+ISBN"
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&langRestrict={lang}"
        response = requests.get(url)
        data = response.json()
        if "items" in data and "imageLinks" in data['items'][0]['volumeInfo']:
            return data['items'][0]['volumeInfo']['imageLinks']['thumbnail']
        else:
            return "https://via.placeholder.com/128x195.png?text=Not+Found"
    except:
        return "https://via.placeholder.com/128x195.png?text=Error"

# ---------- FAVORITES ----------
if st.session_state.favorites:
    st.subheader("⭐ Your Favorite Books")
    fav_books = items_df[items_df['i'].isin(st.session_state.favorites)]
    if st.button("🗑️ Clear Favorites"):
        st.session_state.favorites = []

    cols = st.columns(5)
    for i, (_, row) in enumerate(fav_books.iterrows()):
        with cols[i % 5]:
            isbn = str(row['ISBN Valid']).split(";")[0].strip()
            st.image(get_cover_image_google(isbn, lang=lang_code), width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])

# ---------- MOST POPULAR ----------
st.title("📚 Book Recommendation System")
st.header("🔥 Most Popular Books")

popular_ids = interactions_df['i'].value_counts().head(10).index.tolist()
popular_books = items_df[items_df['i'].isin(popular_ids)]

cols = st.columns(5)
for i, (_, row) in enumerate(popular_books.iterrows()):
    with cols[i % 5]:
        isbn = str(row['ISBN Valid']).split(";")[0].strip()
        st.image(get_cover_image_google(isbn, lang=lang_code), width=100)
        st.markdown(f"**{row['Title']}**")
        st.caption(row['Author'])
        if st.button("❤️ Save", key=f"pop_{row['i']}"):
            if row['i'] not in st.session_state.favorites:
                st.session_state.favorites.append(row['i'])

# ---------- PERSONALIZED RECOMMENDATIONS ----------
if recommend_btn:
    st.header("🎯 Recommended for You")
    user_row = recs_df[recs_df['user_id'] == selected_user]
    if not user_row.empty:
        book_ids = list(map(int, user_row.iloc[0]['recommendation'].split()))
        recommended_books = items_df[items_df['i'].isin(book_ids)]

        st.subheader("📖 Top Book Picks for You")
        cols = st.columns(5)
        for i, (_, row) in enumerate(recommended_books.iterrows()):
            with cols[i % 5]:
                isbn = str(row['ISBN Valid']).split(";")[0].strip()
                st.image(get_cover_image_google(isbn, lang=lang_code), width=100)
                st.markdown(f"**{row['Title']}**")
                st.caption(row['Author'])
                if st.button("❤️ Save", key=f"rec_{row['i']}"):
                    if row['i'] not in st.session_state.favorites:
                        st.session_state.favorites.append(row['i'])
    else:
        st.warning("No recommendations found for this user.")

# ---------- BROWSE BY GENRE ----------
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
            st.image(get_cover_image_google(isbn, lang=lang_code), width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
            if st.button("❤️ Save", key=f"genre_{subject}_{row['i']}"):
                if row['i'] not in st.session_state.favorites:
                    st.session_state.favorites.append(row['i'])
