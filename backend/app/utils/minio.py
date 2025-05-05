from minio import Minio
import os

# MinIO client configuration
MINIO_URL = os.getenv("MINIO_URL", "http://minio:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
BUCKET_NAME = os.getenv("BUCKET_NAME", "testing")

# Initialize the MinIO client
minio_client = Minio(
    MINIO_URL.replace("http://", "").replace("https://", ""),
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False,
)

# Ensure the bucket exists
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)
