from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import time
from clients import insert_values, get_all_users, make_oauth_request
import argparse


def get_weight_entries(user_id, access_token, access_token_secret, start_date, end_date):
    all_entries = []
    current_date = start_date

    while current_date <= end_date:
        retries = 0
        max_retries = 3
        success = False

        while retries < max_retries and not success:
            date_int = (current_date - datetime(1970, 1, 1).replace(tzinfo=timezone.utc)).days
            print(f"📅 Fetching entries for user {user_id} on {current_date.strftime('%Y-%m-%d')} (Attempt {retries + 1})...")

            params = {
                "method": "weights.get_month.v2",
                "format": "json",
                "date": str(date_int)
            }

            try:
                data = make_oauth_request(access_token, access_token_secret, params)
                print(f"Data {data}")

                if "error" in data:
                    if data["error"].get("code") == 12:
                        print("⏳ Rate limited. Waiting 30 seconds before retrying...")
                        time.sleep(30)
                        retries += 1
                        continue
                    else:
                        print(f"⚠️ API error on {current_date.strftime('%Y-%m-%d')}: {data['error']}")
                        break

                days = data.get("month", {}).get("day", [])
                entries = []
                for entry in days:
                    date = datetime.utcfromtimestamp(int(entry["date_int"]) * 86400).strftime("%Y-%m-%d")
                    weight = entry.get("weight_kg")
                    if weight is not None:
                        entries.append((user_id, date, float(weight)))

                if entries:
                    all_entries.extend(entries if isinstance(entries, list) else [entries])

                success = True
            except Exception as e:
                print(f"⚠️ Failed to fetch {current_date.strftime('%Y-%m-%d')}: {e}")
                retries += 1
                time.sleep(5)

        current_date += relativedelta(months=1)
        time.sleep(5)  # Respectful delay between calls

    return all_entries


def insert_weight_entries(entries):
    if not entries:
        print("⚠️ No weight entries to insert.")
        return

    insert_sql = """
            INSERT INTO personal_data.weights (user_id, date, weight_kg)
            VALUES %s
            ON CONFLICT (user_id, date) DO UPDATE
            SET weight_kg = EXCLUDED.weight_kg;
        """

    insert_values(insert_sql, entries)


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch and insert food entries.")
    parser.add_argument('--start', type=str, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end', type=str, help='End date in YYYY-MM-DD format')
    return parser.parse_args()


if __name__ == "__main__":
    print("📥 Fetching weight entries for all users...")

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

    all_entries = []
    for user in users:
        print(f"👤 Processing user {user['id']} ({user['fatsecret_user_id']})")
        user_entries = get_weight_entries(
            user['id'],
            user['access_token'],
            user['access_token_secret'],
            start,
            end
        )
        all_entries.extend(user_entries)
        time.sleep(5)  # Delay between users

    insert_weight_entries(all_entries)

