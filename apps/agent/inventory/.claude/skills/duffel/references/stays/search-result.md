# Search Result API Documentation

## Overview

A search result represents a pending availability for accommodation on specified check-in and check-out dates.

## Schema

### Search Result Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (e.g., `srr_0000ASVBuJVLdmqtZDJ4ca`) |
| `accommodation` | object | Associated accommodation details |
| `check_in_date` | date | ISO 8601 check-in date |
| `check_out_date` | date | ISO 8601 check-out date |
| `expires_at` | datetime | ISO 8601 expiration timestamp |
| `rooms` | integer | Number of rooms required |
| `guests` | array | List of traveling guests |
| `cheapest_rate_total_amount` | string | Best-effort price (can change) |
| `cheapest_rate_currency` | string | ISO 4217 currency code |
| `cheapest_rate_base_amount` | string (nullable) | Base amount |
| `cheapest_rate_public_amount` | string (nullable) | Public price comparison |
| `cheapest_rate_due_at_accommodation_amount` | string (nullable) | Due at check-in |
| `supported_negotiated_rates` | array | Negotiated rates used |

---

## Fetch Rates for a Search Result

### Endpoint

```
POST https://api.duffel.com/stays/search_results/{search_result_id}/actions/fetch_all_rates
```

### URL Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search_result_id` | string | Yes | Search result ID |

### Request Headers

```
Accept-Encoding: gzip
Accept: application/json
Content-Type: application/json
Duffel-Version: v2
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

### Response

Returns complete room and rate information including:

- All available room types with bed configurations
- Complete rate details with pricing breakdowns
- Cancellation policies and timelines
- Loyalty program support
- Payment methods and conditions
- Deal types and special rates

---

## Example: Fetch All Rates

```python
import requests

# After getting search results, fetch detailed rates
search_result_id = "srr_0000ASVBuJVLdmqtZDJ4ca"
url = f"https://api.duffel.com/stays/search_results/{search_result_id}/actions/fetch_all_rates"

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers)
data = response.json()["data"]

# Access all rooms and rates
accommodation = data["accommodation"]
for room in accommodation["rooms"]:
    print(f"Room: {room['name']}")
    for rate in room["rates"]:
        print(f"  Rate: {rate['total_amount']} - {rate['board_type']}")
        print(f"  Cancellation: {rate.get('cancellation_timeline', [])}")
```

---

## Response Example

```json
{
  "data": {
    "id": "srr_0000ASVBuJVLdmqtZDJ4ca",
    "accommodation": {
      "id": "acc_0000AWr2VsUNIF1Vl91xg0",
      "name": "Duffel Test Hotel",
      "rooms": [
        {
          "name": "Double Suite",
          "beds": [{"type": "king", "count": 2}],
          "rates": [
            {
              "id": "rat_0000BTVRuKZTavzrZDJ4cb",
              "total_amount": "799.00",
              "base_amount": "665.83",
              "tax_amount": "133.17",
              "board_type": "room_only",
              "payment_type": "pay_now",
              "cancellation_timeline": [
                {
                  "before": "2025-05-30T12:00:00Z",
                  "refund_amount": "799.00",
                  "refund_type": "full"
                }
              ],
              "expires_at": "2025-01-01T12:30:00Z"
            }
          ]
        }
      ]
    }
  }
}
```

## Notes

- `cheapest_rate_total_amount` is a best-effort computation during search; always fetch rates for accurate pricing
- Search results expire - check `expires_at` before proceeding
- Rate IDs are required for creating quotes
