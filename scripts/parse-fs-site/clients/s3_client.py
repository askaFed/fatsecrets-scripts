# fatsecret/s3_client.py

import os
import boto3
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------
# ENV CONFIG
# ---------------------------------------------------------------------
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://192.168.1.136:9000")
S3_BUCKET = os.getenv("S3_BUCKET", "fatsecret")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

# ---------------------------------------------------------------------
# CLIENT INITIALIZATION
# ---------------------------------------------------------------------
def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name=S3_REGION,
        config=Config(signature_version="s3v4"),
    )


# ---------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------
def ensure_bucket_exists(bucket_name: str = S3_BUCKET):
    """Create the bucket if it does not exist."""
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket exists: {bucket_name}")
    except Exception:
        print(f"ℹ️ Creating bucket: {bucket_name}")
        s3.create_bucket(Bucket=bucket_name)
    return s3


def upload_to_s3(file_or_stream, s3_key, bucket_name=S3_BUCKET, extra_args=None):
    """
    Uploads a local file (path) or file-like object (e.g., HTTP stream) to S3.
    """
    s3 = get_s3_client()
    try:
        if isinstance(file_or_stream, str) and os.path.exists(file_or_stream):
            s3.upload_file(file_or_stream, bucket_name, s3_key, ExtraArgs=extra_args or {})
        else:
            s3.upload_fileobj(file_or_stream, bucket_name, s3_key, ExtraArgs=extra_args or {})
        return True
    except Exception as e:
        print(f"❌ Failed to upload {s3_key}: {e}")
        return False



def object_exists(s3_key: str, bucket_name: str = S3_BUCKET) -> bool:
    """Check if object already exists."""
    s3 = get_s3_client()
    try:
        s3.head_object(Bucket=bucket_name, Key=s3_key)
        return True
    except Exception:
        return False
