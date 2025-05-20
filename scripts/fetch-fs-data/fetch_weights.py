import time
from datetime import datetime
from clients import insert_values, make_oauth_request

def get_weight_data_for_month(date_obj):
    epoch_days = (date_obj - datetime(1970, 1, 1)).days
    params = {
        "method": "weights.get_month.v2",
        "format": "json",
        "date": epoch_days,
    }
    try:
        data = make_oauth_request(params)
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

def fetch_and_store_all_weights(start_year=2021):
    current = datetime(start_year, 1, 1)
    today = datetime.today()
    all_results = []

    while current <= today:
        print(f"📆 Fetching data for {current.strftime('%Y-%m')}...")
        entries = get_weight_data_for_month(current)
        all_results.extend(entries)
        # Go to next month
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)
        time.sleep(1)

    if not all_results:
        print("⚠️ No weight entries found.")
        return

    sorted_data = sorted(all_results)
    user_id = 1
    db_rows = [(user_id, date, weight) for date, weight in sorted_data]

    insert_sql = """
            INSERT INTO personal_data.weights (user_id, date, weight_kg)
            VALUES %s
            ON CONFLICT (user_id, date) DO UPDATE
            SET weight_kg = EXCLUDED.weight_kg;
        """

    insert_values(insert_sql, values)
    print(f"\n✅ Inserted/updated {len(db_rows)} rows into personal_data.weights")

if __name__ == "__main__":
    fetch_and_store_all_weights(start_year=2025)
