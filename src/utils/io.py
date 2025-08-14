import pandas as pd
from . import dates

def read_csv(path, **kwargs):
    return pd.read_csv(path, **kwargs)

def to_csv(df: pd.DataFrame, path, index=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)

# --- Notes: Cloud ingestion shortcuts (see ingest/readers.py for implementations) ---
# read_s3(bucket, key) -> pd.DataFrame
# read_azure(container, blob_path) -> pd.DataFrame
# read_gcs(bucket, blob_path) -> pd.DataFrame
# read_kaggle(dataset, file_path_within_dataset) -> pd.DataFrame