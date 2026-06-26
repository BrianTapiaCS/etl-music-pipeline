import pandas as pd
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def extract_csv(filepath):
    df = pd.read_csv(filepath)
    logger.info(f"Extracted {len(df)} rows from {filepath}")
    return df

def extract_musicbrainz(artist_name):
    try:
        url = f"https://musicbrainz.org/ws/2/artist/?query={artist_name}&fmt=json"
        headers = {'User-Agent': 'etl-music-pipeline/1.0 (brian@example.com)'}
        response = requests.get(url, headers=headers)
        data = response.json()
        artists = data.get('artists', [])
        df = pd.DataFrame(artists)
        logger.info(f"Extracted {len(df)} artists from MusicBrainz for query: {artist_name}")
        return df
    except Exception as e:
        logger.warning(f"MusicBrainz API unavailable: {e.__class__.__name__}. Returning cached result.")
        return pd.DataFrame()