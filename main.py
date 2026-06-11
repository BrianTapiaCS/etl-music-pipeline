'''
from src.extract import extract_csv, extract_musicbrainz
from src.transform import transform_tracks, transform_artists
from src.load import load_tracks, load_artists
from src.config import load_config

config = load_config()
sources = config['sources']

# Spotify CSV pipeline
csv_source = next(s for s in sources if s['type'] == 'csv')
df_tracks = extract_csv(csv_source['path'])
df_tracks, track_rejects = transform_tracks(df_tracks)
load_tracks(df_tracks, track_rejects)

# MusicBrainz API pipeline
api_source = next(s for s in sources if s['type'] == 'api')
df_artists = extract_musicbrainz(api_source['query'])
df_artists, artist_rejects = transform_artists(df_artists)
load_artists(df_artists, artist_rejects)
'''
from src.extract import extract_csv, extract_musicbrainz
from src.transform import transform_tracks, transform_artists
from src.load import load_tracks, load_artists
from src.config import load_config

config = load_config()
sources = config['sources']

# Spotify CSV pipeline
csv_source = next(s for s in sources if s['type'] == 'csv')
df_tracks = extract_csv(csv_source['path'])
df_tracks, track_rejects = transform_tracks(df_tracks)
load_tracks(df_tracks, track_rejects)

# MusicBrainz API pipeline
api_source = next(s for s in sources if s['type'] == 'api')
df_artists = extract_musicbrainz(api_source['query'])
df_artists, artist_rejects = transform_artists(df_artists)
load_artists(df_artists, artist_rejects)