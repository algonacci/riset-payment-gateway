import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()
app = Flask(__name__)


@app.route("/webhook/klikqris", methods=["POST"])
def handle_klikqris_webhook():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Body harus JSON object"}), 400

    required = ("order_id", "status", "amount", "total_amount", "signature")
    if any(data.get(field) is None or data[field] == "" for field in required):
        return jsonify({"error": "Field webhook wajib tidak lengkap"}), 400
    if not isinstance(data["order_id"], str) or not isinstance(data["status"], str) or not isinstance(data["signature"], str):
        return jsonify({"error": "Format field webhook tidak valid"}), 400
    if type(data["amount"]) is not int or type(data["total_amount"]) is not int:
        return jsonify({"error": "Nominal webhook harus integer"}), 400

    # Algoritme signature KlikQRIS belum tersedia: jangan percaya status atau proses pembayaran.
    print(f"KlikQRIS webhook (belum terverifikasi): order_id={data['order_id']!r}, status={data['status']!r}")
    return jsonify({"status": "received", "verified": False, "processed": False}), 200


@app.route("/webhook/klikqris", methods=["GET"])
def webhook_health():
    return jsonify({"status": "ok", "message": "KlikQRIS webhook aktif"}), 200


@app.route("/pembayaran/selesai", methods=["GET"])
def payment_return():
    return render_template("klikqris_selesai.html")


@app.route("/pembayaran/snap", methods=["GET"])
def payment_snap():
    return render_template(
        "klikqris_snap.html",
        order_id=request.args.get("order_id", ""),
        signature=request.args.get("signature", ""),
    )


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    print(f"KlikQRIS webhook: http://localhost:{port}/webhook/klikqris")
    print(f"KlikQRIS redirect: http://localhost:{port}/pembayaran/selesai")
    print(f"KlikQRIS Snap: http://localhost:{port}/pembayaran/snap")
    app.run(host=host, port=port, debug=False)
