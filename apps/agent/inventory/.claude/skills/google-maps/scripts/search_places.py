#!/usr/bin/env python3
"""
Search for places using Google Maps Places API.

Builds exhaustive activity masterlist for inventory agent.
Outputs flat list format suitable for occasions.activities.

Usage:
    python3 search_places.py \
        --city "Monaco" \
        --country "Monaco" \
        --category "restaurant" \
        --output "files/content/activities/restaurants.json"
"""
import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

# Load .env from inventory agent root (5 levels up: scripts -> google-maps -> skills -> .claude -> inventory)
inventory_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(inventory_root / ".env")

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from maps_client import get_client
except ImportError:
    get_client = None


def geocode_city(city: str, country: str) -> tuple:
    """Get coordinates for a city."""
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if api_key:
        try:
            import requests
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": f"{city}, {country}",
                "key": api_key
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
    }

    city_lower = city.lower()
    if city_lower in known_cities:
        return known_cities[city_lower]

    print(f"Warning: Could not geocode {city}, {country}. Using Monaco coordinates.", file=sys.stderr)
    return (43.7384, 7.4246)


def transform_to_flat_format(place: dict, category: str) -> dict:
    """Transform Google Maps place to flat list format."""
    geometry = place.get("geometry", {})
    location = geometry.get("location", {})

    return {
        "id": place.get("place_id"),
        "source": "google_maps",
        "name": place.get("name"),
        "category": category,
        "rating": place.get("rating"),
        "rating_count": place.get("user_ratings_total"),
        "address": place.get("formatted_address") or place.get("vicinity"),
        "latitude": location.get("lat"),
        "longitude": location.get("lng"),
        "price_level": place.get("price_level"),
        "types": place.get("types", []),
        "occasion_relevance": None  # Can be set by activities subagent
    }


def search_places(city: str, country: str, category: str, query: str = None, radius: int = 5000) -> list:
    """
    Search for all places in a city by category.

    Args:
        city: City name
        country: Country name
        category: Place category (restaurant, museum, etc.)
        query: Additional search query
        radius: Search radius in meters

    Returns:
        List of places in flat list format
    """
    # Get city coordinates
    lat, lng = geocode_city(city, country)
    location = f"{lat},{lng}"
    print(f"Searching {category} near ({lat}, {lng}) with radius {radius}m", file=sys.stderr)

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("Error: GOOGLE_MAPS_API_KEY environment variable not set", file=sys.stderr)
        return []

    try:
        if get_client:
            client = get_client()

            # Build search query
            search_query = f"{category} in {city}"
            if query:
                search_query = f"{query} {category} in {city}"

            # Use text search for better results
            response = client.search_places(
                query=search_query,
                location=location,
                radius=radius,
                type=category
            )
        else:
            # Inline implementation
            import requests

            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            search_query = f"{category} in {city}"
            if query:
                search_query = f"{query} {category} in {city}"

            params = {
                "query": search_query,
                "location": location,
                "radius": radius,
                "type": category,
                "key": api_key
            }

            resp = requests.get(url, params=params, timeout=30)
            response = resp.json()

        places = response.get("results", [])
        print(f"Found {len(places)} {category} places", file=sys.stderr)

        # Handle pagination if available
        all_places = list(places)
        next_page_token = response.get("next_page_token")

        # Fetch additional pages (up to 3 pages total = 60 results)
        import time
        page_count = 1
        while next_page_token and page_count < 3:
            time.sleep(2)  # Required delay between page token requests
            page_count += 1

            if get_client:
                # Would need to add pagination support to client
                break
            else:
                params = {
                    "pagetoken": next_page_token,
                    "key": api_key
                }
                resp = requests.get(url, params=params, timeout=30)
                response = resp.json()
                all_places.extend(response.get("results", []))
                next_page_token = response.get("next_page_token")
                print(f"Fetched page {page_count}, total: {len(all_places)} places", file=sys.stderr)

        # Transform to flat list format
        results = []
        for place in all_places:
            transformed = transform_to_flat_format(place, category)
            if transformed.get("id"):  # Only include if has valid ID
                results.append(transformed)

        return results

    except Exception as e:
        print(f"Error searching places: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="Search for places via Google Maps API")
    parser.add_argument("--city", required=True, help="City name")
    parser.add_argument("--country", required=True, help="Country name")
    parser.add_argument("--category", required=True, help="Place category (restaurant, museum, etc.)")
    parser.add_argument("--query", help="Additional search query")
    parser.add_argument("--radius", type=int, default=5000, help="Search radius in meters")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    # Search places
    places = search_places(
        city=args.city,
        country=args.country,
        category=args.category,
        query=args.query,
        radius=args.radius
    )

    # Output results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(places, f, indent=2)
        print(f"Saved {len(places)} {args.category} places to {args.output}")
    else:
        # Output as JSON to stdout
        print(json.dumps({
            "source": "google_maps",
            "city": args.city,
            "country": args.country,
            "category": args.category,
            "search_date": datetime.now().isoformat(),
            "count": len(places),
            "places": places
        }, indent=2))


if __name__ == "__main__":
    main()
