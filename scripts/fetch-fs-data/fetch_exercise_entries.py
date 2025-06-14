from datetime import datetime, timedelta, timezone
import time
from clients import insert_values, get_all_users, make_oauth_request
import argparse


def get_exercise_entries(user_id, access_token, access_token_secret, start_date, end_date):
    all_entries = []
    current_date = start_date

    while current_date <= end_date:
        retries = 0
        max_retries = 3
        success = False

        while retries < max_retries and not success:
            date_int = (int(current_date.timestamp()) // 86400)
            print(f"🏋️ Fetching exercise entries for user {user_id} on {current_date.strftime('%Y-%m-%d')} (Attempt {retries + 1})...")

            params = {
                "method": "exercise_entries.get",
                "format": "json",
                "date": str(date_int)
            }

            try:
                data = make_oauth_request(access_token, access_token_secret, params)

                if "error" in data:
                    if data["error"].get("code") == 12:
                        print("⏳ Rate limited. Waiting 30 seconds before retrying...")
                        time.sleep(30)
                        retries += 1
                        continue
                    else:
                        print(f"⚠️ API error on {current_date.strftime('%Y-%m-%d')}: {data['error']}")
                        break

                exercise_entries_data = data.get("exercise_entries")
                if not exercise_entries_data:
                    print(f"ℹ️ No exercise entries for {current_date.strftime('%Y-%m-%d')}")
                    success = True
                    break

                entries = exercise_entries_data.get("exercise_entry", [])
                if not isinstance(entries, list):
                    entries = [entries]

                for entry in entries:
                    entry["entry_date"] = current_date.date().isoformat()
                    entry["user_id"] = user_id

                all_entries.extend(entries)
                success = True
            except Exception as e:
                print(f"⚠️ Failed to fetch {current_date.strftime('%Y-%m-%d')}: {e}")
                retries += 1
                time.sleep(5)

        current_date += timedelta(days=1)
        time.sleep(1)  # Respectful delay between calls

    return all_entries


def insert_exercise_entries(entries):
    if not entries:
        print("⚠️ No exercise entries to insert.")
        return

    values = []
    for entry in entries:
        try:
            values.append((
                entry.get("user_id"),
                entry.get("entry_date"),
                entry.get("exercise_name"),
                entry.get("minutes"),
                entry.get("calories"),
                entry.get("exercise_id"),
            ))
        except Exception as e:
            print(f"⚠️ Skipping entry due to error: {e}")

    insert_sql = """
            INSERT INTO personal_data.exercise_entries (
                user_id, date, exercise_name, duration_minutes, calories, fatsecret_exercise_id
            ) VALUES %s
            ON CONFLICT (user_id, date, fatsecret_exercise_id) DO UPDATE SET
                exercise_name = EXCLUDED.exercise_name,
                duration_minutes = EXCLUDED.duration_minutes,
                calories = EXCLUDED.calories;
    """

    insert_values(insert_sql, values)


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch and insert exercise entries.")
    parser.add_argument('--start', type=str, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end', type=str, help='End date in YYYY-MM-DD format')
    return parser.parse_args()


if __name__ == "__main__":
    print("📥 Fetching exercise entries for all users...")

    args = parse_args()

    # Default to yesterday and today if not provided
    today = datetime.now().replace(tzinfo=timezone.utc)
    default_start = today - timedelta(days=1)
    default_end = today

    # Parse dates or use defaults
    start = datetime.strptime(args.start, '%Y-%m-%d').replace(tzinfo=timezone.utc) if args.start else default_start
    end = datetime.strptime(args.end, '%Y-%m-%d').replace(tzinfo=timezone.utc) if args.end else default_end

    # Get all users with their access tokens
    users = get_all_users()
    
    if not users:
        print("❌ No users found in the database")
        exit(1)

    for user in users:
        print(f"👤 Processing user {user['id']} ({user['fatsecret_user_id']})")
        user_entries = get_exercise_entries(
            user['id'],
            user['access_token'],
            user['access_token_secret'],
            start,
            end
        )
        insert_exercise_entries(user_entries)
        time.sleep(5)  # Delay between users