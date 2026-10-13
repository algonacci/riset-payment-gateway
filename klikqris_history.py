import json
import os

import httpx
from dotenv import load_dotenv


def main():
    load_dotenv()

    api_key = os.getenv("KLIKQRIS_X_API_KEY")
    merchant_id = os.getenv("KLIKQRIS_MERCHANT_ID")
    base_url = os.getenv("KLIKQRIS_BASE_URL")
    if not all((api_key, merchant_id, base_url)):
        print("Error: KLIKQRIS_X_API_KEY, KLIKQRIS_MERCHANT_ID, dan KLIKQRIS_BASE_URL wajib diisi di .env")
        return 1

    try:
        response = httpx.get(
            f"{base_url.rstrip('/')}/qris/history",
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
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except ValueError:
        print(response.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
