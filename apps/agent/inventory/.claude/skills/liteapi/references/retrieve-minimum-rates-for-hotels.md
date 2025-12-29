# Retrieve Minimum Rate for Hotels

Get the cheapest available rate for each hotel in your list.

## Endpoint

```
POST https://api.liteapi.travel/v3.0/hotels/min-rates
```

## Overview

Perfect for displaying price comparisons without loading full rate details. Returns only the minimum rate per hotel for optimized performance.

## When to Use

- Show price ranges on hotel listing pages
- Quick price comparisons across multiple hotels
- Optimize performance when you only need the lowest price
- Build price filters or sorting by price

## What You Get

- **Minimum rate per hotel** - The cheapest available room option
- **Basic rate information** - Price, currency, and availability
- **Fast response** - Optimized for quick price lookups

## Key Features

- **Lightweight** - Returns only the minimum rate, not all options
- **Same parameters** as the main rates endpoint for consistency
- **Perfect for listings** - Ideal when displaying multiple hotels

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `hotelIds` | array | List of hotel IDs |
| `checkin` | string | Check-in date (YYYY-MM-DD) |
| `checkout` | string | Check-out date (YYYY-MM-DD) |
| `currency` | string | Currency code |
| `guestNationality` | string | Guest nationality (ISO 2-letter code) |
| `occupancies` | array | Guest configuration per room |

## Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `timeout` | number | Request timeout in seconds |

## Example Request

```python
import requests
import os

api_key = os.environ.get('LITEAPI_API_KEY')
url = "https://api.liteapi.travel/v3.0/hotels/min-rates"

payload = {
    "hotelIds": ["lp3803c", "lp1f982", "lp1897"],
    "checkin": "2026-01-15",
    "checkout": "2026-01-20",
    "currency": "USD",
    "guestNationality": "US",
    "occupancies": [
        {"adults": 2, "children": []}
    ],
    "timeout": 10
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API-Key": api_key
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()
print(data)
```

## Example Response

```json
{
  "data": [
    {
      "hotelId": "lp3803c",
      "price": 99.99,
      "suggestedSellingPrice": 120.99
    },
    {
      "hotelId": "lp1f982",
      "price": 200,
      "suggestedSellingPrice": 220
    }
  ],
  "sandbox": true
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `hotelId` | string | Hotel identifier |
| `price` | number | Minimum rate amount |
| `suggestedSellingPrice` | number | Suggested retail price |

## Responses

| Code | Description |
|------|-------------|
| 200 | OK - Success with minimum rates |
| 401 | Bad Request |
