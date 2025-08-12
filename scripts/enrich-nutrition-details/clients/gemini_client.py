import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

GEMINI_AI_API_KEY = os.getenv("GEMINI_AI_API_KEY")

if not GEMINI_AI_API_KEY:
    raise ValueError("Missing GEMINI_AI_API_KEY environment variable.")

genai.configure(api_key=GEMINI_AI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-pro")

def exec_ai_request(prompt: str, retries=3, backoff_factor=2.0) -> []:
    print("Sending prompt:")
    print(prompt)
    print(">>>>")

    attempt = 0
    while attempt <= retries:
        try:
            response = model.generate_content(prompt.strip())
            raw_text = response.text
            print(f"Raw text: {raw_text}")

            cleaned_response = raw_text.strip()
            return json.loads(cleaned_response)

        except Exception as e:
            attempt += 1
            if attempt > retries:
                print("❌ Maximum retries reached. Giving up.")
                raise ValueError(str(e))

            if "429" in str(e):
                print(f"⚠️ Rate limit error on attempt {attempt}/{retries}: {e}")
            else:
                print(f"❌ API error on attempt {attempt}/{retries}: {e}")

            sleep_time = backoff_factor ** attempt
            print(f"⏳ Retrying in {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
