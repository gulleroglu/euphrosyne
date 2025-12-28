#!/usr/bin/env python3
"""
Search for hotel/stay accommodations using Duffel API.

Usage:
    python3 search_hotels.py \
        --location "Paris, France" \
        --check-in 2025-03-15 \
        --check-out 2025-03-20 \
        --adults 2 \
        --rooms 1 \
        --output files/content/hotels/search_001/
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from duffel_client import get_client


def format_price(amount: str, currency: str) -> str:
    """Format price with currency symbol."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, currency + " ")
    return f"{symbol}{float(amount):,.2f}"


def create_summary(properties: list, request_params: dict) -> str:
    """Create human-readable summary of hotel results."""
    lines = [
        f"# Hotel Search Results",
        f"",
        f"## Search Parameters",
        f"- **Location**: {request_params.get('location', 'N/A')}",
        f"- **Check-in**: {request_params['check_in']}",
        f"- **Check-out**: {request_params['check_out']}",
        f"- **Guests**: {request_params['adults']} adult(s)",
        f"- **Rooms**: {request_params['rooms']}",
        f"- **Results Found**: {len(properties)}",
        f"",
        f"## Top Hotel Options",
        f""
    ]

    for i, prop in enumerate(properties[:10], 1):
        name = prop.get("name", "Unknown Hotel")
        rating = prop.get("rating")
        address = prop.get("address", {})
        address_str = f"{address.get('line_1', '')}, {address.get('city', '')}"

        # Get cheapest rate
        rates = prop.get("rates", [])
        cheapest_rate = None
        if rates:
            cheapest_rate = min(rates, key=lambda r: float(r.get("total_amount", "999999")))

        lines.append(f"### Option {i}: {name}")

        if rating:
            lines.append(f"- **Rating**: {'⭐' * int(rating)}")

        lines.append(f"- **Address**: {address_str}")

        amenities = prop.get("amenities", [])
        if amenities:
            amenities_str = ", ".join(amenities[:5])
            lines.append(f"- **Amenities**: {amenities_str}")

        if cheapest_rate:
            amount = cheapest_rate.get("total_amount", "0")
            currency = cheapest_rate.get("total_currency", "USD")
            lines.append(f"- **Price**: {format_price(amount, currency)} total")

            cancellation = cheapest_rate.get("cancellation_policy", {})
            if cancellation.get("free_cancellation"):
                lines.append(f"- **Cancellation**: Free cancellation available")

        # Property ID for booking
        prop_id = prop.get("id", "")
        lines.append(f"- *Property ID: {prop_id}*")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    lines.extend([
        f"## Data Location",
        f"- Full properties: `properties.json`",
        f"- Top properties: `top_properties.json`",
        f"- Request parameters: `search_request.json`"
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search hotels via Duffel API")
    parser.add_argument("--location", help="Location name (e.g., 'Paris, France')")
    parser.add_argument("--latitude", type=float, help="Latitude coordinate")
    parser.add_argument("--longitude", type=float, help="Longitude coordinate")
    parser.add_argument("--check-in", required=True, help="Check-in date (YYYY-MM-DD)")
    parser.add_argument("--check-out", required=True, help="Check-out date (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=2, help="Number of adult guests")
    parser.add_argument("--rooms", type=int, default=1, help="Number of rooms")
    parser.add_argument("--output", required=True, help="Output directory for results")

    args = parser.parse_args()

    # Validate location input
    if not args.location and (args.latitude is None or args.longitude is None):
        print("Error: Either --location or --latitude/--longitude required", file=sys.stderr)
        sys.exit(1)

    # Build request parameters
    request_params = {
        "location": args.location,
        "latitude": args.latitude,
        "longitude": args.longitude,
        "check_in": args.check_in,
        "check_out": args.check_out,
        "adults": args.adults,
        "rooms": args.rooms,
        "searched_at": datetime.now().isoformat()
    }

    print(f"Searching hotels in: {args.location or f'{args.latitude}, {args.longitude}'}", file=sys.stderr)
    print(f"Dates: {args.check_in} to {args.check_out}", file=sys.stderr)

    try:
        client = get_client()

        # Build location object
        if args.latitude and args.longitude:
            location = {
                "geographic_coordinates": {
                    "latitude": args.latitude,
                    "longitude": args.longitude
                },
                "radius": 10  # km
            }
        else:
            # For location name, we'll use geocoding in a real implementation
            # For now, use as-is and let API handle it
            location = {
                "name": args.location
            }

        # Make API request
        response = client.search_stays(
            location=location,
            check_in_date=args.check_in,
            check_out_date=args.check_out,
            rooms=args.rooms,
            adults=args.adults
        )

        properties = response.get("data", {}).get("results", [])
        print(f"Found {len(properties)} properties", file=sys.stderr)

        # Sort by rating (descending) then price (ascending)
        def sort_key(prop):
            rating = prop.get("rating", 0) or 0
            rates = prop.get("rates", [])
            min_price = 999999
            if rates:
                min_price = min(float(r.get("total_amount", "999999")) for r in rates)
            return (-rating, min_price)

        properties_sorted = sorted(properties, key=sort_key)

        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        with open(output_dir / "search_request.json", 'w') as f:
            json.dump(request_params, f, indent=2)

        with open(output_dir / "properties.json", 'w') as f:
            json.dump(properties_sorted, f, indent=2)

        top_properties = properties_sorted[:10]
        with open(output_dir / "top_properties.json", 'w') as f:
            json.dump(top_properties, f, indent=2)

        summary = create_summary(properties_sorted, request_params)
        with open(output_dir / "summary.md", 'w') as f:
            f.write(summary)

        print(f"Results saved to {output_dir}", file=sys.stderr)

        # Output summary to stdout
        cheapest = None
        if properties_sorted:
            rates = properties_sorted[0].get("rates", [])
            if rates:
                cheapest = min(float(r.get("total_amount", "999999")) for r in rates)

        print(json.dumps({
            "status": "success",
            "properties_count": len(properties),
            "output_dir": str(output_dir),
            "top_property": properties_sorted[0].get("name") if properties_sorted else None,
            "cheapest_price": cheapest
        }, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print(json.dumps({
            "status": "error",
            "error": str(e)
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
