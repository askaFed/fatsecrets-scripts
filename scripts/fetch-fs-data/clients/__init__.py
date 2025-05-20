# fatsecret/__init__.py
from .fatsecret_client import make_oauth_request
from .pg_client import insert_values

__all__ = ["make_oauth_request", "insert_values"]
