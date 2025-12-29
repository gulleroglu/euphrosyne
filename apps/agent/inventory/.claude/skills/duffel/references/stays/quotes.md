# Quotes API Documentation

## Overview

The Quotes endpoint provides the final price and availability verification for accommodation rates, confirming bookings before creation.

## Base Endpoint

```
https://api.duffel.com/stays/quotes
```

---

## Create Quote

**Endpoint:** `POST /stays/quotes`

**Description:** Creates a ready-to-book Duffel Stay Quote — a prospective booking — from a given room rate.

### Request Body

```json
{
  "data": {
    "rate_id": "rat_0000ARxBI85qTkbVapZDD2"
  }
}
```

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `rate_id` | string | Yes | Rate identifier to convert to quote |

### Response Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Quote identifier |
| `total_amount` | string | Total price for all nights and guests |
| `total_currency` | string | ISO 4217 currency code |
| `base_amount` | string (nullable) | Price excluding taxes/fees |
| `tax_amount` | string (nullable) | Tax portion |
| `fee_amount` | string (nullable) | Commission fees |
| `deposit_amount` | string (nullable) | Pre-check-in deposit |
| `due_at_accommodation_amount` | string (nullable) | Due at accommodation |
| `check_in_date` | date | ISO 8601 date format |
| `check_out_date` | date | ISO 8601 date format |
| `rooms` | integer | Number of rooms |
| `guests` | array | Guest objects with type and age |
| `accommodation` | object | Full accommodation details |
| `supported_loyalty_programme` | object (nullable) | Loyalty program info |
| `expires_at` | datetime | Quote expiration |

---

## Get Quote

**Endpoint:** `GET /stays/quotes/{id}`

**Description:** Retrieves a specific quote created by your organization.

### URL Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Quote identifier |

---

## Example: Create and Use Quote

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

# Step 1: Create quote from rate
url = "https://api.duffel.com/stays/quotes"
payload = {
    "data": {
        "rate_id": "rat_0000ARxBI85qTkbVapZDD2"
    }
}

response = requests.post(url, json=payload, headers=headers)
quote = response.json()["data"]

print(f"Quote ID: {quote['id']}")
print(f"Total: {quote['total_amount']} {quote['total_currency']}")
print(f"Check-in: {quote['check_in_date']}")
print(f"Check-out: {quote['check_out_date']}")
print(f"Expires: {quote['expires_at']}")

# Step 2: Use quote_id to create booking
# See Bookings API documentation
```

---

## Example Response

```json
{
  "data": {
    "id": "quo_0000AS0NZdKjjnnHZmSUbI",
    "total_amount": "799.00",
    "total_currency": "GBP",
    "base_amount": "665.83",
    "tax_amount": "133.17",
    "fee_amount": null,
    "deposit_amount": null,
    "due_at_accommodation_amount": null,
    "check_in_date": "2025-06-01",
    "check_out_date": "2025-06-05",
    "rooms": 1,
    "guests": [
      {"type": "adult"},
      {"type": "adult"}
    ],
    "accommodation": {
      "id": "acc_0000AWr2VsUNIF1Vl91xg0",
      "name": "Duffel Test Hotel",
      "rating": 5
    },
    "supported_loyalty_programme": null,
    "expires_at": "2025-01-01T12:30:00Z"
  }
}
```

## Notes

- Quotes confirm final pricing and availability
- Quotes expire - check `expires_at` before creating booking
- Quote ID is required for booking creation
- Pricing may differ from search results due to real-time availability
