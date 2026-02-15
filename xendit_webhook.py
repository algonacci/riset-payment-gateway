#!/usr/bin/env python3
# webhook.py - Webhook handler untuk Xendit Payment Requests V3

import os
from flask import Flask, request, jsonify
import hmac
import hashlib
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Webhook verification token (dari Xendit Dashboard)
WEBHOOK_TOKEN = os.getenv("XENDIT_WEBHOOK_TOKEN")

if not WEBHOOK_TOKEN:
    print("❌ Warning: XENDIT_WEBHOOK_TOKEN tidak ditemukan di environment variables!")
    print("   Pastikan file .env sudah dibuat dan berisi webhook token.")


def verify_webhook_signature(payload, signature):
    """Verify webhook signature dari Xendit"""
    if not WEBHOOK_TOKEN:
        print("⚠️  WEBHOOK_TOKEN not set, skipping signature verification")
        return True
    expected_signature = hmac.new(
        WEBHOOK_TOKEN.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


@app.route("/webhook/xendit", methods=["POST"])
def handle_xendit_webhook():
    print("\n" + "=" * 60)
    print("📡 WEBHOOK RECEIVED")
    print("=" * 60)

    # Get raw payload (untuk signature verification)
    raw_payload = request.get_data(as_text=True)
    signature = request.headers.get("x-xendit-signature")

    # Verify signature (optional tapi recommended)
    if signature:
        if not verify_webhook_signature(raw_payload, signature):
            print("❌ Signature verification failed!")
            return jsonify({"error": "Invalid signature"}), 401

    # Parse JSON payload
    try:
        data = json.loads(raw_payload)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400

    print(f"Event: {data.get('event', 'N/A')}")
    print(f"Data: {json.dumps(data, indent=2)}")

    # Handle berdasarkan event type
    event = data.get("event")

    if event == "payment_request.succeeded":
        print("\n✅ 💰 PAYMENT BERHASIL!")
        payment_id = data["data"]["id"]
        amount = data["data"]["amount"]
        reference_id = data["data"].get("reference_id")

        print(f"   Payment ID   : {payment_id}")
        print(f"   Amount       : Rp {amount:,}")
        print(f"   Reference ID : {reference_id}")

        # 🎯 TODO: Update status di database kamu
        # update_order_status(reference_id, "PAID")

    elif event == "payment_request.failed":
        print("\n❌ PAYMENT GAGAL!")
        payment_id = data["data"]["id"]
        reference_id = data["data"].get("reference_id")

        print(f"   Payment ID   : {payment_id}")
        print(f"   Reference ID : {reference_id}")

        # 🎯 TODO: Handle payment failed
        # update_order_status(reference_id, "FAILED")

    elif event == "payment_request.expired":
        print("\n⏰ PAYMENT EXPIRED!")
        # 🎯 TODO: Handle expired payment

    else:
        print(f"\nℹ️  Event lain: {event}")

    # Return 200 OK untuk acknowledge webhook
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    print("=" * 60)
    print("🚀 WEBHOOK SERVER RUNNING")
    print(f"📡 Listening on http://{host}:{port}/webhook/xendit")
    print("=" * 60)
    app.run(host=host, port=port, debug=debug)
