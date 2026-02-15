from flask import Flask, request, jsonify
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

PRIVATE_KEY = os.getenv("TRIPAY_PRIVATE_KEY")

if not PRIVATE_KEY:
    raise ValueError("TRIPAY_PRIVATE_KEY environment variable tidak ditemukan")


@app.route("/callback", methods=["POST"])
def handle_callback():
    try:
        # 🔑 AMBIL RAW REQUEST BODY (INI YANG PENTING!)
        raw_body = request.get_data(as_text=True)

        # Ambil signature dari header
        received_signature = request.headers.get("X-Callback-Signature")

        if not received_signature:
            return jsonify(
                {"success": False, "message": "Signature tidak ditemukan di header"}
            ), 400

        # 🔐 Buat signature dari RAW BODY (bukan parsed JSON)
        calculated_signature = hmac.new(
            bytes(PRIVATE_KEY, "latin-1"), bytes(raw_body, "latin-1"), hashlib.sha256
        ).hexdigest()

        # 🐛 Debug output
        print("\n" + "=" * 70)
        print("🔍 DEBUG CALLBACK SIGNATURE")
        print("=" * 70)
        print(f"Raw Body: {raw_body}")
        print(f"\nReceived Signature:  {received_signature}")
        print(f"Calculated Signature: {calculated_signature}")
        print(f"\n✅ Match: {received_signature == calculated_signature}")
        print("=" * 70 + "\n")

        # Validasi signature
        if received_signature != calculated_signature:
            return jsonify({"success": False, "message": "Signature tidak valid"}), 403

        # Parse JSON setelah validasi berhasil
        callback_data = request.get_json(force=True)

        # 📊 Proses data callback
        print("\n" + "=" * 70)
        print("✅ CALLBACK DITERIMA & VALID")
        print("=" * 70)
        print(f"Reference: {callback_data.get('reference')}")
        print(f"Merchant Ref: {callback_data.get('merchant_ref')}")
        print(f"Status: {callback_data.get('status')}")
        print(f"Payment Method: {callback_data.get('payment_method')}")
        print(f"Total Amount: Rp {callback_data.get('total_amount'):,}")
        print(f"Amount Received: Rp {callback_data.get('amount_received'):,}")
        print(f"Fee Merchant: Rp {callback_data.get('fee_merchant'):,}")
        print(f"Paid At: {callback_data.get('paid_at')}")
        print("=" * 70 + "\n")

        # 🎯 TODO: Di sini update database, kirim email, dll
        # Contoh:
        # update_order_status(callback_data['merchant_ref'], 'PAID')
        # send_email_notification(callback_data['customer_email'])

        # ✅ Return success ke Tripay
        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"❌ Error processing callback: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint untuk cek apakah server hidup"""
    return jsonify({"status": "ok", "message": "Callback server is running"}), 200


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 TRIPAY CALLBACK SERVER")
    print("=" * 70)
    print(f"Server running on http://localhost:5000")
    print(f"Callback URL: http://localhost:5000/callback")
    print(f"Health Check: http://localhost:5000/health")
    print("\n⚠️  Pastikan ngrok sudah running dan URL di-set di Tripay!")
    print("=" * 70 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
