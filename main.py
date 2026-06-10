from src.extract import extract_csv
from src.transform import transform_tracks
from src.load import load_tracks

df = extract_csv('data/spotify-tracks-dataset.csv')
df, rejects = transform_tracks(df)
load_tracks(df, rejects)