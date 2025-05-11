import streamlit as st
import pickle
import pandas as pd
import requests


# Function to fetch movie poster
def fetch_poster(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=b951ac56f996f2d61092f91294bcb097&language=en-us')
    data = response.json()
    return "http://image.tmdb.org/t/p/w500/" + data.get('poster_path', '') if data.get(
        'poster_path') else "https://via.placeholder.com/500x750?text=No+Image"


st.header('Movie Recommender System')
movies = pickle.load(open('model/movie_list.pkl','rb'))
similarity = pickle.load(open('model/similarity.pkl','rb'))


# Recommendation function
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


# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title(" Movie Recommender System ")
st.sidebar.title("🔍 Explore")
page = st.sidebar.radio("Navigate", ["Home", "Recommendations"])

if page == "Home":
    st.markdown("### Welcome to the Movie Recommender! 🎥")
    st.markdown("Find your next favorite movie with our AI-powered recommendations.")
    st.markdown("## How It Works:")
    st.write("1️⃣ Select a movie you like.")
    st.write("2️⃣ Click 'Get Recommendations'.")
    st.write("3️⃣ Discover new movies tailored to your taste!")

elif page == "Recommendations":
    selected = st.selectbox('🎞️ Select a movie:', movies['title'].values)
    if st.button('🎥 Get Recommendations'):
        names, posters = recommend(selected)

        if not names:
            st.error("No recommendations found!")
        else:
            st.write("## Recommended Movies")
            movie_cols = st.columns(len(names))

            for i, col in enumerate(movie_cols):
                with col:
                    st.image(posters[i], use_container_width=True)
                    st.write(f"**{names[i]}**")
