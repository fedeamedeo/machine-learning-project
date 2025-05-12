import streamlit as st
import pandas as pd

# ------------------ DATA LOAD ------------------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items_improved.csv")
    interactions = pd.read_csv("interactions.csv")
    return recs, items, interactions

recs_df, items_df, interactions_df = load_data()
# 🔥 Most Popular Books
st.title("📚 Book Recommendation System")
st.header("🔥 Most Popular Books")

# Get top 10 popular book IDs by interaction count
popular_ids = interactions_df['i'].value_counts().head(10).index.tolist()
popular_books = items_df[items_df['i'].isin(popular_ids)][['Title', 'Author', 'Subjects']]
st.dataframe(popular_books)
# 🎯 Personalized Recommendations
st.header("🎯 Recommended for You")

user_ids = recs_df['user_id'].unique()
selected_user = st.selectbox("Select a User ID", sorted(user_ids))

if st.button("Show Recommendations"):
    user_row = recs_df[recs_df['user_id'] == selected_user]
    
    if not user_row.empty:
        book_ids = list(map(int, user_row.iloc[0]['recommendation'].split()))
        recommended_books = items_df[items_df['i'].isin(book_ids)]

        st.subheader("Top Book Picks for You")
        st.dataframe(recommended_books[['Title', 'Author', 'Subjects']])
    else:
        st.warning("No recommendations found for this user.")
# 📚 Browse by Subject/Genre
st.header("📚 Browse by Genre")

# Example: top genres (you can update this list based on your dataset)
top_subjects = ["Mangas", "Roman", "Sciences", "Fantasy", "Histoire"]

for subject in top_subjects:
    st.subheader(f"📖 {subject}")
    subject_books = items_df[
        items_df['Subjects'].str.contains(subject, case=False, na=False)
    ].head(5)  # Show 5 per genre
    
    cols = st.columns(5)
    for i, (_, row) in enumerate(subject_books.iterrows()):
        with cols[i % 5]:
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
