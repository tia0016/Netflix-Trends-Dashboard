import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------ Page Config ------------------------
st.set_page_config(page_title="Netflix Trends Dashboard", layout="wide")

# ------------------------ Netflix Logo (from web) ------------------------
st.markdown(
    "<div style='text-align: center;'><img src='https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg' width='160'></div>",
    unsafe_allow_html=True
)

# ------------------------ Custom CSS ------------------------
st.markdown("""
    <style>
        body {
            background-color: #141414;
            color: #ffffff;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #E50914;
            font-family: 'Segoe UI', sans-serif;
        }
        .stButton>button {
            background-color: #E50914;
            color: white;
            border-radius: 5px;
        }
        .css-1v3fvcr, .css-18e3th9 {
            background-color: #1c1c1c !important;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------ Header ------------------------
st.markdown("<h1 style='text-align: center;'>🎬 Netflix Trends Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dive into the data behind your favorite Netflix shows and movies!</p>", unsafe_allow_html=True)
st.markdown("---")

# ------------------------ Load Data ------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    return df.dropna(subset=['year_added'])

df = load_data()

# ------------------------ Sidebar Filters ------------------------
st.sidebar.header("🔎 Filter Options")

# Reset button
if st.sidebar.button("🔁 Reset Filters"):
    st.experimental_rerun()

# Type Filter
content_type = st.sidebar.selectbox("Select Type", options=["All"] + sorted(df['type'].dropna().unique()))

# Rating Filter with Meaningful Labels
rating_labels = {
    "TV-MA": "TV-MA (Mature Audience 18+)",
    "PG": "PG (Parental Guidance)",
    "R": "R (Restricted 17+)",
    "TV-14": "TV-14 (Teens and older)",
    "TV-Y": "TV-Y (All children)",
    "TV-Y7": "TV-Y7 (Ages 7+)",
    "G": "G (General Audience)",
    "NR": "NR (Not Rated)",
    "TV-G": "TV-G (General Audience)",
    "NC-17": "NC-17 (Adults Only)",
    "UR": "UR (Unrated)",
    "PG-13": "PG-13 (Parents Strongly Cautioned)"
}

available_ratings = sorted(df['rating'].dropna().unique())
dropdown_options = ["All"] + [rating_labels.get(r, r + " (Unknown)") for r in available_ratings]
selected_rating_label = st.sidebar.selectbox("Select Rating", options=dropdown_options)
label_to_code = {v: k for k, v in rating_labels.items()}
selected_rating_code = label_to_code.get(selected_rating_label, None)

# Year Range Filter
min_year = int(df['year_added'].min())
max_year = int(df['year_added'].max())
selected_year_range = st.sidebar.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(2010, 2021))

# Apply filters
filtered_df = df.copy()

if content_type != "All":
    filtered_df = filtered_df[filtered_df['type'] == content_type]

if selected_rating_label != "All" and selected_rating_code:
    filtered_df = filtered_df[filtered_df['rating'] == selected_rating_code]

filtered_df = filtered_df[
    (filtered_df['year_added'] >= selected_year_range[0]) &
    (filtered_df['year_added'] <= selected_year_range[1])
]

# Summary of filters
st.markdown(
    f"<p>Currently showing: <strong>{content_type}</strong> | Rating: <strong>{selected_rating_label}</strong> | Year Range: <strong>{selected_year_range[0]} – {selected_year_range[1]}</strong></p>",
    unsafe_allow_html=True
)

# ------------------------ Charts Row 1 ------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Releases per Year")
    st.caption("Number of Netflix titles released each year based on your selected filters.")
    year_count = filtered_df['year_added'].value_counts().sort_index()
    fig, ax = plt.subplots()
    year_count.plot(kind='line', marker='o', color='#E50914', ax=ax)
    ax.set_xlabel("Year", color='white')
    ax.set_ylabel("Number of Titles", color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, color='#444444')
    ax.set_facecolor("#111")
    fig.patch.set_facecolor('#111')
    st.pyplot(fig)

with col2:
    st.subheader("🌍 Top 10 Countries")
    st.caption("Countries that produced the most Netflix content (some titles have more than one country).")
    top_countries = filtered_df['country'].dropna().str.split(', ').explode().value_counts().head(10)
    fig2, ax2 = plt.subplots()
    top_countries.plot(kind='barh', color='#E50914', ax=ax2)
    ax2.set_xlabel("Number of Titles", color='white')
    ax2.tick_params(axis='x', colors='white')
    ax2.tick_params(axis='y', colors='white')
    ax2.invert_yaxis()
    ax2.set_facecolor("#111")
    fig2.patch.set_facecolor('#111')
    st.pyplot(fig2)

# ------------------------ Charts Row 2 ------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("🎭 Popular Genres")
    st.caption("Top 10 genres of Netflix content based on your selected filters.")
    genre_series = filtered_df['listed_in'].dropna().str.split(', ').explode()
    top_genres = genre_series.value_counts().head(10)
    st.bar_chart(top_genres, use_container_width=True)

with col4:
    st.subheader("🧑‍🎤 Top Actors")
    st.caption("Actors who appeared most frequently in Netflix titles within your selected filters.")
    top_actors = filtered_df['cast'].dropna().str.split(', ').explode().value_counts().head(10)
    st.bar_chart(top_actors, use_container_width=True)

# ------------------------ Directors ------------------------
st.subheader("🎬 Top 10 Directors")
st.caption("Directors with the highest number of titles on Netflix based on your filters.")
top_directors = filtered_df['director'].dropna().str.split(', ').explode().value_counts().head(10)
st.bar_chart(top_directors, use_container_width=True)
