# Duffel Offer Requests API Documentation

## Overview

The Offer Requests API allows you to search for flights by creating an offer request that describes passengers, travel destinations, and travel dates.

## Resource Schema

### Offer Request Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Duffel's unique identifier |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `live_mode` | boolean | True if created in live mode |
| `cabin_class` | enum | Travel class: "first", "business", "premium_economy", or "economy" |
| `slices` | array | Journey segments (one for one-way, two for returns) |
| `passengers` | array | Travelers included in the request |
| `offers` | array | Returned airline offers matching criteria |
| `airline_credit_ids` | array | IDs of airline credits evaluated for applicability |
| `client_key` | string | Key for Duffel Ancillaries component integration |

## API Endpoints

### List Offer Requests

**GET** `https://api.duffel.com/air/offer_requests`

Lists paginated offer requests in any order.

**Query Parameters:**
- `limit` (integer, default: 50) — Results per page (1-200)
- `after` (string) — Cursor for next page
- `before` (string) — Cursor for previous page

**Response:** Paginated list of offer request objects with `meta` containing `limit` and pagination cursors.

---

### Create Offer Request

**POST** `https://api.duffel.com/air/offer_requests`

Initiates a flight search by creating an offer request.

**Query Parameters:**
- `return_offers` (boolean, default: true) — Include all offers in response
- `supplier_timeout` (integer, default: 20000) — Max milliseconds to wait per airline (2000-60000)

**Request Body:**
```json
{
  "data": {
    "slices": [
      {
        "origin": "LHR",
        "destination": "JFK",
        "departure_date": "2020-04-24",
        "departure_time": {"from": "09:45", "to": "17:00"},
        "arrival_time": {"from": "09:45", "to": "17:00"}
      }
    ],
    "passengers": [
      {"family_name": "Earhart", "given_name": "Amelia", "type": "adult"},
      {"age": 14},
      {"fare_type": "student"}
    ],
    "cabin_class": "economy",
    "max_connections": 0,
    "airline_credit_ids": ["acd_00009htYpSCXrwaB9DnUm1"],
    "private_fares": {
      "QF": [{"corporate_code": "FLX53", "tracking_reference": "ABN:2345678"}]
    }
  }
}
```

**Response:** Offer request object with populated `offers` array containing airline matches.

---

### Get Single Offer Request

**GET** `https://api.duffel.com/air/offer_requests/{id}`

Retrieves a specific offer request by ID.

**URL Parameters:**
- `id` (string, required) — Offer request identifier

**Response:** Complete offer request object with all associated data.

---

## Slice Schema

| Field | Type | Description |
|-------|------|-------------|
| `origin` | string | IATA airport or city code |
| `destination` | string | IATA airport or city code |
| `departure_date` | string | Date in YYYY-MM-DD format |
| `departure_time` | object | Optional time window {from, to} |
| `arrival_time` | object | Optional time window {from, to} |

## Passenger Schema

| Field | Type | Description |
|-------|------|-------------|
| `type` | enum | "adult", "child", "infant_without_seat" |
| `age` | integer | Passenger age (alternative to type) |
| `given_name` | string | First name |
| `family_name` | string | Last name |
| `fare_type` | string | Special fare type (e.g., "student") |

## Key Notes

- Display the "full name of the operating carrier of each segment" prominently on offer presentation screens to comply with US regulations.
- Specify either `age` OR `type` for passengers, not both.
- Different airlines apply different passenger classification rules (e.g., age 14 may be adult or young adult).
- Set `supplier_timeout` lower than your HTTP request timeout to receive partial results before timeout.

## Cabin Classes

- `economy`
- `premium_economy`
- `business`
- `first`

## Example: Round Trip Search

```python
import requests

url = "https://api.duffel.com/air/offer_requests"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

payload = {
    "data": {
        "slices": [
            {
                "origin": "LHR",
                "destination": "JFK",
                "departure_date": "2025-06-01"
            },
            {
                "origin": "JFK",
                "destination": "LHR",
                "departure_date": "2025-06-08"
            }
        ],
        "passengers": [{"type": "adult"}],
        "cabin_class": "economy",
        "max_connections": 1
    }
}

response = requests.post(url, json=payload, headers=headers, timeout=60)
data = response.json()
offers = data["data"]["offers"]
```
