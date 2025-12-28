#!/usr/bin/env python3
"""
Search for hotels using Duffel Stays API.

Builds exhaustive hotel masterlist for inventory agent.
Outputs flat list format suitable for occasions.accommodations.

Usage:
    python3 search_hotels.py \
        --city "Monaco" \
        --country "Monaco" \
        --check-in "2025-05-23" \
        --check-out "2025-05-25" \
        --output "files/content/accommodations/duffel_hotels.json"
"""
import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Load .env from inventory agent root (5 levels up: scripts -> duffel -> skills -> .claude -> inventory)
inventory_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(inventory_root / ".env")

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from duffel_client import get_client
except ImportError:
    get_client = None


def geocode_city(city: str, country: str) -> tuple:
    """
    Get coordinates for a city using Google Maps Geocoding API or fallback.
    """
    # Try Google Maps geocoding if API key available
    google_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if google_api_key:
        try:
            import requests
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": f"{city}, {country}",
                "key": google_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if data.get("results"):
                location = data["results"][0]["geometry"]["location"]
                return (location["lat"], location["lng"])
        except Exception as e:
            print(f"Geocoding warning: {e}", file=sys.stderr)

    # Fallback to known cities
    known_cities = {
        "monaco": (43.7384, 7.4246),
        "paris": (48.8566, 2.3522),
        "london": (51.5074, -0.1278),
        "new york": (40.7128, -74.0060),
        "tokyo": (35.6762, 139.6503),
        "dubai": (25.2048, 55.2708),
        "singapore": (1.3521, 103.8198),
        "hong kong": (22.3193, 114.1694),
        "sydney": (-33.8688, 151.2093),
        "los angeles": (34.0522, -118.2437),
        "miami": (25.7617, -80.1918),
        "rome": (41.9028, 12.4964),
        "barcelona": (41.3851, 2.1734),
        "amsterdam": (52.3676, 4.9041),
        "berlin": (52.5200, 13.4050),
        "vienna": (48.2082, 16.3738),
        "zurich": (47.3769, 8.5417),
        "milan": (45.4642, 9.1900),
    }

    city_lower = city.lower()
    if city_lower in known_cities:
        return known_cities[city_lower]

    print(f"Warning: Could not geocode {city}, {country}. Using Monaco coordinates.", file=sys.stderr)
    return (43.7384, 7.4246)


def transform_to_flat_format(accommodation: dict) -> dict:
    """Transform Duffel accommodation result to flat list format."""
    # Handle nested structure from Duffel API
    acc_data = accommodation.get("accommodation", accommodation)

    location = acc_data.get("location", {})
    geo = location.get("geographic_coordinates", {})
    address_obj = location.get("address", {})

    # Build address string
    address_parts = []
    if address_obj.get("line_one"):
        address_parts.append(address_obj["line_one"])
    if address_obj.get("city_name"):
        address_parts.append(address_obj["city_name"])
    if address_obj.get("country_code"):
        address_parts.append(address_obj["country_code"])
    address = ", ".join(address_parts) if address_parts else None

    return {
        "id": acc_data.get("id"),
        "source": "duffel",
        "name": acc_data.get("name"),
        "stars": acc_data.get("rating"),
        "rating": acc_data.get("review_score"),
        "rating_count": acc_data.get("review_count"),
        "address": address,
        "latitude": geo.get("latitude"),
        "longitude": geo.get("longitude"),
        "amenities": acc_data.get("amenities", []),
        "price_range": None  # Not filtering by price for masterlist
    }


def search_hotels(city: str, country: str, check_in: str, check_out: str, radius: int = 10) -> list:
    """
    Search for all hotels in a city via Duffel API.

    Args:
        city: City name
        country: Country name
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        radius: Search radius in km

    Returns:
        List of hotels in flat list format
    """
    # Get city coordinates
    lat, lng = geocode_city(city, country)
    print(f"Searching hotels near ({lat}, {lng}) with radius {radius}km", file=sys.stderr)

    # Check for API key
    api_key = os.environ.get("DUFFEL_API_KEY")
    if not api_key:
        print("Error: DUFFEL_API_KEY environment variable not set", file=sys.stderr)
        return []

    try:
        if get_client:
            client = get_client()
        else:
            # Inline client if import failed
            import requests

            class InlineClient:
                def __init__(self):
                    self.session = requests.Session()
                    self.session.headers.update({
                        "Authorization": f"Bearer {api_key}",
                        "Duffel-Version": "v2",
                        "Content-Type": "application/json"
                    })

                def search_stays(self, location, check_in_date, check_out_date, rooms=1, adults=2):
                    url = "https://api.duffel.com/stays/search"
                    payload = {
                        "data": {
                            "location": location,
                            "check_in_date": check_in_date,
                            "check_out_date": check_out_date,
                            "rooms": rooms,
                            "guests": [{"type": "adult"} for _ in range(adults)]
                        }
                    }
                    response = self.session.post(url, json=payload, timeout=60)
                    response.raise_for_status()
                    return response.json()

            client = InlineClient()

        # Build location object
        location = {
            "geographic_coordinates": {
                "latitude": lat,
                "longitude": lng
            },
            "radius": radius
        }

        # Make API request
        response = client.search_stays(
            location=location,
            check_in_date=check_in,
            check_out_date=check_out,
            rooms=1,
            adults=2
        )

        results = response.get("data", {}).get("results", [])
        print(f"Found {len(results)} properties from Duffel", file=sys.stderr)

        # Transform to flat list format
        hotels = []
        for result in results:
            hotel = transform_to_flat_format(result)
            if hotel.get("id"):  # Only include if has valid ID
                hotels.append(hotel)

        return hotels

    except Exception as e:
        print(f"Error searching hotels: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="Search for hotels via Duffel API")
    parser.add_argument("--city", required=True, help="City name")
    parser.add_argument("--country", required=True, help="Country name")
    parser.add_argument("--check-in", help="Check-in date (YYYY-MM-DD)")
    parser.add_argument("--check-out", help="Check-out date (YYYY-MM-DD)")
    parser.add_argument("--radius", type=int, default=10, help="Search radius in km")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    # Default dates if not provided (30-32 days from now)
    check_in = args.check_in or (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    check_out = args.check_out or (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")

    # Search hotels
    hotels = search_hotels(
        city=args.city,
        country=args.country,
        check_in=check_in,
        check_out=check_out,
        radius=args.radius
    )

    # Output results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(hotels, f, indent=2)
        print(f"Saved {len(hotels)} hotels to {args.output}")
    else:
        # Output as JSON to stdout
        print(json.dumps({
            "source": "duffel",
            "city": args.city,
            "country": args.country,
            "search_date": datetime.now().isoformat(),
            "count": len(hotels),
            "hotels": hotels
        }, indent=2))


if __name__ == "__main__":
    main()
