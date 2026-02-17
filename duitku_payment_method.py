import http.client
import hashlib
import json
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

load_dotenv()

MERCHANT_CODE = os.getenv("DUITKU_MERCHANT_CODE", "")
API_KEY = os.getenv("DUITKU_API_KEY", "")
URL = os.getenv("DUITKU_SANDBOX_URL", "")
AMOUNT = "10000"
DATETIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

signature_string = MERCHANT_CODE + AMOUNT + DATETIME + API_KEY
signature = hashlib.sha256(signature_string.encode()).hexdigest()

payload = {
    "merchantcode": MERCHANT_CODE,
    "amount": AMOUNT,
    "datetime": DATETIME,
    "signature": signature
}

parsed_url = urlparse(URL)
host = str(parsed_url.netloc)
path = str(parsed_url.path)

conn = http.client.HTTPSConnection(host)
headers = {
    "Content-Type": "application/json"
}

conn.request("POST", path, body=json.dumps(payload), headers=headers)

response = conn.getresponse()
data = response.read().decode("utf-8")

print(f"Status: {response.status}")
print(f"Response: {data}")

conn.close()
