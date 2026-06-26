import pandas as pd
from unittest.mock import patch, MagicMock
from src.extract import extract_csv, extract_musicbrainz

@patch('src.extract.requests.get')
def test_extract_musicbrainz_handles_ssl_error(mock_get):
    mock_get.side_effect = Exception("SSLError")
    df = extract_musicbrainz('Drake')
    assert len(df) == 0
    
def test_extract_csv_returns_dataframe():
    df = extract_csv('data/spotify-tracks-dataset.csv')
    assert isinstance(df, pd.DataFrame)

def test_extract_csv_has_correct_columns():
    df = extract_csv('data/spotify-tracks-dataset.csv')
    assert 'track_id' in df.columns
    assert 'artists' in df.columns
    assert 'track_name' in df.columns

def test_extract_csv_row_count():
    df = extract_csv('data/spotify-tracks-dataset.csv')
    assert len(df) == 114000

@patch('src.extract.requests.get')
def test_extract_musicbrainz_returns_dataframe(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'artists': [
            {'id': '1', 'name': 'Drake', 'type': 'Person', 'gender': 'male', 'country': 'CA'}
        ]
    }
    mock_get.return_value = mock_response
    df = extract_musicbrainz('Drake')
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1

@patch('src.extract.requests.get')
def test_extract_musicbrainz_empty_response(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {'artists': []}
    mock_get.return_value = mock_response
    df = extract_musicbrainz('unknown_artist_xyz')
    assert len(df) == 0