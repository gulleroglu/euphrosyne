# Order Change Requests API Documentation

## Overview

To change an order, you'll need to create an order change request. An order change request describes the slices of an existing paid order that you want to remove and search criteria for new slices you want to add.

## Schema

### Order Change Request Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (e.g., `ocr_0000A3bQP9RLVfNUcdpLpw`) |
| `order_id` | string | The order being modified |
| `created_at` | datetime | ISO 8601 timestamp of creation |
| `updated_at` | datetime | ISO 8601 timestamp of last update |
| `live_mode` | boolean | Whether created in live or test mode |
| `slices` | object | Slices to add/remove |
| `order_change_offers` | array | Available replacement flight options |

### Slices Object

| Field | Type | Description |
|-------|------|-------------|
| `remove` | array | Slice IDs to remove from order |
| `add` | array | New slices to search for |

### Add Slice Schema

| Field | Type | Description |
|-------|------|-------------|
| `origin` | string | IATA airport/city code |
| `destination` | string | IATA airport/city code |
| `departure_date` | string | Date in YYYY-MM-DD format |
| `cabin_class` | enum | economy, premium_economy, business, first |

---

## Endpoints

### Create Order Change Request

**Endpoint:** `POST https://api.duffel.com/air/order_change_requests`

**Request Body:**
```json
{
  "data": {
    "order_id": "ord_0000A3bQ8FJIQoEfuC07n6",
    "slices": {
      "remove": [
        {
          "slice_id": "sli_00009htYpSCXrwaB9Dn123"
        }
      ],
      "add": [
        {
          "origin": "LHR",
          "destination": "JFK",
          "departure_date": "2020-04-24",
          "cabin_class": "economy"
        }
      ]
    },
    "private_fares": {
      "UA": [
        {
          "corporate_code": "1234",
          "tour_code": "578DFL"
        }
      ]
    }
  }
}
```

**Response:**
Returns the created order change request with `order_change_offers` array.

---

### Get Order Change Request

**Endpoint:** `GET https://api.duffel.com/air/order_change_requests/{id}`

**URL Parameters:**
- `id` (required): Order change request ID

---

## Example: Change Return Flight

```python
import requests

url = "https://api.duffel.com/air/order_change_requests"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

payload = {
    "data": {
        "order_id": "ord_0000A3bQ8FJIQoEfuC07n6",
        "slices": {
            "remove": [
                {"slice_id": "sli_return_slice_id"}
            ],
            "add": [
                {
                    "origin": "JFK",
                    "destination": "LHR",
                    "departure_date": "2025-06-15",
                    "cabin_class": "economy"
                }
            ]
        }
    }
}

response = requests.post(url, json=payload, headers=headers, timeout=60)
data = response.json()["data"]

# Get available change offers
offers = data.get("order_change_offers", [])
for offer in offers:
    print(f"Change cost: {offer['change_total_amount']} {offer['change_total_currency']}")
    print(f"Penalty: {offer['penalty_total_amount']} {offer['penalty_total_currency']}")
```

## Key Notes

- All new slices must use the same cabin class
- Always show the full name of the operating carrier per US regulations
- Offers expire at a specified datetime
- Pricing reflects airline penalties and change fees
- Private fares are optional and airline-specific

## Change Flow

```
1. Create order change request with slices to remove/add
2. Review order change offers returned
3. Select an offer
4. Confirm the order change (see Order Changes API)
```
