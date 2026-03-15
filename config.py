import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
]

# filter out any None keys
GEMINI_API_KEYS = [k for k in GEMINI_API_KEYS if k]
