# Duffel Payments API Documentation

## Overview

The Payments API manages payments for various order types. Payments transition from `pending` to either `failed` or `succeeded` status.

## Schema

### Payment Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (e.g., `pay_00009hthhsUZ8W4LxQgkjo`) |
| `order_id` | string | Associated order identifier |
| `type` | enum | `arc_bsp_cash`, `balance`, `card`, or `airline_credit` |
| `status` | enum | `succeeded`, `failed`, `pending`, or `cancelled` |
| `amount` | string | Payment price (e.g., `"30.20"`) |
| `currency` | string | ISO 4217 code |
| `failure_reason` | string | Present when status is `failed` |
| `airline_credit_id` | string | Credit identifier if applicable |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `live_mode` | boolean | True if production, false if test mode |

---

## Endpoints

### List Payments

**GET** `https://api.duffel.com/air/payments`

Retrieves paginated payment records.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `order_id` | string | Yes | Filter by specific order ID |
| `limit` | integer | No | Records per page (1-200, default: 50) |
| `after` | string | No | Pagination cursor |
| `before` | string | No | Pagination cursor |

#### Response Example

```json
{
  "meta": {
    "limit": 50,
    "after": "g2wAAAACbQAAABBBZXJvbWlzdC1LaGFya2l2bQAAAB="
  },
  "data": [
    {
      "id": "pay_00009hthhsUZ8W4LxQgkjo",
      "order_id": "ord_00009hthhsUZ8W4LxQgkjo",
      "type": "balance",
      "status": "succeeded",
      "amount": "30.20",
      "currency": "GBP",
      "created_at": "2020-04-11T15:48:11.642Z",
      "live_mode": false
    }
  ]
}
```

---

### Create Payment

**POST** `https://api.duffel.com/air/payments`

Creates a payment for a `hold` order. Must complete before `payment_required_by` deadline.

#### Request Body

```json
{
  "data": {
    "order_id": "ord_00003x8pVDGcS8y2AWCoWv",
    "payment": {
      "type": "balance",
      "amount": "30.20",
      "currency": "GBP"
    }
  }
}
```

#### Payment Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | Yes | `arc_bsp_cash`, `balance`, or `card` |
| `amount` | string | Yes | Total order plus services amount |
| `currency` | string | Yes | ISO 4217 code matching order currency |
| `three_d_secure_session_id` | string | No | Required for card payments |

#### Validation Errors

| Field | Code | Issue |
|-------|------|-------|
| `order_id` | `order_type_not_eligible_for_payment` | Not a hold order |
| `amount` | `payment_amount_does_not_match_order_amount` | Amount mismatch |
| `currency` | `payment_currency_does_not_match_order_currency` | Currency mismatch |

#### Invalid States

| Error | Description |
|-------|-------------|
| `already_paid` | Order already paid |
| `already_cancelled` | Order cancelled |
| `past_payment_required_by_date` | Deadline passed |
| `schedule_changed` | Airline-side changes detected |

---

### Get Single Payment

**GET** `https://api.duffel.com/air/payments/{id}`

Retrieves a payment by its identifier.

#### URL Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Payment ID |

---

## Payment Types

| Type | Description |
|------|-------------|
| `balance` | Duffel wallet balance |
| `card` | Credit/debit card payment |
| `arc_bsp_cash` | IATA agent cash payment |
| `airline_credit` | Airline credit voucher |

## Payment Status

| Status | Description |
|--------|-------------|
| `pending` | Payment in progress |
| `succeeded` | Payment completed |
| `failed` | Payment failed |
| `cancelled` | Payment cancelled |

## Common Failure Reasons

| Reason | Description |
|--------|-------------|
| `insufficient_balance` | Wallet lacks funds |
| `payment_declined` | Card rejected |
| `ineligible_airline_credit` | Credit not applicable |

---

## Required Headers

All requests require:
```
Authorization: Bearer <YOUR_ACCESS_TOKEN>
Duffel-Version: v2
Accept: application/json
Content-Type: application/json
```

## Example: Pay for Hold Order

```python
import requests

url = "https://api.duffel.com/air/payments"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

payload = {
    "data": {
        "order_id": "ord_00003x8pVDGcS8y2AWCoWv",
        "payment": {
            "type": "balance",
            "amount": "90.80",
            "currency": "GBP"
        }
    }
}

response = requests.post(url, json=payload, headers=headers)
payment = response.json()["data"]
print(f"Payment status: {payment['status']}")
```
