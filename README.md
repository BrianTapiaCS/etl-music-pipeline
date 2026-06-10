# ETL Music Pipeline

A data ingestion pipeline that extracts music data from two sources, validates and transforms it, and loads it into a PostgreSQL database.

## Data Sources

- **Spotify Tracks Dataset** (CSV) — 114,000 tracks with audio features like danceability, energy, tempo, and genre
- **MusicBrainz API** — Artist metadata including country, type, and disambiguation

## Pipeline Architecture