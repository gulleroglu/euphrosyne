---
name: google-maps
description: "Search for places and activities via Google Maps Places API. For inventory agent: builds exhaustive activity masterlist across multiple categories."
---

# Google Maps Skill - Inventory Agent

Search for all activities, restaurants, attractions, and points of interest using Google Maps Places API. This skill is used to build exhaustive activity masterlists.

## Purpose

Build a comprehensive list of ALL activities in a location, across multiple categories. This is for quarterly masterlist building, not for trip planning.

## Environment Variables Required

- `GOOGLE_MAPS_API_KEY`: Google Maps API key (required)

## Available Scripts

### search_places.py

Search for places by category and output flat list format.

```bash
python3 .claude/skills/google-maps/scripts/search_places.py \
  --city "Monaco" \
  --country "Monaco" \
  --category "restaurant" \
  --output "files/content/activities/restaurants.json"
```

**Parameters:**
- `--city` (required): City name
- `--country` (required): Country name
- `--category` (required): Place category (restaurant, museum, tourist_attraction, etc.)
- `--output` (optional): Output file path (default: stdout)
- `--radius` (optional): Search radius in meters (default: 5000)
- `--query` (optional): Additional search query to refine results

**Output Format (Flat List):**
```json
[
  {
    "id": "place_xyz789",
    "source": "google_maps",
    "name": "Café de Paris Monte-Carlo",
    "category": "restaurant",
    "rating": 4.5,
    "rating_count": 2500,
    "address": "Place du Casino, Monaco",
    "latitude": 43.7392,
    "longitude": 7.4277,
    "price_level": 3,
    "types": ["restaurant", "cafe", "food"],
    "occasion_relevance": null
  }
]
```

## Place Categories

Common categories for inventory building:

**Dining:**
- `restaurant` - Restaurants
- `cafe` - Cafes and coffee shops
- `bar` - Bars and pubs

**Attractions:**
- `tourist_attraction` - General attractions
- `museum` - Museums
- `art_gallery` - Art galleries
- `church` - Churches and religious sites

**Leisure:**
- `park` - Parks and gardens
- `spa` - Spas and wellness
- `shopping_mall` - Shopping centers
- `casino` - Casinos

**Occasion-Specific:**
- Use `--query` to search for specific venues (e.g., "Formula 1 viewing", "yacht club")

## Usage in Activities Subagent

```bash
# 1. Search restaurants
python3 .claude/skills/google-maps/scripts/search_places.py \
  --city "Monaco" --country "Monaco" \
  --category "restaurant" \
  --output "files/content/activities/restaurants.json"

# 2. Search cafes
python3 .claude/skills/google-maps/scripts/search_places.py \
  --city "Monaco" --country "Monaco" \
  --category "cafe" \
  --output "files/content/activities/cafes.json"

# 3. Search tourist attractions
python3 .claude/skills/google-maps/scripts/search_places.py \
  --city "Monaco" --country "Monaco" \
  --category "tourist_attraction" \
  --output "files/content/activities/attractions.json"

# 4. Search occasion-specific (e.g., Grand Prix related)
python3 .claude/skills/google-maps/scripts/search_places.py \
  --city "Monaco" --country "Monaco" \
  --category "point_of_interest" \
  --query "Formula 1 racing" \
  --output "files/content/activities/f1_venues.json"
```

## Key Principles

1. **Multiple categories** - Search across all relevant categories
2. **No price filtering** - Include all places regardless of price level
3. **Use occasion description** - Search for occasion-specific venues
4. **Wide radius** - Use 5000-10000m to capture all places
5. **Source tagging** - All results tagged with `"source": "google_maps"`
6. **Flat list format** - Simple array of objects for masterlist

## API Reference

See `references/api.md` for Google Maps Places API documentation.
