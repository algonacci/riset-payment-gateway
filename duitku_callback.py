from flask import Flask, request, jsonify
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MERCHANT_CODE = os.getenv("DUITKU_MERCHANT_CODE", "")
API_KEY = os.getenv("DUITKU_API_KEY", "")

# IP Whitelist Duitku
DUITKU_IPS_SANDBOX = ["182.23.85.11", "182.23.85.12", "103.177.101.187", "103.177.101.188"]
DUITKU_IPS_PRODUCTION = [
    "182.23.85.8", "182.23.85.9", "182.23.85.10", "182.23.85.13", "182.23.85.14",
    "103.177.101.184", "103.177.101.185", "103.177.101.186", "103.177.101.189", "103.177.101.190"
]
DUITKU_IPS = DUITKU_IPS_SANDBOX + DUITKU_IPS_PRODUCTION


def verify_callback_signature(merchant_code, amount, merchant_order_id, api_key, received_signature):
    """Verify callback signature MD5(merchantCode + amount + merchantOrderId + apiKey)"""
    signature_string = merchant_code + amount + merchant_order_id + api_key
    expected_signature = hashlib.md5(signature_string.encode()).hexdigest()
    
    print("=" * 70)
    print("🔐 SIGNATURE VERIFICATION")
    print("=" * 70)
    print(f"String to Hash: {merchant_code} + {amount} + {merchant_order_id} + {api_key[:10]}...")
    print(f"Expected: {expected_signature}")
    print(f"Received: {received_signature}")
    print(f"Match: {expected_signature == received_signature}")
    print("=" * 70)
    
    return expected_signature == received_signature


def verify_ip_whitelist(client_ip):
    """Verify if IP is from Duitku"""
    # In production, check X-Forwarded-For if behind proxy
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        client_ip = forwarded_for.split(',')[0].strip()
    
    is_whitelisted = client_ip in DUITKU_IPS
    print(f"🌐 IP Check: {client_ip} - {'✅ Whitelisted' if is_whitelisted else '❌ Not in whitelist'}")
    return is_whitelisted


@app.route("/callback/duitku", methods=["POST"])
def handle_duitku_callback():
    try:
        # 🌐 Get client IP
        client_ip = request.remote_addr
        
        # 🔒 Optional: IP Whitelist Check (skip di development)
        # if not verify_ip_whitelist(client_ip):
        #     return jsonify({"error": "Unauthorized IP"}), 403
        
        # 📦 Parse form data (x-www-form-urlencoded)
        data = request.form
        
        merchant_code = data.get("merchantCode", "")
        amount = data.get("amount", "")
        merchant_order_id = data.get("merchantOrderId", "")
        product_details = data.get("productDetails", "")
        payment_code = data.get("paymentCode", "")
        result_code = data.get("resultCode", "")
        reference = data.get("reference", "")
        signature = data.get("signature", "")
        publisher_order_id = data.get("publisherOrderId", "")
        sp_user_hash = data.get("spUserHash", "")
        settlement_date = data.get("settlementDate", "")
        issuer_code = data.get("issuerCode", "")
        additional_param = data.get("additionalParam", "")
        merchant_user_id = data.get("merchantUserId", "")
        
        # 📝 Log incoming callback
        print("\n" + "=" * 70)
        print("📡 DUITKU CALLBACK RECEIVED")
        print("=" * 70)
        print(f"Merchant Code     : {merchant_code}")
        print(f"Order ID          : {merchant_order_id}")
        print(f"Amount            : Rp {amount}")
        print(f"Product           : {product_details}")
        print(f"Payment Method    : {payment_code}")
        print(f"Result Code       : {result_code} {'(SUCCESS)' if result_code == '00' else '(FAILED)'}")
        print(f"Reference         : {reference}")
        print(f"Publisher Order ID: {publisher_order_id}")
        print(f"Settlement Date   : {settlement_date}")
        print(f"Issuer Code       : {issuer_code}")
        if sp_user_hash:
            print(f"SP User Hash      : {sp_user_hash}")
        print("=" * 70)
        
        # 🔐 Verify signature
        if not verify_callback_signature(merchant_code, amount, merchant_order_id, API_KEY, signature):
            print("❌ Signature verification failed!")
            return jsonify({"status": "error", "message": "Invalid signature"}), 401
        
        print("\n✅ Signature verified successfully!")
        
        # 💰 Process payment based on result code
        if result_code == "00":
            # 🎯 TODO: Update order status to PAID in database
            # update_order_status(merchant_order_id, "PAID", reference)
            print(f"\n💰 PAYMENT SUCCESS - Order {merchant_order_id}")
            
        else:
            # 🎯 TODO: Handle failed payment
            # update_order_status(merchant_order_id, "FAILED", reference)
            print(f"\n❌ PAYMENT FAILED - Order {merchant_order_id}")
        
        # ✅ Must return HTTP 200 OK
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"❌ Error processing callback: {str(e)}")
        import traceback
        traceback.print_exc()
        # Still return 200 to prevent Duitku from retrying
        return jsonify({"status": "error", "message": str(e)}), 200


@app.route("/return/duitku", methods=["GET"])
def handle_duitku_return():
    """Handle return URL setelah user selesai/batal bayar"""
    merchant_order_id = request.args.get("merchantOrderId", "")
    reference = request.args.get("reference", "")
    result_code = request.args.get("resultCode", "")
    
    print("\n" + "=" * 70)
    print("🔄 USER RETURNED FROM PAYMENT PAGE")
    print("=" * 70)
    print(f"Order ID    : {merchant_order_id}")
    print(f"Reference   : {reference}")
    print(f"Result Code : {result_code} {'(SUCCESS)' if result_code == '00' else '(PENDING/CANCEL)' if result_code == '01' else '(CANCELED)'}")
    print("=" * 70)
    print("⚠️  INFORMASI SAJA - Jangan update database di sini!")
    print("📡 Tunggu callback untuk update status yang valid")
    print("=" * 70)
    
    # Return simple HTML atau redirect ke halaman sukses/gagal
    if result_code == "00":
        return f"""
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>✅ Pembayaran Berhasil</h1>
            <p>Order ID: {merchant_order_id}</p>
            <p>Reference: {reference}</p>
            <p><small>Status akan diupdate otomatis...</small></p>
        </body>
        </html>
        """, 200
    else:
        return f"""
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>⏳ Pembayaran Diproses</h1>
            <p>Order ID: {merchant_order_id}</p>
            <p>Silakan cek status pembayaran Anda</p>
        </body>
        </html>
        """, 200


@app.route("/callback/duitku", methods=["GET"])
def callback_health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Duitku callback endpoint is active",
        "merchant_code": MERCHANT_CODE[:5] + "..." if MERCHANT_CODE else "Not set"
    }), 200


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    print("=" * 70)
    print("🚀 DUITKU CALLBACK SERVER")
    print("=" * 70)
    print(f"Server running on http://localhost:{port}")
    print(f"\n📡 Callback URL (POST): http://localhost:{port}/callback/duitku")
    print(f"🔄 Return URL   (GET) : http://localhost:{port}/return/duitku")
    print(f"\n📋 Duitku Sandbox IPs: {', '.join(DUITKU_IPS_SANDBOX)}")
    print(f"\n⚠️  PERBEDAAN CALLBACK vs RETURN:")
    print("   Callback: POST, update database ✅")
    print("   Return  : GET, informasi UX saja ⚠️")
    print("\n⚠️  Pastikan:")
    print("   1. Callback URL & Return URL di-set di dashboard Duitku")
    print("   2. Gunakan ngrok untuk expose localhost ke internet")
    print("   3. IP whitelist aktif di production")
    print("=" * 70 + "\n")
    
    app.run(host=host, port=port, debug=debug)
