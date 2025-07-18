from clients import exec_ai_request
import json


# Load food log from file
with open("/Users/aska/IdeaProjects/fatsectets-scripts/scripts/enrich-nutrition-details/food_entries_202507141602.csv", "r", encoding="utf-8") as f:
    food_log = f.read()

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
        "fatsecret_food_id": 123,
        "vitamin_a_mcg": 12.0,
        "vitamin_c_mg": 4.0
    },
    {
        "fatsecret_food_id": 124,
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

Food log:
{food_log}
"""
nutrition_estimates = exec_ai_request(prompt)

for nutrition_estimate in nutrition_estimates:
    print(nutrition_estimate)
