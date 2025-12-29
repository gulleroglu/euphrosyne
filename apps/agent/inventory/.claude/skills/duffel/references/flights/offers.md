# Duffel Offers API Documentation

## Overview

After conducting a flight search via offer request, airlines return offers representing available flights at specific prices matching search criteria. Each offer contains slices with one or more segments (individual flights). Offers typically expire within 30 minutes, as indicated by the `expires_at` field.

## Key Endpoints

### Get a Single Offer

**Endpoint:** `GET https://api.duffel.com/air/offers/{id}`

**URL Parameters:**
- `id` (string, required): Duffel's unique identifier

**Query Parameters:**
- `return_available_services` (boolean, default: false): Include available services in response

**Response includes:** Complete, current offer information including available services, payment requirements, and conditions.

---

### Price an Offer

**Endpoint:** `POST https://api.duffel.com/air/offers/{id}/actions/price`

**URL Parameters:**
- `id` (string, required): Offer identifier

**Request Body:**
```json
{
  "data": {
    "intended_services": [
      {
        "quantity": 1,
        "id": "ase_00009UhD4ongolulWd9123"
      }
    ],
    "intended_payment_methods": []
  }
}
```

Returns total amount including applicable surcharges.

---

### Update Offer Passenger

**Endpoint:** `PATCH https://api.duffel.com/air/offers/{offer_id}/passengers/{offer_passenger_id}`

**Request Body:**
```json
{
  "data": {
    "given_name": "Amelia",
    "family_name": "Earhart",
    "loyalty_programme_accounts": [
      {
        "airline_iata_code": "BA",
        "account_number": "12901014"
      }
    ]
  }
}
```

---

### List Offers

**Endpoint:** `GET https://api.duffel.com/air/offers`

**Query Parameters:**
- `offer_request_id` (string, required): Associated offer request ID
- `sort` (enum): `total_amount` or `total_duration` (prepend `-` for descending)
- `max_connections` (integer, default: 1): Filter by maximum connections
- `limit` (integer, default: 50, range: 1-200): Results per page
- `after`, `before` (string): Pagination cursors

---

## Core Schema Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique offer identifier |
| `total_amount` | string | Total price including taxes |
| `base_amount` | string | Base price excluding taxes |
| `tax_amount` | string | Tax amount (nullable) |
| `total_currency` | string | ISO 4217 currency code |
| `expires_at` | datetime | ISO 8601 expiration timestamp |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `slices` | array | Journey segments with flights |
| `passengers` | array | Passengers included in offer |
| `conditions` | object | Post-booking modification terms |
| `available_services` | array | Optional bookable services |
| `available_airline_credit_ids` | array | Applicable airline credits |
| `owner` | object | Airline providing offer |
| `partial` | boolean | Whether offer is partial |
| `passenger_identity_documents_required` | boolean | Passport required flag |

## Slice Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Slice identifier |
| `origin` | object | Origin airport details |
| `destination` | object | Destination airport details |
| `duration` | string | Total slice duration |
| `segments` | array | Individual flights |

## Segment Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Segment identifier |
| `origin` | object | Departure airport |
| `destination` | object | Arrival airport |
| `departing_at` | datetime | Departure time |
| `arriving_at` | datetime | Arrival time |
| `operating_carrier` | object | Airline operating flight |
| `marketing_carrier` | object | Airline marketing flight |
| `operating_carrier_flight_number` | string | Flight number |
| `aircraft` | object | Aircraft type |
| `duration` | string | Flight duration |

## Conditions Schema

| Field | Type | Description |
|-------|------|-------------|
| `refund_before_departure` | object | Refund terms before departure |
| `change_before_departure` | object | Change terms before departure |

## Important Notes

- **This endpoint does not guarantee that the offer will be available at the time of booking.**
- Always call the single offer endpoint before booking to confirm current pricing and availability.
- Prices may change between search results and booking time due to airline system limitations.
- Offers typically expire within 15-30 minutes.

## Example: Get Offer with Services

```python
import requests

offer_id = "off_00009htyDGjIfajdNBZRlw"
url = f"https://api.duffel.com/air/offers/{offer_id}"
params = {"return_available_services": "true"}
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Accept": "application/json"
}

response = requests.get(url, params=params, headers=headers)
offer = response.json()["data"]

print(f"Total: {offer['total_amount']} {offer['total_currency']}")
print(f"Expires: {offer['expires_at']}")
```
