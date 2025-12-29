# Get the Reviews of a Hotel

Retrieve guest reviews and ratings for a specific hotel.

## Endpoint

```
GET https://api.liteapi.travel/v3.0/data/reviews
```

## Overview

Display authentic feedback from previous guests to help users make informed booking decisions.

## When to Use

- **Review display** - Show guest reviews on hotel detail pages
- **Rating aggregation** - Display average ratings and review counts
- **Trust building** - Show authentic guest feedback
- **Decision support** - Help users evaluate hotels before booking

## What You Get

- **Guest reviews** - Individual review text and ratings
- **Review dates** - When each review was written
- **Ratings** - Numerical and textual ratings
- **Guest feedback** - Detailed comments from previous guests
- **Sentiment analysis** - AI-powered analysis of reviews (optional)

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `hotelId` | string | **Yes** | Unique ID of the hotel |
| `limit` | integer | No | Max results (default: 200, max: 5000) |
| `offset` | integer | No | Number of reviews to skip (default: 0) |
| `timeout` | float | No | Request timeout in seconds (default: 4) |
| `getSentiment` | boolean | No | Return AI sentiment analysis (default: false) |
| `language` | string | No | ISO 639-1 code to translate reviews (max 10 when used) |

## Example Request

```python
import requests
import os

api_key = os.environ.get('LITEAPI_API_KEY')
url = "https://api.liteapi.travel/v3.0/data/reviews"

params = {
    "hotelId": "lp1897",
    "limit": 10,
    "getSentiment": True
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
      "averageScore": 8,
      "country": "ps",
      "type": "solo traveller",
      "name": "Hala",
      "date": "2026-07-16 07:52:57",
      "headline": "Very good",
      "language": "en",
      "pros": "",
      "cons": "",
      "source": "Nuitee"
    },
    {
      "averageScore": 8,
      "country": "ma",
      "type": "solo traveller",
      "name": "Saharian.prince",
      "date": "2026-07-15 15:24:22",
      "headline": "Very good",
      "language": "en",
      "pros": "Great location, good people, good prices and a nice breakfast included.",
      "cons": "Construction site nearby and slow wifi.",
      "source": "Tripadvisor"
    }
  ],
  "total": 10
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `averageScore` | number | Review score (0-10) |
| `country` | string | Reviewer's country code |
| `type` | string | Traveler type (e.g., "solo traveller", "family") |
| `name` | string | Reviewer name |
| `date` | string | Review date |
| `headline` | string | Review headline/title |
| `language` | string | Review language |
| `pros` | string | Positive feedback |
| `cons` | string | Negative feedback |
| `source` | string | Review source (e.g., "Tripadvisor") |

## Sentiment Analysis Response

When `getSentiment=true`, the response includes AI-analyzed insights:

```json
{
  "sentiment_analysis": {
    "pros": ["Location", "Friendly staff", "Clean rooms"],
    "cons": ["Limited parking", "Expensive breakfast"],
    "categories": [
      {
        "name": "Location",
        "rating": 8.3,
        "description": "Great proximity to attractions"
      },
      {
        "name": "Service",
        "rating": 7.6,
        "description": "Friendly and helpful staff"
      }
    ]
  }
}
```

## Responses

| Code | Description |
|------|-------------|
| 200 | OK - List of hotel reviews |
| 400 | Bad Request |
| 401 | Unauthorized |
