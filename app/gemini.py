import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing! Please check your .env file.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')
