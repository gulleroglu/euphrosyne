# Order Cancellations API Documentation

## Overview

The Order Cancellations API allows you to cancel flight orders and receive refund information. The workflow requires creating a pending cancellation first, then confirming it to finalize the cancellation with the airline.

**Key principle:** You can only confirm the most recent order cancellation that you have created for an order.

---

## Schema

### Order Cancellation Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (e.g., `ore_00009qzZWzjDipIkqpaUAj`) |
| `order_id` | string | Associated order identifier |
| `refund_amount` | string/null | Amount returned to original payment method |
| `refund_currency` | string/null | ISO 4217 currency code |
| `refund_to` | enum | Destination: `arc_bsp_cash`, `balance`, `card`, `voucher`, `awaiting_payment`, `airline_credits` |
| `airline_credits` | array | Generated or prospective airline credits |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `confirmed_at` | datetime/null | ISO 8601 confirmation timestamp |
| `expires_at` | datetime/null | Deadline to confirm cancellation |
| `live_mode` | boolean | Whether created in production or test mode |

---

## API Endpoints

### 1. List Order Cancellations

**Endpoint:** `GET https://api.duffel.com/air/order_cancellations`

**Query Parameters:**
- `order_id` (string): Filter by specific order
- `limit` (integer): Records per page, default 50, max 200
- `after`, `before` (string): Pagination cursors

---

### 2. Create Pending Order Cancellation

**Endpoint:** `POST https://api.duffel.com/air/order_cancellations`

**Request Body:**
```json
{
  "data": {
    "order_id": "ord_001"
  }
}
```

**Response:**
Returns the pending cancellation with calculated refund details.

---

### 3. Get Single Order Cancellation

**Endpoint:** `GET https://api.duffel.com/air/order_cancellations/{id}`

**URL Parameters:**
- `id` (string, required): Cancellation identifier

---

### 4. Confirm Order Cancellation

**Endpoint:** `POST https://api.duffel.com/air/order_cancellations/{id}/actions/confirm`

**URL Parameters:**
- `id` (string, required): Cancellation identifier

**Effect:** Finalizes cancellation with airline; refund applied to original payment method.

---

## Cancellation Flow

```
1. Create pending cancellation → Get refund quote
2. Review refund amount and destination
3. Confirm cancellation → Execute with airline
4. Refund customer from your balance
```

## Refund Destinations

| Destination | Description |
|-------------|-------------|
| `arc_bsp_cash` | IATA agent cash |
| `balance` | Duffel wallet balance |
| `card` | Original payment card |
| `voucher` | Travel voucher |
| `awaiting_payment` | Hold order not yet paid |
| `airline_credits` | Airline credit voucher |

## Example: Cancel an Order

```python
import requests

# Step 1: Create pending cancellation
url = "https://api.duffel.com/air/order_cancellations"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

payload = {
    "data": {
        "order_id": "ord_00009hthhsUZ8W4LxQgkjo"
    }
}

response = requests.post(url, json=payload, headers=headers)
cancellation = response.json()["data"]

print(f"Refund amount: {cancellation['refund_amount']} {cancellation['refund_currency']}")
print(f"Expires at: {cancellation['expires_at']}")

# Step 2: Confirm cancellation
confirm_url = f"{url}/{cancellation['id']}/actions/confirm"
response = requests.post(confirm_url, headers=headers)
confirmed = response.json()["data"]

print(f"Confirmed at: {confirmed['confirmed_at']}")
```

## Notes

- Refund amounts may be null when airline data is unavailable
- Always check `expires_at` before confirming
- Cancellation cannot be reversed once confirmed
