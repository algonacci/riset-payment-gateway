import os
import uuid
import hmac
import hashlib
from dotenv import load_dotenv
import httpx

load_dotenv()  # Load environment variables from .env file

privateKey = os.getenv("TRIPAY_PRIVATE_KEY")
merchant_code = os.getenv("TRIPAY_MERCHANT_CODE")

if not privateKey or not merchant_code:
    print("Error: TRIPAY_PRIVATE_KEY atau TRIPAY_MERCHANT_CODE tidak ditemukan")
    exit(1)

merchant_ref = str(uuid.uuid4())  # Generate UUID otomatis
amount = 100000  # Ganti sesuai kebutuhan

# Buat signature
signStr = "{}{}{}".format(merchant_code, merchant_ref, amount)
signature = hmac.new(
    bytes(privateKey, "latin-1"), bytes(signStr, "latin-1"), hashlib.sha256
).hexdigest()

print(f"Merchant Ref: {merchant_ref}")
print(f"Signature: {signature}")
