'''
Author: Tharun Chand Kantu
Email: tharunkantu0421@gmail.com
Date: 2024-Nov-15
'''

import pickle
import streamlit as st
import requests
from azure.storage.blob import BlobServiceClient
import os

# Azure Blob Storage connection details (Do not hardcode sensitive information, use environment variables)
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '<YOUR_AZURE_STORAGE_ACCOUNT_CONNECTION_STRING>')
CONTAINER_NAME = "pickflix-files"

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def download_blob_to_file(container_name, blob_name, local_file_name):
    """Download a blob from Azure Blob Storage to a local file."""
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    with open(local_file_name, "wb") as file:
        file.write(blob_client.download_blob().readall())

# Download required files from Azure Blob Storage
try:
    download_blob_to_file(CONTAINER_NAME, "movie_list.pkl", "movie_list.pkl")
    download_blob_to_file(CONTAINER_NAME, "similarity.pkl", "similarity.pkl")
except Exception as e:
    st.error(f"Error downloading files from Azure Blob Storage: {e}")

# Load the pickled files
try:
    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
except FileNotFoundError as e:
    st.error(f"Required file not found: {e}")
    st.stop()

def fetch_poster(movie_id):
    """Fetch the poster of a movie using The Movie Database API."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching movie poster: {e}")
        return None

def recommend(movie):
    """Recommend similar movies based on the selected movie."""
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)
        return recommended_movie_names, recommended_movie_posters
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return [], []

# Streamlit app interface
st.set_page_config(page_title="Movie Recommender", page_icon=":movie_camera:", layout="wide")

# Add a header with branding
st.markdown("""
    <style>
        .header {
            background-image: url('https://wallpapercave.com/wp/wp9049514.jpg');
            background-size: cover;
            text-align: center;
            color: white;
            padding: 50px 0;
        }
        .header h1 {
            font-size: 50px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: bold;
        }
        .header h3 {
            font-size: 30px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .contact-section {
            background-color: #f2f2f2;
            padding: 30px;
            border-radius: 8px;
        }
        .contact-section h3 {
            color: #333;
            font-size: 26px;
            font-weight: bold;
        }
        .footer {
            background-color: #222;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 18px;
        }
        .footer a {
            color: #0e76a8;
        }
        .movie-container {
            margin-top: 20px;
        }
        .movie-box {
            transition: transform 0.2s;
        }
        .movie-box:hover {
            transform: scale(1.1);
        }
        .movie-box img {
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
    </style>
    <div class="header">
        <h1>Welcome to MovieMaze</h1>
        <h3>Your Ultimate Movie Recommendation System</h3>
    </div>
""", unsafe_allow_html=True)

# Add a description of the app
st.markdown("""
    <p style='text-align: center;'>MovieMaze uses machine learning to suggest similar movies based on your favorite movie!</p>
""", unsafe_allow_html=True)

# Dropdown for movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

# Button to show recommendations
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    if recommended_movie_names and recommended_movie_posters:
        # Display the recommended movies and their posters
        cols = st.columns(5)
        with st.container():
            for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
                with col:
                    st.text(name)
                    st.image(poster, width=150)
                    st.markdown(f"<div class='movie-box'>{name}</div>", unsafe_allow_html=True)

# Contact Me section
st.markdown("""
    <div class="contact-section">
        <h3>Contact Me</h3>
        <p>If you have any questions or feedback, feel free to reach out to me!</p>
        <p>Email: <a href="mailto:tharunkantu0421@gmail.com">tharunkantu0421@gmail.com</a></p>
    </div>
""", unsafe_allow_html=True)

# Footer with your name
st.markdown("""
    <div class="footer">
        Made with ❤️ by <strong>Tharun Chand Kantu</strong>
    </div>
""", unsafe_allow_html=True)
