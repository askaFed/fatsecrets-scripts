import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
from requests_oauthlib import OAuth1Session

# === CREDENTIALS (replace with your actual values) ===
CONSUMER_KEY = '7c6bfe0a5c1a4937b8bbc21097e8060c'
CONSUMER_SECRET = '103b6a8e1bcb4757aaa10732aca57498'
ACCESS_TOKEN = '71f101c43bc3431193545c72f5a5b51e'
ACCESS_SECRET = '706e82306ddd4d6bb0749638a4a23ff1'

# === API CONFIGURATION ===
BASE_URL = 'https://platform.fatsecret.com/rest/server.api'
START_DATE = datetime.date(2023, 1, 1)  # Adjust as needed
END_DATE = datetime.date.today()

# === OAuth1 Session ===
oauth = OAuth1Session(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=ACCESS_TOKEN,
    resource_owner_secret=ACCESS_SECRET
)

def fetch_month_weights(date: datetime.date):
    # Convert date to epoch days (FatSecret expects days since Jan 1, 1970)
    epoch_days = (date - datetime.date(1970, 1, 1)).days

    params = {
        'method': 'weight.get_month.v2',
        'format': 'json',
        'date': str(epoch_days)
    }

    response = oauth.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get('month', {}).get('day', [])

def main():
    all_entries = []
    date_ptr = START_DATE

    while date_ptr <= END_DATE:
        print(f"Fetching weight data for {date_ptr.strftime('%Y-%m')}")
        try:
            month_data = fetch_month_weights(date_ptr)
            all_entries.extend(month_data)
        except Exception as e:
            print(f"Error on {date_ptr.strftime('%Y-%m')}: {e}")
        date_ptr += relativedelta(months=1)

    if all_entries:
        df = pd.DataFrame(all_entries)
        df['date'] = pd.to_datetime(df['date_int'], unit='D', origin='unix')
        df = df.sort_values('date')
        df.to_csv('weight_data.csv', index=False)
        print("✅ Exported to weight_data.csv")
    else:
        print("⚠️ No data found.")

if __name__ == '__main__':
    main()
