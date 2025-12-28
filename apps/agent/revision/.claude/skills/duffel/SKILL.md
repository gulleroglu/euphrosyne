---
name: duffel
description: "Search flights and hotels via Duffel API for revision workflows. Use for: (1) Finding alternative flights that meet revision criteria (cheaper, direct, different times), (2) Comparing existing bookings with new options. Always use existing data as baseline and filter for improvements."
---

# Duffel Travel API - Revision Agent

## Overview

Access flight and hotel search via Duffel API for the **revision workflow**. When revising travel plans:
1. Use existing booking data as **baseline**
2. Search for alternatives that meet revision criteria
3. Filter results to show **improvements** over current selection

## Environment Variables Required

- `DUFFEL_API_KEY`: Duffel API access token (required)
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase service key

## Revision Workflow

### 1. Read Baseline Data

Before searching, read the existing data from revision context:

```python
# From files/process/revision_context.json
existing_transportation = context["existing_plan"]["transportation"]
existing_flight = existing_transportation["selected_flight"]

baseline_price = existing_flight["total_amount"]
baseline_stops = existing_flight["stops"]
baseline_departure = existing_flight["departure_time"]
```

### 2. Apply Revision Constraints

Based on user requests, filter or sort results:

| Request | Search Modification |
|---------|---------------------|
| "cheaper flight" | Filter: price < baseline_price |
| "direct flight" | Filter: stops == 0 |
| "earlier departure" | Filter: departure_time < baseline_departure |
| "later departure" | Filter: departure_time > baseline_departure |
| "different airline" | Filter: carrier != baseline_carrier |

### 3. Output Revised Selection

Write to `files/content/transportation/revised.json`:

```json
{
  "previous_selection": {
    "id": "offer_123",
    "summary": "AA 100, $684, 1 stop"
  },
  "revised_selection": {
    "id": "offer_456",
    "summary": "DL 200, $542, nonstop",
    "improvement": "22% cheaper, direct flight"
  },
  "summary": "Changed from AA $684 with 1 stop to DL $542 nonstop",
  "alternatives_considered": 5
}
```

## Available Scripts

### 1. Search Flights

```bash
python3 .claude/skills/duffel/scripts/search_flights.py \
  --origin JFK \
  --destination CDG \
  --departure-date 2025-03-15 \
  --return-date 2025-03-20 \
  --adults 2 \
  --cabin-class economy \
  --output files/content/transportation/search/
```

**Parameters:**
- `--origin`: Origin airport IATA code
- `--destination`: Destination airport IATA code
- `--departure-date`: Departure date (YYYY-MM-DD)
- `--return-date`: Return date for round-trip (optional)
- `--adults`: Number of adult passengers
- `--cabin-class`: Cabin class preference
- `--output`: Output directory

### 2. Search Hotels

For revision agent, hotels typically come from masterlist. Only use this for fresh search when:
- User requests a hotel NOT in masterlist
- User has specific requirements not in masterlist

```bash
python3 .claude/skills/duffel/scripts/search_hotels.py \
  --location "Monaco" \
  --check-in 2025-05-23 \
  --check-out 2025-05-25 \
  --adults 2 \
  --rooms 1 \
  --output files/content/accommodation/search/
```

## Revision Examples

### Example 1: Cheaper Flight

User request: "I want a cheaper flight"

```python
# 1. Get baseline
baseline = context["existing_plan"]["transportation"]["selected_flight"]
baseline_price = float(baseline["total_amount"])

# 2. Search alternatives
# (run search_flights.py)

# 3. Filter results
cheaper_options = [
    offer for offer in search_results
    if float(offer["total_amount"]) < baseline_price
]

# 4. Sort by price
cheaper_options.sort(key=lambda x: float(x["total_amount"]))

# 5. Write revised selection
revised = {
    "previous_selection": baseline,
    "revised_selection": cheaper_options[0],
    "summary": f"Saved ${baseline_price - float(cheaper_options[0]['total_amount']):.2f}"
}
```

### Example 2: Direct Flight

User request: "I want a direct flight"

```python
# Filter for nonstop flights
direct_options = [
    offer for offer in search_results
    if all(len(slice.get("segments", [])) == 1 for slice in offer.get("slices", []))
]
```

### Example 3: Earlier Departure

User request: "I need an earlier departure"

```python
from datetime import datetime

baseline_departure = datetime.fromisoformat(baseline["departure_time"])

earlier_options = [
    offer for offer in search_results
    if datetime.fromisoformat(offer["slices"][0]["segments"][0]["departing_at"]) < baseline_departure
]
```

## Output Format for Revision

The transportation subagent should write `files/content/transportation/revised.json`:

```json
{
  "revision_type": "transportation",
  "request_addressed": "I want a cheaper flight",
  "previous_selection": {
    "offer_id": "offer_abc123",
    "carrier": "American Airlines",
    "flight_number": "AA 100",
    "departure": "2025-05-23T08:00:00",
    "arrival": "2025-05-23T14:00:00",
    "stops": 1,
    "price": "684.00",
    "currency": "USD"
  },
  "revised_selection": {
    "offer_id": "offer_xyz789",
    "carrier": "Delta",
    "flight_number": "DL 200",
    "departure": "2025-05-23T09:30:00",
    "arrival": "2025-05-23T14:45:00",
    "stops": 0,
    "price": "542.00",
    "currency": "USD"
  },
  "improvement": {
    "price_saved": "142.00",
    "price_saved_percent": "20.8%",
    "stops_reduced": true,
    "notes": "Direct flight, slightly later departure"
  },
  "alternatives_considered": 12,
  "summary": "Changed to Delta DL 200: $142 cheaper (21% savings) and direct flight"
}
```

## Error Handling

- If no better alternatives found, explain why and keep existing selection
- If API fails, report error and recommend manual review
- Always preserve existing data as fallback

## References

See `references/api.md` for detailed Duffel API documentation.
