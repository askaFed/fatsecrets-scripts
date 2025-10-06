# fatsecret/pg_client.py

import os
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT", 5432)
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DB = os.getenv("PG_DB")


def get_connection():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DB
    )


def get_all_users():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT u.id, u.fatsecret_user_id, t.access_token, t.access_token_secret
            FROM personal_data.users u
            JOIN personal_data.access_tokens t ON u.id = t.user_id
        """)
        users = cursor.fetchall()
        return users
    except Exception as e:
        print(f"❌ DB error getting users: {e}")
        raise ValueError({str(e)})
    finally:
        cursor.close()
        conn.close()


def get_user_details(user_id):
    """Get user demographic details for calculating daily goals"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT ud.gender, ud.age, ud.weight_kg, ud.height_cm, ud.activity_level, ud.pregnancy_status
            FROM personal_data.user_details ud
            WHERE ud.user_id = %s
        """, (user_id,))
        user_details = cursor.fetchone()
        return user_details
    except Exception as e:
        print(f"❌ DB error getting user details: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def insert_daily_micronutrient_goals(goals_data_list):
    """Insert daily micronutrient goals for users"""
    if not goals_data_list:
        print("⚠️ No goals data to insert.")
        return

    keys = list(goals_data_list[0].keys())
    columns = ', '.join(keys)
    placeholders = ', '.join([f'%({key})s' for key in keys])

    sql = f"""
        INSERT INTO personal_data.daily_micronutrient_goals ({columns})
        VALUES %s
        ON CONFLICT (user_id, date) DO UPDATE SET
        {', '.join([f"{k} = EXCLUDED.{k}" for k in keys if k not in ['user_id', 'date']])}
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()
        execute_values(cursor, sql, goals_data_list, template=f"({placeholders})")
        conn.commit()
        print(f"✅ Inserted/updated {len(goals_data_list)} daily goals records.")
    except Exception as e:
        print(f"❌ DB error inserting daily goals: {e}")
        raise ValueError({str(e)})
    finally:
        cursor.close()
        conn.close()


def insert_nutrient_data(nutrient_data_list):
    if not nutrient_data_list:
        print("⚠️ No nutrient data to insert.")
        return

    keys = list(nutrient_data_list[0].keys())
    columns = ', '.join(keys)
    placeholders = ', '.join([f'%({key})s' for key in keys])

    sql = f"""
        INSERT INTO personal_data.estimated_food_nutrients ({columns})
        VALUES %s
        ON CONFLICT (food_entry_id) DO UPDATE SET
        {', '.join([f"{k} = EXCLUDED.{k}" for k in keys if k != 'food_entry_id'])}
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()
        execute_values(cursor, sql, nutrient_data_list, template=f"({placeholders})")
        conn.commit()
        print(f"✅ Inserted/updated {len(nutrient_data_list)} nutrient records.")
    except Exception as e:
        print(f"❌ DB error inserting nutrient data: {e}")
        raise ValueError({str(e)})
    finally:
        cursor.close()
        conn.close()


def get_food_log_entries_by_date(start, end, user):
    food_log_cols = [
        "id AS food_entry_id",
        "food_name",
        "meal_type",
        "date",
        "user_id",
        "calories",
        "quantity"
    ]
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = f"""
            SELECT {', '.join(food_log_cols)}
            FROM personal_data.food_entries
            WHERE user_id = {user}
            AND date BETWEEN date('{start}') AND date('{end}')
        """

        print(f" SQL {query} ")
        print(">>>>")

        cursor.execute(query)
        results = cursor.fetchall()

        clean_results = [
            {
                key: float(value) if isinstance(value, Decimal) else value
                for key, value in dict(row).items()
            }
            for row in results
        ]

        print(f"Results {clean_results}")
        return clean_results

    except Exception as e:
        print(f"❌ DB error fetching food logs: {e}")
        raise ValueError({str(e)})
    finally:
        cursor.close()
        conn.close()


# ----------------------
# Normalized nutrients API
# ----------------------

_NUTRIENT_CODE_CACHE = None


def _load_nutrient_code_map(cursor):
    global _NUTRIENT_CODE_CACHE
    cursor.execute("SELECT id, code FROM personal_data.nutrients")
    rows = cursor.fetchall()
    _NUTRIENT_CODE_CACHE = {row[1]: row[0] for row in rows}
    return _NUTRIENT_CODE_CACHE


def _get_nutrient_code_map(cursor):
    global _NUTRIENT_CODE_CACHE
    if _NUTRIENT_CODE_CACHE is None:
        return _load_nutrient_code_map(cursor)
    return _NUTRIENT_CODE_CACHE


NORMALIZED_NUTRIENT_CODES = [
    'carbohydrate_g','protein_g','fat_g','fiber_g','vitamin_a_mcg','vitamin_c_mg','vitamin_d_mcg',
    'vitamin_b12_mcg','calcium_mg','iron_mg','magnesium_mg','potassium_mg','zinc_mg','selenium_mcg',
    'vitamin_k_mcg','folate_mcg','inositol_mg','thiamin_mg','riboflavin_mg','niacin_mg','pantothenic_acid_mg',
    'vitamin_b6_mg','biotin_mcg','iodine_mcg','omega_3_fatty_acids_mg','choline_mg','chromium_mcg'
]


def insert_food_entry_nutrients_normalized(nutrient_data_list):
    """Accepts list of dicts in the current wide format and writes rows into personal_data.food_entry_nutrients.

    Expected input keys per dict: food_entry_id, date, user_id, plus any of NORMALIZED_NUTRIENT_CODES.
    """
    if not nutrient_data_list:
        print("⚠️ No nutrient data to insert.")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()

        code_map = _get_nutrient_code_map(cursor)

        rows = []
        for item in nutrient_data_list:
            food_entry_id = item.get('food_entry_id')
            date = item.get('date')
            user_id = item.get('user_id')
            if not food_entry_id or not date or not user_id:
                # skip malformed
                continue
            for code in NORMALIZED_NUTRIENT_CODES:
                value = item.get(code)
                if value is None:
                    continue
                nutrient_id = code_map.get(code)
                if nutrient_id is None:
                    continue
                rows.append((user_id, food_entry_id, date, nutrient_id, float(value)))

        if not rows:
            print("⚠️ No normalized rows to insert.")
            return

        sql = """
            INSERT INTO personal_data.food_entry_nutrients (user_id, food_entry_id, date, nutrient_id, amount)
            VALUES %s
            ON CONFLICT (food_entry_id, nutrient_id) DO UPDATE SET amount = EXCLUDED.amount
        """

        execute_values(cursor, sql, rows)
        conn.commit()
        print(f"✅ Inserted/updated {len(rows)} food_entry_nutrient rows.")
    except Exception as e:
        print(f"❌ DB error inserting normalized nutrient data: {e}")
        raise ValueError({str(e)})
    finally:
        cursor.close()
        conn.close()


def insert_daily_nutrient_goals_normalized(goals_data_list):
    """Accepts list of dicts with wide goal keys and writes to personal_data.daily_nutrient_goals."""
    if not goals_data_list:
        print("⚠️ No goals data to insert.")
        return

    goal_key_to_code = {
        'protein_goal_g': 'protein_g',
        'carbohydrate_goal_g': 'carbohydrate_g',
        'fat_goal_g': 'fat_g',
        'fiber_goal_g': 'fiber_g',
        'vitamin_a_goal_mcg': 'vitamin_a_mcg',
        'vitamin_c_goal_mg': 'vitamin_c_mg',
        'vitamin_d_goal_mcg': 'vitamin_d_mcg',
        'vitamin_b12_goal_mcg': 'vitamin_b12_mcg',
        'calcium_goal_mg': 'calcium_mg',
        'iron_goal_mg': 'iron_mg',
        'magnesium_goal_mg': 'magnesium_mg',
        'potassium_goal_mg': 'potassium_mg',
        'zinc_goal_mg': 'zinc_mg',
        'selenium_goal_mcg': 'selenium_mcg',
        'vitamin_k_goal_mcg': 'vitamin_k_mcg',
        'folate_goal_mcg': 'folate_mcg',
        'inositol_goal_mg': 'inositol_mg',
        'thiamin_goal_mg': 'thiamin_mg',
        'riboflavin_goal_mg': 'riboflavin_mg',
        'niacin_goal_mg': 'niacin_mg',
        'pantothenic_acid_goal_mg': 'pantothenic_acid_mg',
        'vitamin_b6_goal_mg': 'vitamin_b6_mg',
        'biotin_goal_mcg': 'biotin_mcg',
        'iodine_goal_mcg': 'iodine_mcg',
        'omega_3_fatty_acids_goal_mg': 'omega_3_fatty_acids_mg',
        'choline_goal_mg': 'choline_mg',
        'chromium_goal_mcg': 'chromium_mcg'
    }

    try:
        conn = get_connection()
        cursor = conn.cursor()

        code_map = _get_nutrient_code_map(cursor)

        rows = []
        for goals in goals_data_list:
            user_id = goals.get('user_id')
            date = goals.get('date')
            if not user_id or not date:
                continue
            for goal_key, code in goal_key_to_code.items():
                val = goals.get(goal_key)
                if val is None:
                    continue
                nutrient_id = code_map.get(code)
                if nutrient_id is None:
                    continue
                rows.append((user_id, date, nutrient_id, float(val)))

        if not rows:
            print("⚠️ No normalized goals rows to insert.")
            return

        sql = """
            INSERT INTO personal_data.daily_nutrient_goals (user_id, date, nutrient_id, goal_amount)
            VALUES %s
            ON CONFLICT (user_id, date, nutrient_id) DO UPDATE SET goal_amount = EXCLUDED.goal_amount
        """
        execute_values(cursor, sql, rows)
        conn.commit()
        print(f"✅ Inserted/updated {len(rows)} daily_nutrient_goals rows.")
    except Exception as e:
        print(f"❌ DB error inserting normalized daily goals: {e}")
        raise ValueError({str(e)})
    finally:
        cursor.close()
        conn.close()
