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
st.set_page_config(page_title="MovieMaze", page_icon="🎬", layout="wide")

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    body {
        font-family: 'Poppins', sans-serif;
        background-color: #0f0f0f;
        color: #ffffff;
    }
    
    .header {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://wallpaperaccess.com/full/329633.jpg');
        background-size: cover;
        background-position: center;
        text-align: center;
        padding: 100px 0;
        border-radius: 0 0 50px 50px;
        margin-bottom: 30px;
    }
    
    .header h1 {
        font-size: 60px;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .header h3 {
        font-size: 24px;
        font-weight: 400;
        margin-bottom: 20px;
    }
    
    .stSelectbox {
        background-color: #2c2c2c;
        color: #ffffff;
        border-radius: 10px;
        padding: 5px;
        margin-bottom: 20px;
    }
    
    .stButton>button {
        background-color: #e50914;
        color: #ffffff;
        font-weight: 600;
        padding: 10px 20px;
        border-radius: 30px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #b2070e;
        transform: scale(1.05);
    }
    
    .movie-container {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        margin-top: 30px;
    }
    
    .movie-box {
        background-color: #1f1f1f;
        border-radius: 15px;
        padding: 15px;
        margin: 10px;
        width: 180px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .movie-box:hover {
        transform: translateY(-10px);
        box-shadow: 0 10px 20px rgba(229, 9, 20, 0.3);
    }
    
    .movie-box img {
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    .contact-section {
        background-color: #1f1f1f;
        padding: 30px;
        border-radius: 15px;
        margin-top: 50px;
    }
    
    .contact-section h3 {
        color: #e50914;
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    .contact-form {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    
    .contact-form input, .contact-form textarea {
        background-color: #2c2c2c;
        border: none;
        border-radius: 5px;
        padding: 10px;
        color: #ffffff;
    }
    
    .contact-form button {
        background-color: #e50914;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 10px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    
    .contact-form button:hover {
        background-color: #b2070e;
    }
    
    .footer {
        background-color: #1f1f1f;
        color: #ffffff;
        text-align: center;
        padding: 20px;
        margin-top: 50px;
        border-radius: 15px 15px 0 0;
    }
    
    .footer a {
        color: #e50914;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header">
        <h1>MovieMaze</h1>
        <h3>Discover Your Next Cinematic Adventure</h3>
    </div>
""", unsafe_allow_html=True)

# App description
st.markdown("""
    <p style='text-align: center; font-size: 18px; margin-bottom: 30px;'>
        Embark on a journey through the world of cinema with MovieMaze. Our advanced AI-powered recommendation system 
        will guide you to your next favorite film based on your current preferences. Let's explore the magic of movies together!
    </p>
""", unsafe_allow_html=True)

# Movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "🎬 Enter your favorite movie or select from the list",
    movie_list
)

# Recommendation button
if st.button('🚀 Discover Similar Movies'):
    with st.spinner('Searching the cinematic universe...'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    if recommended_movie_names and recommended_movie_posters:
        st.markdown("<h2 style='text-align: center; margin-top: 30px;'>Your Personalized Movie Recommendations</h2>", unsafe_allow_html=True)
        
        # Display recommendations in a more visually appealing way
        st.markdown("<div class='movie-container'>", unsafe_allow_html=True)
        for name, poster in zip(recommended_movie_names, recommended_movie_posters):
            st.markdown(f"""
                <div class='movie-box'>
                    <img src="{poster}" alt="{name}" style="width:100%; height:auto;">
                    <h4>{name}</h4>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Contact section
st.markdown("""
    <div class="contact-section">
        <h3>Get in Touch</h3>
        <p>Have questions, suggestions, or just want to talk movies? Reach out to us!</p>
        <div class="contact-form">
            <input type="text" placeholder="Your Name">
            <input type="email" placeholder="Your Email">
            <textarea placeholder="Your Message" rows="4"></textarea>
            <button type="submit">Send Message</button>
        </div>
    </div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        Crafted with 🎬 by <strong>Tharun Chand Kantu</strong> | 
        <a href="mailto:tharunkantu0421@gmail.com">tharunkantu0421@gmail.com</a> | 
        <a href="https://www.linkedin.com/in/tharun-chand-kantu/" target="_blank">LinkedIn</a>
    </div>
""", unsafe_allow_html=True)
