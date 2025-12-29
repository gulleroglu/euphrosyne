# Airline Credits API Documentation

## Overview

Airline credits represent credit issued by an airline for a canceled or disrupted flight. These credits can be used as payment for future bookings.

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Duffel's unique identifier |
| `airline_iata_code` | string | Two-character IATA code |
| `amount` | string | Value of the airline credit |
| `amount_currency` | string (nullable) | ISO 4217 currency code |
| `code` | string (nullable) | Credit identifier from airline |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `expires_at` | datetime (nullable) | Expiration timestamp |
| `family_name` | string | Passenger's family name |
| `given_name` | string (nullable) | Passenger's given name |
| `invalidated_at` | datetime (nullable) | Invalidation timestamp |
| `issued_on` | date | ISO 8601 issuance date |
| `live_mode` | boolean | Whether created in live mode |
| `order_id` | string (nullable) | Associated order identifier |
| `passenger_id` | string (nullable) | Associated passenger identifier |
| `spent_at` | datetime (nullable) | Redemption timestamp |
| `type` | enum | `eticket` or `mco` |
| `user_id` | string (nullable) | Associated customer user ID |

---

## Endpoints

### Get a Single Airline Credit

**Endpoint:** `GET https://api.duffel.com/air/airline_credits/{id}`

**Parameters:**
- `id` (required): Airline credit identifier

---

### List Airline Credits

**Endpoint:** `GET https://api.duffel.com/air/airline_credits`

**Query Parameters:**
- `after` (optional): Cursor for pagination
- `before` (optional): Cursor for pagination
- `limit` (optional, default: 50, max: 200): Records per page
- `user_id` (optional): Filter by customer user ID

---

### Create an Airline Credit

**Endpoint:** `POST https://api.duffel.com/air/airline_credits`

**Required Body Parameters:**
- `airline_iata_code` (string): Two-character IATA code
- `amount` (string): Monetary value
- `amount_currency` (string): ISO 4217 currency code
- `code` (string): Redemption code
- `expires_at` (datetime): Expiration timestamp
- `issued_on` (date): Issuance date
- `type` (enum): `eticket` or `mco`

**Optional Body Parameters:**
- `user_id` (string): Customer user identifier
- `given_name` (string): Customer's given name
- `family_name` (string): Customer's family name

---

## Credit Types

| Type | Description |
|------|-------------|
| `eticket` | Electronic ticket credit |
| `mco` | Miscellaneous Charges Order |

---

## Example: Using Airline Credits in Search

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

# List available credits for a user
url = "https://api.duffel.com/air/airline_credits"
params = {"user_id": "usr_xxx"}
response = requests.get(url, params=params, headers=headers)
credits = response.json()["data"]

# Filter valid credits
valid_credits = [
    c for c in credits
    if c["spent_at"] is None and c["invalidated_at"] is None
]

# Use in offer request
if valid_credits:
    credit_ids = [c["id"] for c in valid_credits]

    offer_url = "https://api.duffel.com/air/offer_requests"
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
            "cabin_class": "economy",
            "airline_credit_ids": credit_ids
        }
    }

    response = requests.post(offer_url, json=payload, headers=headers)
    offers = response.json()["data"]["offers"]

    # Check which offers can use the credits
    for offer in offers:
        applicable = offer.get("available_airline_credit_ids", [])
        print(f"Offer {offer['id']}: Credits applicable: {applicable}")
```

---

## Example: Create Airline Credit

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

url = "https://api.duffel.com/air/airline_credits"
payload = {
    "data": {
        "airline_iata_code": "BA",
        "amount": "150.00",
        "amount_currency": "GBP",
        "code": "CREDIT123456",
        "expires_at": "2026-01-01T00:00:00Z",
        "issued_on": "2025-01-01",
        "type": "eticket",
        "family_name": "Earhart",
        "given_name": "Amelia"
    }
}

response = requests.post(url, json=payload, headers=headers)
credit = response.json()["data"]
print(f"Created credit: {credit['id']}")
```

## Notes

- Credits must be issued by the airline operating the flight
- Credits can only be applied to matching airline offers
- Check `expires_at` before attempting to use credits
- Use `airline_credit_ids` in offer requests to check applicability
