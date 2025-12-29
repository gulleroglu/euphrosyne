#!/usr/bin/env python3
"""
Get reviews for places using Google Maps Places API.

Fetches detailed reviews for places by their place IDs.

Usage:
    python3 get_reviews.py --place_ids "id1,id2,id3" --limit 5
    python3 get_reviews.py --place_ids "ChIJfxDFMbwJxkcReUviSODvJb0" --limit 5
"""
import argparse
import json
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from inventory agent root
inventory_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(inventory_root / ".env")


def get_place_reviews(place_id: str, limit: int = 5) -> dict:
    """
    Get reviews for a specific place.

    Args:
        place_id: Google Maps place ID
        limit: Maximum number of reviews to return

    Returns:
        Dictionary with place info and reviews
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY environment variable not set"}

    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "id,displayName,rating,userRatingCount,reviews"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()

        if "error" in data:
            return {"error": data["error"]["message"], "place_id": place_id}

        reviews = data.get("reviews", [])[:limit]

        formatted_reviews = []
        for review in reviews:
            formatted_reviews.append({
                "author": review.get("authorAttribution", {}).get("displayName", "Anonymous"),
                "rating": review.get("rating", 0),
                "text": review.get("text", {}).get("text", ""),
                "time": review.get("relativePublishTimeDescription", ""),
                "language": review.get("text", {}).get("languageCode", "")
            })

        return {
            "place_id": place_id,
            "name": data.get("displayName", {}).get("text", "Unknown"),
            "rating": data.get("rating"),
            "rating_count": data.get("userRatingCount"),
            "reviews": formatted_reviews
        }

    except Exception as e:
        return {"error": str(e), "place_id": place_id}


def main():
    parser = argparse.ArgumentParser(description="Get reviews for places via Google Maps API")
    parser.add_argument("--place_ids", required=True, help="Comma-separated list of place IDs")
    parser.add_argument("--limit", type=int, default=5, help="Maximum reviews per place (default: 5)")
    parser.add_argument("--output", help="Output file path (optional)")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    place_ids = [pid.strip() for pid in args.place_ids.split(",")]

    results = []
    for place_id in place_ids:
        result = get_place_reviews(place_id, args.limit)
        results.append(result)

    if args.format == "json":
        output = json.dumps(results, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Saved reviews to {args.output}", file=sys.stderr)
        else:
            print(output)
    else:
        # Text format for readability
        for result in results:
            print(f"\n{'='*60}")
            if "error" in result:
                print(f"Error for {result.get('place_id', 'unknown')}: {result['error']}")
                continue

            print(f"  {result['name']}")
            print(f"{'='*60}")
            print(f"Rating: {result['rating']} ({result['rating_count']} reviews)\n")

            for i, review in enumerate(result['reviews'], 1):
                stars = '' * review['rating']
                print(f"Review {i}: {stars} ({review['time']})")
                print(f"By: {review['author']}")
                text = review['text']
                if len(text) > 500:
                    text = text[:500] + "..."
                print(f"{text}\n")

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\nSaved JSON to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
