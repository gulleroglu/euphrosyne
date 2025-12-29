# Batch Offer Requests API Documentation

## Overview

Batch offer requests are a mechanism for retrieving offers as they become available, instead of waiting for the entire offer payload to finish processing.

These resources function as long-polling endpoints that can be repeatedly queried to retrieve offers progressively. Batch requests expire after one minute, though offers remain accessible via the standard offer request ID.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Duffel's unique identifier |
| `created_at` | datetime | ISO 8601 timestamp of creation |
| `client_key` | string | Token for Duffel Ancillaries component |
| `live_mode` | boolean | Whether created in live or test mode |
| `total_batches` | number | Total number of expected offer batches |
| `remaining_batches` | number | Number of batches still pending |
| `offers` | array | Available offers (populated on GET) |

---

## Endpoints

### Create a Batch Offer Request

**Method:** `POST`
**URL:** `https://api.duffel.com/air/batch_offer_requests`

**Query Parameters:**
- `supplier_timeout` (integer, optional): Milliseconds to wait per airline (2000-60000, default: 20000)

**Request Body:**
```json
{
  "data": {
    "slices": [
      {
        "origin": "LHR",
        "destination": "JFK",
        "departure_date": "2020-04-24",
        "departure_time": { "from": "09:45", "to": "17:00" }
      }
    ],
    "passengers": [
      { "type": "adult", "family_name": "Earhart", "given_name": "Amelia" },
      { "age": 14 }
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
    "total_batches": 2,
    "remaining_batches": 2,
    "live_mode": false,
    "client_key": "SFMyNTY..."
  }
}
```

---

### Get a Single Batch Offer Request

**Method:** `GET`
**URL:** `https://api.duffel.com/air/batch_offer_requests/{id}`

**URL Parameters:**
- `id` (required): Batch offer request identifier

**Response:**
Returns batch metadata plus `offers` array containing available offers.

---

## Polling Pattern

Call the GET endpoint repeatedly to retrieve all offers as they become available. Once you get a response with `remaining_batches` of 0, you can stop requesting.

```python
import requests
import time

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

# Step 1: Create batch offer request
create_url = "https://api.duffel.com/air/batch_offer_requests"
payload = {
    "data": {
        "slices": [
            {
                "origin": "LHR",
                "destination": "JFK",
                "departure_date": "2025-06-01"
            }
        ],
        "passengers": [{"type": "adult"}],
        "cabin_class": "economy"
    }
}

response = requests.post(create_url, json=payload, headers=headers)
batch = response.json()["data"]
batch_id = batch["id"]

print(f"Created batch: {batch_id}")
print(f"Total batches: {batch['total_batches']}")

# Step 2: Poll for offers
all_offers = []
get_url = f"{create_url}/{batch_id}"

while True:
    response = requests.get(get_url, headers=headers)
    data = response.json()["data"]

    # Collect new offers
    new_offers = data.get("offers", [])
    all_offers.extend(new_offers)

    remaining = data["remaining_batches"]
    print(f"Remaining batches: {remaining}, Offers so far: {len(all_offers)}")

    if remaining == 0:
        break

    # Wait before polling again
    time.sleep(1)

print(f"Total offers retrieved: {len(all_offers)}")
```

## Use Cases

- **Progressive Loading**: Display offers to users as they arrive
- **Faster Initial Response**: Show first results quickly while others load
- **Better UX**: Provide visual feedback during search

## Notes

- Batch requests expire after one minute
- Offers remain accessible via standard offer request ID after expiry
- Each batch may contain offers from different airlines
- Use `remaining_batches` to determine completion status
