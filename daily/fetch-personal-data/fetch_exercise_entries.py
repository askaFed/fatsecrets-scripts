# fetch_exercise_entries.py

import os
import time
import uuid
import hmac
import base64
import hashlib
import urllib.parse
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# FatSecret API credentials
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
API_URL = "https://platform.fatsecret.com/rest/server.api"

# PostgreSQL credentials
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT", 5432)
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DB = os.getenv("PG_DB")

def percent_encode(val):
    return urllib.parse.quote(str(val), safe='~')

def generate_oauth_signature(method, base_url, params, consumer_secret, token_secret):
    sorted_params = sorted((percent_encode(k), percent_encode(v)) for k, v in params.items())
    param_str = '&'.join(f"{k}={v}" for k, v in sorted_params)
    base_string = '&'.join([method.upper(), percent_encode(base_url), percent_encode(param_str)])
    signing_key = f"{percent_encode(consumer_secret)}&{percent_encode(token_secret)}"
    hashed = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1)
    return base64.b64encode(hashed.digest()).decode()

def get_exercise_entries():
    method = "GET"
    base_url = API_URL
    extra_params = {
        "method": "exercise_entries.get",
        "format": "json"
    }
    oauth_params = {
        "oauth_consumer_key": CONSUMER_KEY,
        "oauth_token": ACCESS_TOKEN,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_version": "1.0",
    }
    all_params = {**extra_params, **oauth_params}
    signature = generate_oauth_signature(method, base_url, all_params, CONSUMER_SECRET, ACCESS_SECRET)
    oauth_params["oauth_signature"] = signature
    all_params = {**extra_params, **oauth_params}

    response = requests.get(API_URL, params=all_params)
    try:
        data = response.json()
        print("🔍 Raw response data:", data)

        entry_data = data.get("exercise_entries", {}).get("exercise_entry", [])
        if isinstance(entry_data, dict):
            return [entry_data]  # wrap single entry in a list
        return entry_data
    except Exception as e:
        print(f"❌ Error parsing exercise entries: {e}")
        return []

def insert_exercise_entries(entries):
    if not entries:
        print("⚠️ No exercise entries to insert.")
        return

    user_id = 1
    values = []
    for entry in entries:
        print(f"🔍 Raw entry: {entry}")

        try:
            values.append((
                user_id,
                datetime.utcfromtimestamp(int(entry["date_int"]) * 86400).date(),
                entry.get("exercise_name", ""),
                float(entry.get("calories", 0)),
                float(entry.get("minutes", 0)),
                entry.get("exercise_id", "")
            ))
        except Exception as e:
            print(f"⚠️ Skipping entry due to error: {e}")

    insert_sql = """
        INSERT INTO personal_data.exercise_entries (
            user_id, date, exercise_name, calories_burned, duration_minutes, fatsecret_exercise_id
        )
        VALUES %s;
    """

    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, user=PG_USER,
            password=PG_PASSWORD, dbname=PG_DB
        )
        cursor = conn.cursor()
        execute_values(cursor, insert_sql, values)
        conn.commit()
        print(f"✅ Inserted {len(values)} exercise entries.")
    except Exception as e:
        print(f"❌ DB error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("📥 Fetching exercise entries...")
    exercise_entries = get_exercise_entries()
    insert_exercise_entries(exercise_entries)
