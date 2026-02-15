from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
import os
import httpx

apiKey = os.getenv("TRIPAY_API_KEY")

if not apiKey:
    print("Error: TRIPAY_API_KEY environment variable tidak ditemukan")
    exit(1)

try:
    headers = {"Authorization": "Bearer " + apiKey}

    result = httpx.get(
        url="https://tripay.co.id/api-sandbox/merchant/payment-channel",
        params={},
        headers=headers,
    )
    response = result.text
    print(response)
except Exception as e:
    print("Request Error: " + str(e))
