#!/usr/bin/env python3
"""
Search for places using Google Maps Places API.

Usage:
    python3 search_places.py \
        --query "museums in Paris" \
        --location 48.8566,2.3522 \
        --radius 5000 \
        --type museum \
        --output files/content/activities/paris/museums/
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from maps_client import get_client


def create_summary(places: list, request_params: dict) -> str:
    """Create human-readable summary of place results."""
    lines = [
        f"# Places Search Results",
        f"",
        f"## Search Parameters",
        f"- **Query**: {request_params.get('query', 'N/A')}",
    ]

    if request_params.get('location'):
        lines.append(f"- **Location**: {request_params['location']}")
        lines.append(f"- **Radius**: {request_params.get('radius', 5000)}m")

    if request_params.get('type'):
        lines.append(f"- **Type Filter**: {request_params['type']}")

    lines.extend([
        f"- **Results Found**: {len(places)}",
        f"",
        f"## Top Places",
        f""
    ])

    for i, place in enumerate(places[:10], 1):
        name = place.get("name", "Unknown Place")
        address = place.get("formatted_address", "Address not available")
        rating = place.get("rating")
        user_ratings = place.get("user_ratings_total", 0)
        price_level = place.get("price_level")

        lines.append(f"### {i}. {name}")

        if rating:
            stars = "⭐" * int(rating)
            lines.append(f"- **Rating**: {rating}/5 {stars} ({user_ratings} reviews)")

        lines.append(f"- **Address**: {address}")

        if price_level is not None:
            price_str = "$" * (price_level + 1)
            lines.append(f"- **Price Level**: {price_str}")

        # Opening hours
        opening_hours = place.get("opening_hours", {})
        if opening_hours.get("open_now") is not None:
            status = "Open now" if opening_hours["open_now"] else "Closed"
            lines.append(f"- **Status**: {status}")

        # Types
        types = place.get("types", [])
        if types:
            readable_types = [t.replace("_", " ").title() for t in types[:3]]
            lines.append(f"- **Categories**: {', '.join(readable_types)}")

        # Place ID for reference
        place_id = place.get("place_id", "")
        lines.append(f"- *Place ID: {place_id}*")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    lines.extend([
        f"## Data Location",
        f"- Full results: `places.json`",
        f"- Top places: `top_places.json`",
        f"- Request parameters: `search_request.json`"
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search places via Google Maps API")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--location", help="Center point as lat,lng")
    parser.add_argument("--radius", type=int, default=5000, help="Search radius in meters")
    parser.add_argument("--type", help="Place type filter")
    parser.add_argument("--output", required=True, help="Output directory for results")

    args = parser.parse_args()

    # Build request parameters
    request_params = {
        "query": args.query,
        "location": args.location,
        "radius": args.radius,
        "type": args.type,
        "searched_at": datetime.now().isoformat()
    }

    print(f"Searching places: {args.query}", file=sys.stderr)
    if args.location:
        print(f"Near: {args.location} (radius: {args.radius}m)", file=sys.stderr)

    try:
        client = get_client()

        # Make API request
        response = client.search_places(
            query=args.query,
            location=args.location,
            radius=args.radius,
            type=args.type
        )

        places = response.get("results", [])
        print(f"Found {len(places)} places", file=sys.stderr)

        # Sort by rating (descending)
        places_sorted = sorted(
            places,
            key=lambda x: (x.get("rating") or 0, x.get("user_ratings_total") or 0),
            reverse=True
        )

        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        with open(output_dir / "search_request.json", 'w') as f:
            json.dump(request_params, f, indent=2)

        with open(output_dir / "places.json", 'w') as f:
            json.dump(places_sorted, f, indent=2)

        top_places = places_sorted[:10]
        with open(output_dir / "top_places.json", 'w') as f:
            json.dump(top_places, f, indent=2)

        summary = create_summary(places_sorted, request_params)
        with open(output_dir / "summary.md", 'w') as f:
            f.write(summary)

        print(f"Results saved to {output_dir}", file=sys.stderr)

        # Output summary to stdout
        print(json.dumps({
            "status": "success",
            "places_count": len(places),
            "output_dir": str(output_dir),
            "top_place": places_sorted[0].get("name") if places_sorted else None,
            "top_rating": places_sorted[0].get("rating") if places_sorted else None
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
