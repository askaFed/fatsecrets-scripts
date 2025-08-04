import json
import time
from datetime import datetime, timedelta, timezone
import argparse
from clients import exec_ai_request, get_all_users, get_food_log_entries_by_date, insert_nutrient_data

nutrients = """
- Carbohydrate (g)
- Protein (g)
- Fat (g)
- Fiber (g)
- Vitamin A (μg)
- Vitamin C (mg)
- Vitamin D (μg)
- Vitamin B12 (μg)
- Calcium (mg)
- Iron (mg)
- Magnesium (mg)
- Potassium (mg)
- Zinc (mg)
- Selenium (μg)
- Vitamin K (μg)
- Folate (μg)
- Inositol (mg)
- Thiamin (mg)
- Riboflavin (mg)
- Niacin (mg)
- Pantothenic Acid (mg)
- Vitamin B6 (mg)
- Biotin (μg)
- Iodine (μg)
- Omega-3 Fatty Acids (mg)
- Choline (mg)
- Chromium (μg)
"""

data_format = """
[
    {
        "food_entry_id": 123,
        "vitamin_a_mcg": 12.0,
        "vitamin_c_mg": 4.0
    },
    {
        "food_entry_id": 124,
        "vitamin_a_mcg": 15.0,
        "vitamin_c_mg": 2.0
    }
]
"""

data_format_string = json.dumps(data_format)


prompt = f"""
Analyze the following list of foods I consumed today and estimate the intake of the following nutrients:
{nutrients}

Use general nutritional knowledge and make reasonable approximations for local products in list.
Assume average homemade recipes where needed.

Output ONLY the result as a JSON object, exactly in the following format. 

{data_format_string}

DO NOT include any additional text, explanations, or code block delimiters (e.g., ```json).

"""


def parse_args():
    parser = argparse.ArgumentParser(description="Fetch and insert food entries.")
    parser.add_argument('--start', type=str, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end', type=str, help='End date in YYYY-MM-DD format')
    return parser.parse_args()


if __name__ == "__main__":
    print("📥 Fetching food entries for all users...")

    args = parse_args()

    # Default to yesterday and today if not provided
    today = datetime.now().replace(tzinfo=timezone.utc)
    default_start = today - timedelta(days=1)
    default_end = today

    # Parse dates or use defaults
    start = datetime.strptime(args.start, '%Y-%m-%d').date() if args.start else default_start.date()
    end = datetime.strptime(args.end, '%Y-%m-%d').date() if args.end else default_end.date()


    # Get all users with their access tokens
    users = get_all_users()

    if not users:
        print("❌ No users found in the database")
        exit(1)

    for user in users:
        print(f"👤 Processing user {user['id']} ({user['fatsecret_user_id']})")

        user_food_log = get_food_log_entries_by_date(start, end, user['id'])

        full_prompt = prompt + f"""
        Food log:
        {user_food_log}
        """

        nutrition_estimates = exec_ai_request(full_prompt)

        for nutrition_estimate in nutrition_estimates:
            insert_nutrient_data(nutrition_estimates)

        time.sleep(5)  # Delay between users
