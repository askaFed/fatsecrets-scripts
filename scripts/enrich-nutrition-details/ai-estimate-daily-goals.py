import json
import time
from datetime import datetime, timedelta, timezone
import argparse
from clients import exec_ai_request, get_all_users, get_user_details, insert_daily_micronutrient_goals

nutrients = """
- Calories (kcal)
- Protein (g)
- Carbohydrate (g)
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
{
    "user_id": 123,
    "date": "2024-01-15",
    "calories_goal": 2000.0,
    "protein_goal_g": 150.0,
    "carbohydrate_goal_g": 250.0,
    "fat_goal_g": 67.0,
    "fiber_goal_g": 25.0,
    "vitamin_a_goal_mcg": 900.0,
    "vitamin_c_goal_mg": 90.0,
    "vitamin_d_goal_mcg": 15.0,
    "vitamin_b12_goal_mcg": 2.4,
    "calcium_goal_mg": 1000.0,
    "iron_goal_mg": 8.0,
    "magnesium_goal_mg": 400.0,
    "potassium_goal_mg": 3500.0,
    "zinc_goal_mg": 11.0,
    "selenium_goal_mcg": 55.0,
    "vitamin_k_goal_mcg": 120.0,
    "folate_goal_mcg": 400.0,
    "inositol_goal_mg": 1000.0,
    "thiamin_goal_mg": 1.2,
    "riboflavin_goal_mg": 1.3,
    "niacin_goal_mg": 16.0,
    "pantothenic_acid_goal_mg": 5.0,
    "vitamin_b6_goal_mg": 1.3,
    "biotin_goal_mcg": 30.0,
    "iodine_goal_mcg": 150.0,
    "omega_3_fatty_acids_goal_mg": 1100.0,
    "choline_goal_mg": 550.0,
    "chromium_goal_mcg": 35.0
}
"""

data_format_string = json.dumps(data_format, indent=2)

prompt = f"""
You are a nutrition expert. Based on the user's demographic information, calculate their daily recommended intake for the following nutrients:

{nutrients}

Use the following guidelines:
- Follow RDA (Recommended Dietary Allowance) and AI (Adequate Intake) values from the National Academy of Medicine
- Adjust for age, gender, pregnancy status, and activity level
- Consider special requirements for pregnant/breastfeeding women
- Use moderate activity level as baseline unless specified otherwise
- For missing demographic data, use conservative estimates for a healthy adult

Output ONLY the result as a JSON object, exactly in the following format:

{data_format_string}

DO NOT include any additional text, explanations, or code block delimiters (e.g., ```json).

"""


def parse_args():
    parser = argparse.ArgumentParser(description="Estimate daily micronutrient goals for users.")
    parser.add_argument('--start', type=str, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end', type=str, help='End date in YYYY-MM-DD format')
    return parser.parse_args()


def create_user_prompt(user_details):
    """Create a detailed prompt with user demographic information"""
    if not user_details:
        return "User demographic information not available. Use conservative estimates for a healthy adult."
    
    details = []
    if user_details.get('gender'):
        details.append(f"Gender: {user_details['gender']}")
    if user_details.get('age'):
        details.append(f"Age: {user_details['age']} years")
    if user_details.get('weight_kg'):
        details.append(f"Weight: {user_details['weight_kg']} kg")
    if user_details.get('height_cm'):
        details.append(f"Height: {user_details['height_cm']} cm")
    if user_details.get('activity_level'):
        details.append(f"Activity Level: {user_details['activity_level']}")
    if user_details.get('pregnancy_status'):
        details.append(f"Pregnancy Status: {user_details['pregnancy_status']}")
    
    return f"""
User Demographic Information:
{chr(10).join(details)}

Please calculate daily recommended intake based on these factors.
"""


if __name__ == "__main__":
    print("🎯 Estimating daily micronutrient goals for all users...")

    args = parse_args()

    # Default to today if not provided
    today = datetime.now().replace(tzinfo=timezone.utc)
    default_start = today.date()
    default_end = today.date()

    # Parse dates or use defaults
    start = datetime.strptime(args.start, '%Y-%m-%d').date() if args.start else default_start
    end = datetime.strptime(args.end, '%Y-%m-%d').date() if args.end else default_end

    # Get all users
    users = get_all_users()

    if not users:
        print("❌ No users found in the database")
        exit(1)

    for user in users:
        print(f"👤 Processing user {user['id']} ({user['fatsecret_user_id']})")

        # Get user demographic details
        user_details = get_user_details(user['id'])
        
        if not user_details:
            print(f"⚠️ No demographic details found for user {user['id']}, using conservative estimates")
            user_details = {}

        # Create full prompt with user details
        user_prompt = create_user_prompt(user_details)
        full_prompt = prompt + user_prompt

        try:
            # Get AI estimate for daily goals
            daily_goals = exec_ai_request(full_prompt)
            
            if daily_goals and isinstance(daily_goals, dict):
                # Add user_id and date to the goals
                daily_goals['user_id'] = user['id']
                daily_goals['date'] = start.strftime('%Y-%m-%d')
                
                # Insert the daily goals
                #insert_daily_micronutrient_goals([daily_goals])
                print(f"✅ Estimated daily goals for user {user['id']}")
            else:
                print(f"❌ Invalid AI response format for user {user['id']}")
                
        except Exception as e:
            print(f"❌ Error processing user {user['id']}: {e}")
            continue

        time.sleep(2)  # Delay between users

    print("🎉 Daily micronutrient goals estimation completed!") 