import streamlit as st
import requests
import speech_recognition as sr

OMDB_API_KEY = "c126e2be"

# Mood-to-genre map
mood_genre_map = {
    "happy": ["Comedy", "Musical"],
    "sad": ["Drama", "Biography"],
    "angry": ["Action", "Thriller"],
    "romantic": ["Romance", "Drama"],
    "bored": ["Adventure", "Sci-Fi"],
    "curious": ["Mystery", "Sci-Fi"],
    "scared": ["Horror", "Thriller"],
    "inspired": ["Biography", "Documentary"]
}

# Genre to movies
genre_movies = {
    "Comedy": ["The Hangover", "Superbad"],
    "Musical": ["La La Land", "The Greatest Showman"],
    "Drama": ["The Pursuit of Happyness", "Forrest Gump"],
    "Biography": ["Bohemian Rhapsody", "The Social Network"],
    "Action": ["John Wick", "Mad Max: Fury Road"],
    "Thriller": ["Inception", "Gone Girl"],
    "Romance": ["The Notebook", "P.S. I Love You"],
    "Adventure": ["Interstellar", "Life of Pi"],
    "Sci-Fi": ["Arrival", "Blade Runner 2049"],
    "Mystery": ["Shutter Island", "The Prestige"],
    "Horror": ["The Conjuring", "Get Out"],
    "Documentary": ["The Last Dance", "Free Solo"]
}

def fetch_movie_data(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    return requests.get(url).json()

def recognize_mood():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("🎙️ Speak your mood clearly into the microphone...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        mood_text = recognizer.recognize_google(audio)
        return mood_text.lower().strip()
    except sr.UnknownValueError:
        st.warning("❌ Could not understand your voice. Please try again or use the dropdown.")
        return None
    except sr.RequestError:
        st.error("⚠️ Speech recognition service is unavailable.")
        return None

# Page Configuration
st.set_page_config(page_title="🎭 Mood Movie Recommender", page_icon="🎬", layout="wide")

# 🎨 Custom CSS Styling
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #fceabb, #f8b500);
    }
    .movie-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    h1 {
        color: #e91e63;
        text-align: center;
        font-size: 3em;
        margin-bottom: 0;
    }
    .stButton>button {
        background-color: #e91e63;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 🎬 App Title
st.markdown("<h1>🎬 Mood & Voice Based Movie Recommender</h1>", unsafe_allow_html=True)
st.markdown("#### Get personalized movie suggestions based on your **mood** or search by title. Now with **voice input**!")

# 🎤 Form
with st.form("mood_form"):
    user_name = st.text_input("👤 What's your name?")
    search_query = st.text_input("🔍 Search for any movie (optional):")
    use_voice = st.checkbox("🎙️ Use voice to detect mood?")
    selected_mood = ""
    if not use_voice:
        selected_mood = st.selectbox("🎭 Select your mood:", list(mood_genre_map.keys()))
    submitted = st.form_submit_button("🎞️ Get Recommendations")

# Logic After Form Submission
if submitted and user_name:
    if use_voice:
        mood_voice = recognize_mood()
        if mood_voice and mood_voice in mood_genre_map:
            selected_mood = mood_voice
            st.success(f"🗣️ You said you're feeling **{mood_voice}**")
        elif mood_voice:
            st.warning(f"'{mood_voice}' not recognized as a supported mood.")

    if selected_mood:
        if search_query:
            movie_data = fetch_movie_data(search_query)
            if movie_data.get("Response") == "True":
                st.markdown(f"### 🎬 Search Result for **{search_query.title()}**")
                with st.container():
                    st.image(movie_data.get("Poster"), width=220)
                    st.subheader(f"{movie_data.get('Title')} ({movie_data.get('Year')})")
                    st.write(f"⭐ **IMDb:** {movie_data.get('imdbRating')}")
                    st.write(f"🎭 **Genre:** {movie_data.get('Genre')}")
                    st.write(f"📝 **Plot:** {movie_data.get('Plot')}")
            else:
                st.error("❌ Movie not found. Please check spelling or try another title.")

        st.markdown(f"## 🧠 Because you're feeling **{selected_mood.title()}**, try these picks:")
        genres = mood_genre_map.get(selected_mood.lower(), [])
        shown = set()
        for genre in genres:
            for title in genre_movies.get(genre, []):
                if title in shown:
                    continue
                shown.add(title)
                data = fetch_movie_data(title)
                if data.get("Response") == "True":
                    with st.container():
                        st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                        cols = st.columns([1, 3])
                        with cols[0]:
                            st.image(data.get("Poster"), width=160)
                        with cols[1]:
                            st.subheader(f"{data.get('Title')} ({data.get('Year')})")
                            st.write(f"⭐ IMDb: {data.get('imdbRating')}")
                            st.write(f"🎭 Genre: {data.get('Genre')}")
                            st.write(f"📝 {data.get('Plot')}")
                            st.markdown(f"[🔗 IMDb Page](https://www.imdb.com/title/{data.get('imdbID')}/)")
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("")

    else:
        st.warning("Please select your mood or speak it clearly.")
elif submitted:
    st.warning("⚠️ Please enter your name to continue.")
