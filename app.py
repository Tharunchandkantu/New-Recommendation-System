'''
Author: Tharun Chand Kantu
Email: tharunkantu0421@gmail.com
Date: 2025-Jan-21
'''

import pickle
import streamlit as st
import requests
from azure.storage.blob import BlobServiceClient
import os

# Azure Blob Storage connection details
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '<YOUR_AZURE_STORAGE_ACCOUNT_CONNECTION_STRING>')
CONTAINER_NAME = "pickflix-files"

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def download_blob_to_file(container_name, blob_name, local_file_name):
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
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    
    body {
        font-family: 'Montserrat', sans-serif;
        background-color: #0a0a0a;
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
        animation: fadeIn 2s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .header h1 {
        font-size: 72px;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        animation: slideIn 1s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateY(-50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .header h3 {
        font-size: 28px;
        font-weight: 400;
        margin-bottom: 20px;
        animation: fadeIn 2s 0.5s backwards;
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
        padding: 12px 24px;
        border-radius: 30px;
        border: none;
        transition: all 0.3s ease;
        font-size: 18px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        background-color: #b2070e;
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(229, 9, 20, 0.4);
    }
    
    .movie-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 20px;
        margin-top: 30px;
    }
    
    .movie-box {
        background-color: #1f1f1f;
        border-radius: 15px;
        padding: 15px;
        width: 200px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: popIn 0.5s;
    }
    
    @keyframes popIn {
        from { transform: scale(0.8); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    .movie-box:hover {
        transform: translateY(-10px);
        box-shadow: 0 10px 20px rgba(229, 9, 20, 0.3);
    }
    
    .movie-box img {
        border-radius: 10px;
        margin-bottom: 10px;
        width: 100%;
        height: auto;
    }
    
    .contact-section {
        background-color: #1f1f1f;
        padding: 30px;
        border-radius: 15px;
        margin-top: 50px;
        animation: slideUp 1s;
    }
    
    @keyframes slideUp {
        from { transform: translateY(50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
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
        padding: 12px;
        color: #ffffff;
        font-size: 16px;
    }
    
    .contact-form button {
        background-color: #e50914;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 12px;
        cursor: pointer;
        transition: background-color 0.3s ease;
        font-size: 18px;
        font-weight: 600;
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
        transition: color 0.3s ease;
    }
    
    .footer a:hover {
        color: #ff3c4a;
    }
    
    .movie-details {
        background-color: #1f1f1f;
        border-radius: 15px;
        padding: 20px;
        margin-top: 30px;
        animation: fadeIn 1s;
    }
    
    .movie-details h4 {
        color: #e50914;
        font-size: 24px;
        margin-bottom: 10px;
    }
    
    .movie-details p {
        font-size: 16px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header">
        <h1>MovieMaze</h1>
        <h3>Embark on Your Cinematic Journey</h3>
    </div>
""", unsafe_allow_html=True)

# App description
st.markdown("""
    <p style='text-align: center; font-size: 18px; margin-bottom: 30px;'>
        Dive into the world of cinema with MovieMaze. Our cutting-edge AI-powered recommendation system 
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
        
        # Display recommendations in rows
        for i in range(0, len(recommended_movie_names), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(recommended_movie_names):
                    with cols[j]:
                        st.image(recommended_movie_posters[i+j], caption=recommended_movie_names[i+j], use_column_width=True)
        
        # Movie details section
        st.markdown("<div class='movie-details'>", unsafe_allow_html=True)
        st.markdown(f"<h4>About {selected_movie}</h4>", unsafe_allow_html=True)
        st.markdown("<p>This is where you can add more details about the selected movie, such as plot summary, cast, director, release date, etc. You can fetch this information from an API or your database.</p>", unsafe_allow_html=True)
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
st.markdown(f"""
    <div class="footer">
        Crafted with 🎬 by <strong>Tharun Chand Kantu</strong> | 
        <a href="mailto:tharunkantu0421@gmail.com">tharunkantu0421@gmail.com</a> | 
        <a href="https://www.linkedin.com/in/tharun-chand-kantu-333531147" target="_blank">LinkedIn</a>
    </div>
""", unsafe_allow_html=True)
