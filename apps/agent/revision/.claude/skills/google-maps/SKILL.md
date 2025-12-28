---
name: google-maps
description: "Search places and calculate routes for revision workflows. For activities revision, primarily uses occasion masterlists rather than fresh API searches. Use API for: (1) Getting additional details on masterlist items, (2) Searching when masterlist insufficient, (3) Route/distance calculations for revised itinerary."
---

# Google Maps API - Revision Agent

## Overview

For the **revision workflow**, this skill supports:
1. Selecting alternatives from **occasion masterlist** (primary method)
2. Fresh API searches when masterlist is insufficient
3. Route/distance calculations for revised itineraries

## Key Principle: Use Masterlists First

The revision agent should:
1. **Read `occasion.activities`** from revision_context.json (masterlist)
2. **Filter/sort masterlist** based on revision requests
3. Only use API if masterlist doesn't satisfy the request

## Environment Variables Required

- `GOOGLE_MAPS_API_KEY`: Google Maps API key (required)

## Revision Workflow for Activities

### 1. Read Existing and Masterlist Data

```python
# From files/process/revision_context.json
existing_activities = context["existing_plan"]["activities"]
masterlist = context["occasion"]["activities"]  # All available activities
requests = context["requests"]  # User's revision requests
```

### 2. Apply Revision Constraints to Masterlist

| Request | Masterlist Filter |
|---------|-------------------|
| "upscale restaurant" | price_level >= 3, category == "restaurant" |
| "add museum" | category == "museum", NOT in existing |
| "cheaper dining" | price_level < existing_price_level |
| "closer to hotel" | sort by distance to accommodation |
| "remove X" | filter out matching name |

### 3. Output Revised Selection

Write to `files/content/activities/revised.json`:

```json
{
  "revision_type": "activities",
  "requests_addressed": ["I want a more upscale restaurant for Saturday dinner"],
  "previous_selection": [
    {"id": "place_xyz", "name": "Cafe de Paris", "price_level": 2}
  ],
  "revised_selection": [
    {"id": "place_abc", "name": "Le Louis XV", "price_level": 4, "rating": 4.8}
  ],
  "changes": {
    "added": ["Le Louis XV - Michelin 3-star restaurant"],
    "removed": ["Cafe de Paris"],
    "kept": ["Casino de Monte-Carlo visit", "Port Hercule walk"]
  },
  "summary": "Upgraded Saturday dinner from Cafe de Paris to Le Louis XV (Michelin 3-star)"
}
```

## Available Scripts

### 1. Search Places (Use Sparingly)

Only use when masterlist doesn't satisfy the request:

```bash
python3 .claude/skills/google-maps/scripts/search_places.py \
  --query "fine dining Monaco" \
  --location 43.7384,7.4246 \
  --radius 5000 \
  --type restaurant \
  --output files/content/activities/search/
```

### 2. Get Directions

Use for updated route planning after revisions:

```bash
python3 .claude/skills/google-maps/scripts/get_directions.py \
  --origin "Hotel Ambassador Monaco" \
  --destination "Le Louis XV Restaurant" \
  --mode walking \
  --output files/content/routes/dinner_route/
```

### 3. Distance Matrix

Use to validate revised activity schedule:

```bash
python3 .claude/skills/google-maps/scripts/distance_matrix.py \
  --origins "Hotel Ambassador Monaco" \
  --destinations "Le Louis XV,Casino de Monte-Carlo,Port Hercule" \
  --mode walking \
  --output files/content/routes/day_distances/
```

## Revision Examples

### Example 1: Upscale Restaurant

User request: "I want a more upscale restaurant for dinner"

```python
# 1. Get existing and masterlist
existing = context["existing_plan"]["activities"]
masterlist = context["occasion"]["activities"]

# Find current dinner selection
current_dinner = next(a for a in existing if a.get("meal_slot") == "dinner")
current_price_level = current_dinner.get("price_level", 2)

# 2. Filter masterlist for upgrades
upscale_options = [
    a for a in masterlist
    if a.get("category") == "restaurant"
    and a.get("price_level", 0) > current_price_level
]

# 3. Sort by rating
upscale_options.sort(key=lambda x: x.get("rating", 0), reverse=True)

# 4. Select best option
revised_dinner = upscale_options[0]
```

### Example 2: Add Museum

User request: "Add some museum tours"

```python
# Get existing activity IDs
existing_ids = {a["id"] for a in existing}

# Filter masterlist for museums not already selected
available_museums = [
    a for a in masterlist
    if a.get("category") == "museum"
    and a["id"] not in existing_ids
]

# Add top-rated museums
new_activities = existing + available_museums[:2]
```

### Example 3: Remove Activity

User request: "Remove the casino visit"

```python
revised_activities = [
    a for a in existing
    if "casino" not in a.get("name", "").lower()
]
```

## Output Format

The activities subagent should write `files/content/activities/revised.json`:

```json
{
  "revision_type": "activities",
  "requests_addressed": [
    "I want a more upscale restaurant for Saturday dinner",
    "Add a museum tour"
  ],
  "previous_selection": {
    "total": 6,
    "items": [
      {"id": "place_1", "name": "Cafe de Paris", "category": "restaurant"},
      {"id": "place_2", "name": "Casino visit", "category": "entertainment"},
      {"id": "place_3", "name": "Port Hercule walk", "category": "attraction"}
    ]
  },
  "revised_selection": {
    "total": 7,
    "items": [
      {"id": "place_4", "name": "Le Louis XV", "category": "restaurant", "revision_note": "Upgraded per upscale dining request"},
      {"id": "place_2", "name": "Casino visit", "category": "entertainment"},
      {"id": "place_3", "name": "Port Hercule walk", "category": "attraction"},
      {"id": "place_5", "name": "Oceanographic Museum", "category": "museum", "revision_note": "Added per museum request"}
    ]
  },
  "changes": {
    "added": [
      {"name": "Le Louis XV", "reason": "Upgraded dining - Michelin 3-star"},
      {"name": "Oceanographic Museum", "reason": "Added museum per request"}
    ],
    "removed": [
      {"name": "Cafe de Paris", "reason": "Replaced with upscale option"}
    ],
    "kept": 4
  },
  "masterlist_used": true,
  "api_calls_made": 0,
  "summary": "Upgraded dinner to Le Louis XV and added Oceanographic Museum tour"
}
```

## When to Use API vs Masterlist

| Scenario | Use |
|----------|-----|
| User wants upscale restaurant | Masterlist |
| User wants specific restaurant by name | Masterlist, then API if not found |
| User wants category (museums, cafes) | Masterlist |
| User wants something NOT in masterlist | API |
| User specifies exact place name/address | API for details |
| Need route between places | API (Directions) |
| Need travel times | API (Distance Matrix) |

## References

See `references/api.md` for detailed Google Maps API documentation.
