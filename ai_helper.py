import google.generativeai as genai
import os
from dotenv import load_dotenv

print("🚀 GEMINI AI HELPER LOADED")

load_dotenv()

API_KEY = ""

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


def ask_ai(user_message):

    print("🔥 GEMINI CALLED")

    prompt = f"""
You are a smart subscription assistant.

Help users choose plans, explain pricing, billing, upgrades.

Speak naturally like ChatGPT.

User message:
{user_message}
"""

    response = model.generate_content(prompt)

    return response.text
