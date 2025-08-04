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
