import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import difflib
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="ETL Music Pipeline",
    layout="wide",
    page_icon="🎵",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0b0d12; }
    section[data-testid="stSidebar"] {
        background-color: #111319;
        border-right: 1px solid #232633;
    }
    .brand { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
    .brand-dot { width: 10px; height: 10px; border-radius: 50%; background: #00d4ff; box-shadow: 0 0 12px #00d4ff; }
    .brand-text { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.01em; }
    .brand-sub { font-size: 0.72rem; color: #5b6478; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 0.08em; }
    .metric-card {
        background: linear-gradient(145deg, #14171f 0%, #10121a 100%);
        border: 1px solid #232633;
        border-radius: 10px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 2px;
        background: linear-gradient(90deg, #00d4ff, transparent);
    }
    .metric-value { font-size: 2.1rem; font-weight: 800; color: #f1f5f9; line-height: 1.15; letter-spacing: -0.02em; }
    .metric-label { font-size: 0.7rem; color: #5b6478; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 6px; }
    .section-header {
        font-size: 0.78rem; font-weight: 700; color: #8b95a8;
        text-transform: uppercase; letter-spacing: 0.08em;
        margin-bottom: 4px; padding-left: 10px;
        border-left: 2px solid #00d4ff;
    }
    .sidebar-block { background-color: #161922; border: 1px solid #232633; border-radius: 10px; padding: 14px; margin-bottom: 10px; }
    .sidebar-block-label { color: #5b6478; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.07em; font-weight: 600; margin-bottom: 6px; }
    .sidebar-block-value { color: #e2e8f0; font-size: 0.88rem; font-weight: 500; }
    .sidebar-block-sub { color: #5b6478; font-size: 0.74rem; margin-top: 2px; }
    .pill { display: inline-block; background: #1a2e35; color: #00d4ff; font-size: 0.7rem; font-weight: 600; padding: 3px 10px; border-radius: 100px; margin: 2px 4px 2px 0; }
    .coverage-big { font-size: 1.6rem; font-weight: 800; color: #00d4ff; }
    div[data-testid="stDataFrame"] { border: 1px solid #232633; border-radius: 10px; }
    hr { border-color: #1c1f29 !important; }
</style>
""", unsafe_allow_html=True)

ACCENT = "#00d4ff"
CHART_BG = "#10121a"
GRID_COLOR = "#1c1f29"
TEXT_COLOR = "#cbd5e1"

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

def chart_layout(fig, height=350):
    fig.update_layout(
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=TEXT_COLOR, family="Inter, sans-serif"),
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor=GRID_COLOR, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=GRID_COLOR, showgrid=False, zeroline=False),
    )
    return fig

df_tracks = load_tracks()
df_artists = load_artists()
df_rejects = load_rejects()

# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-dot"></div>
        <div class="brand-text">ETL Music Pipeline</div>
    </div>
    <div class="brand-sub">Data Ingestion Subsystem</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sidebar-block">
        <div class="sidebar-block-label">Data Sources</div>
        <span class="pill">Spotify CSV</span><span class="pill">MusicBrainz API</span>
        <div class="sidebar-block-sub" style="margin-top:6px;">114,000 raw Spotify tracks + live MusicBrainz artist lookup</div>
    </div>
    <div class="sidebar-block">
        <div class="sidebar-block-label">Database</div>
        <div class="sidebar-block-value">PostgreSQL</div>
        <div class="sidebar-block-sub">stg_tracks · stg_artists · stg_rejects</div>
        <div class="sidebar-block-sub">stg = staging tables (cleaned, validated data)</div>
    </div>
    <div class="sidebar-block">
        <div class="sidebar-block-label">Test Coverage</div>
        <div class="coverage-big">100%</div>
        <div class="sidebar-block-sub">20 tests · pytest · above the 80% requirement</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sidebar-block-label' style='margin-top:18px;'>Filters</div>", unsafe_allow_html=True)
    genre_filter = st.selectbox("Filter by genre", ["All"] + sorted(df_tracks['track_genre'].unique().tolist()))
    search = st.text_input("Search track or artist", placeholder="e.g. kendrick, drake, HUMBLE.")

    st.markdown("<div class='sidebar-block-label' style='margin-top:18px;'>Stack</div>", unsafe_allow_html=True)
    st.markdown("""
    <span class="pill">Python</span><span class="pill">pandas</span><span class="pill">PostgreSQL</span>
    <span class="pill">psycopg2</span><span class="pill">pytest</span><span class="pill">Streamlit</span>
    """, unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────
st.markdown("# ETL Music Pipeline")
st.markdown("<span style='color:#8b95a8;'>This dashboard shows the results of a Python ETL pipeline that extracted 114,000 Spotify tracks and 25 MusicBrainz artists, validated and cleaned them, and loaded the results into PostgreSQL staging tables.</span>", unsafe_allow_html=True)
st.markdown("---")

# ── METRICS ──────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
metrics = [
    ("Clean Tracks Loaded", f"{len(df_tracks):,}", col1),
    ("Artists Loaded", str(len(df_artists)), col2),
    ("Rows Rejected", f"{len(df_rejects):,}", col3),
    ("Unique Genres", str(df_tracks['track_genre'].nunique()), col4),
    ("Avg Popularity Score", f"{df_tracks['popularity'].mean():.1f}", col5),
]
for label, value, col in metrics:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── ROW 1 ────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">Top 10 Genres by Track Count</div>', unsafe_allow_html=True)
    st.caption("From stg_tracks. The Kaggle Spotify dataset is balanced with roughly 1,000 tracks per genre across 113 genres. Small differences like 999 vs 1,000 come from duplicate removal in the transform step.")
    genre_counts = df_tracks['track_genre'].value_counts().head(10).reset_index()
    genre_counts.columns = ['genre', 'count']
    fig = px.bar(genre_counts, x='count', y='genre', orientation='h',
                 text='count', color_discrete_sequence=[ACCENT])
    fig.update_traces(textposition='outside', textfont=dict(color=TEXT_COLOR))
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(chart_layout(fig, 380), use_container_width=True)

with col2:
    st.markdown('<div class="section-header">Artist Countries — MusicBrainz Drake Query</div>', unsafe_allow_html=True)
    st.caption("From stg_artists. This shows the countries of the 25 artists returned by the MusicBrainz API when queried for 'Drake'. These are real artists named Drake, not duplicates. The query is configured in config/sources.yml.")
    country_counts = df_artists[df_artists['country'] != 'Unknown']['country'].value_counts().head(10).reset_index()
    country_counts.columns = ['country', 'count']
    fig = px.bar(country_counts, x='country', y='count',
                 text='count', color_discrete_sequence=[ACCENT])
    fig.update_traces(textposition='outside', textfont=dict(color=TEXT_COLOR))
    st.plotly_chart(chart_layout(fig, 380), use_container_width=True)

st.markdown("---")

# ── ROW 2 ────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="section-header">Popularity Distribution</div>', unsafe_allow_html=True)
    st.caption("Spotify scores every track 0-100 based on recent streams. Most tracks in this dataset score low, meaning they are obscure songs. Only 1,282 tracks score 76-100, those are the actual hits.")
    pop_bins = pd.cut(df_tracks['popularity'], bins=[0, 25, 50, 75, 100],
                      labels=['0-25', '26-50', '51-75', '76-100'])
    pop_counts = pop_bins.value_counts().sort_index().reset_index()
    pop_counts.columns = ['range', 'count']
    fig = px.bar(pop_counts, x='range', y='count',
                 text='count', color_discrete_sequence=[ACCENT])
    fig.update_traces(textposition='outside', textfont=dict(color=TEXT_COLOR))
    st.plotly_chart(chart_layout(fig, 320), use_container_width=True)

with col2:
    st.markdown('<div class="section-header">Explicit vs Clean</div>', unsafe_allow_html=True)
    st.caption("From stg_tracks. Shows what percentage of the 89,740 loaded tracks are marked explicit by Spotify vs clean.")
    explicit_counts = df_tracks['explicit'].value_counts().reset_index()
    explicit_counts.columns = ['explicit', 'count']
    explicit_counts['explicit'] = explicit_counts['explicit'].map({True: 'Explicit', False: 'Clean'})
    fig = px.pie(explicit_counts, values='count', names='explicit',
                 color_discrete_map={'Explicit': '#ef4444', 'Clean': ACCENT},
                 hole=0.55)
    fig.update_traces(textposition='inside', textinfo='percent+label',
                      textfont=dict(color=TEXT_COLOR))
    fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                      font=dict(color=TEXT_COLOR), height=320,
                      margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown('<div class="section-header">Rejection Reasons</div>', unsafe_allow_html=True)
    st.caption("From stg_rejects. Every row that failed validation is stored here with a reason. 24,258 were duplicate track IDs, the same song listed under multiple genres in the source dataset. Only 2 had missing values.")
    reject_reasons = df_rejects.groupby('reason').size().reset_index(name='count')
    fig = px.bar(reject_reasons, x='count', y='reason', orientation='h',
                 text='count', color_discrete_sequence=['#ef4444'])
    fig.update_traces(textposition='outside', textfont=dict(color=TEXT_COLOR))
    st.plotly_chart(chart_layout(fig, 320), use_container_width=True)

st.markdown("---")

# ── ROW 3 ────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">Average Popularity by Genre</div>', unsafe_allow_html=True)
    st.caption("From stg_tracks. For each genre, this shows the average Spotify popularity score across all tracks in that genre. Higher means more streamed on average.")
    avg_pop = df_tracks.groupby('track_genre')['popularity'].mean().sort_values(ascending=False).head(10).reset_index()
    avg_pop.columns = ['genre', 'avg_popularity']
    avg_pop['avg_popularity'] = avg_pop['avg_popularity'].round(1)
    fig = px.bar(avg_pop, x='avg_popularity', y='genre', orientation='h',
                 text='avg_popularity', color_discrete_sequence=[ACCENT])
    fig.update_traces(textposition='outside', textfont=dict(color=TEXT_COLOR))
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(chart_layout(fig, 380), use_container_width=True)

with col2:
    st.markdown('<div class="section-header">Top 10 Artists by Track Count</div>', unsafe_allow_html=True)
    st.caption("From stg_tracks. Shows which artists appear most frequently across the 89,740 loaded tracks. Artists with many tracks appear across multiple genres in the dataset.")
    artist_counts = df_tracks['artists'].value_counts().head(10).reset_index()
    artist_counts.columns = ['artist', 'count']
    fig = px.bar(artist_counts, x='count', y='artist', orientation='h',
                 text='count', color_discrete_sequence=[ACCENT])
    fig.update_traces(textposition='outside', textfont=dict(color=TEXT_COLOR))
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(chart_layout(fig, 380), use_container_width=True)

st.markdown("---")

# ── TOP 10 TRACKS ─────────────────────────────────────────
st.markdown('<div class="section-header">Top 10 Most Popular Tracks</div>', unsafe_allow_html=True)
st.caption("From stg_tracks. Ranked by Spotify popularity score out of 100. Popularity is based on recent stream counts and updates over time.")
top_tracks = df_tracks.nlargest(10, 'popularity')[['track_name', 'artists', 'album_name', 'popularity', 'track_genre']].copy()
top_tracks.index = range(1, 11)
st.dataframe(top_tracks, use_container_width=True)

st.markdown("---")

# ── TRACKS EXPLORER ───────────────────────────────────────
st.markdown('<div class="section-header">Tracks Explorer</div>', unsafe_allow_html=True)
st.caption("Search across 89,740 clean tracks from stg_tracks. Typos are okay, fuzzy matching will find the closest result.")

filtered = df_tracks.copy()
if genre_filter != "All":
    filtered = filtered[filtered['track_genre'] == genre_filter]

used_fuzzy = False
fuzzy_suggestions = []

if search:
    search_lower = search.lower().strip()
    exact = filtered[
        filtered['track_name'].str.lower().str.contains(search_lower, na=False) |
        filtered['artists'].str.lower().str.contains(search_lower, na=False)
    ]
    if len(exact) > 0:
        filtered = exact
    else:
        candidates = pd.concat([
            filtered['artists'].dropna(),
            filtered['track_name'].dropna()
        ]).unique().tolist()
        fuzzy_suggestions = difflib.get_close_matches(search, candidates, n=5, cutoff=0.6)
        if fuzzy_suggestions:
            used_fuzzy = True
            mask = (
                filtered['artists'].isin(fuzzy_suggestions) |
                filtered['track_name'].isin(fuzzy_suggestions)
            )
            filtered = filtered[mask]
        else:
            filtered = filtered.iloc[0:0]

if search and used_fuzzy:
    st.warning(f"No exact match for **\"{search}\"** — showing closest matches: {', '.join(fuzzy_suggestions)}")
elif search and len(filtered) > 0:
    st.success(f"Found **{len(filtered):,}** tracks matching **\"{search}\"**")
elif search and len(filtered) == 0:
    st.error(f"No tracks found for **\"{search}\"** — try a different spelling")
elif genre_filter != "All":
    st.info(f"Showing **{len(filtered):,}** tracks in **{genre_filter}**")
else:
    st.markdown(f"Showing **{len(filtered):,}** tracks — use the sidebar to search or filter by genre", unsafe_allow_html=True)

filtered_display = filtered[['track_name', 'artists', 'album_name', 'popularity', 'track_genre']].head(50).copy()
filtered_display.index = range(1, len(filtered_display) + 1)
st.dataframe(filtered_display, use_container_width=True)

st.markdown("---")

# ── ARTISTS ───────────────────────────────────────────────
st.markdown('<div class="section-header">Artists — MusicBrainz Drake Query</div>', unsafe_allow_html=True)
st.caption("From stg_artists. These 25 artists were returned by a live MusicBrainz API call querying the name 'Drake'. They are real, distinct artists whose names match or contain Drake. The query is set in config/sources.yml and runs every time the pipeline executes.")
artists_display = df_artists[['name', 'type', 'gender', 'country', 'disambiguation']].copy()
artists_display.index = range(1, len(artists_display) + 1)
st.dataframe(artists_display, use_container_width=True)