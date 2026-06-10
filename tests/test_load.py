import pandas as pd
from unittest.mock import patch, MagicMock
from src.load import load_tracks, load_artists

@patch('src.load.psycopg2.connect')
def test_load_tracks_connects(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    df = pd.DataFrame({
        'track_id': ['1'], 'artists': ['Drake'], 'album_name': ['Album'],
        'track_name': ['Song'], 'popularity': [80], 'duration_ms': [200000],
        'explicit': [False], 'danceability': [0.8], 'energy': [0.9],
        'tempo': [120.0], 'track_genre': ['rap']
    })
    load_tracks(df, [])
    assert mock_connect.called

@patch('src.load.psycopg2.connect')
def test_load_tracks_commits(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    df = pd.DataFrame({
        'track_id': ['1'], 'artists': ['Drake'], 'album_name': ['Album'],
        'track_name': ['Song'], 'popularity': [80], 'duration_ms': [200000],
        'explicit': [False], 'danceability': [0.8], 'energy': [0.9],
        'tempo': [120.0], 'track_genre': ['rap']
    })
    load_tracks(df, [])
    assert mock_conn.commit.called

@patch('src.load.psycopg2.connect')
def test_load_artists_connects(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    df = pd.DataFrame({
        'id': ['1'], 'name': ['Drake'], 'type': ['Person'],
        'gender': ['male'], 'country': ['CA'], 'disambiguation': ['rapper']
    })
    load_artists(df, [])
    assert mock_connect.called

@patch('src.load.psycopg2.connect')
def test_load_artists_commits(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    df = pd.DataFrame({
        'id': ['1'], 'name': ['Drake'], 'type': ['Person'],
        'gender': ['male'], 'country': ['CA'], 'disambiguation': ['rapper']
    })
    load_artists(df, [])
    assert mock_conn.commit.called