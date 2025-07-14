import os
import time
import uuid
import hmac
import base64
import hashlib
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
API_URL = "https://platform.fatsecret.com/rest/server.api"

def percent_encode(val):
    return urllib.parse.quote(str(val), safe='~')

def generate_oauth_signature(method, base_url, params, consumer_secret, token_secret):
    sorted_params = sorted((percent_encode(k), percent_encode(v)) for k, v in params.items())
    param_str = '&'.join(f"{k}={v}" for k, v in sorted_params)
    base_string = '&'.join([method.upper(), percent_encode(base_url), percent_encode(param_str)])
    signing_key = f"{percent_encode(consumer_secret)}&{percent_encode(token_secret)}"
    hashed = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1)
    return base64.b64encode(hashed.digest()).decode()

def make_oauth_request(access_token, access_token_secret, extra_params, method="GET", base_url=API_URL):
    oauth_params = {
        "oauth_consumer_key": CONSUMER_KEY,
        "oauth_token": access_token,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_version": "1.0",
    }

    all_params = {**extra_params, **oauth_params}
    signature = generate_oauth_signature(method, base_url, all_params, CONSUMER_SECRET, access_token_secret)
    oauth_params["oauth_signature"] = signature
    signed_params = {**extra_params, **oauth_params}

    response = requests.get(base_url, params=signed_params)
    response.raise_for_status()
    return response.json()
