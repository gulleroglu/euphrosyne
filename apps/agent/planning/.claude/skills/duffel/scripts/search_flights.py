#!/usr/bin/env python3
"""
Search for flight offers using Duffel API.

Usage:
    python3 search_flights.py \
        --origin JFK \
        --destination CDG \
        --departure-date 2025-03-15 \
        --return-date 2025-03-20 \
        --adults 2 \
        --cabin-class economy \
        --output files/content/flights/search_001/
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from duffel_client import get_client


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human readable string."""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def format_price(amount: str, currency: str) -> str:
    """Format price with currency symbol."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, currency + " ")
    return f"{symbol}{float(amount):,.2f}"


def create_summary(offers: list, request_params: dict) -> str:
    """Create human-readable summary of flight offers."""
    lines = [
        f"# Flight Search Results",
        f"",
        f"## Search Parameters",
        f"- **Origin**: {request_params['origin']}",
        f"- **Destination**: {request_params['destination']}",
        f"- **Departure**: {request_params['departure_date']}",
    ]

    if request_params.get('return_date'):
        lines.append(f"- **Return**: {request_params['return_date']}")

    lines.extend([
        f"- **Passengers**: {request_params['adults']} adult(s)",
        f"- **Cabin Class**: {request_params['cabin_class']}",
        f"- **Results Found**: {len(offers)}",
        f"",
        f"## Top Flight Options",
        f""
    ])

    for i, offer in enumerate(offers[:5], 1):
        total_amount = offer.get("total_amount", "0")
        total_currency = offer.get("total_currency", "USD")
        slices = offer.get("slices", [])

        lines.append(f"### Option {i}: {format_price(total_amount, total_currency)} total")
        lines.append(f"")

        for j, slice_data in enumerate(slices):
            segments = slice_data.get("segments", [])
            if segments:
                first_seg = segments[0]
                last_seg = segments[-1]

                origin = first_seg.get("origin", {}).get("iata_code", "???")
                dest = last_seg.get("destination", {}).get("iata_code", "???")
                dep_time = first_seg.get("departing_at", "")[:16].replace("T", " ")
                arr_time = last_seg.get("arriving_at", "")[:16].replace("T", " ")
                duration = slice_data.get("duration", "")

                carrier = first_seg.get("operating_carrier", {}).get("name", "Unknown")
                flight_num = first_seg.get("operating_carrier_flight_number", "")
                stops = len(segments) - 1

                direction = "Outbound" if j == 0 else "Return"
                stops_text = "nonstop" if stops == 0 else f"{stops} stop(s)"

                lines.extend([
                    f"**{direction}**: {origin} → {dest}",
                    f"- {carrier} {flight_num}",
                    f"- Departs: {dep_time}",
                    f"- Arrives: {arr_time}",
                    f"- Duration: {duration} ({stops_text})",
                    f""
                ])

        # Booking info
        offer_id = offer.get("id", "")
        lines.append(f"*Offer ID: {offer_id}*")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    lines.extend([
        f"## Data Location",
        f"- Full offers: `offers.json`",
        f"- Top offers: `top_offers.json`",
        f"- Request parameters: `search_request.json`"
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search flights via Duffel API")
    parser.add_argument("--origin", required=True, help="Origin airport IATA code")
    parser.add_argument("--destination", required=True, help="Destination airport IATA code")
    parser.add_argument("--departure-date", required=True, help="Departure date (YYYY-MM-DD)")
    parser.add_argument("--return-date", help="Return date for round-trip (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=1, help="Number of adult passengers")
    parser.add_argument("--children", type=int, default=0, help="Number of child passengers")
    parser.add_argument("--cabin-class", default="economy",
                        choices=["economy", "premium_economy", "business", "first"],
                        help="Cabin class preference")
    parser.add_argument("--output", required=True, help="Output directory for results")

    args = parser.parse_args()

    # Build request parameters
    request_params = {
        "origin": args.origin,
        "destination": args.destination,
        "departure_date": args.departure_date,
        "return_date": args.return_date,
        "adults": args.adults,
        "children": args.children,
        "cabin_class": args.cabin_class,
        "searched_at": datetime.now().isoformat()
    }

    print(f"Searching flights: {args.origin} → {args.destination}", file=sys.stderr)
    print(f"Date: {args.departure_date}", file=sys.stderr)
    if args.return_date:
        print(f"Return: {args.return_date}", file=sys.stderr)

    try:
        client = get_client()

        # Build slices
        slices = [
            {
                "origin": args.origin,
                "destination": args.destination,
                "departure_date": args.departure_date
            }
        ]

        if args.return_date:
            slices.append({
                "origin": args.destination,
                "destination": args.origin,
                "departure_date": args.return_date
            })

        # Build passengers
        passengers = []
        for _ in range(args.adults):
            passengers.append({"type": "adult"})
        for _ in range(args.children):
            passengers.append({"type": "child"})

        # Make API request
        response = client.create_offer_request(
            slices=slices,
            passengers=passengers,
            cabin_class=args.cabin_class
        )

        offers = response.get("data", {}).get("offers", [])
        print(f"Found {len(offers)} offers", file=sys.stderr)

        # Sort by price
        offers_sorted = sorted(
            offers,
            key=lambda x: float(x.get("total_amount", "999999"))
        )

        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        with open(output_dir / "search_request.json", 'w') as f:
            json.dump(request_params, f, indent=2)

        with open(output_dir / "offers.json", 'w') as f:
            json.dump(offers_sorted, f, indent=2)

        top_offers = offers_sorted[:5]
        with open(output_dir / "top_offers.json", 'w') as f:
            json.dump(top_offers, f, indent=2)

        summary = create_summary(offers_sorted, request_params)
        with open(output_dir / "summary.md", 'w') as f:
            f.write(summary)

        print(f"Results saved to {output_dir}", file=sys.stderr)

        # Output summary to stdout
        print(json.dumps({
            "status": "success",
            "offers_count": len(offers),
            "output_dir": str(output_dir),
            "top_offer_price": offers_sorted[0].get("total_amount") if offers_sorted else None,
            "currency": offers_sorted[0].get("total_currency") if offers_sorted else None
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
