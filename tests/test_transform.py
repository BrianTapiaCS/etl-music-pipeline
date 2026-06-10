import pandas as pd
from src.transform import transform_tracks, transform_artists

def test_tracks_removes_missing_values():
    data = {
        'track_id': ['1', '2'],
        'artists': ['Drake', None],
        'album_name': ['Album1', 'Album2'],
        'track_name': ['Song1', 'Song2'],
        'popularity': [80, 70],
        'duration_ms': [200000, 180000],
        'explicit': [False, False],
        'danceability': [0.8, 0.6],
        'energy': [0.9, 0.7],
        'tempo': [120.0, 110.0],
        'track_genre': ['rap', 'rap']
    }
    df = pd.DataFrame(data)
    clean_df, rejects = transform_tracks(df)
    assert len(clean_df) == 1
    assert rejects[0]['reason'] == 'missing value'

def test_tracks_removes_invalid_popularity():
    data = {
        'track_id': ['1', '2'],
        'artists': ['Drake', 'Drake'],
        'album_name': ['Album1', 'Album2'],
        'track_name': ['Song1', 'Song2'],
        'popularity': [80, 150],
        'duration_ms': [200000, 180000],
        'explicit': [False, False],
        'danceability': [0.8, 0.6],
        'energy': [0.9, 0.7],
        'tempo': [120.0, 110.0],
        'track_genre': ['rap', 'rap']
    }
    df = pd.DataFrame(data)
    clean_df, rejects = transform_tracks(df)
    assert len(clean_df) == 1
    assert rejects[0]['reason'] == 'invalid popularity'

def test_tracks_removes_duplicates():
    data = {
        'track_id': ['1', '1'],
        'artists': ['Drake', 'Drake'],
        'album_name': ['Album1', 'Album1'],
        'track_name': ['Song1', 'Song1'],
        'popularity': [80, 80],
        'duration_ms': [200000, 200000],
        'explicit': [False, False],
        'danceability': [0.8, 0.8],
        'energy': [0.9, 0.9],
        'tempo': [120.0, 120.0],
        'track_genre': ['rap', 'rap']
    }
    df = pd.DataFrame(data)
    clean_df, rejects = transform_tracks(df)
    assert len(clean_df) == 1
    assert rejects[0]['reason'] == 'duplicate track_id'

def test_artists_removes_missing_name():
    data = {
        'id': ['1', '2'],
        'name': ['Drake', None],
        'type': ['Person', 'Person'],
        'gender': ['male', 'male'],
        'country': ['CA', 'US'],
        'disambiguation': ['rapper', 'rapper']
    }
    df = pd.DataFrame(data)
    clean_df, rejects = transform_artists(df)
    assert len(clean_df) == 1
    assert rejects[0]['reason'] == 'missing id or name'

def test_artists_removes_duplicates():
    data = {
        'id': ['1', '1'],
        'name': ['Drake', 'Drake'],
        'type': ['Person', 'Person'],
        'gender': ['male', 'male'],
        'country': ['CA', 'CA'],
        'disambiguation': ['rapper', 'rapper']
    }
    df = pd.DataFrame(data)
    clean_df, rejects = transform_artists(df)
    assert len(clean_df) == 1
    assert rejects[0]['reason'] == 'duplicate artist id'