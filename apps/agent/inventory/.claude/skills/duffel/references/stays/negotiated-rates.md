# Negotiated Rates API Documentation

## Overview

The Negotiated Rates API enables passing rate access codes for specific accommodation to Duffel sources, allowing customized pricing for stays bookings.

## Base Endpoint

```
https://api.duffel.com/stays/negotiated_rates
```

---

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Negotiated Rate identifier |
| `display_name` | string | Display name of the negotiated rate |
| `rate_access_code` | string | Rate access code for this negotiated rate |
| `accommodation_ids` | string[] | Accommodation IDs this rate is valid for |
| `live_mode` | boolean | Whether for live mode (false = test mode) |

---

## Endpoints

### 1. Create Negotiated Rate

**Method:** `POST`
**Endpoint:** `/stays/negotiated_rates`

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `rate_access_code` | string | Access code for the rate |
| `display_name` | string | Display name |
| `accommodation_ids` | string[] | Valid accommodation IDs |

#### Example

```python
import requests

url = "https://api.duffel.com/stays/negotiated_rates"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

payload = {
    "data": {
        "rate_access_code": "DUFFEL",
        "display_name": "2025 Negotiated Rate",
        "accommodation_ids": ["acc_0000AWr2VsUNIF1Vl91xg0"]
    }
}

response = requests.post(url, json=payload, headers=headers)
rate = response.json()["data"]
print(f"Created: {rate['id']}")
```

---

### 2. List Negotiated Rates

**Method:** `GET`
**Endpoint:** `/stays/negotiated_rates`

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Records per page (1-200) |
| `after` | string | - | Pagination cursor |
| `before` | string | - | Pagination cursor |

---

### 3. Get Negotiated Rate

**Method:** `GET`
**Endpoint:** `/stays/negotiated_rates/{id}`

#### URL Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Negotiated Rate ID |

---

### 4. Update Negotiated Rate

**Method:** `PATCH`
**Endpoint:** `/stays/negotiated_rates/{id}`

#### Modifiable Fields

| Parameter | Type | Description |
|-----------|------|-------------|
| `display_name` | string | New display name |
| `accommodation_ids` | string[] | Updated accommodation IDs |

**Note:** `rate_access_code` and `live_mode` are immutable.

---

### 5. Delete Negotiated Rate

**Method:** `DELETE`
**Endpoint:** `/stays/negotiated_rates/{id}`

Returns the deleted negotiated rate object.

---

## Example Response

```json
{
  "data": {
    "id": "nre_0000AvtkNoC81yBytDM9PE",
    "display_name": "2025 Negotiated Rate",
    "rate_access_code": "DUFFEL",
    "accommodation_ids": ["acc_0000AWr2VsUNIF1Vl91xg0"],
    "live_mode": true
  }
}
```

