import argparse
import json
import os
from urllib.parse import quote

import httpx
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description="Cek status transaksi QRIS sandbox KlikQRIS")
    parser.add_argument("order_id", help="ID transaksi yang ingin dicek")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("KLIKQRIS_X_API_KEY")
    merchant_id = os.getenv("KLIKQRIS_MERCHANT_ID")
    base_url = os.getenv("KLIKQRIS_BASE_URL")
    if not all((api_key, merchant_id, base_url)):
        print("Error: KLIKQRIS_X_API_KEY, KLIKQRIS_MERCHANT_ID, dan KLIKQRIS_BASE_URL wajib diisi di .env")
        return 1

    try:
        response = httpx.get(
            f"{base_url.rstrip('/')}/qris/status/{quote(args.order_id, safe='')}",
            headers={"x-api-key": api_key, "id_merchant": merchant_id},
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

    if isinstance(result, dict) and isinstance(result.get("data"), dict):
        data = result["data"]
        if "qris_image" in data:
            result = {**result, "data": {key: value for key, value in data.items() if key != "qris_image"}}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if isinstance(result, dict) and result.get("status") else 1


if __name__ == "__main__":
    raise SystemExit(main())
