import streamlit as st
import pandas as pd
import os
import webbrowser

# ---------- CONFIG ----------
st.set_page_config(page_title="📚 Book Recommender", layout="wide", initial_sidebar_state="expanded")

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "selected_user" not in st.session_state:
    st.session_state.selected_user = None

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items_improved_image2.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    return recs, items, interactions

recs_df, items_df, interactions_df = load_data()

# ---------- SIDEBAR ----------
st.sidebar.title("🔧 Settings")
st.sidebar.markdown("Chat with the system to get personalized book recommendations using precomputed TF-IDF matches.")
st.session_state.selected_user = st.sidebar.selectbox("Select a User ID", recs_df['user_id'].unique(), index=0, key="user_select")

if st.sidebar.button("Show Recommendations", key="sidebar_show_recs"):
    user_row = recs_df[recs_df['user_id'] == st.session_state.selected_user]

    if not user_row.empty:
        book_ids = list(map(int, user_row.iloc[0]['recommendation'].split()))[:10]
        recommended_books = items_df[items_df['i'].isin(book_ids)]

        st.subheader("📖 Top Book Picks for You")
        cols = st.columns(5)
        for i, (_, row) in enumerate(recommended_books.iterrows()):
            interactions_count = interactions_df[interactions_df['i'] == row['i']].shape[0]
            with cols[i % 5]:
                st.image(row['cover_url'], width=100)
                st.markdown(f"**{row['Title']}**")
                st.caption(row['Author'])
                st.caption(f"👥 {interactions_count} interactions")
                if row.get('link'):
                    st.link_button("🔗 Open Link", row['link'], use_container_width=True)
                if st.button("❤️ Save", key=f"rec_{row['i']}"):
                    if row['i'] not in st.session_state.favorites:
                        st.session_state.favorites.append(row['i'])
    else:
        st.warning("No recommendations found for this user.")

# ---------- SEARCH BAR ----------
st.title("🔍 Search the Book Database")
search_query = st.text_input("Search for a book by title, author, or subject:")
if search_query:
    results = items_df[
        items_df['Title'].str.lower().str.contains(search_query.lower(), na=False) |
        items_df['Author'].str.lower().str.contains(search_query.lower(), na=False) |
        items_df['Subjects'].str.lower().str.contains(search_query.lower(), na=False)
    ]
    st.subheader(f"Found {len(results)} result(s):")
    cols = st.columns(5)
    for i, (_, row) in enumerate(results.head(15).iterrows()):
        interactions_count = interactions_df[interactions_df['i'] == row['i']].shape[0]
        with cols[i % 5]:
            st.image(row.get('cover_url', "https://via.placeholder.com/128x195.png?text=No+Image"), width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
            st.caption(f"👥 {interactions_count} interactions")
            if row.get('link'):
                st.link_button("🔗 Open Link", row['link'], use_container_width=True)

# ------------------ FAVORITES SECTION ------------------
if st.session_state.favorites:
    st.subheader("⭐ Your Favorite Books")
    fav_books = items_df[items_df['i'].isin(st.session_state.favorites)]
    clear = st.button("🗑️ Clear Favorites")
    if clear:
        st.session_state.favorites = []

    cols = st.columns(5)
    for i, (_, row) in enumerate(fav_books.iterrows()):
        interactions_count = interactions_df[interactions_df['i'] == row['i']].shape[0]
        with cols[i % 5]:
            st.image(row['cover_url'], width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
            st.caption(f"👥 {interactions_count} interactions")
            if row.get('link'):
                st.link_button("🔗 Open Link", row['link'], use_container_width=True)

# ------------------ MOST POPULAR ------------------
st.title("📚 Book Recommendation System")
st.header("🔥 Most Popular Books")

popular_ids = interactions_df['i'].value_counts().head(10).index.tolist()
popular_books = items_df[items_df['i'].isin(popular_ids)]

cols = st.columns(5)
for i, (_, row) in enumerate(popular_books.iterrows()):
    interactions_count = interactions_df[interactions_df['i'] == row['i']].shape[0]
    with cols[i % 5]:
        st.image(row['cover_url'], width=100)
        st.markdown(f"**{row['Title']}**")
        st.caption(row['Author'])
        st.caption(f"👥 {interactions_count} interactions")
        if row.get('link'):
            st.link_button("🔗 Open Link", row['link'], use_container_width=True)
        if st.button("❤️ Save", key=f"pop_{row['i']}"):
            if row['i'] not in st.session_state.favorites:
                st.session_state.favorites.append(row['i'])

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
        interactions_count = interactions_df[interactions_df['i'] == row['i']].shape[0]
        with cols[i % 5]:
            st.image(row['cover_url'], width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
            st.caption(f"👥 {interactions_count} interactions")
            if row.get('link'):
                st.link_button("🔗 Open Link", row['link'], use_container_width=True)
            if st.button("❤️ Save", key=f"genre_{row['i']}"):
                if row['i'] not in st.session_state.favorites:
                    st.session_state.favorites.append(row['i'])
