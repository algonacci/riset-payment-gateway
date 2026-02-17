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
INQUIRY_URL = "https://sandbox.duitku.com/webapi/api/merchant/v2/inquiry"

merchant_order_id = f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}"
payment_amount = 40000
payment_method = "SP"  # ShopeePay QRIS

signature_string = MERCHANT_CODE + merchant_order_id + str(payment_amount) + API_KEY
signature = hashlib.md5(signature_string.encode()).hexdigest()

payload = {
    "merchantCode": MERCHANT_CODE,
    "paymentAmount": payment_amount,
    "paymentMethod": payment_method,
    "merchantOrderId": merchant_order_id,
    "productDetails": "Test Product",
    "customerVaName": "John Doe",
    "email": "test@test.com",
    "callbackUrl": "https://your-ngrok-url.ngrok.io/callback/duitku",
    "returnUrl": "https://your-ngrok-url.ngrok.io/return/duitku",
    "signature": signature
}

print(f"Signature: {signature}")
print(f"Payload: {json.dumps(payload, indent=2)}\n")

parsed_url = urlparse(INQUIRY_URL)
host = str(parsed_url.netloc)
path = str(parsed_url.path)

conn = http.client.HTTPSConnection(host)
headers = {"Content-Type": "application/json"}

conn.request("POST", path, body=json.dumps(payload), headers=headers)

response = conn.getresponse()
data = response.read().decode("utf-8")

print(f"Status: {response.status}")
print(f"Order ID: {merchant_order_id}")
print(f"Response: {data}")

conn.close()
