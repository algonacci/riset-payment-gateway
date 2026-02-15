# xendit_simulate_simple.py
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

payment_id = input("Masukkan payment_request_id (pr-...): ").strip()

resp = httpx.post(
    f"https://api.xendit.co/v3/payment_requests/{payment_id}/simulate",
    auth=httpx.BasicAuth(secret_key, ""),
    headers={"api-version": "2024-11-11"},
    json={"amount": 10000}  # Sesuaikan amount
)

print(resp.status_code, resp.json())
