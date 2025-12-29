# Order Change Offers API Documentation

## Overview

After you've searched for flights to add to your order by creating an order change request, we'll send information about the changes you want to make to the airline, which may return order change offers.

Each offer represents available flights at a specific price meeting search criteria, organized into slices containing segments (individual flights).

## Base URL
```
https://api.duffel.com/air/order_change_offers
```

## Schema

### Order Change Offer Object

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Unique identifier (e.g., `oco_0000A3vUda8dKRtUSQPSXw`) |
| `change_total_amount` | string | Amount charged/refunded to original payment |
| `change_total_currency` | string | ISO 4217 currency code |
| `new_total_amount` | string | Price if newly purchased |
| `new_total_currency` | string | ISO 4217 currency code |
| `penalty_total_amount` | string | Airline penalty for change |
| `penalty_total_currency` | string | Currency of penalty |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `expires_at` | datetime | ISO 8601 expiration timestamp |
| `live_mode` | boolean | True if created in live mode |
| `order_change_id` | string | ID of order change if already created |
| `refund_to` | enum | `original_form_of_payment`, `airline_credits`, or `voucher` |
| `conditions` | object | Post-booking modification rules |
| `slices` | object | Slices being added/removed |
| `private_fares` | array | Applied private fares |

### Conditions Object

| Field | Type | Description |
|-------|------|-------------|
| `change_before_departure` | object | Change terms |
| `refund_before_departure` | object | Refund terms |

Each contains:
- `allowed` (boolean)
- `penalty_amount` (string)
- `penalty_currency` (string)

---

## Endpoints

### List Order Change Offers

**Endpoint:** `GET /air/order_change_offers`

**Query Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| `order_change_request_id` | Yes | Order change request ID |
| `limit` | No | Max records per page (1-200, default 50) |
| `after` | No | Pagination cursor |
| `before` | No | Pagination cursor |
| `sort` | No | `change_total_amount` or `total_duration` |
| `max_connections` | No | Filter by max connections (default 1) |

**Request:**
```bash
curl -X GET --compressed \
  "https://api.duffel.com/air/order_change_offers?order_change_request_id=ocr_0000A3bQP9RLVfNUcdpLpw" \
  -H "Accept: application/json" \
  -H "Duffel-Version: v2" \
  -H "Authorization: Bearer <TOKEN>"
```

---

### Get Single Order Change Offer

**Endpoint:** `GET /air/order_change_offers/{id}`

**URL Parameters:**
- `id` (required): Order change offer ID

---

## Example Response

```json
{
  "data": {
    "id": "oco_0000A3vUda8dKRtUSQPSXw",
    "change_total_amount": "90.80",
    "change_total_currency": "GBP",
    "new_total_amount": "35.50",
    "new_total_currency": "GBP",
    "penalty_total_amount": "10.50",
    "penalty_total_currency": "GBP",
    "order_change_id": "oce_0000A4QasEUIjJ6jHKfhHU",
    "created_at": "2020-01-17T10:12:14.545Z",
    "expires_at": "2020-01-17T10:42:14.545Z",
    "live_mode": false,
    "refund_to": "original_form_of_payment",
    "slices": {
      "remove": [],
      "add": []
    },
    "conditions": {
      "change_before_departure": {
        "allowed": true,
        "penalty_amount": "100.00",
        "penalty_currency": "GBP"
      },
      "refund_before_departure": {
        "allowed": true,
        "penalty_amount": "100.00",
        "penalty_currency": "GBP"
      }
    }
  }
}
```

## Refund Destinations

| Value | Description |
|-------|-------------|
| `original_form_of_payment` | Refund to original payment method |
| `airline_credits` | Airline credit voucher |
| `voucher` | Travel voucher |

## Example: List and Select Offer

```python
import requests

# List available offers
url = "https://api.duffel.com/air/order_change_offers"
params = {
    "order_change_request_id": "ocr_0000A3bQP9RLVfNUcdpLpw",
    "sort": "change_total_amount"
}
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2"
}

response = requests.get(url, params=params, headers=headers)
offers = response.json()["data"]

# Find cheapest offer
cheapest = min(offers, key=lambda x: float(x["change_total_amount"]))
print(f"Cheapest change: {cheapest['change_total_amount']} {cheapest['change_total_currency']}")
print(f"Penalty: {cheapest['penalty_total_amount']}")
print(f"Expires: {cheapest['expires_at']}")
```

## Notes

- Offers expire at `expires_at` - check before confirming
- `change_total_amount` can be negative (refund) or positive (charge)
- Always display penalty information to customers
