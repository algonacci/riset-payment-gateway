from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
import os
import httpx

apiKey = os.getenv("TRIPAY_API_KEY")

try:
    payload = {"code": "QRIS2"}
    headers = {"Authorization": "Bearer " + apiKey}

    result = httpx.get(
        url="https://tripay.co.id/api-sandbox/payment/instruction",
        params=payload,
        headers=headers,
    )
    response = result.text
    print(response)
except Exception as e:
    print("Request Error: " + str(e))
