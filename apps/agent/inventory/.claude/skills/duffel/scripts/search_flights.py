#!/usr/bin/env python3
"""
Search for flights using Duffel API.

Usage:
    python3 search_flights.py \
        --origin "AMS" \
        --destination "BCN" \
        --departure-date "2026-01-15" \
        --passengers 1 \
        --cabin-class "economy"
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


def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = None,
    passengers: int = 1,
    cabin_class: str = "economy",
    max_connections: int = None
) -> dict:
    """
    Search for flights using Duffel API.

    Args:
        origin: IATA airport/city code (e.g., "AMS")
        destination: IATA airport/city code (e.g., "BCN")
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Optional return date for round trip
        passengers: Number of adult passengers
        cabin_class: economy, premium_economy, business, first
        max_connections: Maximum number of stops (0 for direct only)

    Returns:
        Dictionary with flight offers
    """
    api_key = os.environ.get("DUFFEL_API_KEY")
    if not api_key:
        return {"error": "DUFFEL_API_KEY environment variable not set"}

    url = "https://api.duffel.com/air/offer_requests"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Duffel-Version": "v2",
        "Content-Type": "application/json"
    }

    # Build slices
    slices = [{
        "origin": origin.upper(),
        "destination": destination.upper(),
        "departure_date": departure_date
    }]

    if return_date:
        slices.append({
            "origin": destination.upper(),
            "destination": origin.upper(),
            "departure_date": return_date
        })

    # Build passengers list
    passenger_list = [{"type": "adult"} for _ in range(passengers)]

    payload = {
        "data": {
            "slices": slices,
            "passengers": passenger_list,
            "cabin_class": cabin_class
        }
    }

    if max_connections is not None:
        payload["data"]["max_connections"] = max_connections

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        data = response.json()

        if "errors" in data:
            return {"error": data["errors"]}

        return data

    except Exception as e:
        return {"error": str(e)}


def format_duration(iso_duration: str) -> str:
    """Convert ISO duration to readable format."""
    # PT2H30M -> 2h 30m
    duration = iso_duration.replace("PT", "").replace("H", "h ").replace("M", "m")
    return duration.strip()


def format_offer(offer: dict, index: int) -> dict:
    """Format an offer for display."""
    slices = offer.get("slices", [])

    formatted = {
        "index": index,
        "id": offer.get("id"),
        "total_amount": offer.get("total_amount"),
        "total_currency": offer.get("total_currency"),
        "owner": offer.get("owner", {}).get("name"),
        "owner_iata": offer.get("owner", {}).get("iata_code"),
        "slices": []
    }

    for slice_data in slices:
        segments = slice_data.get("segments", [])
        slice_info = {
            "origin": slice_data.get("origin", {}).get("iata_code"),
            "origin_name": slice_data.get("origin", {}).get("name"),
            "destination": slice_data.get("destination", {}).get("iata_code"),
            "destination_name": slice_data.get("destination", {}).get("name"),
            "duration": format_duration(slice_data.get("duration", "")),
            "segments": []
        }

        for seg in segments:
            seg_info = {
                "flight_number": f"{seg.get('marketing_carrier', {}).get('iata_code', '')}{seg.get('marketing_carrier_flight_number', '')}",
                "operating_carrier": seg.get("operating_carrier", {}).get("name"),
                "aircraft": (seg.get("aircraft") or {}).get("name"),
                "origin": seg.get("origin", {}).get("iata_code"),
                "destination": seg.get("destination", {}).get("iata_code"),
                "departing_at": seg.get("departing_at"),
                "arriving_at": seg.get("arriving_at"),
                "duration": format_duration(seg.get("duration", ""))
            }
            slice_info["segments"].append(seg_info)

        formatted["slices"].append(slice_info)

    return formatted


def main():
    parser = argparse.ArgumentParser(description="Search flights via Duffel API")
    parser.add_argument("--origin", required=True, help="Origin IATA code (e.g., AMS)")
    parser.add_argument("--destination", required=True, help="Destination IATA code (e.g., BCN)")
    parser.add_argument("--departure-date", required=True, help="Departure date (YYYY-MM-DD)")
    parser.add_argument("--return-date", help="Return date for round trip (YYYY-MM-DD)")
    parser.add_argument("--passengers", type=int, default=1, help="Number of adult passengers")
    parser.add_argument("--cabin-class", default="economy",
                        choices=["economy", "premium_economy", "business", "first"])
    parser.add_argument("--max-connections", type=int, help="Max stops (0 for direct only)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--limit", type=int, default=10, help="Max offers to display")
    parser.add_argument("--format", choices=["json", "text"], default="text")

    args = parser.parse_args()

    print(f"Searching flights: {args.origin} → {args.destination} on {args.departure_date}", file=sys.stderr)

    result = search_flights(
        origin=args.origin,
        destination=args.destination,
        departure_date=args.departure_date,
        return_date=args.return_date,
        passengers=args.passengers,
        cabin_class=args.cabin_class,
        max_connections=args.max_connections
    )

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    offers = result.get("data", {}).get("offers", [])
    print(f"Found {len(offers)} offers", file=sys.stderr)

    # Sort by price
    offers_sorted = sorted(offers, key=lambda x: float(x.get("total_amount", "999999")))

    # Format offers
    formatted_offers = []
    for i, offer in enumerate(offers_sorted[:args.limit], 1):
        formatted_offers.append(format_offer(offer, i))

    output_data = {
        "search": {
            "origin": args.origin.upper(),
            "destination": args.destination.upper(),
            "departure_date": args.departure_date,
            "return_date": args.return_date,
            "passengers": args.passengers,
            "cabin_class": args.cabin_class,
            "search_date": datetime.now().isoformat()
        },
        "total_offers": len(offers),
        "offers": formatted_offers
    }

    if args.format == "json":
        output = json.dumps(output_data, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Saved to {args.output}", file=sys.stderr)
        else:
            print(output)
    else:
        # Text format
        print(f"\n{'='*70}")
        print(f"  Flights: {args.origin.upper()} → {args.destination.upper()}")
        print(f"  Date: {args.departure_date} | Passengers: {args.passengers} | Class: {args.cabin_class}")
        print(f"  Found: {len(offers)} offers (showing top {min(args.limit, len(offers))})")
        print(f"{'='*70}\n")

        for offer in formatted_offers:
            slice_info = offer["slices"][0] if offer["slices"] else {}
            segments = slice_info.get("segments", [])

            stops = len(segments) - 1
            stops_text = "Direct" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"

            print(f"#{offer['index']} | {offer['owner']} ({offer['owner_iata']}) | €{offer['total_amount']} {offer['total_currency']}")
            print(f"   Duration: {slice_info.get('duration', 'N/A')} | {stops_text}")

            for seg in segments:
                print(f"   ✈ {seg['flight_number']}: {seg['origin']} {seg['departing_at'][11:16]} → {seg['destination']} {seg['arriving_at'][11:16]} ({seg['duration']})")

            print()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"Saved JSON to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
