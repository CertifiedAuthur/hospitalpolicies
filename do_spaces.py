import boto3
from botocore.exceptions import ClientError
from pathlib import Path
import streamlit as st

SPACE_NAME = "lightrag-bucket"
SPACE_REGION = "nyc3"  # change if yours differs
FOLDER_NAME = "knowledge-base"

DO_ENDPOINT = f"https://{SPACE_REGION}.digitaloceanspaces.com"
ACCESS_KEY = st.secrets["DO_SPACES_ACCESS_KEY"]
SECRET_KEY = st.secrets["DO_SPACES_SECRET_KEY"]

session = boto3.session.Session()
client = session.client('s3',
    region_name=SPACE_REGION,
    endpoint_url=DO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

def list_files():
    try:
        response = client.list_objects_v2(Bucket=SPACE_NAME, Prefix=FOLDER_NAME + "/")
        return [content["Key"] for content in response.get("Contents", [])]
    except ClientError as e:
        print("Error listing files:", e)
        return []

def delete_existing_files():
    files = list_files()
    for file_key in files:
        client.delete_object(Bucket=SPACE_NAME, Key=file_key)

def upload_file(file_path: Path):
    file_key = f"{FOLDER_NAME}/{file_path.name}"
    with open(file_path, "rb") as f:
        client.upload_fileobj(f, SPACE_NAME, file_key)

def download_all_files(download_dir: Path):
    download_dir.mkdir(parents=True, exist_ok=True)
    files = list_files()
    for file_key in files:
        file_name = file_key.split("/")[-1]
        download_path = download_dir / file_name
        client.download_file(SPACE_NAME, file_key, str(download_path))


def delete_all():
    delete_existing_files()
