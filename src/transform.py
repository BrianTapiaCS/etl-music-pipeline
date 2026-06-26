import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def transform_tracks(df):
    logger.info(f"Before cleaning: {len(df)} rows")
    rejects = []

    # drop unnecessary columns
    df = df.drop(columns=['Unnamed: 0'], errors='ignore')
    df = df.drop(columns=[''], errors='ignore')

    # drop rows with missing values
    missing = df[df.isnull().any(axis=1)]
    for _, row in missing.iterrows():
        rejects.append({'row': row.to_dict(), 'reason': 'missing value'})
    df = df.dropna()

    # drop rows where popularity is not between 0 and 100
    invalid_popularity = df[(df['popularity'] < 0) | (df['popularity'] > 100)]
    for _, row in invalid_popularity.iterrows():
        rejects.append({'row': row.to_dict(), 'reason': 'invalid popularity'})
    df = df[(df['popularity'] >= 0) & (df['popularity'] <= 100)]

    # drop duplicate track_ids
    dupes = df[df.duplicated(subset=['track_id'])]
    for _, row in dupes.iterrows():
        rejects.append({'row': row.to_dict(), 'reason': 'duplicate track_id'})
    df = df.drop_duplicates(subset=['track_id'])

    logger.info(f"After cleaning: {len(df)} rows | Rejected: {len(rejects)} rows")
    return df, rejects

def transform_artists(df):
    if df.empty:
        logger.warning("No artist data to transform — skipping.")
        return df, []
    logger.info(f"Before cleaning artists: {len(df)} rows")
    rejects = []

    # keep only relevant columns
    keep = ['id', 'name', 'type', 'gender', 'country', 'disambiguation']
    df = df[[col for col in keep if col in df.columns]]

    # drop rows with missing id or name
    missing = df[df[['id', 'name']].isnull().any(axis=1)]
    for _, row in missing.iterrows():
        rejects.append({'row': row.to_dict(), 'reason': 'missing id or name'})
    df = df.dropna(subset=['id', 'name'])

    # drop duplicates
    dupes = df[df.duplicated(subset=['id'])]
    for _, row in dupes.iterrows():
        rejects.append({'row': row.to_dict(), 'reason': 'duplicate artist id'})
    df = df.drop_duplicates(subset=['id'])

    logger.info(f"After cleaning artists: {len(df)} rows | Rejected: {len(rejects)} rows")
    return df, rejects