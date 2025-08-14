import os
import io
import pandas as pd
from ..utils.io import read_csv


# 1) Local CSV (default)
def read_local_csv(path):
    return read_csv(path, encoding='latin')

# 2) AWS S3 (commented credentials usage)
# Requires boto3, AWS creds in env (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
def read_s3_csv(bucket: str, key: str, **read_csv_kwargs) -> pd.DataFrame:
    import boto3
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket = bucket, Key = key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()), **read_csv_kwargs)


# 3) Azure Blob Storage
# Requires: azure-storage-blob, env AZURE_STORAGE_CONNECTION_STRING
# or use a SAS URL directly
def read_azure_blob_csv(container: str, blob_path: str, **read_csv_kwargs) -> pd.DataFrame:
    from azure.storage.blob import BlobServiceClient
    conn = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if not conn:
        raise RuntimeError("Set AZURE_STORAGE_CONNECTION_STRING in env")
    
    svc = BlobServiceClient.from_connection_string(conn)
    blob = svc.get_blob_client(container=container, blob=blob_path)
    data = blob.download_blob().readall()
    return pd.read_csv(io.BytesIO(data), **read_csv_kwargs)


# 4) Google Cloud Storage
# Requires: google-cloud-storage and GOOGLE_APPLICATION_CREDENTIALS env pointing to service account JSON
def read_gcs_csv(bucket: str, blob_path: str, **read_csv_kwargs) -> pd.DataFrame:
    from google.cloud import storage
    client = storage.Client()
    b = client.bucket(bucket)
    blob = b.blob(blob_path)
    data = blob.download_as_bytes()
    return pd.read_csv(io.BytesIO(data), **read_csv_kwargs)


# 5) Kaggle
# Requires: kaggle api configured (~/.kaggle/kaggle.json)
# dataset example: "visheshsr/superstore-dataset"
def read_kaggle_csv(dataset: str, file_within: str, **read_csv_kwargs) -> pd.DataFrame:
    from kaggle.api.kaggle_api_extended import KaggleApi
    import tempfile
    api = KaggleApi(); api.authenticate()
    with tempfile.TemporaryDirectory() as td:
        api.dataset_download_files(dataset, path=td, unzip=True)
        fp = os.path.join(td, file_within)
        return pd.read_csv(fp, **read_csv_kwargs)