#!/usr/bin/env python3
"""
Get directions between two points using Google Maps Directions API.

Usage:
    python3 get_directions.py \
        --origin "Charles de Gaulle Airport" \
        --destination "Hotel Le Bristol Paris" \
        --mode transit \
        --departure-time 2025-03-15T14:00:00 \
        --output files/content/routes/cdg_to_hotel/
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from maps_client import get_client


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes} min"


def format_distance(meters: int) -> str:
    """Format distance in meters to human readable string."""
    if meters >= 1000:
        return f"{meters / 1000:.1f} km"
    return f"{meters} m"


def create_summary(routes: list, request_params: dict) -> str:
    """Create human-readable summary of directions."""
    lines = [
        f"# Directions",
        f"",
        f"## Route Details",
        f"- **From**: {request_params['origin']}",
        f"- **To**: {request_params['destination']}",
        f"- **Mode**: {request_params['mode'].title()}",
    ]

    if request_params.get('departure_time'):
        lines.append(f"- **Departure**: {request_params['departure_time']}")

    lines.extend([
        f"- **Routes Found**: {len(routes)}",
        f"",
    ])

    for i, route in enumerate(routes, 1):
        legs = route.get("legs", [])
        if not legs:
            continue

        leg = legs[0]  # For simple routes, there's one leg

        duration = leg.get("duration", {})
        distance = leg.get("distance", {})

        lines.extend([
            f"## Route {i}" if len(routes) > 1 else f"## Recommended Route",
            f"",
            f"- **Total Distance**: {distance.get('text', 'N/A')}",
            f"- **Total Duration**: {duration.get('text', 'N/A')}",
            f""
        ])

        # Traffic duration for driving
        duration_in_traffic = leg.get("duration_in_traffic", {})
        if duration_in_traffic:
            lines.append(f"- **With Traffic**: {duration_in_traffic.get('text', 'N/A')}")
            lines.append(f"")

        # Steps
        steps = leg.get("steps", [])
        if steps:
            lines.append(f"### Step-by-Step Directions")
            lines.append(f"")

            for j, step in enumerate(steps, 1):
                instruction = step.get("html_instructions", "")
                # Remove HTML tags
                import re
                instruction = re.sub('<[^<]+?>', '', instruction)

                step_distance = step.get("distance", {}).get("text", "")
                step_duration = step.get("duration", {}).get("text", "")

                lines.append(f"{j}. {instruction}")
                if step_distance and step_duration:
                    lines.append(f"   *{step_distance} - {step_duration}*")
                lines.append(f"")

                # Transit details
                transit = step.get("transit_details")
                if transit:
                    line = transit.get("line", {})
                    line_name = line.get("name") or line.get("short_name", "")
                    vehicle = line.get("vehicle", {}).get("type", "")
                    departure_stop = transit.get("departure_stop", {}).get("name", "")
                    arrival_stop = transit.get("arrival_stop", {}).get("name", "")
                    num_stops = transit.get("num_stops", 0)

                    if line_name:
                        lines.append(f"   - Take **{line_name}** ({vehicle})")
                    if departure_stop and arrival_stop:
                        lines.append(f"   - From *{departure_stop}* to *{arrival_stop}*")
                    if num_stops:
                        lines.append(f"   - {num_stops} stops")
                    lines.append(f"")

        lines.append(f"---")
        lines.append(f"")

    lines.extend([
        f"## Data Location",
        f"- Full routes: `routes.json`",
        f"- Request parameters: `request.json`"
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Get directions via Google Maps API")
    parser.add_argument("--origin", required=True, help="Starting point")
    parser.add_argument("--destination", required=True, help="End point")
    parser.add_argument("--mode", default="driving",
                        choices=["driving", "walking", "bicycling", "transit"],
                        help="Travel mode")
    parser.add_argument("--departure-time", help="Departure time (ISO format)")
    parser.add_argument("--alternatives", action="store_true", help="Include alternative routes")
    parser.add_argument("--output", required=True, help="Output directory for results")

    args = parser.parse_args()

    # Build request parameters
    request_params = {
        "origin": args.origin,
        "destination": args.destination,
        "mode": args.mode,
        "departure_time": args.departure_time,
        "alternatives": args.alternatives,
        "searched_at": datetime.now().isoformat()
    }

    print(f"Getting directions: {args.origin} → {args.destination}", file=sys.stderr)
    print(f"Mode: {args.mode}", file=sys.stderr)

    try:
        client = get_client()

        # Make API request
        response = client.get_directions(
            origin=args.origin,
            destination=args.destination,
            mode=args.mode,
            departure_time=args.departure_time,
            alternatives=args.alternatives
        )

        routes = response.get("routes", [])
        print(f"Found {len(routes)} route(s)", file=sys.stderr)

        if not routes:
            print("No routes found", file=sys.stderr)

        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        with open(output_dir / "request.json", 'w') as f:
            json.dump(request_params, f, indent=2)

        with open(output_dir / "routes.json", 'w') as f:
            json.dump(routes, f, indent=2)

        summary = create_summary(routes, request_params)
        with open(output_dir / "summary.md", 'w') as f:
            f.write(summary)

        print(f"Results saved to {output_dir}", file=sys.stderr)

        # Output summary to stdout
        main_route = routes[0] if routes else {}
        main_leg = main_route.get("legs", [{}])[0]

        print(json.dumps({
            "status": "success",
            "routes_count": len(routes),
            "output_dir": str(output_dir),
            "distance": main_leg.get("distance", {}).get("text"),
            "duration": main_leg.get("duration", {}).get("text")
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
