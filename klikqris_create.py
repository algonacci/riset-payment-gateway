import argparse
import json
import os
from uuid import uuid4

import httpx
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description="Buat transaksi QRIS sandbox KlikQRIS")
    parser.add_argument("amount", type=int, help="Nominal tagihan dalam rupiah")
    parser.add_argument("--order-id", default=None, help="ID unik transaksi (default: dibuat otomatis)")
    parser.add_argument("--keterangan", default="Testing Sandbox Transaction")
    args = parser.parse_args()
    if args.amount <= 0:
        parser.error("amount harus lebih besar dari 0")

    load_dotenv()
    api_key = os.getenv("KLIKQRIS_X_API_KEY")
    merchant_id = os.getenv("KLIKQRIS_MERCHANT_ID")
    base_url = os.getenv("KLIKQRIS_BASE_URL")
    if not all((api_key, merchant_id, base_url)):
        print("Error: KLIKQRIS_X_API_KEY, KLIKQRIS_MERCHANT_ID, dan KLIKQRIS_BASE_URL wajib diisi di .env")
        return 1

    payload = {
        "order_id": args.order_id or f"STEST-{uuid4().hex[:12].upper()}",
        "amount": args.amount,
        "id_merchant": merchant_id,
        "keterangan": args.keterangan,
    }
    try:
        response = httpx.post(
            f"{base_url.rstrip('/')}/qris/create",
            headers={"x-api-key": api_key, "id_merchant": merchant_id},
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(f"HTTP {exc.response.status_code}: {exc.response.text}")
        return 1
    except httpx.RequestError as exc:
        print(f"Request gagal: {exc}")
        return 1

    try:
        result = response.json()
    except ValueError:
        print(f"Response bukan JSON: {response.text}")
        return 1

    if not isinstance(result, dict):
        print(f"Response tidak sesuai format: {result}")
        return 1
    data = result.get("data")
    if isinstance(data, dict) and "qris_image" in data:
        result = {**result, "data": {key: value for key, value in data.items() if key != "qris_image"}}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result.get("status"):
        return 1
    if isinstance(data, dict) and data.get("total_amount") is not None:
        print(f"Nominal simulasi pembayaran: Rp{data['total_amount']} (total_amount, bukan amount)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
