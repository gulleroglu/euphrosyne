# Search Hotels by Semantic Query (Beta)

Search hotels using natural language queries with AI-powered semantic matching.

## Endpoint

```
GET https://api.liteapi.travel/v3.0/data/hotels/semantic-search
```

## Overview

This beta feature uses AI to understand search intent and find hotels that match the meaning, not just keywords. Perfect for conversational and intent-based hotel discovery.

## When to Use

- **Natural language search** - Let users search with phrases like "romantic getaway in London"
- **Intent-based matching** - Find hotels matching the vibe or style, not just location
- **Conversational search** - Support natural language hotel discovery
- **Semantic matching** - Get hotels that semantically match the query

## What You Get

- **Matching hotels** - Hotels that semantically match your query
- **Semantic attributes** - Tags, persona, style, location_type, and story for each hotel
- **Relevance scores** - How well each hotel matches the query
- **Hotel metadata** - ID, name, photos, address, city, country

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | **Yes** | Natural language search query |
| `limit` | integer | No | Max results (default: 3) |
| `min_rating` | float | No | Minimum hotel rating (default: 0) |

## Example Queries

- "Romantic getaway in London with Italian vibes"
- "Hotels near Paris"
- "Family-friendly beachfront hotels"
- "Boutique hotel in Amsterdam for business travelers"
- "Luxury spa resort in the mountains"

## Example Request

```python
import requests
import os

api_key = os.environ.get('LITEAPI_API_KEY')
url = "https://api.liteapi.travel/v3.0/data/hotels/semantic-search"

params = {
    "query": "romantic getaway in London with Italian vibes",
    "limit": 5,
    "min_rating": 8.0
}

headers = {
    "accept": "application/json",
    "X-API-Key": api_key
}

response = requests.get(url, params=params, headers=headers)
data = response.json()
print(data)
```

## Example Response

```json
{
  "data": [
    {
      "id": "lp5d8a7",
      "name": "Point Pleasant Inn & Resort",
      "main_photo": "https://example.com/hotel-photo.jpg",
      "address": "123 Main Street",
      "city": "Bristol",
      "country": "US",
      "tags": [
        "boutique hotel",
        "coastal retreat",
        "historic charm",
        "waterfront views",
        "romantic getaway"
      ],
      "score": 0.7,
      "persona": "Discerning Couple",
      "style": "Classic Elegance",
      "location_type": "Waterfront Estate",
      "story": "Historic waterfront inn offering an exclusive and tranquil escape near local cultural attractions."
    }
  ]
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Hotel identifier |
| `name` | string | Hotel name |
| `main_photo` | string | Primary photo URL |
| `address` | string | Street address |
| `city` | string | City name |
| `country` | string | Country code |
| `tags` | array | Semantic tags describing the hotel |
| `score` | number | Relevance score (0-1) |
| `persona` | string | Target guest persona |
| `style` | string | Hotel style/aesthetic |
| `location_type` | string | Type of location |
| `story` | string | AI-generated description |

## Responses

| Code | Description |
|------|-------------|
| 200 | OK - Success |
| 400 | Bad Request |
| 500 | Internal Server Error |

> **Note:** This is a beta feature and may be subject to changes.
