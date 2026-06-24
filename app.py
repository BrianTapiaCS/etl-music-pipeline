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
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.main { background: #07080A; }
.block-container { padding: 2rem 2.5rem 4rem 2.5rem; }

section[data-testid="stSidebar"] {
    background: #0B0D10;
    border-right: 1px solid rgba(255,255,255,0.05);
}
section[data-testid="stSidebar"] .block-container { padding: 2rem 1.2rem; }

/* Hero */
.hero { border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 1.8rem; margin-bottom: 2.4rem; }
.hero-eyebrow {
    font-size: 0.65rem; font-weight: 500; color: #7B8EE0;
    letter-spacing: 0.18em; text-transform: uppercase;
    margin-bottom: 10px; display: flex; align-items: center; gap: 8px;
}
.hero-eyebrow::before { content: ''; display: inline-block; width: 20px; height: 1px; background: #7B8EE0; }
.hero-title { font-size: 2.6rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.04em; line-height: 1.05; margin-bottom: 10px; }
.hero-title span { color: #7B8EE0; }
.hero-desc { font-size: 0.88rem; font-weight: 300; color: #8A95A8; line-height: 1.7; max-width: 680px; }

/* Metrics */
.metric-grid {
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: 1px; background: rgba(255,255,255,0.05);
    border-radius: 12px; overflow: hidden; margin-bottom: 2rem;
}
.metric-cell { background: #0B0D10; padding: 20px 22px; }
.metric-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.85rem; font-weight: 500; color: #FFFFFF;
    letter-spacing: -0.03em; line-height: 1; margin-bottom: 6px;
}
.metric-number.accent { color: #7B8EE0; }
.metric-name { font-size: 0.65rem; font-weight: 500; color: #5A6070; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 3px; }
.metric-source { font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #2E3340; }

/* Section labels */
.section-wrap { margin-bottom: 0.4rem; }
.section-title { font-size: 0.72rem; font-weight: 600; color: #FFFFFF; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 5px; }
.section-explain { font-size: 0.8rem; font-weight: 300; color: #8A95A8; line-height: 1.65; margin-bottom: 12px; }

/* Insight */
.insight {
    background: #0F1118; border: 1px solid rgba(123,142,224,0.2);
    border-left: 3px solid #7B8EE0; border-radius: 0 8px 8px 0;
    padding: 14px 18px; margin-bottom: 2rem;
    font-size: 0.82rem; color: #8A95A8; line-height: 1.7;
}
.insight strong { color: #B0BEFF; font-weight: 500; }

/* Divider */
.section-divider { height: 1px; background: rgba(255,255,255,0.05); margin: 2.5rem 0; }

/* Sidebar */
.sb-logo { font-size: 1rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em; margin-bottom: 2px; }
.sb-sub { font-size: 0.65rem; color: #3A4050; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1.5rem; padding-bottom: 1.2rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
.sb-section { font-size: 0.58rem; font-weight: 600; color: #3A4050; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 6px; margin-top: 18px; }
.sb-item { font-size: 0.78rem; color: #8A95A8; margin-bottom: 3px; line-height: 1.5; }
.sb-item code { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #7B8EE0; background: rgba(123,142,224,0.1); padding: 1px 5px; border-radius: 3px; }
.sb-coverage { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 500; color: #7B8EE0; letter-spacing: -0.04em; line-height: 1; margin-bottom: 2px; }
.sb-note { font-size: 0.68rem; color: #3A4050; }
.sb-pill { display: inline-block; font-size: 0.6rem; font-weight: 500; color: #5A6070; border: 1px solid rgba(255,255,255,0.07); border-radius: 20px; padding: 2px 9px; margin: 2px 2px 2px 0; letter-spacing: 0.04em; }

/* Streamlit overrides */
div[data-testid="stDataFrame"] { border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; overflow: hidden; }
.stSelectbox > div > div { background: #0B0D10; border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; }
.stTextInput > div > div > input { background: #0B0D10; border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; color: #FFFFFF; font-family: 'Sora', sans-serif; }
.stTextInput > div > div > input::placeholder { color: #3A4050; }
</style>
""", unsafe_allow_html=True)

ACCENT   = "#7B8EE0"
REJECT   = "#C0392B"
BG_CHART = "#0B0D10"
GRID     = "rgba(255,255,255,0.04)"
TEXT     = "#8A95A8"

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
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
    df = pd.read_sql("""SELECT artist_id,
        COALESCE(name,'Unknown') as name,
        COALESCE(type,'Unknown') as type,
        COALESCE(gender,'Unknown') as gender,
        COALESCE(country,'Unknown') as country,
        COALESCE(disambiguation,'Unknown') as disambiguation
        FROM stg_artists""", conn)
    conn.close()
    return df

@st.cache_data
def load_rejects():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM stg_rejects", conn)
    conn.close()
    return df

def chart_base(fig, h=300):
    fig.update_layout(
        paper_bgcolor=BG_CHART, plot_bgcolor=BG_CHART,
        font=dict(color=TEXT, family="Sora, sans-serif", size=11),
        height=h, margin=dict(l=0, r=48, t=8, b=0),
        showlegend=False, coloraxis_showscale=False,
        xaxis=dict(gridcolor=GRID, showgrid=True, zeroline=False,
                   tickfont=dict(size=10, color="#5A6070")),
        yaxis=dict(gridcolor=GRID, showgrid=False, zeroline=False,
                   tickfont=dict(size=10, color="#8A95A8")),
    )
    return fig

df_tracks  = load_tracks()
df_artists = load_artists()
df_rejects = load_rejects()

# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sb-logo'>ETL Music Pipeline</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-sub'>Data Ingestion Subsystem</div>", unsafe_allow_html=True)

    st.markdown("<div class='sb-section'>What this is</div>", unsafe_allow_html=True)
    st.markdown("""<div class='sb-item'>A Python pipeline that pulls music data
    from two sources, checks every row for problems,
    and stores only clean data in a database.</div>""", unsafe_allow_html=True)

    st.markdown("<div class='sb-section'>Data Sources</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-item'>Spotify CSV — 114,000 song tracks</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-item'>MusicBrainz API — live artist lookup</div>", unsafe_allow_html=True)

    st.markdown("<div class='sb-section'>Database Tables</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-item'><code>stg_tracks</code> — 89,740 clean songs</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-item'><code>stg_artists</code> — 25 artists</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-item'><code>stg_rejects</code> — 24,260 bad rows</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-note' style='margin-top:4px;'>stg = staging, a holding area for validated data</div>", unsafe_allow_html=True)

    st.markdown("<div class='sb-section'>Test Coverage</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-coverage'>100%</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-note'>20 tests · pytest · requirement was 80%</div>", unsafe_allow_html=True)

    st.markdown("<div class='sb-section'>Filters</div>", unsafe_allow_html=True)
    genre_filter = st.selectbox("Genre", ["All"] + sorted(df_tracks['track_genre'].unique().tolist()), label_visibility="collapsed")
    search = st.text_input("Search", placeholder="song or artist name", label_visibility="collapsed")

    st.markdown("<div class='sb-section'>Built with</div>", unsafe_allow_html=True)
    for t in ["Python","pandas","PostgreSQL","psycopg2","pytest","Streamlit","Plotly"]:
        st.markdown(f"<span class='sb-pill'>{t}</span>", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
  <div class='hero-eyebrow'>Data Engineering · Bootcamp Project</div>
  <div class='hero-title'>ETL <span>Music</span> Pipeline</div>
  <div class='hero-desc'>
    This dashboard shows the results of a Python ETL pipeline.
    It pulled 114,000 Spotify songs and 25 artists from the MusicBrainz website,
    checked every row for problems, removed bad data,
    and stored the clean results in a PostgreSQL database.
    Everything you see below comes directly from that database.
  </div>
</div>
""", unsafe_allow_html=True)

# ── METRICS ──────────────────────────────────────────────
st.markdown(f"""
<div class='metric-grid'>
  <div class='metric-cell'>
    <div class='metric-name'>Songs loaded</div>
    <div class='metric-number accent'>{len(df_tracks):,}</div>
    <div class='metric-source'>from stg_tracks</div>
  </div>
  <div class='metric-cell'>
    <div class='metric-name'>Artists loaded</div>
    <div class='metric-number'>{len(df_artists)}</div>
    <div class='metric-source'>from stg_artists</div>
  </div>
  <div class='metric-cell'>
    <div class='metric-name'>Rows rejected</div>
    <div class='metric-number'>{len(df_rejects):,}</div>
    <div class='metric-source'>from stg_rejects</div>
  </div>
  <div class='metric-cell'>
    <div class='metric-name'>Music genres</div>
    <div class='metric-number'>{df_tracks['track_genre'].nunique()}</div>
    <div class='metric-source'>from stg_tracks</div>
  </div>
  <div class='metric-cell'>
    <div class='metric-name'>Avg popularity</div>
    <div class='metric-number'>{df_tracks['popularity'].mean():.1f}<span style='font-size:1rem;color:#3A4050'>/100</span></div>
    <div class='metric-source'>Spotify score · stg_tracks</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── INSIGHT ───────────────────────────────────────────────
st.markdown(f"""
<div class='insight'>
  <strong>What happened when the pipeline ran:</strong> It started with
  <strong>114,000 raw songs</strong> from a Spotify dataset.
  After checking every row for problems, <strong>89,740 passed</strong> and were saved.
  <strong>24,260 were rejected</strong> — almost all because the same song appeared
  multiple times under different genre labels in the original file.
  Every rejected row is stored with the exact reason, so nothing disappears silently.
</div>
""", unsafe_allow_html=True)

# ── ROW 1 ─────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("""<div class='section-wrap'>
      <div class='section-title'>Top 10 genres by song count</div>
      <div class='section-explain'>The Spotify dataset was built with roughly 1,000 songs per genre across 113 genres — so every bar looks similar. Small differences come from removing duplicate songs during cleaning.</div>
    </div>""", unsafe_allow_html=True)
    gc = df_tracks['track_genre'].value_counts().head(10).reset_index()
    gc.columns = ['genre','count']
    fig = px.bar(gc, x='count', y='genre', orientation='h', text='count', color_discrete_sequence=[ACCENT])
    fig.update_traces(textposition='outside', textfont=dict(color="#8A95A8", size=10), marker_line_width=0)
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(chart_base(fig, 340), use_container_width=True)

with col2:
    st.markdown("""<div class='section-wrap'>
      <div class='section-title'>Countries of artists named Drake</div>
      <div class='section-explain'>The pipeline searched the MusicBrainz music database live for "Drake" and got back 25 real, different people — not the same person 25 times. The 7 from the US are 7 distinct artists who happen to share the name Drake.</div>
    </div>""", unsafe_allow_html=True)
    cc = df_artists[df_artists['country'] != 'Unknown']['country'].value_counts().head(10).reset_index()
    cc.columns = ['country','count']
    fig = px.bar(cc, x='country', y='count', text='count', color_discrete_sequence=[ACCENT])
    fig.update_traces(textposition='outside', textfont=dict(color="#8A95A8", size=10), marker_line_width=0)
    st.plotly_chart(chart_base(fig, 340), use_container_width=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── ROW 2 ─────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""<div class='section-wrap'>
      <div class='section-title'>How popular are these songs?</div>
      <div class='section-explain'>Spotify scores every song 0–100 based on how much it's being streamed right now, not ever. Most songs are obscure. Only 1,282 songs score 76–100 — those are the current hits.</div>
    </div>""", unsafe_allow_html=True)
    pb = pd.cut(df_tracks['popularity'], bins=[0,25,50,75,100],
                labels=['0–25  Unknown','26–50  Moderate','51–75  Popular','76–100  Hit'])
    pc = pb.value_counts().sort_index().reset_index()
    pc.columns = ['range','count']
    fig = px.bar(pc, x='range', y='count', text='count', color_discrete_sequence=[ACCENT])
    fig.update_traces(textposition='outside', textfont=dict(color="#8A95A8", size=10), marker_line_width=0)
    st.plotly_chart(chart_base(fig, 300), use_container_width=True)

with col2:
    st.markdown("""<div class='section-wrap'>
      <div class='section-title'>Explicit vs clean songs</div>
      <div class='section-explain'>Spotify marks each song as explicit or clean. This shows the split across all 89,740 loaded songs. The flag comes directly from Spotify — the pipeline stores it as-is.</div>
    </div>""", unsafe_allow_html=True)
    ec = df_tracks['explicit'].value_counts().reset_index()
    ec.columns = ['explicit','count']
    ec['explicit'] = ec['explicit'].map({True:'Explicit', False:'Clean'})
    fig = px.pie(ec, values='count', names='explicit',
                 color_discrete_map={'Explicit':REJECT,'Clean':ACCENT}, hole=0.62)
    fig.update_traces(textposition='inside', textinfo='percent+label',
                      textfont=dict(size=11, color="#FFFFFF"),
                      marker=dict(line=dict(color=BG_CHART, width=2)))
    fig.update_layout(paper_bgcolor=BG_CHART, plot_bgcolor=BG_CHART,
                      font=dict(color=TEXT, family="Sora, sans-serif"),
                      height=300, margin=dict(l=0,r=0,t=8,b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown("""<div class='section-wrap'>
      <div class='section-title'>Why were songs rejected?</div>
      <div class='section-explain'>Every song that failed the quality check is stored here with the specific reason why. Almost all 24,258 duplicates exist because Spotify lists the same song once per genre it belongs to.</div>
    </div>""", unsafe_allow_html=True)
    rr = df_rejects.groupby('reason').size().reset_index(name='count')
    fig = px.bar(rr, x='count', y='reason', orientation='h', text='count', color_discrete_sequence=[REJECT])
    fig.update_traces(textposition='outside', textfont=dict(color="#8A95A8", size=10), marker_line_width=0)
    st.plotly_chart(chart_base(fig, 300), use_container_width=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── ROW 3 ─────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("""<div class='section-wrap'>
      <div class='section-title'>Which genres have the most popular songs on average?</div>
      <div class='section-explain'>For each genre, this averages the Spotify popularity score across all its songs. Higher means people are actively streaming those songs right now.</div>
    </div>""", unsafe_allow_html=True)
    ap = df_tracks.groupby('track_genre')['popularity'].mean().sort_values(ascending=False).head(10).reset_index()
    ap.columns = ['genre','avg_popularity']
    ap['avg_popularity'] = ap['avg_popularity'].round(1)
    fig = px.bar(ap, x='avg_popularity', y='genre', orientation='h', text='avg_popularity', color_discrete_sequence=[ACCENT])
    fig.update_traces(textposition='outside', textfont=dict(color="#8A95A8", size=10), marker_line_width=0)
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(chart_base(fig, 340), use_container_width=True)

with col2:
    st.markdown("""<div class='section-wrap'>
      <div class='section-title'>Artists appearing in the most songs</div>
      <div class='section-explain'>Artists with high counts here appear across many genres in the dataset — not because they made more songs, but because their songs were tagged under multiple genres in the Spotify source file.</div>
    </div>""", unsafe_allow_html=True)
    ac = df_tracks['artists'].value_counts().head(10).reset_index()
    ac.columns = ['artist','count']
    fig = px.bar(ac, x='count', y='artist', orientation='h', text='count', color_discrete_sequence=[ACCENT])
    fig.update_traces(textposition='outside', textfont=dict(color="#8A95A8", size=10), marker_line_width=0)
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(chart_base(fig, 340), use_container_width=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── TOP 10 TRACKS ─────────────────────────────────────────
st.markdown("""<div class='section-wrap'>
  <div class='section-title'>Top 10 most popular songs right now</div>
  <div class='section-explain'>Ranked by Spotify's popularity score out of 100. This score reflects recent streaming activity, not how famous a song was historically.</div>
</div>""", unsafe_allow_html=True)
tt = df_tracks.nlargest(10,'popularity')[['track_name','artists','album_name','popularity','track_genre']].copy()
tt.index = range(1,11)
tt.columns = ['Song','Artist','Album','Popularity (0–100)','Genre']
st.dataframe(tt, use_container_width=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── TRACKS EXPLORER ───────────────────────────────────────
st.markdown("""<div class='section-wrap'>
  <div class='section-title'>Search all 89,740 songs</div>
  <div class='section-explain'>Type a song name or artist in the sidebar search box. Typos are fine — the search finds the closest match automatically.</div>
</div>""", unsafe_allow_html=True)

filtered = df_tracks.copy()
if genre_filter != "All":
    filtered = filtered[filtered['track_genre'] == genre_filter]

used_fuzzy = False
fuzzy_suggestions = []
if search:
    s = search.lower().strip()
    exact = filtered[
        filtered['track_name'].str.lower().str.contains(s, na=False) |
        filtered['artists'].str.lower().str.contains(s, na=False)
    ]
    if len(exact) > 0:
        filtered = exact
    else:
        candidates = pd.concat([filtered['artists'].dropna(), filtered['track_name'].dropna()]).unique().tolist()
        fuzzy_suggestions = difflib.get_close_matches(search, candidates, n=5, cutoff=0.6)
        if fuzzy_suggestions:
            used_fuzzy = True
            mask = filtered['artists'].isin(fuzzy_suggestions) | filtered['track_name'].isin(fuzzy_suggestions)
            filtered = filtered[mask]
        else:
            filtered = filtered.iloc[0:0]

if search and used_fuzzy:
    st.warning(f"No exact match for **\"{search}\"** — showing closest results: {', '.join(fuzzy_suggestions)}")
elif search and len(filtered) > 0:
    st.success(f"Found **{len(filtered):,}** songs matching **\"{search}\"**")
elif search and len(filtered) == 0:
    st.error(f"No songs found for **\"{search}\"** — try a different spelling")
elif genre_filter != "All":
    st.info(f"Showing **{len(filtered):,}** songs in the **{genre_filter}** genre")
else:
    st.markdown(f"<div class='section-explain'>Showing all {len(filtered):,} songs. Use the sidebar to search or filter.</div>", unsafe_allow_html=True)

fd = filtered[['track_name','artists','album_name','popularity','track_genre']].head(50).copy()
fd.columns = ['Song','Artist','Album','Popularity','Genre']
fd.index = range(1, len(fd)+1)
st.dataframe(fd, use_container_width=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# ── ARTISTS ───────────────────────────────────────────────
st.markdown("""<div class='section-wrap'>
  <div class='section-title'>25 artists returned by the MusicBrainz search</div>
  <div class='section-explain'>The pipeline searched the MusicBrainz music database live for the name "Drake." It returned 25 real, distinct artists — musicians, composers, bands — whose names match or include Drake. These are not the same person. The search query is set in the config file and runs every time the pipeline executes.</div>
</div>""", unsafe_allow_html=True)
ad = df_artists[['name','type','gender','country','disambiguation']].copy()
ad.columns = ['Name','Type','Gender','Country','Description']
ad.index = range(1, len(ad)+1)
st.dataframe(ad, use_container_width=True)