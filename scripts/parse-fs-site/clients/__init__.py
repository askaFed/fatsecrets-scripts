# fatsecret/__init__.py

from .s3_client  import ensure_bucket_exists, upload_to_s3, object_exists

__all__ = ["ensure_bucket_exists", "upload_to_s3", "object_exists"]
