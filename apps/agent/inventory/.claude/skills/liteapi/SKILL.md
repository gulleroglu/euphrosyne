# LiteAPI Skill

Hotel search, rates, and booking API for building travel applications.

## Quick Reference Guide

**What do you need to do?** Find the right reference:

| Task | Reference File |
|------|---------------|
| Search hotels by location | [retrieve-a-list-of-hotels.md](references/retrieve-a-list-of-hotels.md) |
| Get hotel details | [get-the-details-of-a-hotel.md](references/get-the-details-of-a-hotel.md) |
| Get hotel reviews | [get-the-reviews-of-a-hotel.md](references/get-the-reviews-of-a-hotel.md) |
| Search with real-time rates | [retrieve-hotel-rates.md](references/retrieve-hotel-rates.md) |
| Get minimum prices only | [retrieve-minimum-rates-for-hotels.md](references/retrieve-minimum-rates-for-hotels.md) |
| AI-powered semantic search | [search-hotels-by-semantic-query.md](references/search-hotels-by-semantic-query.md) |
| Authentication setup | [authentication.md](references/authentication.md) |
| All endpoints overview | [endpoints-overview.md](references/endpoints-overview.md) |
| Getting started guide | [getting-started.md](references/getting-started.md) |

---

## API Endpoints Summary

### Base URLs

```
Data API:    https://api.liteapi.travel/v3.0
Booking API: https://book.liteapi.travel/v3.0
```

### Hotel Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/data/hotels` | Search hotels by location/filters |
| GET | `/data/hotel` | Get detailed hotel information |
| GET | `/data/reviews` | Get hotel reviews |
| GET | `/data/hotels/semantic-search` | AI-powered natural language search |

### Rate Search Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hotels/rates` | Get real-time rates with availability |
| POST | `/hotels/min-rates` | Get minimum rates for price comparison |

### Booking Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rates/prebook` | Create checkout session |
| POST | `/rates/book` | Complete booking |
| GET | `/bookings` | List all bookings |
| GET | `/bookings/{id}` | Get booking details |
| PUT | `/bookings/{id}` | Cancel booking |

---

## Authentication

All requests require the `X-API-Key` header:

```
X-API-Key: YOUR_API_KEY
```

**Sandbox API Key (for testing):**
```
sand_c0155ab8-c683-4f26-8f94-b5e92c5797b9
```

---

## Environment Variables

```bash
LITEAPI_API_KEY=your_api_key_here
```

---

## Common Workflows

### 1. Search Hotels by City

```python
import requests
import os

api_key = os.environ.get('LITEAPI_API_KEY')

response = requests.get(
    "https://api.liteapi.travel/v3.0/data/hotels",
    params={
        "countryCode": "ES",
        "cityName": "Barcelona",
        "limit": 20
    },
    headers={"X-API-Key": api_key}
)
hotels = response.json()["data"]
```

### 2. Get Hotel Rates with Availability

```python
response = requests.post(
    "https://api.liteapi.travel/v3.0/hotels/rates",
    json={
        "checkin": "2026-01-15",
        "checkout": "2026-01-20",
        "currency": "EUR",
        "guestNationality": "US",
        "occupancies": [{"adults": 2, "children": []}],
        "countryCode": "ES",
        "cityName": "Barcelona",
        "limit": 10,
        "includeHotelData": True
    },
    headers={
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
)
rates = response.json()["data"]
```

### 3. Complete Booking Flow

```
1. Search Hotels     →  GET  /data/hotels
2. Get Rates         →  POST /hotels/rates
3. Create Prebook    →  POST /rates/prebook (with offerId)
4. Complete Booking  →  POST /rates/book (with prebookId + guest details)
```

---

## Search Options

### By City/Country
```python
params = {
    "countryCode": "ES",
    "cityName": "Barcelona"
}
```

### By Coordinates
```python
params = {
    "latitude": 41.3874,
    "longitude": 2.1686,
    "radius": 5000  # meters (min 1000)
}
```

### By AI Search (Natural Language)
```python
params = {
    "aiSearch": "romantic boutique hotel near the beach in Barcelona"
}
```

### By Hotel IDs
```python
params = {
    "hotelIds": "lp1897,lp42fec,lp50f7f"
}
```

---

## Filtering Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `minRating` | float | Minimum guest rating (e.g., 8.0) |
| `minReviewsCount` | integer | Minimum number of reviews |
| `starRating` | string | Star ratings (e.g., "4.0,4.5,5.0") |
| `facilityIds` | string | Facility IDs to filter by |
| `hotelTypeIds` | string | Hotel type IDs |
| `chainIds` | string | Hotel chain IDs |

---

## Board Types (Meal Plans)

| Code | Description |
|------|-------------|
| `RO` | Room Only |
| `BB` | Bed & Breakfast |
| `HB` | Half Board (breakfast + dinner) |
| `FB` | Full Board (all meals) |
| `AI` | All Inclusive |

---

## Available Scripts

### search_hotels.py

Search hotels and output flat list for inventory building.

```bash
python3 .claude/skills/liteapi/scripts/search_hotels.py \
  --city "Barcelona" \
  --country "ES" \
  --check-in "2026-01-15" \
  --check-out "2026-01-20" \
  --output "files/content/accommodations/liteapi_hotels.json"
```

### get_reviews.py

Fetch hotel reviews from LiteAPI for LLM analysis. Output is displayed directly, not saved to files.

```bash
python3 .claude/skills/liteapi/scripts/get_reviews.py \
  --hotel-id "lp55143" \
  --limit 30
```

**Workflow:** Script fetches raw JSON → LLM analyzes → returns formatted summary to user.

### get_rates.py

Get real-time hotel rates and availability.

```bash
# By hotel ID(s)
python3 .claude/skills/liteapi/scripts/get_rates.py \
  --hotel-ids "lp55143,lp368af" \
  --check-in 2026-01-15 \
  --check-out 2026-01-20

# By city
python3 .claude/skills/liteapi/scripts/get_rates.py \
  --city "Barcelona" --country "ES" \
  --check-in 2026-01-15 --check-out 2026-01-20 \
  --limit 5

# By coordinates (radius in meters)
python3 .claude/skills/liteapi/scripts/get_rates.py \
  --lat 52.209 --lon 5.023 --radius 10000 \
  --check-in 2026-01-15 --check-out 2026-01-20
```

**Options:** `--adults` (default: 2), `--currency` (default: EUR), `--nationality` (default: US), `--limit` (default: 10)

**Workflow:** Script fetches rates JSON → LLM formats into readable table with room types, prices, taxes, cancellation policy.

#### Review Summary Template

After fetching reviews, generate a summary using this format:

```markdown
## {Hotel Name} Reviews

**Overall: {avg_score}/10** ({total} reviews)

### Recent Highlights

| Score | Guest | Type | Headline |
|-------|-------|------|----------|
| {score} | {name} ({country}) | {type} | "{headline}" |
...(top 5-7 reviews with score >= 9 and meaningful headlines)

### What Guests Love ✓

- **{Theme}** - "{representative quote from pros}"
- **{Theme}** - "{representative quote}"
...(3-5 themes extracted from pros/headlines: building, breakfast, staff, rooms, restaurant, location, atmosphere, etc.)

### What to Know ⚠️

- **{Concern}** - "{quote from cons}"
- **{Concern}** - "{quote}"
...(3-5 concerns extracted from cons: price, noise, remote location, dated decor, extra charges, etc.)

### Guest Types

Mostly **{top traveler types}** from {top countries}.
```

**Analysis guidance:**
- Extract themes by reading pros text and headlines, find recurring praise
- Pick quotes that are specific and vivid, not generic
- For concerns, focus on actionable info (price levels, location trade-offs)
- Note if any reviews scored ≤4 (red flags)
- Map country codes to names (gb→UK, de→Germany, fr→France, etc.)
- Map traveler types (couple→Couples, family_with_children→Family, etc.)

---

## Example: Building an Accommodation Masterlist

```bash
# 1. Search hotels in Barcelona
python3 .claude/skills/liteapi/scripts/search_hotels.py \
  --city "Barcelona" \
  --country "ES" \
  --check-in "2026-01-15" \
  --check-out "2026-01-20" \
  --min-rating 8.0 \
  --output "files/content/accommodations/barcelona_hotels.json"

# 2. Search with AI query for specific vibe
python3 .claude/skills/liteapi/scripts/search_hotels.py \
  --ai-search "luxury beachfront resort in Barcelona" \
  --check-in "2026-01-15" \
  --check-out "2026-01-20" \
  --output "files/content/accommodations/barcelona_luxury.json"
```

---

## Decision Tree

```
User Request
│
├── "Search/find hotels" ───────────► references/retrieve-a-list-of-hotels.md
├── "Hotels with prices/rates" ─────► references/retrieve-hotel-rates.md
├── "Cheapest hotel prices" ────────► references/retrieve-minimum-rates-for-hotels.md
├── "Hotel details" ────────────────► references/get-the-details-of-a-hotel.md
├── "Hotel reviews" ────────────────► references/get-the-reviews-of-a-hotel.md
├── "Natural language search" ──────► references/search-hotels-by-semantic-query.md
│
├── "Book a hotel" ─────────────────► references/endpoints-overview.md (Booking API)
│
├── "How does LiteAPI work?" ───────► references/getting-started.md
└── "Authentication/API key" ───────► references/authentication.md
```

---

## Complete Hotel Search Flow

```
1. retrieve-a-list-of-hotels.md  → Search hotels by location
2. retrieve-hotel-rates.md       → Get real-time rates
3. get-the-details-of-a-hotel.md → Get full hotel info (optional)
4. get-the-reviews-of-a-hotel.md → Get guest reviews (optional)
```

## Complete Booking Flow

```
1. Search hotels    → GET  /data/hotels
2. Get rates        → POST /hotels/rates
3. Prebook          → POST /rates/prebook (locks price)
4. Book             → POST /rates/book (confirms reservation)
```

---

## Key Concepts

### Hotel IDs
- Format: `lp` prefix + alphanumeric (e.g., `lp1897`, `lp42fec`)
- Use for subsequent API calls (rates, details, reviews)

### Offer IDs
- Returned from rate search
- Required for prebook/booking flow
- Time-limited validity

### Occupancies
- Specify guest configuration per room
- Format: `{"adults": 2, "children": [5, 8]}`
- Children ages in array

### Rate Types
- `RFN` = Refundable
- `NRFN` = Non-Refundable

---

## Rate Limits & Best Practices

1. **Timeout**: Set 6-12 seconds for rate searches
2. **Limit**: Default 200 hotels, max 5000
3. **Caching**: Hotel data can be cached; rates are real-time
4. **Pagination**: Use `offset` and `limit` for large result sets
