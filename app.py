import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch movie poster from TMDB
def fetch_poster(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=b951ac56f996f2d61092f91294bcb097&language=en-US')
    data = response.json()
    return "http://image.tmdb.org/t/p/w500/" + data.get('poster_path', '') if data.get(
        'poster_path') else "https://via.placeholder.com/500x750?text=No+Image"

# Page configuration
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("Movie Recommender System")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Recommendations"])

# Load movie data
try:
    movies = pickle.load(open('movie_dict.pkl', 'rb'))

    # Convert to DataFrame if it's a dictionary
    if isinstance(movies, dict):
        movies = pd.DataFrame(movies)

    # Validate required columns
    if 'title' not in movies.columns or 'movie_id' not in movies.columns:
        st.error("The file 'movie_dict.pkl' must contain 'title' and 'movie_id' columns.")
        st.stop()
except FileNotFoundError:
    st.error("The file 'movie_dict.pkl' was not found in the current directory.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred while loading movie data: {e}")
    st.stop()

# Load similarity matrix
try:
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("The file 'similarity.pkl' was not found in the current directory.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred while loading similarity data: {e}")
    st.stop()

# Recommendation logic
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    movie_ind = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_ind]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommend_movies = []
    recommend_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommend_movies.append(movies.iloc[i[0]].title)
        poster = fetch_poster(movie_id)
        recommend_movies_posters.append(poster)

    return recommend_movies, recommend_movies_posters

# Streamlit Pages
if page == "Home":
    st.subheader("Welcome")
    st.markdown("This application helps you find new movies based on what you already like.")
    st.markdown("How It Works:")
    st.write("1. Select a movie from the list.")
    st.write("2. Click the 'Get Recommendations' button.")
    st.write("3. View a list of recommended movies with their posters.")

elif page == "Recommendations":
    selected = st.selectbox('Select a movie:', movies['title'].values)
    if st.button('Get Recommendations'):
        names, posters = recommend(selected)

        if not names:
            st.error("No recommendations found for the selected movie. Please try another.")
        else:
            st.subheader("Recommended Movies")
            movie_cols = st.columns(len(names))

            for i, col in enumerate(movie_cols):
                with col:
                    st.image(posters[i])  # Removed use_container_width for compatibility
                    st.caption(names[i])
