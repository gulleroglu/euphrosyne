---
name: google-maps
description: "Search places, calculate routes, and get directions via Google Maps API. Use for: (1) Activity/POI discovery by location and category, (2) Route planning between points with transit/driving/walking options, (3) Distance and travel time calculations, (4) Place details including hours, reviews, and photos. Essential for activity planning and ground transportation."
---

# Google Maps API Integration

## Overview

Access location-based services via Google Maps Platform:
- Places API (nearby search, text search, place details)
- Directions API (routes with different travel modes)
- Distance Matrix API (travel times between multiple points)

## Environment Variables Required

- `GOOGLE_MAPS_API_KEY`: Google Maps API key (required)

## Available Scripts

### 1. Search Places

Search for points of interest, restaurants, attractions, etc.

```bash
python3 .claude/skills/google-maps/scripts/search_places.py \
  --query "museums in Paris" \
  --location 48.8566,2.3522 \
  --radius 5000 \
  --type museum \
  --output files/content/activities/paris/museums/
```

**Parameters:**
- `--query`: Search query (e.g., "restaurants near Eiffel Tower")
- `--location`: Center point as latitude,longitude
- `--radius`: Search radius in meters (max 50000)
- `--type`: Place type filter (restaurant, museum, tourist_attraction, etc.)
- `--output`: Output directory for results

**Output:**
```
files/content/activities/paris/museums/
├── search_request.json    # Original request parameters
├── places.json            # All returned places
├── top_places.json        # Top 10 by rating
└── summary.md             # Human-readable summary
```

### 2. Get Directions

Calculate route between two points.

```bash
python3 .claude/skills/google-maps/scripts/get_directions.py \
  --origin "Charles de Gaulle Airport" \
  --destination "Hotel Le Bristol Paris" \
  --mode transit \
  --departure-time 2025-03-15T14:00:00 \
  --output files/content/routes/cdg_to_hotel/
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
files/content/routes/cdg_to_hotel/
├── request.json           # Original request
├── routes.json            # All routes with steps
└── summary.md             # Human-readable directions
```

### 3. Distance Matrix

Calculate travel times between multiple origins and destinations.

```bash
python3 .claude/skills/google-maps/scripts/distance_matrix.py \
  --origins "Hotel Le Bristol Paris" \
  --destinations "Louvre Museum,Eiffel Tower,Notre-Dame" \
  --mode walking \
  --output files/content/routes/day_1_distances/
```

**Parameters:**
- `--origins`: One or more origin points (comma-separated)
- `--destinations`: One or more destination points (comma-separated)
- `--mode`: Travel mode
- `--output`: Output directory for results

**Output:**
```
files/content/routes/day_1_distances/
├── request.json           # Original request
├── matrix.json            # Distance/duration matrix
└── summary.md             # Human-readable table
```

## Place Types

Common place types for travel planning:
- `tourist_attraction` - General attractions
- `museum` - Museums and galleries
- `restaurant` - Restaurants
- `cafe` - Cafes and coffee shops
- `bar` - Bars and pubs
- `park` - Parks and gardens
- `church` - Churches and religious sites
- `art_gallery` - Art galleries
- `shopping_mall` - Shopping centers
- `spa` - Spas and wellness
- `gym` - Fitness centers
- `airport` - Airports
- `train_station` - Train stations
- `bus_station` - Bus stations

## Workflow

1. **Read trip_context.json** to get destination and preferences
2. **Call search_places.py** for activity discovery
3. **Call get_directions.py** for transportation routes
4. **Call distance_matrix.py** for itinerary optimization
5. **Read summary.md files** to provide recommendations

## References

See `references/api.md` for detailed Google Maps API documentation.
