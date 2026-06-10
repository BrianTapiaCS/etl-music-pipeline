import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
st.cache_data.clear()

load_dotenv()

st.cache_data.clear()

st.set_page_config(page_title="ETL Music Pipeline", layout="wide")

#st.set_page_config(page_title="ETL Music Pipeline", layout="wide")

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@st.cache_data
def load_tracks():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stg_tracks", conn)
    conn.close()
    return df

@st.cache_data
def load_artists():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            artist_id,
            COALESCE(name, 'Unknown') as name,
            COALESCE(type, 'Unknown') as type,
            COALESCE(gender, 'Unknown') as gender,
            COALESCE(country, 'Unknown') as country,
            COALESCE(disambiguation, 'Unknown') as disambiguation
        FROM stg_artists
    """, conn)
    conn.close()
    return df

@st.cache_data
def load_rejects():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stg_rejects", conn)
    conn.close()
    return df

# load data
df_tracks = load_tracks()
df_artists = load_artists()
df_rejects = load_rejects()

# header
st.title("🎵 ETL Music Pipeline Dashboard")
st.markdown("Live view of data loaded from Spotify CSV and MusicBrainz API")

# metrics row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Tracks", f"{len(df_tracks):,}")
col2.metric("Total Artists", len(df_artists))
col3.metric("Total Rejects", f"{len(df_rejects):,}")
col4.metric("Genres", df_tracks['track_genre'].nunique())

st.divider()

# two columns layout
left, right = st.columns(2)

with left:
    st.subheader("🎸 Top 10 Genres")
    genre_counts = df_tracks['track_genre'].value_counts().head(10).reset_index()
    genre_counts.columns = ['genre', 'count']
    st.bar_chart(genre_counts.set_index('genre'))

with right:
    st.subheader("🌍 Artist Countries")
    country_counts = df_artists[df_artists['country'] != 'Unknown']['country'].value_counts().head(10).reset_index()
    country_counts.columns = ['country', 'count']
    st.bar_chart(country_counts.set_index('country'))

st.divider()

# rejects breakdown
st.subheader("❌ Rejection Reasons")
reject_reasons = df_rejects.groupby('reason').size().reset_index(name='count')
st.bar_chart(reject_reasons.set_index('reason'))

st.divider()

# tracks explorer
st.subheader("🔍 Tracks Explorer")
genre_filter = st.selectbox("Filter by genre", ["All"] + sorted(df_tracks['track_genre'].unique().tolist()))
if genre_filter != "All":
    filtered = df_tracks[df_tracks['track_genre'] == genre_filter]
else:
    filtered = df_tracks
st.dataframe(filtered[['track_name', 'artists', 'album_name', 'popularity', 'track_genre']].head(50))

st.divider()

# artists table
st.subheader("🎤 Artists")
st.dataframe(df_artists[['name', 'type', 'gender', 'country', 'disambiguation']])