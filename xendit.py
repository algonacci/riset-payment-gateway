#!/usr/bin/env python3
# xendit.py - QRIS Payment Request dengan reference_id unik

import os
import httpx
import json
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("=" * 60)
print("🚀 MEMBUAT QRIS PAYMENT (UNIQUE REFERENCE)")
print("=" * 60)

# Generate unique reference_id
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
random_suffix = uuid.uuid4().hex[:8]
reference_id = f"order_{timestamp}_{random_suffix}"

# Get secret key based on environment
xendit_env = os.getenv("XENDIT_ENV", "development").lower()
if xendit_env == "production":
    secret_key = os.getenv("XENDIT_SECRET_KEY_PROD")
    env_label = "PRODUCTION"
else:
    secret_key = os.getenv("XENDIT_SECRET_KEY_DEV")
    env_label = "DEVELOPMENT"

if not secret_key:
    print(f"\n❌ Error: XENDIT_SECRET_KEY_{env_label.upper()} tidak ditemukan di environment variables!")
    print("   Pastikan file .env sudah dibuat dan berisi secret key.")
    exit(1)

print(f"\n🌍 Environment: {env_label}")

print(f"\n🆔 Reference ID: {reference_id}")
print("📡 Mengirim request ke Xendit API...")

try:
    response = httpx.post(
        "https://api.xendit.co/v3/payment_requests",
        auth=httpx.BasicAuth(username=secret_key, password=""),
        headers={
            "accept": "application/json",
            "api-version": "2024-11-11"
        },
        json={
            "reference_id": reference_id,
            "type": "PAY",
            "country": "ID",
            "currency": "IDR",
            "request_amount": 10000,
            "capture_method": "AUTOMATIC",
            "channel_code": "QRIS",
            "channel_properties": {
                "success_return_url": "https://example.com/success",
                "failure_return_url": "https://example.com/failure"
            },
            "description": f"Pembayaran QRIS {reference_id}",
            "customer": {
                "reference_id": f"cust_{uuid.uuid4().hex[:8]}",
                "type": "INDIVIDUAL",
                "individual_detail": {
                    "given_names": "John",
                    "surname": "Doe",
                    "email": "john.doe@example.com",
                    "mobile_number": "+6281234567890"
                }
            }
        },
        timeout=15.0
    )
    
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        payment_id = data["payment_request_id"]
        status = data["status"]
        amount = data["request_amount"]
        
        # 🔍 DEBUG: Print lengkap struktur actions
        print("\n" + "=" * 60)
        print("🔍 STRUKTUR ACTIONS (QRIS)")
        print("=" * 60)
        print(json.dumps(data.get("actions", []), indent=2))
        
        # Ambil QR content
        actions = data.get("actions", [])
        if actions and len(actions) > 0:
            action = actions[0]
            qr_type = action.get("type")
            descriptor = action.get("descriptor")
            qr_value = action.get("value", "")
            
            print("\n" + "=" * 60)
            print("✅ QRIS BERHASIL DIBUAT!")
            print("=" * 60)
            print(f"🆔 Payment Request ID: {payment_id}")
            print(f"💰 Amount            : Rp {amount:,}")
            print(f"📊 Status            : {status}")
            print(f"\n📱 Action Type       : {qr_type}")
            print(f"🔍 Descriptor        : {descriptor}")
            print(f"🔤 QR Value (length) : {len(qr_value)} chars")
            print(f"\n📱 QR Content:")
            print(f"   {qr_value}")
            
            # Generate QR image (opsional)
            try:
                import qrcode
                from PIL import Image
                
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=8,
                    border=2,
                )
                qr.add_data(qr_value)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                filename = f"qris_{timestamp}.png"
                img.save(filename)
                print(f"\n🖼️ QR Code disimpan sebagai: {filename}")
                print("\n💡 Cara Test:")
                print("   1. Buka file QR yang baru dibuat")
                print("   2. Scan dengan Xendit QRIS Simulator")
                print("      (Dashboard → Tools → QRIS Simulator)")
                print("   3. Pilih 'Success' untuk simulasi pembayaran")
            except ImportError:
                print("\n⚠️ Library 'qrcode' belum terinstall")
                print("   Install dengan: uv add qrcode[pil]")
            except Exception as e:
                print(f"\n⚠️ Gagal generate QR image: {e}")
        else:
            print("\n❌ Tidak ada actions di response!")
            print("Response lengkap:")
            print(json.dumps(data, indent=2))
            
    elif response.status_code == 409:
        print("\n❌ DUPLICATE_ERROR: Reference ID sudah dipakai")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n❌ Error {response.status_code}:")
        print(json.dumps(response.json(), indent=2))
        
except httpx.RequestError as e:
    print(f"\n❌ Request Error: {e}")
    print("   Pastikan URL endpoint TANPA SPASI di akhir!")
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✨ SELESAI")
print("=" * 60)
