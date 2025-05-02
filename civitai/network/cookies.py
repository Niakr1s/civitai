import os

from dotenv import load_dotenv

load_dotenv()

SECURE_CIVITAI_TOKEN = os.getenv("SECURE_CIVITAI_TOKEN")
if not SECURE_CIVITAI_TOKEN:
    raise ValueError("SECURE_CIVITAI_TOKEN is not set in the environment variables.")


cookies = {"__Secure-civitai-token": SECURE_CIVITAI_TOKEN}
