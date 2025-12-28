---
name: duffel
description: "Search for hotels using the Duffel Stays API. For inventory agent: builds exhaustive hotel masterlist without price/availability filters."
---

# Duffel Skill - Inventory Agent

Search for all hotels in a location using the Duffel Stays API. This skill is used to build exhaustive accommodation masterlists.

## Purpose

Build a comprehensive list of ALL available hotels in a location, regardless of price or availability. This is for quarterly masterlist building, not for booking.

## Environment Variables Required

- `DUFFEL_API_KEY`: Duffel API access token (required)

## Available Scripts

### search_hotels.py

Search for hotels in a location and output flat list format.

```bash
python3 .claude/skills/duffel/scripts/search_hotels.py \
  --city "Monaco" \
  --country "Monaco" \
  --check-in "2025-05-23" \
  --check-out "2025-05-25" \
  --output "files/content/accommodations/duffel_hotels.json"
```

**Parameters:**
- `--city` (required): City name for hotel search
- `--country` (required): Country name
- `--check-in` (optional): Check-in date (YYYY-MM-DD), defaults to 30 days from now
- `--check-out` (optional): Check-out date (YYYY-MM-DD), defaults to 32 days from now
- `--output` (optional): Output file path (default: stdout)
- `--radius` (optional): Search radius in km (default: 10)

**Output Format (Flat List):**
```json
[
  {
    "id": "hot_xxx",
    "source": "duffel",
    "name": "Hotel Hermitage Monte-Carlo",
    "stars": 5,
    "rating": 4.8,
    "rating_count": 1234,
    "address": "Square Beaumarchais, Monaco",
    "latitude": 43.7384,
    "longitude": 7.4246,
    "amenities": ["pool", "spa", "restaurant", "wifi"],
    "price_range": null
  }
]
```

## Usage in Accommodation Subagent

```bash
# 1. Read occasion context to get location and dates
# 2. Search hotels via duffel

python3 .claude/skills/duffel/scripts/search_hotels.py \
  --city "Monaco" \
  --country "Monaco" \
  --check-in "2025-05-23" \
  --check-out "2025-05-25" \
  --radius 15 \
  --output "files/content/accommodations/duffel_hotels.json"
```

## Key Principles

1. **No price filtering** - Include all hotels regardless of price
2. **No availability filtering** - Include all hotels even if not available for dates
3. **Exhaustive search** - Use wide radius to capture all properties
4. **Source tagging** - All results tagged with `"source": "duffel"`
5. **Flat list format** - Simple array of objects for masterlist

## API Reference

See `references/api.md` for Duffel Stays API documentation.
