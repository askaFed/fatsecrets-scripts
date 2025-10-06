# __init__.py
from .gemini_client import exec_ai_request
from .pg_client import (
    get_all_users,
    get_food_log_entries_by_date,
    insert_nutrient_data,
    get_user_details,
    insert_daily_micronutrient_goals,
    insert_food_entry_nutrients_normalized,
    insert_daily_nutrient_goals_normalized,
)

__all__ = [
    "exec_ai_request",
    "get_all_users",
    "get_food_log_entries_by_date",
    "insert_nutrient_data",
    "get_user_details",
    "insert_daily_micronutrient_goals",
    "insert_food_entry_nutrients_normalized",
    "insert_daily_nutrient_goals_normalized",
]
