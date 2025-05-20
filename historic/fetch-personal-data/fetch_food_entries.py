# fetch_food_entries.py

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
from datetime import datetime, timedelta
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

from datetime import timedelta

def get_food_entries(start_date, end_date):
    all_entries = []
    current_date = start_date

    while current_date <= end_date:
        retries = 0
        max_retries = 3
        success = False

        while retries < max_retries and not success:
            date_int = int(current_date.timestamp()) // 86400
            print(f"📅 Fetching entries for {current_date.strftime('%Y-%m-%d')} (Attempt {retries + 1})...")

            method = "GET"
            base_url = API_URL
            extra_params = {
                "method": "food_entries.get",
                "format": "json",
                "date": str(date_int)
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

            try:
                response = requests.get(API_URL, params=all_params)
                response.raise_for_status()
                data = response.json()

                if "error" in data:
                    if data["error"].get("code") == 12:
                        print("⏳ Rate limited. Waiting 30 seconds before retrying...")
                        time.sleep(30)
                        retries += 1
                        continue
                    else:
                        print(f"⚠️ API error on {current_date.strftime('%Y-%m-%d')}: {data['error']}")
                        break

                food_entries_data = data.get("food_entries")
                if not food_entries_data:
                    print(f"ℹ️ No food entries for {current_date.strftime('%Y-%m-%d')}")
                    success = True
                    break

                entries = food_entries_data.get("food_entry", [])
                if entries:
                    all_entries.extend(entries if isinstance(entries, list) else [entries])

                success = True
            except Exception as e:
                print(f"⚠️ Failed to fetch {current_date.strftime('%Y-%m-%d')}: {e}")
                retries += 1
                time.sleep(5)

        current_date += timedelta(days=1)
        time.sleep(1)  # Respectful delay between calls

    return all_entries



def insert_food_entries(entries):
    if not entries:
        print("⚠️ No food entries to insert.")
        return

    user_id = 1
    values = []
    for entry in entries:
        try:
            values.append((
                user_id,
                datetime.utcfromtimestamp(int(entry["date_int"]) * 86400).date(),
                entry.get("meal", ""),
                entry.get("food_name", ""),
                float(entry.get("calories", 0)),
                float(entry.get("number_of_units", 1)),
                entry.get("metric_serving_unit", ""),
                entry.get("food_id", "")
            ))
        except Exception as e:
            print(f"⚠️ Skipping entry due to error: {e}")

    insert_sql = """
        INSERT INTO personal_data.food_entries (
            user_id, date, meal_type, food_name, calories, quantity, unit, fatsecret_food_id
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
        print(f"✅ Inserted {len(values)} food entries.")
    except Exception as e:
        print(f"❌ DB error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("📥 Fetching food entries...")
    start = datetime(2024, 1, 1)
    end = datetime(2025, 1, 1)
    food_entries = get_food_entries(start, end)
    insert_food_entries(food_entries)
