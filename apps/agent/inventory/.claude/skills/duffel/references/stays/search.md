# Duffel Stays Search API Documentation

## Endpoint

**POST** `https://api.duffel.com/stays/search`

## Overview

The Search endpoint returns all available accommodations that match your search criteria. You may search by location or accommodation, but not both simultaneously. Results include the cheapest available rate per accommodation.

## Required Headers

```
Accept-Encoding: gzip
Accept: application/json
Content-Type: application/json
Duffel-Version: v2
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

## Request Body Parameters

### Required Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `rooms` | integer | Number of rooms needed |
| `guests` | array | List of guest objects with `type` (adult/child) and optional `age` |
| `check_in_date` | date | ISO 8601 format; max 330 days future |
| `check_out_date` | date | ISO 8601 format; max 99-night stays |

### Optional Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `location` | object | Geographic search with `latitude`, `longitude`, and `radius` (1-100 km) |
| `accommodation` | object | Specific accommodation IDs (max 200 without rates, 10 with rates) |
| `free_cancellation_only` | boolean | Filter to free cancellation rates only |
| `mobile` | boolean | Indicates if search originates from mobile device |

## Location Object

```json
{
  "location": {
    "geographic_coordinates": {
      "latitude": 51.5071,
      "longitude": -0.1416
    },
    "radius": 5
  }
}
```

## Response Schema

### Search Result Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique search result identifier |
| `accommodation` | object | Full accommodation details |
| `cheapest_rate_total_amount` | string | Total price |
| `cheapest_rate_currency` | string | ISO 4217 currency code |
| `check_in_date` | date | Guest check-in date |
| `check_out_date` | date | Guest check-out date |
| `expires_at` | datetime | Search result expiration |
| `guests` | array | Guest information from request |
| `rooms` | integer | Number of rooms |

### Accommodation Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique accommodation ID |
| `name` | string | Property name |
| `location` | object | Address and coordinates |
| `rating` | integer | Star rating (1-5) |
| `review_score` | number | Guest review average |
| `review_count` | integer | Number of reviews |
| `amenities` | array | Available facilities |
| `rooms` | array | Room types with rates |
| `photos` | array | Property images |
| `brand` | object | Brand/chain information |

### Rate Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Rate identifier |
| `total_amount` | string | Full price (base + tax + fee) |
| `base_amount` | string | Price excluding taxes/fees |
| `tax_amount` | string | Tax component |
| `fee_amount` | string | Fee component |
| `board_type` | enum | room_only, breakfast, half_board, full_board, all_inclusive |
| `payment_type` | enum | pay_now, guarantee, deposit |
| `cancellation_timeline` | array | Refund schedule with deadlines |
| `expires_at` | datetime | Rate expiration |

## Example Request

```python
import requests

url = "https://api.duffel.com/stays/search"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

payload = {
    "data": {
        "rooms": 1,
        "guests": [
            {"type": "adult"},
            {"type": "adult"}
        ],
        "check_in_date": "2025-06-01",
        "check_out_date": "2025-06-05",
        "location": {
            "geographic_coordinates": {
                "latitude": 43.7384,
                "longitude": 7.4246
            },
            "radius": 10
        }
    }
}

response = requests.post(url, json=payload, headers=headers, timeout=60)
data = response.json()["data"]

for result in data["results"]:
    acc = result["accommodation"]
    print(f"{acc['name']}: {result['cheapest_rate_total_amount']} {result['cheapest_rate_currency']}")
```

## Example Response

```json
{
  "data": {
    "results": [
      {
        "id": "srr_0000ASVBuJVLdmqtZDJ4ca",
        "check_in_date": "2025-06-01",
        "check_out_date": "2025-06-05",
        "cheapest_rate_total_amount": "799.00",
        "cheapest_rate_currency": "GBP",
        "expires_at": "2025-06-01T12:00:00Z",
        "accommodation": {
          "id": "acc_0000AWr2VsUNIF1Vl91xg0",
          "name": "Duffel Test Hotel",
          "rating": 5,
          "review_score": 8.5,
          "location": {
            "address": {
              "city_name": "Monaco",
              "country_code": "MC"
            },
            "geographic_coordinates": {
              "latitude": 43.7384,
              "longitude": 7.4246
            }
          }
        }
      }
    ],
    "created_at": "2025-01-01T15:21:01Z"
  }
}
```

## Board Types

| Type | Description |
|------|-------------|
| `room_only` | No meals included |
| `breakfast` | Breakfast included |
| `half_board` | Breakfast and dinner |
| `full_board` | All meals included |
| `all_inclusive` | All meals, drinks, and amenities |

## Notes

- Search by location OR accommodation, not both
- Results expire - check `expires_at` before booking
- Use `free_cancellation_only` for flexible bookings
- Maximum 330 days advance booking
- Maximum 99-night stays
