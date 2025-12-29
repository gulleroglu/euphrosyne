# Retrieve a List of Hotels

Search and retrieve hotel listings based on various criteria.

## Endpoint

```
GET https://api.liteapi.travel/v3.0/data/hotels
```

## Overview

Get hotel metadata including names, addresses, ratings, amenities, and images for display in your application.

## When to Use

- **Hotel listings** - Display hotel search results
- **Location-based search** - Find hotels by city, coordinates, or Place ID
- **Hotel discovery** - Browse hotels in specific areas
- **Metadata retrieval** - Get hotel information for display

## What You Get

- **Hotel list** - Matching hotels with complete metadata
- **Basic information** - Names, addresses, ratings, and locations
- **Amenities** - Available facilities and features
- **Images** - Hotel photos for display
- **Identifiers** - Hotel IDs for use in rate searches

## Search Options

| Method | Description |
|--------|-------------|
| By city | Search hotels in a specific city |
| By coordinates | Find hotels near latitude/longitude with radius |
| By Place ID | Get hotels within a specific place boundary |
| By hotel IDs | Retrieve specific hotels by their IDs |
| By AI search | Semantic search using natural language |

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `countryCode` | string | No | Country code ISO-2 (e.g., "ES") |
| `cityName` | string | No | Name of the city |
| `hotelName` | string | No | Hotel name (loose match, case-insensitive) |
| `hotelIds` | string | No | Comma-separated list of hotel IDs |
| `latitude` | number | No | Latitude coordinate |
| `longitude` | number | No | Longitude coordinate |
| `radius` | integer | No | Radius in meters (min 1000m) |
| `aiSearch` | string | No | Semantic search query |
| `offset` | integer | No | Number of rows to skip |
| `limit` | integer | No | Max results (default: 200, max: 5000) |
| `minRating` | float | No | Minimum rating (e.g., 8.6) |
| `minReviewsCount` | number | No | Minimum number of reviews |
| `starRating` | string | No | Comma-separated star ratings (e.g., "3.5,4.0,5.0") |
| `facilityIds` | string | No | Comma-separated facility IDs |
| `hotelTypeIds` | string | No | Comma-separated hotel type IDs |
| `chainIds` | string | No | Comma-separated chain IDs |
| `placeId` | string | No | Place ID for location search |
| `zip` | string | No | ZIP code |
| `language` | string | No | Language code (e.g., "fr") |
| `timeout` | float | No | Request timeout in seconds |

## Example Request

```python
import requests
import os

api_key = os.environ.get('LITEAPI_API_KEY')
url = "https://api.liteapi.travel/v3.0/data/hotels"

params = {
    "countryCode": "ES",
    "cityName": "Barcelona",
    "limit": 10
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
      "id": "lp42fec",
      "name": "Hotel Jadran",
      "hotelDescription": "Location description and amenities...",
      "currency": "EUR",
      "country": "HR",
      "city": "Sibenik",
      "latitude": 43.73464,
      "longitude": 15.88974,
      "address": "Obala dr. Franje Tudmana 52",
      "zip": "22000",
      "main_photo": "https://liteapi-travel-static-data.s3.amazonaws.com/images/hotels/main/274412.jpg",
      "thumbnail": "https://liteapi-travel-static-data.s3.amazonaws.com/images/hotels/main/274412.jpg",
      "hotelTypeId": 204,
      "chainId": 0,
      "chain": "Not Available",
      "stars": 3,
      "facilityIds": [1, 2, 3]
    }
  ],
  "hotelIds": ["lp42fec"],
  "total": 1004
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique hotel identifier |
| `name` | string | Hotel name |
| `hotelDescription` | string | Full description |
| `country` | string | Country code |
| `city` | string | City name |
| `latitude` | number | Latitude coordinate |
| `longitude` | number | Longitude coordinate |
| `address` | string | Street address |
| `zip` | string | Postal code |
| `main_photo` | string | Main photo URL |
| `thumbnail` | string | Thumbnail URL |
| `stars` | number | Star rating |
| `facilityIds` | array | List of facility IDs |

## Responses

| Code | Description |
|------|-------------|
| 200 | OK - Success |
| 400 | Bad Request |
| 401 | Unauthorized |
