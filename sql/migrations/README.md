# Database Migrations

SQL scripts to create the staging tables for the ETL Music Pipeline.

## Tables

### stg_tracks
Stores clean Spotify track data extracted from the Kaggle CSV dataset.

| Column | Type | Description |
|--------|------|-------------|
| track_id | TEXT | Spotify unique track ID (primary key) |
| artists | TEXT | Artist name(s) |
| album_name | TEXT | Album name |
| track_name | TEXT | Track name |
| popularity | INTEGER | Popularity score 0-100 |
| duration_ms | INTEGER | Track duration in milliseconds |
| explicit | BOOLEAN | Whether track has explicit content |
| danceability | FLOAT | Danceability score 0-1 |
| energy | FLOAT | Energy score 0-1 |
| tempo | FLOAT | Tempo in BPM |
| track_genre | TEXT | Genre category |
| _loaded_at | TIMESTAMP | When the record was loaded |

### stg_artists
Stores artist metadata extracted from the MusicBrainz API.

| Column | Type | Description |
|--------|------|-------------|
| artist_id | TEXT | MusicBrainz unique artist ID (primary key) |
| name | TEXT | Artist name |
| type | TEXT | Person, Group, etc. |
| gender | TEXT | Artist gender |
| country | TEXT | Country code |
| disambiguation | TEXT | Short description |
| _loaded_at | TIMESTAMP | When the record was loaded |

### stg_rejects
Stores rejected rows from both pipelines with the reason for rejection.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Auto-incrementing ID |
| source_name | TEXT | Which pipeline rejected the row |
| raw_payload | JSONB | The original row data |
| reason | TEXT | Why the row was rejected |
| rejected_at | TIMESTAMP | When the row was rejected |

## Running Migrations

```bash
psql -U postgres -f sql/migrations/001_create_stg_tracks.sql
psql -U postgres -f sql/migrations/002_create_stg_artists.sql
psql -U postgres -f sql/migrations/003_create_stg_rejects.sql
```