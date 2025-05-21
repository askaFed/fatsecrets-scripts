# fatsecret/pg_client.py

import os
import psycopg2
from psycopg2.extras import execute_values
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


def insert_values(sql, values):
    try:
        print(f" SQL {sql} ")
        # print(f" Values: {values} ")

        conn = get_connection()
        cursor = conn.cursor()
        execute_values(cursor, sql, values)
        conn.commit()
        print(f"✅ Inserted {len(values)} rows.")
    except Exception as e:
        print(f"❌ DB error: {e}")
    finally:
        cursor.close()
        conn.close()
