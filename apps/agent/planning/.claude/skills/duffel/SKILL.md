---
name: duffel
description: "Search LIVE flights via Duffel API with pricing and availability. Use for real-time flight search with cabin class selection, fare options, and seat availability. Returns structured flight offers for the transportation subagent."
---

# Duffel API Integration - Planning Agent

## Overview

Access LIVE flight search via Duffel API. This skill provides:
- Real-time flight offer requests (one-way, round-trip)
- Pricing with fare breakdowns
- Cabin class options (economy, premium_economy, business, first)
- Seat selection when available

**Key**: This is a LIVE search - results reflect current availability and pricing.

## Environment Variables Required

- `DUFFEL_API_KEY`: Duffel API access token (required)

## Available Scripts

### Search Flights

Search for flight offers between airports with LIVE pricing.

```bash
python3 .claude/skills/duffel/scripts/search_flights.py \
  --origin JFK \
  --destination NCE \
  --departure-date 2025-05-22 \
  --return-date 2025-05-26 \
  --adults 2 \
  --cabin-class business \
  --output files/content/transportation/
```

**Parameters:**
- `--origin`: Origin airport IATA code (e.g., JFK, LAX, LHR)
- `--destination`: Destination airport IATA code (e.g., NCE, CDG, FCO)
- `--departure-date`: Departure date (YYYY-MM-DD)
- `--return-date`: Return date for round-trip (optional for one-way)
- `--adults`: Number of adult passengers (default: 1)
- `--children`: Number of child passengers (default: 0)
- `--infants`: Number of infant passengers (default: 0)
- `--cabin-class`: Preferred cabin class (economy, premium_economy, business, first)
- `--max-results`: Maximum offers to return (default: 10)
- `--output`: Output directory for results

**Output Files:**
```
files/content/transportation/
├── search_request.json    # Original search parameters
├── offers.json            # All returned offers (raw)
├── results.json           # Structured results for Supabase
└── summary.md             # Human-readable summary
```

## Results Schema

The `results.json` file contains structured data for `user_plans.transportation`:

```json
{
  "outbound": {
    "flight_id": "offer_abc123",
    "airline": "Emirates",
    "flight_number": "EK073",
    "origin": "JFK",
    "destination": "NCE",
    "departure": "2025-05-22T22:00:00",
    "arrival": "2025-05-23T12:30:00",
    "duration": "8h 30m",
    "cabin_class": "business",
    "stops": 0,
    "price": {
      "amount": "2450.00",
      "currency": "USD"
    },
    "seats_available": 4
  },
  "return": {
    "flight_id": "offer_def456",
    "airline": "Emirates",
    "flight_number": "EK074",
    "origin": "NCE",
    "destination": "JFK",
    "departure": "2025-05-26T14:00:00",
    "arrival": "2025-05-26T18:30:00",
    "duration": "9h 30m",
    "cabin_class": "business",
    "stops": 0,
    "price": {
      "amount": "2450.00",
      "currency": "USD"
    }
  },
  "total_price": {
    "amount": "4900.00",
    "currency": "USD"
  },
  "passengers": {
    "adults": 2,
    "children": 0,
    "infants": 0
  },
  "alternatives": [
    {
      "airline": "Air France",
      "total_price": "3200.00",
      "cabin_class": "business",
      "stops": 1
    }
  ]
}
```

## Workflow for Transportation Subagent

1. **Read context files**:
   - `files/process/user_context.json` - Get user preferences
   - `files/process/occasion_context.json` - Get destination and dates

2. **Extract search parameters**:
   - Origin: From user preferences (home airport) or prompt
   - Destination: From occasion city (find nearest airport)
   - Dates: From occasion start_date/end_date (with buffer)
   - Cabin class: From user preferences
   - Passengers: From user preferences or default to 1 adult

3. **Run flight search**:
   ```bash
   python3 .claude/skills/duffel/scripts/search_flights.py \
     --origin [USER_AIRPORT] \
     --destination [OCCASION_AIRPORT] \
     --departure-date [DAY_BEFORE_START] \
     --return-date [DAY_AFTER_END] \
     --adults [COUNT] \
     --cabin-class [PREFERENCE] \
     --output files/content/transportation/
   ```

4. **Review results** and select best option based on preferences

5. **Write final selection** to `files/content/transportation/results.json`

## User Preferences Parsing

The user's `preferences` field is markdown text. Look for:

```markdown
### Flights
- Prefer business class for long haul
- Window seat
- Morning departures
- Home airport: JFK
```

Extract:
- `cabin_class`: "business" | "economy" | "first" | "premium_economy"
- `seat_preference`: "window" | "aisle"
- `departure_time`: "morning" | "afternoon" | "evening"
- `home_airport`: IATA code

## Airport Code Lookup

Common mappings for occasion cities:
- Monaco/Monte Carlo → NCE (Nice)
- Paris → CDG or ORY
- London → LHR or LGW
- Rome → FCO
- Milan → MXP
- Barcelona → BCN

## Error Handling

- If `DUFFEL_API_KEY` missing: Script exits with clear error
- If no flights found: Returns empty results with message
- If API rate limited: Implements exponential backoff

## References

See `references/api.md` for detailed Duffel API documentation.
