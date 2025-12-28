---
name: duffel
description: "Search flights and hotels via Duffel API. Use for: (1) Flight searches with origin/destination airports, dates, and passenger counts, (2) Hotel/stays searches with location, dates, and guest counts, (3) Getting offer details and pricing breakdowns. Returns structured results with pricing and booking links."
---

# Duffel Travel API Integration

## Overview

Access flight and hotel search via Duffel API. This skill provides:
- Flight offer requests (one-way, round-trip, multi-city)
- Stays/accommodation searches
- Offer details and pricing breakdowns

## Environment Variables Required

- `DUFFEL_API_KEY`: Duffel API access token (required)

## Available Scripts

### 1. Search Flights

Search for flight offers between airports.

```bash
python3 .claude/skills/duffel/scripts/search_flights.py \
  --origin JFK \
  --destination CDG \
  --departure-date 2025-03-15 \
  --return-date 2025-03-20 \
  --adults 2 \
  --cabin-class economy \
  --output files/content/flights/search_001/
```

**Parameters:**
- `--origin`: Origin airport IATA code (e.g., JFK, LAX)
- `--destination`: Destination airport IATA code (e.g., CDG, LHR)
- `--departure-date`: Departure date (YYYY-MM-DD)
- `--return-date`: Return date for round-trip (optional)
- `--adults`: Number of adult passengers (default: 1)
- `--children`: Number of child passengers (default: 0)
- `--cabin-class`: Cabin class (economy, premium_economy, business, first)
- `--output`: Output directory for results

**Output:**
```
files/content/flights/search_001/
├── search_request.json    # Original request parameters
├── offers.json            # All returned offers
├── top_offers.json        # Top 5 offers by price
└── summary.md             # Human-readable summary
```

### 2. Search Hotels

Search for hotel/stay accommodations.

```bash
python3 .claude/skills/duffel/scripts/search_hotels.py \
  --location "Paris, France" \
  --check-in 2025-03-15 \
  --check-out 2025-03-20 \
  --adults 2 \
  --rooms 1 \
  --output files/content/hotels/search_001/
```

**Parameters:**
- `--location`: Location name or coordinates
- `--latitude`: Latitude (alternative to location)
- `--longitude`: Longitude (alternative to location)
- `--check-in`: Check-in date (YYYY-MM-DD)
- `--check-out`: Check-out date (YYYY-MM-DD)
- `--adults`: Number of adult guests
- `--rooms`: Number of rooms needed
- `--output`: Output directory for results

**Output:**
```
files/content/hotels/search_001/
├── search_request.json    # Original request parameters
├── properties.json        # All returned properties
├── top_properties.json    # Top 10 by rating/price
└── summary.md             # Human-readable summary
```

## Workflow

1. **Read trip_context.json** to get search parameters
2. **Call appropriate script** with extracted parameters
3. **Write results** to files/content/ directory
4. **Read summary.md** to provide recommendations

## Error Handling

- If API key is missing, script will error with clear message
- If no results found, empty results with message returned
- Rate limits handled with exponential backoff

## References

See `references/api.md` for detailed Duffel API documentation.
