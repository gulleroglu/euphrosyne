# Order Changes API Documentation

## Overview

Once you've created an order change request, and you've chosen which slices to add and remove, you'll then want to create an order change.

To initiate a change, provide the order change offer ID. Payment is required if `change_total_amount` exceeds zero; refunds are issued when the amount is negative.

---

## Schema

### Order Change Object

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Duffel's unique identifier |
| `order_id` | string | Identifier for the order being modified |
| `change_total_amount` | string | Amount charged or refunded (negative = refund) |
| `change_total_currency` | string | ISO 4217 currency code |
| `new_total_amount` | string | Final order price post-change |
| `new_total_currency` | string | ISO 4217 currency code |
| `penalty_total_amount` | string | Airline charge for the modification |
| `penalty_total_currency` | string | ISO 4217 currency code |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `confirmed_at` | datetime | ISO 8601 confirmation timestamp (nullable) |
| `expires_at` | datetime | Deadline for confirmation |
| `refund_to` | enum | `voucher` or `original_form_of_payment` |
| `slices` | object | Slices being added/removed from order |
| `live_mode` | boolean | True if created in live mode |

---

## Endpoints

### 1. Create Pending Order Change

**POST** `https://api.duffel.com/air/order_changes`

#### Request Body
```json
{
  "data": {
    "selected_order_change_offer": "oco_0000A4QasEUIjJ6jHKfhHU"
  }
}
```

#### Response
Returns an OrderChange object with pending status.

---

### 2. Confirm Order Change

**POST** `https://api.duffel.com/air/order_changes/{id}/actions/confirm`

#### URL Parameters
| Parameter | Type | Required |
|-----------|------|----------|
| `id` | string | Yes |

#### Request Body
```json
{
  "data": {
    "payment": {
      "type": "balance",
      "currency": "GBP",
      "amount": "30.20"
    }
  }
}
```

**Note:** Payment object is optional if `change_total_amount` is zero or negative.

---

### 3. Get Single Order Change

**GET** `https://api.duffel.com/air/order_changes/{id}`

---

## Example Response

```json
{
  "data": {
    "id": "ocr_0000A3tQSmKyqOrcySrGbo",
    "order_id": "ord_0000A3tQcCRZ9R8OY0QlxA",
    "change_total_amount": "30.50",
    "change_total_currency": "GBP",
    "new_total_amount": "121.30",
    "new_total_currency": "GBP",
    "penalty_total_amount": "15.50",
    "penalty_total_currency": "GBP",
    "created_at": "2020-04-11T15:48:11.642Z",
    "confirmed_at": "2020-01-17T11:51:43.114803Z",
    "expires_at": "2020-01-17T10:42:14.545052Z",
    "refund_to": "voucher",
    "live_mode": false,
    "slices": {
      "remove": [],
      "add": []
    }
  }
}
```

---

## Complete Change Flow

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

# Step 1: Create pending order change
url = "https://api.duffel.com/air/order_changes"
payload = {
    "data": {
        "selected_order_change_offer": "oco_0000A4QasEUIjJ6jHKfhHU"
    }
}
response = requests.post(url, json=payload, headers=headers)
order_change = response.json()["data"]

print(f"Change amount: {order_change['change_total_amount']}")
print(f"Expires: {order_change['expires_at']}")

# Step 2: Confirm the change (with payment if required)
if float(order_change['change_total_amount']) > 0:
    confirm_url = f"{url}/{order_change['id']}/actions/confirm"
    payment_payload = {
        "data": {
            "payment": {
                "type": "balance",
                "amount": order_change['change_total_amount'],
                "currency": order_change['change_total_currency']
            }
        }
    }
    response = requests.post(confirm_url, json=payment_payload, headers=headers)
else:
    # No payment needed for refund/zero change
    confirm_url = f"{url}/{order_change['id']}/actions/confirm"
    response = requests.post(confirm_url, headers=headers)

confirmed = response.json()["data"]
print(f"Confirmed at: {confirmed['confirmed_at']}")
```

## Notes

- All timestamps use ISO 8601 format
- Currencies follow ISO 4217 standard
- Payment is mandatory only when `change_total_amount > 0`
- Changes must be confirmed before the `expires_at` deadline
