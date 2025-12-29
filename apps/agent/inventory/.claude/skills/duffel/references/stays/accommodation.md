# Accommodation API Documentation

## Overview

The Accommodation API provides access to bookable lodging properties within the Duffel Stays platform. Properties maintain consistent identifiers across searches, enabling reliable tracking and retrieval.

## Base Endpoint

```
https://api.duffel.com/stays/accommodation
```

---

## Schema

### Accommodation Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier persisting across searches |
| `name` | string | Property name |
| `location` | object | Address and geographic coordinates |
| `description` | string (nullable) | Property overview |
| `photos` | array | Property imagery with URLs |
| `rating` | number (nullable) | 1-5 star rating |
| `review_score` | number (nullable) | Aggregated guest score (1.0-10.0) |
| `review_count` | number (nullable) | Contributing review count |
| `ratings` | array (nullable) | Multi-source ratings |
| `email` | string (nullable) | Populated only for completed bookings |
| `phone_number` | string (nullable) | Direct contact |
| `check_in_information` | object | Check-in/out times and policies |
| `key_collection` | object | Key retrieval instructions |
| `supported_loyalty_programme` | enum (nullable) | Supported program type |
| `payment_instruction_supported` | boolean | Payment instruction eligibility |
| `brand` | object (nullable) | Brand association |
| `chain` | object (nullable) | Parent group identification |
| `amenities` | array (nullable) | Available features |

### Room Object

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Room type designation |
| `beds` | array (nullable) | Bed inventory with type and quantity |
| `photos` | array (nullable) | Room-specific imagery |
| `rates` | array | Bookable options with pricing |

### Rate Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Rate identifier |
| `total_amount` | string | Complete per-stay cost |
| `base_amount` | string (nullable) | Pre-tax/fee amount |
| `tax_amount` | string (nullable) | Tax component |
| `fee_amount` | string (nullable) | Additional fees |
| `public_amount` | string (nullable) | Market rate for comparison |
| `due_at_accommodation_amount` | string (nullable) | Amount payable on-site |
| `board_type` | enum | room_only, breakfast, half_board, full_board, all_inclusive |
| `payment_type` | enum | pay_now, deposit, guarantee |
| `available_payment_methods` | array | balance, card |
| `quantity_available` | integer (nullable) | Inventory level |
| `expires_at` | datetime | Rate validity deadline |
| `cancellation_timeline` | array | Refund schedule by date |
| `conditions` | array | Mandatory policies |
| `supported_loyalty_programme` | enum (nullable) | Program eligibility |
| `loyalty_programme_required` | boolean | Membership requirement |
| `estimated_commission_amount` | string (nullable) | Commission estimate |
| `negotiated_rate_id` | string (nullable) | Negotiated rate reference |

---

## Endpoints

### 1. List Accommodation

**Method:** `GET`
**Endpoint:** `/stays/accommodation`

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `latitude` | number | Yes | -90° to 90° |
| `longitude` | number | Yes | -180° to 180° |
| `radius` | integer | Yes | 1-100 km (default 5) |
| `limit` | integer | No | 1-200 (default 50) |
| `after` | string | No | Pagination cursor |
| `before` | string | No | Pagination cursor |

#### Example

```python
import requests

url = "https://api.duffel.com/stays/accommodation"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}
params = {
    "latitude": 51.5071,
    "longitude": -0.1416,
    "radius": 5
}

response = requests.get(url, params=params, headers=headers)
accommodations = response.json()["data"]

for acc in accommodations:
    print(f"{acc['name']}: {acc['rating']} stars")
```

---

### 2. Get Accommodation

**Method:** `GET`
**Endpoint:** `/stays/accommodation/{id}`

#### URL Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Accommodation identifier |

---

### 3. Search Accommodation Suggestions

**Method:** `POST`
**Endpoint:** `/stays/accommodation/suggestions`

Returns abbreviated accommodation data matching search criteria.

#### Request Body

```json
{
  "data": {
    "query": "rits",
    "location": {
      "radius": 5,
      "geographic_coordinates": {
        "latitude": 51.5071,
        "longitude": -0.1416
      }
    }
  }
}
```

#### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Minimum 3 characters |
| `location` | object | No | Geographic filter |

#### Response

```json
{
  "data": [
    {
      "accommodation_id": "acc_0000AWr2VsUNIF1Vl91xg0",
      "accommodation_name": "Duffel Test Hotel",
      "accommodation_location": {...}
    }
  ]
}
```

---

## Notes

- Accommodation IDs remain stable across searches
- Many fields are nullable; implement fallbacks
- Star ratings synthesize multi-source data
- Always validate rate expiry timestamps before presenting to customers
- Cancellation timeline entries appear in chronological order

