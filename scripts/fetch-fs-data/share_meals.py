from datetime import datetime, timezone
import time
import argparse
from clients import get_access_tokens, make_oauth_request

def share_meal(user_from, user_to, meal_type, target_date):
    """Share meal entries from one user to another"""

    print(f"🔄 Sharing {meal_type or 'all'} meals from user {user_from} to user {user_to} on {target_date.strftime('%Y-%m-%d')}")

    # Get access tokens for both users
    print(f"🔑 Retrieving access tokens...")
    try:
        token_from, secret_from = get_access_tokens(user_from)
        token_to, secret_to = get_access_tokens(user_to)
    except ValueError as e:
        print(f"❌ {e}")
        return False

    # Fetch food entries from source user
    print(f"📥 Fetching food entries from user {user_from}...")
    try:
        entries = get_food_entries_by_date_and_meal(token_from, secret_from, target_date, meal_type)

        if not entries:
            print(f"ℹ️ No food entries found for user {user_from}" + (f" for meal {meal_type}" if meal_type else ""))
            return True

        print(f"✅ Found {len(entries)} food entries")
    except Exception as e:
        print(f"❌ Failed to fetch entries: {e}")
        return False

    # Post entries to target user
    print(f"📤 Posting food entries to user {user_to}...")
    successful = 0
    failed = 0

    for entry in entries:
        try:
            print(f"  → Adding {entry.get('food_entry_name')} ({entry.get('number_of_units', 1)} units)...", end=" ")

            add_food_entry(
                token_to,
                secret_to,
                entry,
                target_date
            )
            print("✅")
            successful += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"\n ❌ ({e})")
            failed += 1
            time.sleep(1)

    print(f"\n✅ Sharing complete: {successful} successful, {failed} failed")
    return failed == 0


def get_food_entries_by_date(access_token, access_token_secret, date):
    """Fetch all food entries for a specific date"""
    date_int = int(date.timestamp()) // 86400

    params = {
        "method": "food_entries.get",
        "format": "json",
        "date": str(date_int)
    }

    data = make_oauth_request(access_token, access_token_secret, params)

    if "error" in data:
        raise Exception(f"FatSecret API error: {data['error']}")

    food_entries_data = data.get("food_entries")
    if not food_entries_data:
        return []

    entries = food_entries_data.get("food_entry", [])
    if not isinstance(entries, list):
        entries = [entries]

    return entries

def get_food_entries_by_date_and_meal(access_token, access_token_secret, date, meal_type):
    """Fetch food entries for a specific meal type on a given date"""
    entries = get_food_entries_by_date(access_token, access_token_secret, date)

    if not meal_type:
        return entries

    return [e for e in entries if e.get('meal', '').lower() == meal_type.lower()]

def add_food_entry(access_token, access_token_secret, entry, date):
    """Add a food entry for a user

    Args:
        access_token: User's OAuth access token
        access_token_secret: User's OAuth access token secret
        entry: Food entry object containing food_id, serving_id, food_entry_name, meal, number_of_units
        date: DateTime object for the entry date
    """
    date_int = int(date.timestamp()) // 86400

    # Normalize meal type to lowercase
    meal_normalized = entry.get('meal', 'other').lower()

    params = {
        "method": "food_entry.create",
        "format": "json",
        "food_id": str(entry.get('food_id')),
        "serving_id": str(entry.get('serving_id')),
        "food_entry_name": str(entry.get('food_entry_name')),
        "date": str(date_int),
        "meal": meal_normalized,
        "number_of_units": str(entry.get('number_of_units', 1))
    }

    data = make_oauth_request(access_token, access_token_secret, params)

    if "error" in data:
        raise Exception(f"FatSecret API error: {data['error']}")

    return data.get("food_entry")


def parse_args():
    parser = argparse.ArgumentParser(description="Share meal entries between users on FatSecret")
    parser.add_argument('--user_from', type=int, default=1, help='Source user ID (default: 1)')
    parser.add_argument('--user_to', type=int, default=2, help='Target user ID (default: 2)')
    parser.add_argument('--meal', type=str, default=None,
                        choices=['Breakfast', 'Lunch', 'Dinner', 'Snack'],
                        help='Meal type to share (Breakfast/Lunch/Dinner/Snack). If not specified, all meals are shared')
    parser.add_argument('--date', type=str, default=None, help='Date in YYYY-MM-DD format (default: today)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Parse date or use today
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD")
            exit(1)
    else:
        target_date = datetime.now().replace(tzinfo=timezone.utc)

    # Execute meal sharing
    success = share_meal(args.user_from, args.user_to, args.meal, target_date)
    exit(0 if success else 1)