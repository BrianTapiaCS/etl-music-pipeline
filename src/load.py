import psycopg2
from dotenv import load_dotenv
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def load_tracks(df, rejects):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
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
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stg_rejects (
            source_name TEXT NOT NULL,
            raw_payload JSONB NOT NULL,
            reason TEXT NOT NULL,
            rejected_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO stg_tracks (track_id, artists, album_name, track_name, popularity, duration_ms, explicit, danceability, energy, tempo, track_genre)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (track_id) DO NOTHING
        """, (row['track_id'], row['artists'], row['album_name'], row['track_name'], row['popularity'], row['duration_ms'], row['explicit'], row['danceability'], row['energy'], row['tempo'], row['track_genre']))

    for reject in rejects:
        cursor.execute("""
            INSERT INTO stg_rejects (source_name, raw_payload, reason)
            VALUES (%s, %s, %s)
        """, ('spotify_tracks', json.dumps({k: (None if str(v) == 'nan' else v) for k, v in reject['row'].items()}, default=str), reject['reason']))

    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Loaded {len(df)} tracks into stg_tracks")
    logger.info(f"Loaded {len(rejects)} rejected rows into stg_rejects")

def load_artists(df, rejects):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stg_artists (
            artist_id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            gender TEXT,
            country TEXT,
            disambiguation TEXT,
            _loaded_at TIMESTAMP DEFAULT NOW()
        )
    """)

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO stg_artists (artist_id, name, type, gender, country, disambiguation)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (artist_id) DO NOTHING
        """, (
            row.get('id'),
            row.get('name'),
            row.get('type'),
            row.get('gender'),
            row.get('country'),
            row.get('disambiguation')
        ))

    for reject in rejects:
        cursor.execute("""
            INSERT INTO stg_rejects (source_name, raw_payload, reason)
            VALUES (%s, %s, %s)
        """, ('musicbrainz_artists', json.dumps({k: (None if str(v) == 'nan' else v) for k, v in reject['row'].items()}, default=str), reject['reason']))

    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Loaded {len(df)} artists into stg_artists")
    logger.info(f"Loaded {len(rejects)} rejected artists into stg_rejects")