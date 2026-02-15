import os
from dotenv import load_dotenv
import httpx

load_dotenv()  # Load environment variables from .env file

apiKey = os.getenv("TRIPAY_API_KEY")

if not apiKey:
    print("Error: TRIPAY_API_KEY environment variable tidak ditemukan")
    exit(1)

try:
    payload = {"code": "QRIS2", "amount": 100000}
    headers = {"Authorization": "Bearer " + apiKey}

    result = httpx.get(
        url="https://tripay.co.id/api-sandbox/merchant/fee-calculator",
        params=payload,
        headers=headers,
    )
    response = result.text
    print(response)
except Exception as e:
    print("Request Error: " + str(e))
