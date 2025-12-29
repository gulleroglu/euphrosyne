---
name: google-maps
description: "Search for places and activities via Google Maps Places API (New). For inventory agent: builds exhaustive activity masterlist across multiple categories."
---

# Google Maps Skill

Search for places, activities, restaurants, and points of interest using the Google Maps Places API (New).

## Quick Reference Guide

**What do you need to do?** Find the right reference:

| Task | Reference File |
|------|---------------|
| Search places by text query (e.g., "pizza in NYC") | [text-search.md](references/text-search.md) |
| Search places near a location by type | [nearby-search.md](references/nearby-search.md) |
| Get detailed info for a known place | [place-details.md](references/place-details.md) |
| Get photos for a place | [place-photos.md](references/place-photos.md) |
| Autocomplete as user types | [place-autocomplete.md](references/place-autocomplete.md) |
| Understand place types (restaurant, cafe, etc.) | [place-types.md](references/place-types.md) |
| Choose which fields to request | [choose-fields.md](references/choose-fields.md) |
| Understand all available data fields | [data-fields.md](references/data-fields.md) |
| Work with Place IDs | [place-id.md](references/place-id.md) |
| General API overview | [overview.md](references/overview.md) |
| API capabilities summary | [op-overview.md](references/op-overview.md) |

---

## API Endpoints Summary

### Text Search (POST)
```
https://places.googleapis.com/v1/places:searchText
```
Use for: Free-form text queries like "best coffee shops in Seattle" or "museums near Central Park"

### Nearby Search (POST)
```
https://places.googleapis.com/v1/places:searchNearby
```
Use for: Find places of specific types within a radius of coordinates

### Place Details (GET)
```
https://places.googleapis.com/v1/places/{PLACE_ID}
```
Use for: Get comprehensive info about a specific place using its ID

### Place Photos (GET)
```
https://places.googleapis.com/v1/{PHOTO_NAME}/media
```
Use for: Retrieve photos returned from search or details requests

### Autocomplete (POST)
```
https://places.googleapis.com/v1/places:autocomplete
```
Use for: Real-time suggestions as users type

---

## Authentication

All requests require:
```
X-Goog-Api-Key: YOUR_API_KEY
```

## Field Masks (Required)

You MUST specify which fields to return. No default fields are returned.

**Header format:**
```
X-Goog-FieldMask: places.displayName,places.formattedAddress,places.rating
```

**Common field masks:**

| Use Case | Fields |
|----------|--------|
| Basic listing | `places.id,places.displayName,places.formattedAddress` |
| With ratings | `places.id,places.displayName,places.rating,places.userRatingCount` |
| Full details | `places.id,places.displayName,places.formattedAddress,places.rating,places.priceLevel,places.types,places.photos` |
| For directions | `places.id,places.displayName,places.location` |

See [choose-fields.md](references/choose-fields.md) and [data-fields.md](references/data-fields.md) for complete field lists.

---

## Common Place Types

See [place-types.md](references/place-types.md) for the complete list.

**Food & Drink:** `restaurant`, `cafe`, `bar`, `bakery`, `coffee_shop`, `fast_food_restaurant`, `fine_dining_restaurant`

**Lodging:** `hotel`, `lodging`, `resort_hotel`, `bed_and_breakfast`, `hostel`, `motel`

**Attractions:** `tourist_attraction`, `museum`, `art_gallery`, `amusement_park`, `zoo`, `aquarium`

**Entertainment:** `night_club`, `casino`, `movie_theater`, `spa`, `bowling_alley`

**Outdoors:** `park`, `beach`, `hiking_area`, `national_park`, `garden`

---

## Environment Variables Required

- `GOOGLE_MAPS_API_KEY`: Google Maps API key (required)

---

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
- `--category` (required): Place type (see place-types.md)
- `--output` (optional): Output file path (default: stdout)
- `--radius` (optional): Search radius in meters (default: 5000)
- `--query` (optional): Additional search query to refine results

**Output Format:**
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

---

## Example: Building an Activity Masterlist

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

---

## Pricing Tiers (SKUs)

Fields are billed by tier. See [data-fields.md](references/data-fields.md) for complete mapping.

| Tier | Example Fields |
|------|----------------|
| **Essentials** | `id`, `name`, `location`, `formattedAddress`, `types` |
| **Pro** | `displayName`, `businessStatus`, `primaryType`, `photos` |
| **Enterprise** | `rating`, `priceLevel`, `websiteUri`, `regularOpeningHours` |
| **Enterprise + Atmosphere** | `reviews`, `delivery`, `dineIn`, `reservable`, `outdoorSeating` |

---

## Key Principles

1. **Always specify field masks** - No defaults, requests fail without them
2. **Use appropriate search type** - Text Search for queries, Nearby Search for radius
3. **Mind the pricing tiers** - Only request fields you need
4. **Store Place IDs** - They're cacheable and cheaper for subsequent lookups
5. **Source tagging** - Tag results with `"source": "google_maps"` for tracking
