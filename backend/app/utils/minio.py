from minio import Minio
import os

# MinIO client configuration
MINIO_URL = os.getenv("MINIO_URL")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
IMG_BUCKET = "img-bucket"
MASK_BUCKET = "mask-bucket"
METRICS_BUCKET = "metrics-bucket"

# Initialize the MinIO client
minio_client = Minio(
    MINIO_URL.replace("http://", "").replace("https://", ""),
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False,
)

# Ensure the bucket exists
if not minio_client.bucket_exists(IMG_BUCKET):
    minio_client.make_bucket(IMG_BUCKET)

if not minio_client.bucket_exists(MASK_BUCKET):
    minio_client.make_bucket(MASK_BUCKET)
    
if not minio_client.bucket_exists(METRICS_BUCKET):
    minio_client.make_bucket(METRICS_BUCKET)
