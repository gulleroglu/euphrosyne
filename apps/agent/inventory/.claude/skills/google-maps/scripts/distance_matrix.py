#!/usr/bin/env python3
"""
Calculate distances between multiple origins and destinations using Google Maps Distance Matrix API.

Usage:
    python3 distance_matrix.py \
        --origins "Hotel Le Bristol Paris" \
        --destinations "Louvre Museum,Eiffel Tower,Notre-Dame" \
        --mode walking \
        --output files/content/routes/day_1_distances/
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from maps_client import get_client


def create_summary(data: dict, request_params: dict) -> str:
    """Create human-readable summary of distance matrix."""
    lines = [
        f"# Distance Matrix Results",
        f"",
        f"## Parameters",
        f"- **Mode**: {request_params['mode'].title()}",
        f"",
        f"### Origins",
    ]

    origins = request_params.get("origins", [])
    for i, origin in enumerate(origins, 1):
        lines.append(f"{i}. {origin}")

    lines.extend([
        f"",
        f"### Destinations",
    ])

    destinations = request_params.get("destinations", [])
    for i, dest in enumerate(destinations, 1):
        lines.append(f"{i}. {dest}")

    lines.extend([
        f"",
        f"## Distance/Duration Matrix",
        f""
    ])

    # Create table header
    origin_addresses = data.get("origin_addresses", origins)
    dest_addresses = data.get("destination_addresses", destinations)
    rows = data.get("rows", [])

    # Simplified labels for table
    def shorten(addr):
        parts = addr.split(",")
        return parts[0][:30]

    # Table header
    header = "| From \\ To |"
    for dest in dest_addresses:
        header += f" {shorten(dest)} |"
    lines.append(header)

    # Separator
    sep = "|" + "---|" * (len(dest_addresses) + 1)
    lines.append(sep)

    # Table rows
    for i, row in enumerate(rows):
        elements = row.get("elements", [])
        origin_name = shorten(origin_addresses[i]) if i < len(origin_addresses) else f"Origin {i+1}"
        row_str = f"| {origin_name} |"

        for element in elements:
            status = element.get("status")
            if status == "OK":
                distance = element.get("distance", {}).get("text", "N/A")
                duration = element.get("duration", {}).get("text", "N/A")
                row_str += f" {distance} / {duration} |"
            else:
                row_str += f" {status} |"

        lines.append(row_str)

    lines.extend([
        f"",
        f"## Detailed Results",
        f""
    ])

    # Detailed breakdown
    for i, row in enumerate(rows):
        origin_name = origin_addresses[i] if i < len(origin_addresses) else f"Origin {i+1}"
        lines.append(f"### From: {origin_name}")
        lines.append(f"")

        elements = row.get("elements", [])
        for j, element in enumerate(elements):
            dest_name = dest_addresses[j] if j < len(dest_addresses) else f"Destination {j+1}"
            status = element.get("status")

            if status == "OK":
                distance = element.get("distance", {})
                duration = element.get("duration", {})

                lines.append(f"**To: {dest_name}**")
                lines.append(f"- Distance: {distance.get('text', 'N/A')} ({distance.get('value', 0)} meters)")
                lines.append(f"- Duration: {duration.get('text', 'N/A')} ({duration.get('value', 0)} seconds)")
                lines.append(f"")
            else:
                lines.append(f"**To: {dest_name}**")
                lines.append(f"- Status: {status}")
                lines.append(f"")

    lines.extend([
        f"---",
        f"",
        f"## Data Location",
        f"- Full matrix: `matrix.json`",
        f"- Request parameters: `request.json`"
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Calculate distance matrix via Google Maps API")
    parser.add_argument("--origins", required=True, help="Origin points (comma-separated)")
    parser.add_argument("--destinations", required=True, help="Destination points (comma-separated)")
    parser.add_argument("--mode", default="driving",
                        choices=["driving", "walking", "bicycling", "transit"],
                        help="Travel mode")
    parser.add_argument("--output", required=True, help="Output directory for results")

    args = parser.parse_args()

    # Parse comma-separated lists
    origins = [o.strip() for o in args.origins.split(",")]
    destinations = [d.strip() for d in args.destinations.split(",")]

    # Build request parameters
    request_params = {
        "origins": origins,
        "destinations": destinations,
        "mode": args.mode,
        "searched_at": datetime.now().isoformat()
    }

    print(f"Calculating distance matrix", file=sys.stderr)
    print(f"Origins: {len(origins)}, Destinations: {len(destinations)}", file=sys.stderr)
    print(f"Mode: {args.mode}", file=sys.stderr)

    try:
        client = get_client()

        # Make API request
        response = client.distance_matrix(
            origins=origins,
            destinations=destinations,
            mode=args.mode
        )

        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        with open(output_dir / "request.json", 'w') as f:
            json.dump(request_params, f, indent=2)

        with open(output_dir / "matrix.json", 'w') as f:
            json.dump(response, f, indent=2)

        summary = create_summary(response, request_params)
        with open(output_dir / "summary.md", 'w') as f:
            f.write(summary)

        print(f"Results saved to {output_dir}", file=sys.stderr)

        # Count successful calculations
        rows = response.get("rows", [])
        ok_count = sum(
            1 for row in rows
            for element in row.get("elements", [])
            if element.get("status") == "OK"
        )
        total = len(origins) * len(destinations)

        print(json.dumps({
            "status": "success",
            "origins_count": len(origins),
            "destinations_count": len(destinations),
            "successful_calculations": ok_count,
            "total_calculations": total,
            "output_dir": str(output_dir)
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
