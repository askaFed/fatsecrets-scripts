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

# Load .env variables
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

    base_elems = [method.upper(), percent_encode(base_url), percent_encode(param_str)]
    base_string = '&'.join(base_elems)

    signing_key = f"{percent_encode(consumer_secret)}&{percent_encode(token_secret)}"
    hashed = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1)
    return base64.b64encode(hashed.digest()).decode()

def get_weight_data_for_month(date_obj):
    epoch_days = (date_obj - datetime(1970, 1, 1)).days

    method = "GET"
    base_url = API_URL
    extra_params = {
        "method": "weights.get_month.v2",
        "format": "json",
        "date": epoch_days,
    }

    oauth_params = {
        "oauth_consumer_key": CONSUMER_KEY,
        "oauth_token": ACCESS_TOKEN,
        "oauth_nonce": str(uuid.uuid4().hex),
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
    except Exception as e:
        print(f"❌ Failed to parse response for {date_obj.strftime('%Y-%m')}: {e}")
        return []

    if "error" in data:
        print(f"❌ API Error for {date_obj.strftime('%Y-%m')}: {data['error'].get('message')}")
        return []

    days = data.get("month", {}).get("day", [])
    results = []
    for entry in days:
        date = datetime.utcfromtimestamp(int(entry["date_int"]) * 86400).strftime("%Y-%m-%d")
        weight = entry.get("weight_kg")
        if weight is not None:
            results.append((date, float(weight)))

    return results

if __name__ == "__main__":
    today = datetime.today()
    print(f"📆 Fetching weight data for today: {today.strftime('%Y-%m-%d')}")
    entries = get_weight_data_for_month(today)

    if not entries:
        print("⚠️ No weight entries found for today.")
        exit(0)

    # Filter for today's date only
    entries_today = [entry for entry in entries if entry[0] == today.strftime('%Y-%m-%d')]
    if not entries_today:
        print("⚠️ No weight entry for today.")
        exit(0)

    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DB
        )
        cursor = conn.cursor()

        user_id = 1
        values = [(user_id, entry[0], entry[1]) for entry in entries_today]  # (user_id, date, weight_kg)

        insert_sql = """
            INSERT INTO personal_data.weights (user_id, date, weight_kg)
            VALUES %s
            ON CONFLICT (user_id, date) DO UPDATE
            SET weight_kg = EXCLUDED.weight_kg;
        """

        execute_values(cursor, insert_sql, values)
        conn.commit()
        print(f"\n✅ Inserted/updated {len(values)} rows into personal_data.weights")

    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
