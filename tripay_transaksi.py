import os
import time
import uuid
import hmac
import hashlib
from dotenv import load_dotenv
import httpx

load_dotenv()  # Load environment variables from .env file

apiKey = os.getenv("TRIPAY_API_KEY")
privateKey = os.getenv("TRIPAY_PRIVATE_KEY")

if not apiKey or not privateKey:
    print("Error: TRIPAY_API_KEY atau TRIPAY_PRIVATE_KEY tidak ditemukan")
    exit(1)


merchant_code = os.getenv("TRIPAY_MERCHANT_CODE")
merchant_ref = str(uuid.uuid4())  # Generate UUID otomatis
amount = 100000

if not merchant_code:
    print("Error: TRIPAY_MERCHANT_CODE tidak ditemukan")
    exit(1)

expiry = int(time.time() + (24 * 60 * 60))  # 24 jam

# Buat signature
signStr = "{}{}{}".format(merchant_code, merchant_ref, amount)
signature = hmac.new(
    bytes(privateKey, "latin-1"), bytes(signStr, "latin-1"), hashlib.sha256
).hexdigest()

print(f"Merchant Ref: {merchant_ref}")
print(f"Signature: {signature}")

payload = {
    "method": "QRIS2",  # Ganti ke QRIS
    "merchant_ref": merchant_ref,
    "amount": amount,
    "customer_name": "Nama Pelanggan",
    "customer_email": "emailpelanggan@domain.com",
    "customer_phone": "081234567890",
    "return_url": "https://domainanda.com/redirect",
    "expired_time": expiry,
    "signature": signature,
}

order_items = [
    {
        "sku": "PRODUK1",
        "name": "Nama Produk 1",
        "price": 50000,
        "quantity": 1,
        "product_url": "https://tokokamu.com/product/nama-produk-1",
        "image_url": "https://tokokamu.com/product/nama-produk-1.jpg",
    },
    {
        "sku": "PRODUK2",
        "name": "Nama Produk 2",
        "price": 50000,
        "quantity": 1,
        "product_url": "https://tokokamu.com/product/nama-produk-2",
        "image_url": "https://tokokamu.com/product/nama-produk-2.jpg",
    },
]

# Format order_items untuk form data
i = 0
for item in order_items:
    for k in item:
        payload["order_items[" + str(i) + "][" + str(k) + "]"] = item[k]
    i += 1

headers = {"Authorization": "Bearer " + apiKey}

try:
    result = httpx.post(
        url="https://tripay.co.id/api-sandbox/transaction/create",
        data=payload,
        headers=headers,
    )
    response = result.text
    print(response)
except Exception as e:
    print("Request Error: " + str(e))
