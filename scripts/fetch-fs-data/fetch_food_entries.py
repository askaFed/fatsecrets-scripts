from datetime import datetime, timedelta
import time
from clients import insert_values, make_oauth_request
import argparse


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
        ON CONFLICT (fatsecret_food_entry_id) DO UPDATE SET
            user_id = EXCLUDED.user_id,
            date = EXCLUDED.date,
            meal_type = EXCLUDED.meal_type,
            food_name = EXCLUDED.food_name,
            calories = EXCLUDED.calories,
            carbohydrate = EXCLUDED.carbohydrate,
            protein = EXCLUDED.protein,
            fat = EXCLUDED.fat,
            saturated_fat = EXCLUDED.saturated_fat,
            sugar = EXCLUDED.sugar,
            fiber = EXCLUDED.fiber,
            calcium = EXCLUDED.calcium,
            iron = EXCLUDED.iron,
            cholesterol = EXCLUDED.cholesterol,
            sodium = EXCLUDED.sodium,
            vitamin_a = EXCLUDED.vitamin_a,
            vitamin_c = EXCLUDED.vitamin_c,
            monounsaturated_fat = EXCLUDED.monounsaturated_fat,
            polyunsaturated_fat = EXCLUDED.polyunsaturated_fat,
            quantity = EXCLUDED.quantity,
            unit = EXCLUDED.unit,
            fatsecret_food_id = EXCLUDED.fatsecret_food_id;
        """

    insert_values(insert_sql, values)


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch and insert food entries.")
    parser.add_argument('--start', type=str, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end', type=str, help='End date in YYYY-MM-DD format')
    return parser.parse_args()

if __name__ == "__main__":
    print("📥 Fetching food entries...")

    args = parse_args()

    # Default to yesterday and today if not provided
    today = datetime.now()
    default_start = today - timedelta(days=1)
    default_end = today

    # Parse dates or use defaults
    start = datetime.strptime(args.start, '%Y-%m-%d') if args.start else default_start
    end = datetime.strptime(args.end, '%Y-%m-%d') if args.end else default_end

    food_entries = get_food_entries(start, end)
    insert_food_entries(food_entries)
