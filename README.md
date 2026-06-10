# ETL Music Pipeline

A data ingestion pipeline that extracts music data from two sources, validates and transforms it, and loads it into a PostgreSQL database.

## Data Sources

- **Spotify Tracks Dataset** (CSV) — 114,000 tracks with audio features like danceability, energy, tempo, and genre
- **MusicBrainz API** — Artist metadata including country, type, and disambiguation

## Pipeline Architecture

```
CSV (Spotify)       →  Extract  →  Transform  →  Load  →  stg_tracks
API (MusicBrainz)   →  Extract  →  Transform  →  Load  →  stg_artists
                                                         →  stg_rejects
```

## Project Structure

```
etl-music-pipeline/
  config/          ← YAML configuration
  data/            ← Raw data files
  src/
    extract.py     ← Reads from CSV and API
    transform.py   ← Cleans and validates data
    load.py        ← Loads into PostgreSQL
    config.py      ← Reads YAML config
  tests/           ← PyTest test suite
  main.py          ← Pipeline entry point
  requirements.txt ← Python dependencies
```

## Validation Rules

**Tracks:**
- Drops rows with missing values
- Rejects tracks with popularity outside 0-100
- Removes duplicate track IDs

**Artists:**
- Drops rows missing ID or name
- Removes duplicate artist IDs

All rejected rows are stored in `stg_rejects` with a reason.

## Setup

1. Clone the repo
2. Create a virtual environment and activate it
3. Install dependencies
4. Create a `.env` file with your database credentials
5. Run the pipeline

```bash
git clone https://github.com/BrianTapiaCS/etl-music-pipeline.git
cd etl-music-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Environment Variables

Create a `.env` file in the root directory:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=yourpassword
```

## Testing

```bash
pytest --cov=src tests/
```

## Tech Stack

- Python
- pandas
- PostgreSQL
- psycopg2
- pytest
- MusicBrainz API