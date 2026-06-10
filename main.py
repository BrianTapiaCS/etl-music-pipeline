from src.extract import extract_csv, extract_musicbrainz
from src.transform import transform_tracks, transform_artists
from src.load import load_tracks, load_artists

# Spotify CSV pipeline
df_tracks = extract_csv('data/spotify-tracks-dataset.csv')
df_tracks, track_rejects = transform_tracks(df_tracks)
load_tracks(df_tracks, track_rejects)

# MusicBrainz API pipeline
df_artists = extract_musicbrainz('Drake')
df_artists, artist_rejects = transform_artists(df_artists)
load_artists(df_artists, artist_rejects)