# Booking Payment Instructions API Documentation

## Overview

The Booking Payment Instructions API enables payment processing on behalf of guests for accommodations where payment is due at the hotel. This feature conveys card details, authorization limits, and invoice delivery information to lodging properties.

## Base Endpoint

```
https://api.duffel.com/stays/bookings/{booking_id}/payment_instructions
```

**Status:** Preview (subject to change)

---

## Schema

### Booking Payment Instruction Object

| Field | Type | Description |
|-------|------|-------------|
| `booking_id` | string | Stays booking identifier |
| `card_id` | string | Payment card ID (must be multi-use lodged card) |
| `approved_charges` | object | Authorized charge categories |
| `limit_amount` | string | Maximum chargeable amount |
| `limit_currency` | string | ISO 4217 currency code |
| `invoice` | object | Billing and delivery information |

### Approved Charges Object

| Field | Type | Description |
|-------|------|-------------|
| `base` | boolean | Authorize base accommodation price |
| `taxes` | boolean | Authorize applicable taxes |
| `fees` | boolean | Authorize booking fees |
| `other` | string | Custom authorized charges (free-text) |

### Invoice Object

| Field | Type | Description |
|-------|------|-------------|
| `send_to` | string | Email for invoice delivery |
| `company_name` | string | Recipient organization name |
| `address_line_1` | string | Primary address line |
| `address_line_2` | string | Secondary address line (optional) |
| `address_city` | string | City |
| `address_region` | string | State or region |
| `address_postal_code` | string | Postal code |
| `address_country_code` | string | ISO country code |

---

## Endpoint

### Create Booking Payment Instruction

**Method:** `POST`
**Endpoint:** `/stays/bookings/{booking_id}/payment_instructions`

#### Requirements

- Booking must have `payment_instruction_allowed: true`
- Card must be lodged with `multi_use` enabled

#### Request Example

```python
import requests

booking_id = "bok_0000AS0NZdKjjnnHZmSUbI"
url = f"https://api.duffel.com/stays/bookings/{booking_id}/payment_instructions"

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

payload = {
    "data": {
        "card_id": "tcd_0000AS0NZdKjjnnHZmSUbI",
        "approved_charges": {
            "base": True,
            "taxes": True,
            "fees": True,
            "other": "Parking up to $50. Food up to $20"
        },
        "limit_amount": "1437.55",
        "limit_currency": "USD",
        "invoice": {
            "company_name": "Merchant",
            "address_line_1": "10 Downing St",
            "address_line_2": "Westminster",
            "address_city": "London",
            "address_region": "London",
            "address_postal_code": "SW1A 2AA",
            "address_country_code": "GB",
            "send_to": "invoice@merchant.io"
        }
    }
}

response = requests.post(url, json=payload, headers=headers)
instruction = response.json()["data"]
print(f"Created payment instruction for booking: {instruction['booking_id']}")
```

#### Response

```json
{
  "data": {
    "booking_id": "bok_0000AS0NZdKjjnnHZmSUbI",
    "card_id": "tcd_0000AS0NZdKjjnnHZmSUbI",
    "approved_charges": {
      "base": true,
      "taxes": true,
      "fees": true,
      "other": "Parking up to $50. Food up to $20"
    },
    "limit_amount": "1437.55",
    "limit_currency": "USD",
    "invoice": {
      "company_name": "Merchant",
      "address_line_1": "10 Downing St",
      "address_line_2": "Westminster",
      "address_city": "London",
      "address_region": "London",
      "address_postal_code": "SW1A 2AA",
      "address_country_code": "GB",
      "send_to": "invoice@merchant.io"
    }
  }
}
```

---

## Notes

- This API is in preview and may change
- Only works with bookings where payment is due at accommodation
- Card must be pre-lodged as multi-use before creating instructions

