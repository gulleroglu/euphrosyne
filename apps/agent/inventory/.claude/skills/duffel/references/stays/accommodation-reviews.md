# Accommodation Reviews API Documentation

## Overview

The Accommodation Reviews API provides access to guest reviews of their accommodation experiences through Duffel's stays platform.

## Base Endpoint

```
https://api.duffel.com/stays/accommodation/{id}/reviews
```

---

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `created_at` | string | ISO 8601 date when review was submitted |
| `reviewer_name` | string | Guest's name ("Anonymous" when unavailable) |
| `score` | number | Rating on 1.0-10.0 scale |
| `text` | string | Review content from the traveler |

---

## Endpoint

### Get Accommodation Reviews

**Method:** `GET`
**Endpoint:** `/stays/accommodation/{id}/reviews`

#### URL Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Accommodation identifier |

#### Query Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `limit` | integer | 50 | 1-200 | Records per page |
| `after` | string | - | - | Pagination cursor |
| `before` | string | - | - | Pagination cursor |

#### Example

```python
import requests

accommodation_id = "acc_0000AWr2VsUNIF1Vl91xg0"
url = f"https://api.duffel.com/stays/accommodation/{accommodation_id}/reviews"

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

params = {"limit": 10}

response = requests.get(url, params=params, headers=headers)
data = response.json()["data"]

for review in data["reviews"]:
    print(f"{review['reviewer_name']}: {review['score']}/10")
    print(f"  {review['text'][:100]}...")
```

#### Response

```json
{
  "meta": {
    "limit": 50,
    "after": "g2wAAAACbQAAABBBZXJvbWlzdC1LaGFya2l2bQAAAB="
  },
  "data": {
    "reviews": [
      {
        "text": "Excellent facilities. Polite staff.\nAir conditioning could use some maintenance.\n",
        "score": 8.4,
        "reviewer_name": "Bessie Coleman",
        "created_at": "2025-01-01"
      }
    ]
  }
}
```

---

## Notes

- Reviews are paginated using cursor-based pagination
- Score ranges from 1.0 (lowest) to 10.0 (highest)
- Anonymous reviews show "Anonymous" as `reviewer_name`
- Use reviews alongside `review_score` and `review_count` from accommodation data

