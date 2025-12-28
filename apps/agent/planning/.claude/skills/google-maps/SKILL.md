---
name: google-maps
description: "Calculate directions and travel times via Google Maps API for itinerary planning. Use for route planning between locations, travel time calculations, and logistics verification. Essential for the verification subagent when creating day-by-day plans."
---

# Google Maps API Integration - Planning Agent

## Overview

Access location-based services via Google Maps Platform for itinerary planning:
- Directions API (routes with different travel modes)
- Distance Matrix API (travel times between multiple points)

**Note**: In the planning agent, place search is NOT used - activities and accommodations come from occasion masterlists. This skill is primarily for the **verification** subagent to calculate travel logistics.

## Environment Variables Required

- `GOOGLE_MAPS_API_KEY`: Google Maps API key (required)

## Available Scripts

### 1. Get Directions

Calculate route between two points with detailed steps.

```bash
python3 .claude/skills/google-maps/scripts/get_directions.py \
  --origin "Nice Airport, France" \
  --destination "Hotel Hermitage Monte-Carlo" \
  --mode transit \
  --departure-time 2025-05-23T14:00:00 \
  --output files/content/verification/routes/
```

**Parameters:**
- `--origin`: Starting point (address, place name, or lat,lng)
- `--destination`: End point (address, place name, or lat,lng)
- `--mode`: Travel mode (driving, walking, bicycling, transit)
- `--departure-time`: Departure time for transit (ISO format)
- `--alternatives`: Include alternative routes (flag)
- `--output`: Output directory for results

**Output:**
```
files/content/verification/routes/airport_to_hotel/
├── request.json           # Original request
├── routes.json            # All routes with steps
└── summary.md             # Human-readable directions
```

### 2. Distance Matrix

Calculate travel times between multiple origins and destinations - ideal for itinerary optimization.

```bash
python3 .claude/skills/google-maps/scripts/distance_matrix.py \
  --origins "Hotel Hermitage Monte-Carlo" \
  --destinations "Cafe de Paris,Casino Monte-Carlo,Prince's Palace" \
  --mode walking \
  --output files/content/verification/distances/
```

**Parameters:**
- `--origins`: One or more origin points (comma-separated or JSON array)
- `--destinations`: One or more destination points (comma-separated or JSON array)
- `--mode`: Travel mode (driving, walking, transit)
- `--output`: Output directory for results

**Output:**
```
files/content/verification/distances/
├── request.json           # Original request
├── matrix.json            # Distance/duration matrix
└── summary.md             # Human-readable table
```

## Usage in Verification Subagent

The verification subagent uses this skill to:

### 1. Calculate Airport Transfer Time
```bash
python3 .claude/skills/google-maps/scripts/get_directions.py \
  --origin "[DESTINATION_AIRPORT]" \
  --destination "[HOTEL_ADDRESS]" \
  --mode driving \
  --output files/content/verification/routes/airport_transfer/
```

### 2. Verify Activity Logistics
```bash
python3 .claude/skills/google-maps/scripts/distance_matrix.py \
  --origins "[HOTEL_ADDRESS]" \
  --destinations "[ACTIVITY_1_ADDRESS],[ACTIVITY_2_ADDRESS],[ACTIVITY_3_ADDRESS]" \
  --mode walking \
  --output files/content/verification/distances/day_activities/
```

### 3. Check Event Venue Access
```bash
python3 .claude/skills/google-maps/scripts/get_directions.py \
  --origin "[HOTEL_ADDRESS]" \
  --destination "[EVENT_VENUE]" \
  --mode transit \
  --departure-time [EVENT_START_MINUS_1H] \
  --output files/content/verification/routes/to_venue/
```

## Results Schema

### Direction Results
```json
{
  "origin": "Nice Airport, France",
  "destination": "Hotel Hermitage Monte-Carlo",
  "mode": "transit",
  "distance": "25 km",
  "duration": "45 min",
  "steps": [
    {
      "instruction": "Take bus 100 towards Monaco",
      "distance": "20 km",
      "duration": "35 min"
    }
  ],
  "alternatives": [
    {
      "mode": "taxi",
      "duration": "30 min",
      "estimated_cost": "60-80 EUR"
    }
  ]
}
```

### Distance Matrix Results
```json
{
  "origins": ["Hotel Hermitage Monte-Carlo"],
  "destinations": ["Cafe de Paris", "Casino Monte-Carlo", "Prince's Palace"],
  "matrix": [
    {
      "destination": "Cafe de Paris",
      "distance": "0.3 km",
      "duration": "4 min",
      "mode": "walking"
    },
    {
      "destination": "Casino Monte-Carlo",
      "distance": "0.2 km",
      "duration": "3 min",
      "mode": "walking"
    },
    {
      "destination": "Prince's Palace",
      "distance": "1.2 km",
      "duration": "15 min",
      "mode": "walking"
    }
  ]
}
```

## Integration with Day-by-Day Plan

When creating the plan, include travel logistics:

```json
{
  "days": [
    {
      "date": "2025-05-23",
      "schedule": [
        {
          "time": "12:30",
          "activity": "Arrive Nice Airport",
          "type": "travel"
        },
        {
          "time": "13:15",
          "activity": "Transfer to Monaco",
          "type": "travel",
          "duration": "45 min",
          "mode": "taxi",
          "notes": "Pre-book recommended"
        },
        {
          "time": "14:00",
          "activity": "Check-in Hotel Hermitage",
          "type": "accommodation"
        }
      ]
    }
  ]
}
```

## Verification Checklist

Use this skill to verify:

| Check | How |
|-------|-----|
| Airport to hotel time | get_directions with flight arrival time |
| Hotel to venue time | get_directions with event start time |
| Activities reachable | distance_matrix from hotel |
| Schedule feasible | Compare travel times with slot durations |
| Restaurant proximity | distance_matrix for meal locations |

## Error Handling

- If `GOOGLE_MAPS_API_KEY` missing: Script exits with clear error
- If route not found: Returns error with suggestions
- If API rate limited: Implements exponential backoff

## References

See `references/api.md` for detailed Google Maps API documentation.
