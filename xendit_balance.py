import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get secret key based on environment
xendit_env = os.getenv("XENDIT_ENV", "development").lower()
if xendit_env == "production":
    secret_key = os.getenv("XENDIT_SECRET_KEY_PROD")
    env_label = "PRODUCTION"
else:
    secret_key = os.getenv("XENDIT_SECRET_KEY_DEV")
    env_label = "DEVELOPMENT"

if not secret_key:
    print(f"❌ Error: XENDIT_SECRET_KEY_{env_label.upper()} tidak ditemukan di environment variables!")
    print("   Pastikan file .env sudah dibuat dan berisi secret key.")
    exit(1)

print(f"🌍 Environment: {env_label}")

response = httpx.get(
    "https://api.xendit.co/balance",
    auth=httpx.BasicAuth(username=secret_key, password=""),
    headers={"accept": "application/json"},
    params={
        "account_type": "CASH",
        "at_timestamp": "2024-01-01T00:00:00Z"
    }
)

print(response.json())
