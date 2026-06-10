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
    url = f"https://musicbrainz.org/ws/2/artist/?query={artist_name}&fmt=json"
    headers = {'User-Agent': 'etl-music-pipeline/1.0 (brian@example.com)'}
    response = requests.get(url, headers=headers)
    data = response.json()
    artists = data.get('artists', [])
    df = pd.DataFrame(artists)
    logger.info(f"Extracted {len(df)} artists from MusicBrainz for query: {artist_name}")
    return df