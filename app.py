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
st.header('Movie Recommender System Using Machine Learning')

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
        for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
            with col:
                st.text(name)
                st.image(poster)
