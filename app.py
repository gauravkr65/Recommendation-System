import pickle
import streamlit as st
import pandas as pd
import requests
from typing import List, Dict
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


### Music section
# Spotify API credentials
CLIENT_ID = "4bb2d1a95e894890b1f80d88b29d2d21"
CLIENT_SECRET = "094a6fbd19714817a2888807cce9a8c2"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def recommend_music(song):
    try:
        index = music[music['song'] == song].index[0]
        distances = sorted(list(enumerate(similarity_music[index])), reverse=True, key=lambda x: x[1])
        recommended_music_names = []
        recommended_music_posters = []
        for i in distances[1:6]:
            artist = music.iloc[i[0]].artist
            recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))
            recommended_music_names.append(music.iloc[i[0]].song)

        return recommended_music_names, recommended_music_posters
    except IndexError:
        st.error(f"Song '{song}' not found in the dataset.")
        return [], []


### Movies section
# Load your data and model
@st.cache_data
def load_data():
    final = pd.read_csv('merged.csv')
    with open('similarity_matrix.pkl', 'rb') as f:
        similar = pickle.load(f)
    final['title'] = final['title'].str.lower()
    return final, similar

final, similar = load_data()

@st.cache_data
def get_movie_id(movie_title: str, api_key: str) -> int:
    base_url = 'https://api.themoviedb.org/3'
    search_url = f'{base_url}/search/movie?api_key={api_key}&query={movie_title}'
    
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
        if data['results']:
            return data['results'][0]['id']
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching movie ID for {movie_title}: {e}")
    
    return None

@st.cache_data
def get_poster_url(movie_id: int, api_key: str) -> str:
    if movie_id is None:
        return 'https://via.placeholder.com/500x750?text=No+Poster+Available'
    
    base_url = 'https://api.themoviedb.org/3'
    movie_url = f'{base_url}/movie/{movie_id}?api_key={api_key}'
    
    try:
        response = requests.get(movie_url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f'https://image.tmdb.org/t/p/w500{poster_path}'
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster for movie ID {movie_id}: {e}")
    
    return 'https://via.placeholder.com/500x750?text=No+Poster+Available'

def recommend_movie(movie: str) -> List[Dict[str, str]]:
    api_key = '19db33b799dd4a814c887238a2ee00f3'
    movie = movie.lower()
    
    if movie not in final['title'].values:
        st.write(f"Movie '{movie}' not found in the dataset.")
        return []
    
    movie_index = final[final['title'] == movie].index[0]
    distance = similar[movie_index]
    movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movie_list:
        title = final.iloc[i[0]]['title']
        movie_id = get_movie_id(title, api_key)
        poster_url = get_poster_url(movie_id, api_key)
        recommended_movies.append({'title': title, 'poster_url': poster_url})
    
    return recommended_movies



### Musics section
# Load music data
@st.cache_data
def load_music_data():
    music = pickle.load(open('Music_Recommender\df_musics.pkl', 'rb'))
    similarity_music = pickle.load(open('Music_Recommender\musics_similarity.pkl', 'rb'))
    return music, similarity_music

music, similarity_music = load_music_data()

## Main page
# Sidebar
st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Recommendation System", ["Home", "Movie Recommender System", "Musics Recommender System", "Books Recommender System"])


### Movie 
# Home Page
if app_mode == "Home":
    st.header("Home")
    st.image("moviepic.jpg", width=900)
    st.markdown("""
    ### About the System
    This app provides recommendations in various categories:
     
    - Movies
    - Music
    - Books

    ### About the Dataset
     **Movies**
    
    The TMDb (The Movie Database) is a comprehensive movie database that provides information about movies, including details like titles, ratings, release dates, revenue, genres, and much more.

    This dataset contains a collection of 5000 movies from the TMDB database.
    
    It consist two dataset:
    - movies: it consist 20 columns and 5000 rows.
    - credits: it consist 4 columns and 5000 rows.
    
    ### Movie Recommender System
    
    This project aims to create an intuitive and user-friendly Movie Recommender System using Streamlit. The system leverages a precomputed similarity matrix to recommend movies based on a given title.

    Key Features:

    Home Page: Provides an overview of the system and the datasets used.
    - Movie Recommender System: Users can enter a movie title to receive personalized movie recommendations. Each recommendation is displayed along with its poster fetched using the TMDB API.
    - Musics and Books Recommender Systems: These systems are in under process. it will come soon.
    
     The project integrates several key technologies:

    - Streamlit: For building an interactive web interface.
    - Pandas: For data manipulation and loading.
    - Pickle: For loading precomputed similarity matrices.
    - Requests: For interacting with the TMDB API to fetch movie posters.
    
     This system is designed to be easily extendable, allowing for the addition of more sophisticated recommendation algorithms and datasets in the future. The use of caching optimizes performance, making the app responsive and efficient.
    
    """)

# Movie Recommender System Page
elif app_mode == "Movie Recommender System":
    st.header("Movie Recommender System")
    st.image("Movie_reco.jpg", width=700)
    movie_title = st.text_input("Enter a movie title:")

    if st.button("Recommend"):
        if movie_title:
            recommendations = recommend_movie(movie_title)
            if recommendations:
                st.write("Recommended movies:")
                for movie in recommendations:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(movie['poster_url'], width=100)
                    with col2:
                        st.write(movie['title'])
            else:
                st.write("No recommendations available.")
        else:
            st.write("Please enter a movie title.")

# Music Recommender System Page
elif app_mode == "Musics Recommender System":
    st.header('Music Recommender System')
    st.image("Music_Recommender\musics_reco.jpg", width=700)
    music_list = music['song'].values
    selected_song = st.selectbox(
        "Type or select a song from the dropdown",
        music_list
    )

    if st.button('Show Recommendation'):
        if selected_song:
            recommended_music_names, recommended_music_posters = recommend_music(selected_song)
            if recommended_music_names:
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.text(recommended_music_names[0])
                    st.image(recommended_music_posters[0])
                with col2:
                    st.text(recommended_music_names[1])
                    st.image(recommended_music_posters[1])
                with col3:
                    st.text(recommended_music_names[2])
                    st.image(recommended_music_posters[2])
                with col4:
                    st.text(recommended_music_names[3])
                    st.image(recommended_music_posters[3])
                with col5:
                    st.text(recommended_music_names[4])
                    st.image(recommended_music_posters[4])
            else:
                st.write("No recommendations available.")
        else:
            st.write("Please select a song.")

# Books Recommendation
elif app_mode == "Books Recommender System":
    st.header("Books Recommender System")
    st.image("Books_Recommender\Book_reco.jpg", width=700)
