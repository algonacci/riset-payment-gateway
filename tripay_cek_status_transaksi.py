import os
from dotenv import load_dotenv
import httpx

load_dotenv()  # Load environment variables from .env file

apiKey = os.getenv("TRIPAY_API_KEY")

if not apiKey:
    print("Error: TRIPAY_API_KEY environment variable tidak ditemukan")
    exit(1)

try:
    # Input reference dari terminal
    reference = input("Masukkan reference transaksi: ").strip()

    if not reference:
        print("Error: Reference tidak boleh kosong")
        exit(1)

    payload = {"reference": reference}
    headers = {"Authorization": "Bearer " + apiKey}

    result = httpx.get(
        url="https://tripay.co.id/api-sandbox/transaction/check-status",
        params=payload,
        headers=headers,
    )
    response = result.text
    print(response)
except Exception as e:
    print("Request Error: " + str(e))
