import os
from dotenv import load_dotenv
import pickle
import streamlit as st
import pandas as pd
import requests


# --- 1. Load Data and Model ---
try:
    movies_dict = pickle.load(open('movies_list.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Error: 'movies_list.pkl' or 'similarity.pkl' not found. Please run 'model_prep.py' first.")
    st.stop()


# 2. Helper Functions ---


load_dotenv()  # loads .env if exists

API_KEY = os.getenv("TMDB_API_KEY")
if not API_KEY:
    st.error("TMDB API key is not set. Please set TMDB_API_KEY as an environment variable or in a .env file.")
    st.stop()

# (fetch_poster و recommend) ...
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to TMDb API: {e}")
        return "https://via.placeholder.com/500x750?text=No+Poster+Available"
    poster_path = data.get('poster_path')
    if poster_path:
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    return "https://via.placeholder.com/500x750?text=No+Poster+Available"


def recommend(movie_title):
    """Recommend 5 similar movies based on cosine similarity."""
    
    # Get index of the selected movie
    try:
        movie_index = movies[movies['title'] == movie_title].index[0]
    except IndexError:
        return ["Movie not found."], [""]

    # Retrieve similarity scores for the selected movie
    distances = similarity[movie_index]

    # Sort and get the top 5 most similar movies (excluding the selected one itself)
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movie_posters = []
    for i in movies_list:
        # Get movie ID to fetch its poster from the API
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
        
    return recommended_movies, recommended_movie_posters


# --- 3. Streamlit User Interface ---

# Page configuration
st.set_page_config(layout="wide")
st.title("🎬 Movie Recommender System")
st.markdown("---")

# Dropdown to select a movie
selected_movie_name = st.selectbox(
    "Please choose a movie from the list below:",
    movies['title'].values
)

# Button to display recommendations
if st.button("🌟 Show Recommendations", type="primary"):
    
    # Fetch recommendations
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie_name)

    # Display results
    st.subheader(f"Top 5 movies similar to **{selected_movie_name}**:")

    # Create 5 columns for displaying recommendations
    cols = st.columns(5)

    # Show poster and title in each column
    for i in range(5):
        with cols[i]:
            st.image(recommended_movie_posters[i], caption=recommended_movie_names[i], width="stretch")



