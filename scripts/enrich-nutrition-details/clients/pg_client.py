# fatsecret/pg_client.py

import os
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from dotenv import load_dotenv

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


def insert_values(sql, values):
    try:
        print(f" SQL {sql} ")
        print(f" Values: {values} ")

        conn = get_connection()
        cursor = conn.cursor()
        execute_values(cursor, sql, values)
        conn.commit()
        print(f"✅ Inserted {len(values)} rows.")
    except Exception as e:
        print(f"❌ DB error: {e}")
        raise ValueError({str(e)})
    finally:
        cursor.close()
        conn.close()


def get_food_log_entries_by_date(start, end, user):
    food_log_cols = "fatsecret_food_entry_id, fatsecret_food_id, food_name, calories, quantity"
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = f"""
            SELECT {food_log_cols}
            FROM personal_data.food_entries
            WHERE user_id = {user}
            AND date BETWEEN date('{start}') AND date('{end}')
        """

        # print(f" SQL {query} ")
        # print(">>>>")

        cursor.execute(query)
        results = cursor.fetchall()

        # Convert RealDictRow objects to plain dicts
        clean_results = [dict(row) for row in results]

        # print(f"Results {clean_results}")
        return clean_results

    except Exception as e:
        print(f"❌ DB error fetching food logs: {e}")
        raise ValueError({str(e)})
    finally:
        cursor.close()
        conn.close()
