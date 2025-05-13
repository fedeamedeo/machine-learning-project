import streamlit as st
import pandas as pd
import os

# ---------- CONFIG ----------
st.set_page_config(page_title="📚 Book Recommender", layout="wide", initial_sidebar_state="expanded")



# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ---------- SIDEBAR ----------
st.sidebar.title("🔧 Settings")
st.sidebar.markdown("Chat with the system to get personalized book recommendations using precomputed TF-IDF matches.")



'''# ------------------ INIT SESSION STATE ------------------
if 'favorites' not in st.session_state:
    st.session_state.favorites = []'''

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items_improved_image2.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    return recs, items, interactions

recs_df, items_df, interactions_df = load_data()

# ------------------ FAVORITES SECTION ------------------
if st.session_state.favorites:
    st.subheader("⭐ Your Favorite Books")
    fav_books = items_df[items_df['i'].isin(st.session_state.favorites)]
    clear = st.button("🗑️ Clear Favorites")
    if clear:
        st.session_state.favorites = []

    cols = st.columns(5)
    for i, (_, row) in enumerate(fav_books.iterrows()):
        with cols[i % 5]:
            st.image(row['cover_url'], width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])

# ------------------ MOST POPULAR ------------------
st.title("📚 Book Recommendation System")
st.header("🔥 Most Popular Books")

popular_ids = interactions_df['i'].value_counts().head(10).index.tolist()
popular_books = items_df[items_df['i'].isin(popular_ids)]

cols = st.columns(5)
for i, (_, row) in enumerate(popular_books.iterrows()):
    with cols[i % 5]:
        st.image(row['cover_url'], width=100)
        st.markdown(f"**{row['Title']}**")
        st.caption(row['Author'])
        if st.button("❤️ Save", key=f"pop_{row['i']}"):
            if row['i'] not in st.session_state.favorites:
                st.session_state.favorites.append(row['i'])

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
                st.image(row['cover_url'], width=100)
                st.markdown(f"**{row['Title']}**")
                st.caption(row['Author'])
                if st.button("❤️ Save", key=f"rec_{row['i']}"):
                    if row['i'] not in st.session_state.favorites:
                        st.session_state.favorites.append(row['i'])
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
            st.image(row['cover_url'], width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
            if st.button("❤️ Save", key=f"genre_{row['i']}"):
                if row['i'] not in st.session_state.favorites:
                    st.session_state.favorites.append(row['i'])
# ------------------ FOOTER ------------------
