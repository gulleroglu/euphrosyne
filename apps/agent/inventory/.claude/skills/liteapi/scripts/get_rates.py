#!/usr/bin/env python3
"""
Get hotel rates from LiteAPI.

Usage:
    # By hotel ID(s)
    python3 get_rates.py --hotel-ids "lp55143,lp368af" --check-in 2026-01-15 --check-out 2026-01-20

    # By city
    python3 get_rates.py --city "Barcelona" --country "ES" --check-in 2026-01-15 --check-out 2026-01-20

    # By coordinates
    python3 get_rates.py --lat 52.209 --lon 5.023 --radius 10000 --check-in 2026-01-15 --check-out 2026-01-20
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
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-Key": api_key
    }


def main():
    parser = argparse.ArgumentParser(description="Get hotel rates from LiteAPI")

    # Location options (one required)
    parser.add_argument("--hotel-ids", help="Comma-separated hotel IDs")
    parser.add_argument("--city", help="City name")
    parser.add_argument("--country", help="Country code (ISO 2-letter)")
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lon", type=float, help="Longitude")
    parser.add_argument("--radius", type=int, default=10000, help="Radius in meters (default: 10000)")

    # Required dates
    parser.add_argument("--check-in", required=True, help="Check-in date (YYYY-MM-DD)")
    parser.add_argument("--check-out", required=True, help="Check-out date (YYYY-MM-DD)")

    # Optional
    parser.add_argument("--adults", type=int, default=2, help="Number of adults (default: 2)")
    parser.add_argument("--currency", default="EUR", help="Currency code (default: EUR)")
    parser.add_argument("--nationality", default="US", help="Guest nationality (default: US)")
    parser.add_argument("--limit", type=int, default=10, help="Max hotels (default: 10)")

    args = parser.parse_args()

    # Build payload
    payload = {
        "checkin": args.check_in,
        "checkout": args.check_out,
        "currency": args.currency,
        "guestNationality": args.nationality,
        "occupancies": [{"adults": args.adults, "children": []}],
        "timeout": 15,
        "limit": args.limit,
        "includeHotelData": True
    }

    # Add location
    if args.hotel_ids:
        payload["hotelIds"] = [h.strip() for h in args.hotel_ids.split(",")]
    elif args.city and args.country:
        payload["countryCode"] = args.country.upper()
        payload["cityName"] = args.city
    elif args.lat and args.lon:
        payload["latitude"] = args.lat
        payload["longitude"] = args.lon
        payload["radius"] = args.radius
    else:
        print("Error: Provide --hotel-ids, --city/--country, or --lat/--lon", file=sys.stderr)
        sys.exit(1)

    response = requests.post(
        f"{BASE_URL}/hotels/rates",
        json=payload,
        headers=get_headers(),
        timeout=30
    )
    data = response.json()

    if "error" in data:
        print(f"Error: {data.get('error', {}).get('message', 'Unknown')}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
