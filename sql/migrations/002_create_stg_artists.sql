CREATE TABLE IF NOT EXISTS stg_artists (
    artist_id TEXT PRIMARY KEY,
    name TEXT,
    type TEXT,
    gender TEXT,
    country TEXT,
    disambiguation TEXT,
    _loaded_at TIMESTAMP DEFAULT NOW()
);