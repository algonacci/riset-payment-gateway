import http.client
import hashlib
import json
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

load_dotenv()

MERCHANT_CODE = os.getenv("DUITKU_MERCHANT_CODE", "")
API_KEY = os.getenv("DUITKU_API_KEY", "")
CHECK_URL = "https://sandbox.duitku.com/webapi/api/merchant/transactionStatus"

print("=" * 70)
print("📋 CEK STATUS TRANSAKSI DUITKU")
print("=" * 70)

merchant_order_id = input("Masukkan Merchant Order ID: ").strip()

if not merchant_order_id:
    print("❌ Order ID tidak boleh kosong!")
    exit(1)

signature_string = MERCHANT_CODE + merchant_order_id + API_KEY
signature = hashlib.md5(signature_string.encode()).hexdigest()

payload = {
    "merchantcode": MERCHANT_CODE,
    "merchantOrderId": merchant_order_id,
    "signature": signature
}

print(f"\n🔍 Mengecek transaksi: {merchant_order_id}")
print(f"📝 Signature: {signature}\n")

parsed_url = urlparse(CHECK_URL)
host = str(parsed_url.netloc)
path = str(parsed_url.path)

conn = http.client.HTTPSConnection(host)
headers = {"Content-Type": "application/json"}

conn.request("POST", path, body=json.dumps(payload), headers=headers)

response = conn.getresponse()
data = response.read().decode("utf-8")

print(f"Status HTTP: {response.status}")
print(f"\n📄 Response:")
print("-" * 70)

try:
    result = json.loads(data)
    print(json.dumps(result, indent=2))
    
    if result.get("statusCode") == "00":
        print(f"\n✅ Status: {result.get('statusMessage', 'SUCCESS')}")
        print(f"💰 Amount: Rp {result.get('amount', 'N/A')}")
        print(f"📅 Settlement Date: {result.get('settlementDate', 'N/A')}")
    else:
        print(f"\n⚠️  Status: {result.get('statusMessage', 'UNKNOWN')}")
        
except json.JSONDecodeError:
    print(data)

print("-" * 70)
conn.close()
