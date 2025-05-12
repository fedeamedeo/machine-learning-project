import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items.csv")
    return recs, items

recs_df, items_df = load_data()

# Title
st.title("📚 Book Recommendation System")

# User selection
user_ids = recs_df['user_id'].unique()
selected_user = st.selectbox("Select a User ID", sorted(user_ids))

# Show recommendations on button click
if st.button("Show Recommendations"):
    user_row = recs_df[recs_df['user_id'] == selected_user]
    
    if not user_row.empty:
        # Get list of book IDs
        book_ids = list(map(int, user_row.iloc[0]['recommendation'].split()))
        recommended_books = items_df[items_df['i'].isin(book_ids)]

        # 🎯 FILTERS SECTION
        st.subheader("🔍 Optional Filters")
        keyword_subject = st.text_input("Filter by subject keyword:")
        keyword_title = st.text_input("Filter by title keyword:")

        # Apply filters
        if keyword_subject:
            recommended_books = recommended_books[
                recommended_books['Subjects'].str.contains(keyword_subject, case=False, na=False)
            ]
        if keyword_title:
            recommended_books = recommended_books[
                recommended_books['Title'].str.contains(keyword_title, case=False, na=False)
            ]

        # Display results
        st.subheader("📖 Top Book Recommendations")
        st.dataframe(recommended_books[['Title', 'Author', 'Subjects']])
    else:
        st.warning("No recommendations found for this user.")
