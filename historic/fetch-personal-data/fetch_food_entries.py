from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv
from fatsecret_client import make_oauth_request
from pg_client import insert_values

load_dotenv()

# PostgreSQL credentials
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT", 5432)
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DB = os.getenv("PG_DB")

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

            params = {
                "method": "food_entries.get",
                "format": "json",
                "date": str(date_int)
            }

            try:
                data = make_oauth_request(params)

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
                entry.get('meal'),
                entry.get('food_entry_name'),
                entry.get('calories'),
                entry.get('carbohydrate'),
                entry.get('protein'),
                entry.get('fat'),
                entry.get('saturated_fat'),
                entry.get('sugar'),
                entry.get('fiber'),
                entry.get('calcium'),
                entry.get('iron'),
                entry.get('cholesterol'),
                entry.get('sodium'),
                entry.get('vitamin_a'),
                entry.get('vitamin_c'),
                entry.get('monounsaturated_fat'),
                entry.get('polyunsaturated_fat'),
                entry.get('number_of_units'),
                entry.get('unit'),
                entry.get('food_id'),
                entry.get('food_entry_id')
            ))
        except Exception as e:
            print(f"⚠️ Skipping entry due to error: {e}")

    insert_sql = """
            INSERT INTO personal_data.food_entries (
                user_id, date, meal_type, food_name, calories,
                carbohydrate, protein, fat, saturated_fat, sugar, fiber,
                calcium, iron, cholesterol, sodium, vitamin_a, vitamin_c,
                monounsaturated_fat, polyunsaturated_fat,
                quantity, unit, fatsecret_food_id, fatsecret_food_entry_id
            ) VALUES %s
            ON CONFLICT (fatsecret_food_entry_id) DO NOTHING
        """

    insert_values(insert_sql, values)


if __name__ == "__main__":
    print("📥 Fetching food entries...")
    start = datetime(2025, 5, 20)
    end = datetime(2025, 5, 21)
    food_entries = get_food_entries(start, end)
    insert_food_entries(food_entries)
