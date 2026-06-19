# ETL Music Pipeline

A production-style data ingestion pipeline that extracts music data from two sources, validates and transforms it, loads it into PostgreSQL, and visualizes results via a live Streamlit dashboard.

Built as a Data Ingestion Subsystem for a data engineering bootcamp — covers the full ETL lifecycle: extraction, validation, deduplication, staged loading, reject tracking, structured logging, and 100% test coverage.

## Data Sources

- **Spotify Tracks Dataset** (CSV) — 114,000 tracks with 22 columns including audio features (danceability, energy, tempo), popularity score (0-100), genre, and artist metadata. Dataset sourced from Kaggle.
- **MusicBrainz API** — Live REST API call returning artist metadata (name, country, type, gender, disambiguation) for a configurable query. No API key required.

## Pipeline Architecture

```
CSV (Spotify)       →  Extract  →  Transform  →  Load  →  stg_tracks
API (MusicBrainz)   →  Extract  →  Transform  →  Load  →  stg_artists
                                                         →  stg_rejects
```

**Layers:**

| Layer | File | Responsibility |
|---|---|---|
| Extract | `src/extract.py` | Reads CSV via pandas, calls MusicBrainz API via requests |
| Transform | `src/transform.py` | Validates, cleans, and deduplicates data |
| Load | `src/load.py` | Writes to PostgreSQL using parameterized UPSERT queries |
| Config | `src/config.py` | Reads YAML configuration file |
| Orchestration | `main.py` | Runs the full pipeline end to end |
| Dashboard | `app.py` | Live Streamlit dashboard reading from PostgreSQL |

## Project Structure

```
etl-music-pipeline/
  config/
    sources.yml        ← Data sources, target tables, and validation rules
  data/
    spotify-tracks-dataset.csv  ← Raw Spotify data (114,000 rows)
  sql/
    migrations/
      001_create_stg_tracks.sql
      002_create_stg_artists.sql
      003_create_stg_rejects.sql
      README.md        ← Table schemas and migration instructions
  src/
    extract.py         ← CSV and API extraction
    transform.py       ← Validation, cleaning, deduplication
    load.py            ← PostgreSQL loading with UPSERT and reject tracking
    config.py          ← YAML config loader
  tests/
    test_extract.py    ← CSV and API extraction tests
    test_transform.py  ← Validation and cleaning tests
    test_load.py       ← Load function tests (mocked DB)
    test_config.py     ← Config loading tests
  app.py               ← Streamlit dashboard
  demo.ipynb           ← End-to-end pipeline demo with real output
  main.py              ← Pipeline entry point
  requirements.txt     ← Python dependencies
```

## Validation Rules

Defined in `config/sources.yml` and enforced in `src/transform.py`.

**Tracks (`stg_tracks`):**
- Drops rows with any missing values
- Rejects tracks with popularity outside 0–100
- Removes duplicate `track_id` entries (deduplication by primary key)

**Artists (`stg_artists`):**
- Drops rows missing `id` or `name`
- Removes duplicate `artist_id` entries

All rejected rows are stored in `stg_rejects` with the source name, original payload (JSONB), and rejection reason.

## Results

| Metric | Value |
|---|---|
| Raw tracks extracted | 114,000 |
| Clean tracks loaded | 89,740 |
| Rejected rows | 24,260 |
| Rejection reason | ~24,258 duplicate track IDs (same song appears across multiple genre tags in source data), 2 missing values |
| Artists loaded | 25 |
| Genres | 113 |
| Average popularity | 33.2 |

## Structured Logging

Every pipeline run produces timestamped structured logs:

```
INFO Loaded config from config/sources.yml
INFO Extracted 114000 rows from data/spotify-tracks-dataset.csv
INFO Before cleaning: 114000 rows
INFO After cleaning: 89740 rows | Rejected: 24260 rows
INFO Loaded 89740 tracks into stg_tracks
INFO Loaded 24260 rejected rows into stg_rejects
INFO ingest.end source=spotify_tracks status=success
INFO Extracted 25 artists from MusicBrainz for query: Drake
INFO Loaded 25 artists into stg_artists
INFO ingest.end source=musicbrainz_artists status=success
```

## Database Tables

```sql
-- Clean Spotify tracks
CREATE TABLE stg_tracks (
    track_id TEXT PRIMARY KEY,
    artists TEXT, album_name TEXT, track_name TEXT,
    popularity INTEGER, duration_ms INTEGER, explicit BOOLEAN,
    danceability FLOAT, energy FLOAT, tempo FLOAT,
    track_genre TEXT, _loaded_at TIMESTAMP DEFAULT NOW()
);

-- MusicBrainz artist metadata
CREATE TABLE stg_artists (
    artist_id TEXT PRIMARY KEY,
    name TEXT, type TEXT, gender TEXT,
    country TEXT, disambiguation TEXT,
    _loaded_at TIMESTAMP DEFAULT NOW()
);

-- Rejected rows with reason
CREATE TABLE stg_rejects (
    id SERIAL PRIMARY KEY,
    source_name TEXT NOT NULL,
    raw_payload JSONB NOT NULL,
    reason TEXT NOT NULL,
    rejected_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## Setup

```bash
git clone https://github.com/BrianTapiaCS/etl-music-pipeline.git
cd etl-music-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=yourpassword
```

Run the SQL migrations (optional — `load.py` also creates tables automatically):

```bash
psql -U postgres -f sql/migrations/001_create_stg_tracks.sql
psql -U postgres -f sql/migrations/002_create_stg_artists.sql
psql -U postgres -f sql/migrations/003_create_stg_rejects.sql
```

Run the pipeline:

```bash
python main.py
```

## Dashboard

```bash
streamlit run app.py
```

The dashboard reads live from PostgreSQL and shows: pipeline metrics, top genres, artist countries, popularity distribution, explicit vs clean breakdown, rejection reasons, average popularity by genre, top artists by track count, top 10 most popular tracks, and a searchable tracks explorer with fuzzy search fallback.

## Testing

```bash
pytest --cov=src tests/
```

20 tests across 4 files — 100% coverage (requirement was 80%).

| File | Tests | What it covers |
|---|---|---|
| `test_transform.py` | 5 | Missing values, invalid popularity, duplicates, artist validation |
| `test_extract.py` | 5 | CSV row count, columns, mocked API responses |
| `test_load.py` | 6 | DB connection, inserts, rejects, commit behavior |
| `test_config.py` | 4 | YAML loading, sources, paths, target tables |

## Tech Stack

- Python 3.13
- pandas
- PostgreSQL + psycopg2
- PyYAML
- python-dotenv
- requests
- pytest + coverage
- Streamlit + Plotly
- MusicBrainz API
