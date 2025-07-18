import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

GEMINI_AI_API_KEY = os.getenv("GEMINI_AI_API_KEY")

if not GEMINI_AI_API_KEY:
    raise ValueError("Missing GEMINI_AI_API_KEY environment variable.")

genai.configure(api_key=GEMINI_AI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-pro")



def exec_ai_request(prompt: str) -> []:
    print("Sending prompt:")
    print(prompt)
    print(">>>>")
    try:
        response = model.generate_content(prompt.strip())
        raw_text = response.text
        print(f"Raw text: {raw_text}")

        cleaned_response = raw_text.strip()

        return json.loads(cleaned_response)
    except Exception as e:
        if "429" in str(e):
            print("⚠️ Gemini Rate limited error:", e)
            raise ValueError({str(e)})
        else:
            print("❌ Gemini API error:", e)
            raise ValueError({str(e)})