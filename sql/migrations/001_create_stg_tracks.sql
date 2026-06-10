CREATE TABLE IF NOT EXISTS stg_tracks (
    track_id TEXT PRIMARY KEY,
    artists TEXT,
    album_name TEXT,
    track_name TEXT,
    popularity INTEGER,
    duration_ms INTEGER,
    explicit BOOLEAN,
    danceability FLOAT,
    energy FLOAT,
    tempo FLOAT,
    track_genre TEXT,
    _loaded_at TIMESTAMP DEFAULT NOW()
);