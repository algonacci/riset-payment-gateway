#!/usr/bin/env python3
# xendit.py - QRIS Payment Request dengan reference_id unik

import os
import httpx
import json
import time
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def print_json_block(title: str, payload):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def extract_urls(payload, key_path=""):
    urls = []

    if isinstance(payload, dict):
        for key, value in payload.items():
            next_path = f"{key_path}.{key}" if key_path else key
            urls.extend(extract_urls(value, next_path))
    elif isinstance(payload, list):
        for idx, value in enumerate(payload):
            next_path = f"{key_path}[{idx}]"
            urls.extend(extract_urls(value, next_path))
    elif isinstance(payload, str) and payload.startswith(("https://", "http://")):
        urls.append((key_path, payload))

    return urls


def classify_action(action):
    action_type = action.get("type", "-")
    descriptor = action.get("descriptor", "-")
    value = action.get("value")

    if descriptor in ("WEB_URL", "DEEPLINK_URL"):
        return ("redirect", action_type, descriptor, value)
    if descriptor == "QR_STRING":
        return ("qr_string", action_type, descriptor, value)
    if action_type == "API_POST_REQUEST":
        return ("api_post_request", action_type, descriptor, value)
    return ("other", action_type, descriptor, value)


def resolve_channel_code(raw_channel_code: str) -> str:
    return raw_channel_code.strip().upper()


def extract_redirect_url_from_actions(actions):
    for action in actions:
        action_type = action.get("type")
        descriptor = action.get("descriptor")
        value = action.get("value")
        if (
            action_type == "REDIRECT_CUSTOMER"
            and descriptor in ("WEB_URL", "DEEPLINK_URL")
            and isinstance(value, str)
            and value.startswith(("https://", "http://"))
        ):
            return value
    return None

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
    print(
        f"\n❌ Error: XENDIT_SECRET_KEY_{env_label.upper()} tidak ditemukan di environment variables!"
    )
    print("   Pastikan file .env sudah dibuat dan berisi secret key.")
    exit(1)

print(f"\n🌍 Environment: {env_label}")
raw_channel_code = os.getenv("XENDIT_CHANNEL_CODE", "QRIS")
channel_code = resolve_channel_code(raw_channel_code)
request_timeout_seconds = float(os.getenv("XENDIT_REQUEST_TIMEOUT_SECONDS", "45"))
max_retries = int(os.getenv("XENDIT_REQUEST_MAX_RETRIES", "2"))
retry_delay_seconds = float(os.getenv("XENDIT_RETRY_DELAY_SECONDS", "1.5"))
request_amount = int(os.getenv("XENDIT_REQUEST_AMOUNT", "500"))

print(f"\n🆔 Reference ID: {reference_id}")
print(f"🏦 Channel Code: {channel_code}")
if raw_channel_code.strip().upper() != channel_code:
    print(f"↪️  Channel alias: {raw_channel_code} -> {channel_code}")
print(f"⏱️  Timeout       : {request_timeout_seconds}s")
print(f"🔁 Max Retries   : {max_retries}")
print(f"💸 Request Amount: Rp {request_amount:,}")
print("📡 Mengirim request ke Xendit API...")

try:
    payload = {
        "reference_id": reference_id,
        "type": "PAY",
        "country": "ID",
        "currency": "IDR",
        "request_amount": request_amount,
        "capture_method": "AUTOMATIC",
        "channel_code": channel_code,
        "channel_properties": {
            "success_return_url": "https://example.com/success",
            "failure_return_url": "https://example.com/failure",
        },
        "description": f"Pembayaran {channel_code} {reference_id}",
        "customer": {
            "reference_id": f"cust_{uuid.uuid4().hex[:8]}",
            "type": "INDIVIDUAL",
            "individual_detail": {
                "given_names": "John",
                "surname": "Doe",
                "email": "john.doe@example.com",
                "mobile_number": "+6281234567890",
            },
        },
    }

    total_attempts = max_retries + 1
    response = None
    for attempt in range(1, total_attempts + 1):
        try:
            response = httpx.post(
                "https://api.xendit.co/v3/payment_requests",
                auth=httpx.BasicAuth(username=secret_key, password=""),
                headers={"accept": "application/json", "api-version": "2024-11-11"},
                json=payload,
                timeout=request_timeout_seconds,
            )
            break
        except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            if attempt >= total_attempts:
                raise
            wait_seconds = retry_delay_seconds * attempt
            print(
                f"\n⚠️ Timeout attempt {attempt}/{total_attempts}: {type(e).__name__}"
            )
            print(f"   Retry dalam {wait_seconds:.1f}s ...")
            time.sleep(wait_seconds)

    if response is None:
        raise RuntimeError("Response kosong setelah retry")

    print(f"\n✅ Status Code: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        payment_id = data["payment_request_id"]
        status = data["status"]
        amount = data["request_amount"]
        actions = data.get("actions", [])

        print_json_block("🔍 RAW RESPONSE XENDIT", data)
        print_json_block("🔍 STRUKTUR ACTIONS", actions)

        # Cari kandidat payment/redirect URL dari seluruh response
        payment_url = extract_redirect_url_from_actions(actions)
        if not payment_url:
            payment_url = data.get("payment_url")
        all_urls = extract_urls(data)
        if not payment_url:
            redirect_keywords = (
                "actions",
                "redirect",
                "checkout",
                "deeplink",
                "payment_url",
            )
            for path, url in all_urls:
                normalized_path = path.lower()
                if "success_return_url" in normalized_path:
                    continue
                if "failure_return_url" in normalized_path:
                    continue
                if any(keyword in normalized_path for keyword in redirect_keywords):
                    payment_url = url
                    break

        if payment_url:
            print(f"\n🔗 Payment URL/Redirect: {payment_url}")
        elif all_urls:
            print("\n🔗 URL ditemukan di response:")
            for path, url in all_urls:
                print(f"   - {path}: {url}")
        else:
            print("\nℹ️ Tidak ada URL sama sekali di response.")

        if actions and len(actions) > 0:
            redirects = []
            qr_strings = []
            api_actions = []
            others = []

            for action in actions:
                category, action_type, descriptor, value = classify_action(action)
                if category == "redirect":
                    redirects.append((action_type, descriptor, value))
                elif category == "qr_string":
                    qr_strings.append((action_type, descriptor, value))
                elif category == "api_post_request":
                    api_actions.append((action_type, descriptor, value))
                else:
                    others.append((action_type, descriptor, value))

            print("\n" + "=" * 60)
            print("✅ PAYMENT REQUEST BERHASIL DIBUAT!")
            print("=" * 60)
            print(f"🆔 Payment Request ID: {payment_id}")
            print(f"💰 Amount            : Rp {amount:,}")
            print(f"📊 Status            : {status}")

            if redirects:
                print("\n🔀 Redirect actions:")
                for action_type, descriptor, value in redirects:
                    print(f"   - type={action_type}, descriptor={descriptor}")
                    print(f"     value={value}")

            if qr_strings:
                print("\n📱 QR actions (tanpa generate QR lokal):")
                for action_type, descriptor, value in qr_strings:
                    length = len(value) if isinstance(value, str) else 0
                    print(f"   - type={action_type}, descriptor={descriptor}, len={length}")
                    print(f"     value={value}")

            if api_actions:
                print("\n🔌 API POST actions:")
                for action_type, descriptor, value in api_actions:
                    print(f"   - type={action_type}, descriptor={descriptor}")
                    print(f"     value={value}")

            if others:
                print("\n🧩 Other actions:")
                for action_type, descriptor, value in others:
                    print(f"   - type={action_type}, descriptor={descriptor}")
                    print(f"     value={value}")
        else:
            print("\n❌ Tidak ada actions di response!")
            print("Response lengkap:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

    elif response.status_code == 409:
        print("\n❌ DUPLICATE_ERROR: Reference ID sudah dipakai")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n❌ Error {response.status_code}:")
        print(json.dumps(response.json(), indent=2))

except httpx.ReadTimeout as e:
    print(f"\n❌ Read Timeout: {e}")
    print("   Respons server terlalu lama.")
    print("   Coba naikkan XENDIT_REQUEST_TIMEOUT_SECONDS atau ulangi request.")
except httpx.ConnectTimeout as e:
    print(f"\n❌ Connect Timeout: {e}")
    print("   Gagal konek ke Xendit API.")
    print("   Cek koneksi internet / DNS / firewall.")
except httpx.RequestError as e:
    print(f"\n❌ Request Error: {e}")
    print("   Cek koneksi network atau endpoint API.")
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("✨ SELESAI")
print("=" * 60)
