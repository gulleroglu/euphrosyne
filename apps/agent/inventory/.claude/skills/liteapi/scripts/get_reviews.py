#!/usr/bin/env python3
"""
Fetch hotel reviews from LiteAPI.

Usage:
    python3 get_reviews.py --hotel-id "lp55143"
    python3 get_reviews.py --hotel-id "lp55143" --limit 30
"""
import argparse
import json
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

inventory_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(inventory_root / ".env")

BASE_URL = "https://api.liteapi.travel/v3.0"


def get_headers():
    api_key = os.environ.get("LITEAPI_API_KEY")
    if not api_key:
        print("Error: LITEAPI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return {"accept": "application/json", "X-API-Key": api_key}


def main():
    parser = argparse.ArgumentParser(description="Fetch hotel reviews from LiteAPI")
    parser.add_argument("--hotel-id", required=True, help="LiteAPI hotel ID")
    parser.add_argument("--limit", type=int, default=30, help="Number of reviews")
    args = parser.parse_args()

    url = f"{BASE_URL}/data/reviews"
    params = {"hotelId": args.hotel_id, "limit": args.limit}

    response = requests.get(url, params=params, headers=get_headers(), timeout=30)
    data = response.json()

    if "error" in data:
        print(f"Error: {data.get('error', {}).get('message', 'Unknown')}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
