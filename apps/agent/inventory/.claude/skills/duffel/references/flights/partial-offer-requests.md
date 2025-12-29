# Partial Offer Requests API Documentation

## Overview

To search for and select flights separately for each slice of the journey, you'll need to create a partial offer request. This feature allows specification of passengers and travel details including slices and additional filters like cabin class.

## Schema

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (e.g., `orq_00009hjdomFOCJyxHG7k7k`) |
| `created_at` | datetime | ISO 8601 timestamp of creation |
| `cabin_class` | enum | `first`, `business`, `premium_economy`, `economy` |
| `airline_credit_ids` | string[] | IDs of airline credits for offer evaluation |
| `live_mode` | boolean | Whether created in live vs. test mode |
| `slices` | list | Journey segments |
| `passengers` | list | Travelers included in the request |
| `offers` | list | Returned airline offers (partial = true) |
| `client_key` | string | Token for Duffel Ancillaries component |

---

## Endpoints

### 1. Create a Partial Offer Request

**Endpoint:** `POST https://api.duffel.com/air/partial_offer_requests`

**Query Parameters:**
- `supplier_timeout` (integer, optional): Max wait time in ms (2000-60000, default: 20000)

**Request Body:**
```json
{
  "data": {
    "slices": [
      {
        "origin": "LHR",
        "destination": "JFK",
        "departure_date": "2020-04-24",
        "departure_time": {
          "from": "09:45",
          "to": "17:00"
        }
      }
    ],
    "passengers": [
      {
        "type": "adult",
        "family_name": "Earhart",
        "given_name": "Amelia"
      }
    ],
    "cabin_class": "economy",
    "max_connections": 0
  }
}
```

**Response:**
```json
{
  "data": {
    "id": "orq_00009hjdomFOCJyxHG7k7k",
    "created_at": "2020-02-12T15:21:01.927Z",
    "live_mode": false,
    "cabin_class": "economy",
    "offers": [
      {
        "id": "off_00009htYpSCXrwaB9DnUm0",
        "partial": true,
        "total_amount": "45.00",
        "total_currency": "GBP"
      }
    ]
  }
}
```

---

### 2. Get a Single Partial Offer Request

**Endpoint:** `GET https://api.duffel.com/air/partial_offer_requests/{id}`

**URL Parameters:**
- `id` (required): Partial offer request identifier

**Query Parameters:**
- `selected_partial_offer[]` (optional): Previously selected partial offer IDs

**Example:**
```
GET /air/partial_offer_requests/prq_xxx?selected_partial_offer[]=off_xxx_0
```

---

### 3. Get Full Offer Fares (Deprecated)

**Endpoint:** `GET https://api.duffel.com/air/partial_offer_requests/{id}/fares`

**Query Parameters:**
- `selected_partial_offer[]` (required): Partial offer IDs from each slice

**Note:** This endpoint will be removed in the next major version.

---

## Use Case: Multi-Slice Journey

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

# Step 1: Create partial offer request for first slice
url = "https://api.duffel.com/air/partial_offer_requests"
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
        "cabin_class": "economy"
    }
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()["data"]

# Step 2: User selects outbound flight
outbound_offers = [o for o in data["offers"] if o["partial"]]
selected_outbound = outbound_offers[0]["id"]

# Step 3: Get return options with outbound selection
get_url = f"{url}/{data['id']}"
params = {"selected_partial_offer[]": selected_outbound}
response = requests.get(get_url, params=params, headers=headers)
return_offers = response.json()["data"]["offers"]

# Step 4: User selects return flight
selected_return = return_offers[0]["id"]

# Now you have both slice selections for booking
```

## Important Notes

- When presenting partial offers, always show the full name of the operating carrier for regulatory compliance
- Each offer includes detailed segment information
- Offers contain conditions regarding refunds, changes, and seat selection
- Partial offers must be combined to create a complete booking
