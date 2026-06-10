import json

nb = {
 "cells": [
  {"cell_type": "markdown", "metadata": {}, "source": ["# ETL Music Pipeline — Demo Notebook\n\nDemonstrates the full ETL pipeline end to end."]},
  {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["from src.extract import extract_csv, extract_musicbrainz\nfrom src.transform import transform_tracks, transform_artists\nfrom src.load import load_tracks, load_artists\nfrom src.config import load_config\nimport pandas as pd"]},
  {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["config = load_config()\nsources = config['sources']\nprint('Sources loaded:', [s['name'] for s in sources])"]},
  {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["csv_source = next(s for s in sources if s['type'] == 'csv')\ndf_tracks = extract_csv(csv_source['path'])\nprint(f'Extracted {len(df_tracks)} rows')\ndf_tracks.head()"]},
  {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["df_tracks, track_rejects = transform_tracks(df_tracks)\nprint(f'Clean rows: {len(df_tracks)}')\nprint(f'Rejected rows: {len(track_rejects)}')\ndf_tracks.head()"]},
  {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["api_source = next(s for s in sources if s['type'] == 'api')\ndf_artists = extract_musicbrainz(api_source['query'])\nprint(f'Extracted {len(df_artists)} artists')\ndf_artists[['name', 'country', 'disambiguation']].head(10)"]},
  {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["df_artists, artist_rejects = transform_artists(df_artists)\nprint(f'Clean artists: {len(df_artists)}')"]},
  {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["load_tracks(df_tracks, track_rejects)\nload_artists(df_artists, artist_rejects)\nprint('Pipeline complete!')"]},
  {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["print(f'Total tracks: {len(df_tracks)}')\nprint(f'Total artists: {len(df_artists)}')\nprint(f'Total rejects: {len(track_rejects)}')\nprint(df_tracks['track_genre'].value_counts().head(10))"]}
 ],
 "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.13.2"}},
 "nbformat": 4,
 "nbformat_minor": 4
}

with open("demo.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
print("done")