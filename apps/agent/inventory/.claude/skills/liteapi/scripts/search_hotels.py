#!/usr/bin/env python3
"""
Search for hotels using LiteAPI.

Supports searching by city, coordinates, or AI semantic query.
Outputs flat list format suitable for inventory building.

Usage:
    python3 search_hotels.py \
        --city "Barcelona" \
        --country "ES" \
        --check-in "2026-01-15" \
        --check-out "2026-01-20" \
        --output "files/content/accommodations/hotels.json"
"""
import argparse
import json
import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load .env from inventory agent root
inventory_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(inventory_root / ".env")

BASE_URL = "https://api.liteapi.travel/v3.0"


def get_headers():
    """Get API headers with authentication."""
    api_key = os.environ.get("LITEAPI_API_KEY")
    if not api_key:
        print("Error: LITEAPI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return {
        "accept": "application/json",
        "X-API-Key": api_key
    }


def search_hotels_by_city(
    city: str,
    country: str,
    limit: int = 200,
    min_rating: float = None,
    min_reviews: int = None,
    star_rating: str = None
) -> list:
    """
    Search hotels by city name.

    Args:
        city: City name
        country: Country code (ISO 2-letter)
        limit: Max results
        min_rating: Minimum guest rating
        min_reviews: Minimum review count
        star_rating: Comma-separated star ratings

    Returns:
        List of hotels
    """
    url = f"{BASE_URL}/data/hotels"
    params = {
        "countryCode": country.upper(),
        "cityName": city,
        "limit": limit
    }

    if min_rating:
        params["minRating"] = min_rating
    if min_reviews:
        params["minReviewsCount"] = min_reviews
    if star_rating:
        params["starRating"] = star_rating

    response = requests.get(url, params=params, headers=get_headers(), timeout=30)
    data = response.json()

    if "error" in data:
        print(f"API Error: {data.get('error', {}).get('message', 'Unknown error')}", file=sys.stderr)
        return []

    return data.get("data", [])


def search_hotels_by_coordinates(
    latitude: float,
    longitude: float,
    radius: int = 5000,
    limit: int = 200,
    min_rating: float = None,
    min_reviews: int = None
) -> list:
    """
    Search hotels by coordinates.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        radius: Search radius in meters (min 1000)
        limit: Max results
        min_rating: Minimum guest rating
        min_reviews: Minimum review count

    Returns:
        List of hotels
    """
    url = f"{BASE_URL}/data/hotels"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": max(radius, 1000),
        "limit": limit
    }

    if min_rating:
        params["minRating"] = min_rating
    if min_reviews:
        params["minReviewsCount"] = min_reviews

    response = requests.get(url, params=params, headers=get_headers(), timeout=30)
    data = response.json()

    if "error" in data:
        print(f"API Error: {data.get('error', {}).get('message', 'Unknown error')}", file=sys.stderr)
        return []

    return data.get("data", [])


def search_hotels_semantic(
    query: str,
    limit: int = 10,
    min_rating: float = None
) -> list:
    """
    Search hotels using AI semantic search.

    Args:
        query: Natural language search query
        limit: Max results (default 3)
        min_rating: Minimum rating filter

    Returns:
        List of hotels with semantic attributes
    """
    url = f"{BASE_URL}/data/hotels/semantic-search"
    params = {
        "query": query,
        "limit": limit
    }

    if min_rating:
        params["min_rating"] = min_rating

    response = requests.get(url, params=params, headers=get_headers(), timeout=30)
    data = response.json()

    if "error" in data:
        print(f"API Error: {data.get('error', {}).get('message', 'Unknown error')}", file=sys.stderr)
        return []

    return data.get("data", [])


def get_hotel_rates(
    hotel_ids: list,
    check_in: str,
    check_out: str,
    currency: str = "EUR",
    nationality: str = "US",
    adults: int = 2
) -> dict:
    """
    Get rates for specific hotels.

    Args:
        hotel_ids: List of hotel IDs
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        currency: Currency code
        nationality: Guest nationality (ISO 2-letter)
        adults: Number of adults

    Returns:
        Dict mapping hotel_id to minimum rate
    """
    url = f"{BASE_URL}/hotels/rates"
    payload = {
        "hotelIds": hotel_ids,
        "checkin": check_in,
        "checkout": check_out,
        "currency": currency,
        "guestNationality": nationality,
        "occupancies": [{"adults": adults, "children": []}],
        "timeout": 15,
        "maxRatesPerHotel": 1
    }

    headers = get_headers()
    headers["content-type"] = "application/json"

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    data = response.json()

    rates = {}
    for hotel in data.get("data", []):
        hotel_id = hotel.get("hotelId")
        room_types = hotel.get("roomTypes", [])
        if room_types:
            offer_rate = room_types[0].get("offerRetailRate", {})
            rates[hotel_id] = {
                "amount": offer_rate.get("amount"),
                "currency": offer_rate.get("currency")
            }

    return rates


def transform_hotel(hotel: dict, rates: dict = None) -> dict:
    """Transform LiteAPI hotel to flat format."""
    hotel_id = hotel.get("id")

    result = {
        "id": hotel_id,
        "source": "liteapi",
        "name": hotel.get("name"),
        "category": "hotel",
        "rating": hotel.get("rating"),
        "rating_count": hotel.get("reviewCount"),
        "stars": hotel.get("stars"),
        "address": hotel.get("address"),
        "city": hotel.get("city"),
        "country": hotel.get("country"),
        "latitude": hotel.get("latitude"),
        "longitude": hotel.get("longitude"),
        "main_photo": hotel.get("main_photo") or hotel.get("thumbnail"),
        "chain": hotel.get("chain"),
        "hotel_type_id": hotel.get("hotelTypeId"),
        "facility_ids": hotel.get("facilityIds", [])
    }

    # Add semantic attributes if present (from AI search)
    if "tags" in hotel:
        result["tags"] = hotel.get("tags")
        result["persona"] = hotel.get("persona")
        result["style"] = hotel.get("style")
        result["location_type"] = hotel.get("location_type")
        result["story"] = hotel.get("story")
        result["relevance_score"] = hotel.get("score")

    # Add rate if available
    if rates and hotel_id in rates:
        result["min_rate"] = rates[hotel_id]

    return result


def main():
    parser = argparse.ArgumentParser(description="Search hotels via LiteAPI")
    parser.add_argument("--city", help="City name")
    parser.add_argument("--country", help="Country code (ISO 2-letter)")
    parser.add_argument("--latitude", type=float, help="Latitude for coordinate search")
    parser.add_argument("--longitude", type=float, help="Longitude for coordinate search")
    parser.add_argument("--radius", type=int, default=5000, help="Search radius in meters")
    parser.add_argument("--ai-search", help="Natural language search query")
    parser.add_argument("--check-in", help="Check-in date (YYYY-MM-DD) for rate lookup")
    parser.add_argument("--check-out", help="Check-out date (YYYY-MM-DD) for rate lookup")
    parser.add_argument("--currency", default="EUR", help="Currency code")
    parser.add_argument("--nationality", default="US", help="Guest nationality")
    parser.add_argument("--adults", type=int, default=2, help="Number of adults")
    parser.add_argument("--min-rating", type=float, help="Minimum guest rating")
    parser.add_argument("--min-reviews", type=int, help="Minimum review count")
    parser.add_argument("--star-rating", help="Comma-separated star ratings")
    parser.add_argument("--limit", type=int, default=200, help="Max results")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--include-rates", action="store_true", help="Include rate lookup")

    args = parser.parse_args()

    # Determine search method
    if args.ai_search:
        print(f"Searching hotels with AI query: {args.ai_search}", file=sys.stderr)
        hotels = search_hotels_semantic(
            query=args.ai_search,
            limit=args.limit,
            min_rating=args.min_rating
        )
    elif args.latitude and args.longitude:
        print(f"Searching hotels near ({args.latitude}, {args.longitude})", file=sys.stderr)
        hotels = search_hotels_by_coordinates(
            latitude=args.latitude,
            longitude=args.longitude,
            radius=args.radius,
            limit=args.limit,
            min_rating=args.min_rating,
            min_reviews=args.min_reviews
        )
    elif args.city and args.country:
        print(f"Searching hotels in {args.city}, {args.country}", file=sys.stderr)
        hotels = search_hotels_by_city(
            city=args.city,
            country=args.country,
            limit=args.limit,
            min_rating=args.min_rating,
            min_reviews=args.min_reviews,
            star_rating=args.star_rating
        )
    else:
        print("Error: Provide --city/--country, --latitude/--longitude, or --ai-search", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(hotels)} hotels", file=sys.stderr)

    # Optionally get rates
    rates = {}
    if args.include_rates and args.check_in and args.check_out and hotels:
        hotel_ids = [h.get("id") for h in hotels if h.get("id")][:50]  # Limit to 50 for rate lookup
        print(f"Fetching rates for {len(hotel_ids)} hotels...", file=sys.stderr)
        rates = get_hotel_rates(
            hotel_ids=hotel_ids,
            check_in=args.check_in,
            check_out=args.check_out,
            currency=args.currency,
            nationality=args.nationality,
            adults=args.adults
        )
        print(f"Got rates for {len(rates)} hotels", file=sys.stderr)

    # Transform to flat format
    transformed = [transform_hotel(h, rates) for h in hotels]

    # Output
    output_data = {
        "source": "liteapi",
        "city": args.city,
        "country": args.country,
        "search_date": datetime.now().isoformat(),
        "count": len(transformed),
        "hotels": transformed
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(transformed)} hotels to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(output_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
