# Get the Details of a Hotel

Get comprehensive details about a specific hotel.

## Endpoint

```
GET https://api.liteapi.travel/v3.0/data/hotel
```

## Overview

Retrieve complete hotel information including descriptions, amenities, images, location, and ratings. Perfect for displaying hotel detail pages.

## When to Use

- **Hotel detail pages** - Show complete hotel information
- **Booking pages** - Display hotel details before booking
- **Hotel profiles** - Build rich hotel information pages
- **Content display** - Show descriptions, amenities, and images

## What You Get

- **Complete hotel information** - Name, address, description, and ratings
- **Amenities list** - All available facilities and services
- **Image gallery** - Hotel photos and images
- **Location details** - Address, coordinates, and location information
- **Room information** - Room types with amenities and photos
- **Policies** - Check-in/out times, pet policies, parking info
- **Sentiment analysis** - AI-analyzed pros/cons from reviews

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `hotelId` | string | **Yes** | Unique ID of the hotel |
| `timeout` | float | No | Request timeout in seconds (default: 4) |
| `language` | string | No | Language code (e.g., "fr") |
| `advancedAccessibilityOnly` | boolean | No | Return accessibility section |

## Example Request

```python
import requests
import os

api_key = os.environ.get('LITEAPI_API_KEY')
url = "https://api.liteapi.travel/v3.0/data/hotel"

params = {
    "hotelId": "lp1897",
    "timeout": 4
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
  "data": {
    "id": "lp1897",
    "name": "The Manhattan at Times Square",
    "hotelDescription": "<p><strong>Central Manhattan Location</strong>...</p>",
    "hotelImportantInformation": "Guests are required to show photo ID...",
    "checkinCheckoutTimes": {
      "checkout": "11:00 AM",
      "checkin": "04:00 PM",
      "checkinStart": "04:00 PM"
    },
    "hotelImages": [
      {
        "url": "https://static.cupid.travel/hotels/524489007.jpg",
        "urlHd": "https://static.cupid.travel/hotels/524489007.jpg",
        "caption": "",
        "order": 0,
        "defaultImage": true
      }
    ],
    "main_photo": "https://static.cupid.travel/hotels/524489007.jpg",
    "country": "us",
    "city": "New York",
    "starRating": 4,
    "location": {
      "latitude": 40.76217,
      "longitude": -73.98306
    },
    "address": "790 7th Avenue",
    "hotelFacilities": [
      "Fitness facilities",
      "Non-smoking rooms",
      "Air conditioning",
      "Pets allowed",
      "Lift / Elevator"
    ],
    "rooms": [
      {
        "id": 2617264,
        "roomName": "Standard Room",
        "description": "The double room includes a private bathroom...",
        "roomSizeSquare": 23,
        "roomSizeUnit": "m2",
        "maxAdults": 2,
        "maxChildren": 1,
        "maxOccupancy": 2,
        "bedTypes": [],
        "roomAmenities": [
          {"amenitiesId": 293, "name": "Safety deposit box"},
          {"amenitiesId": 339, "name": "TV"},
          {"amenitiesId": 11, "name": "Air conditioning"}
        ],
        "photos": [
          {"url": "https://static.cupid.travel/rooms-large-pictures/592392806.jpg"}
        ]
      }
    ],
    "rating": 5.6,
    "reviewCount": 6536,
    "hotelType": "Hotels",
    "policies": [
      {
        "policy_type": "POLICY_HOTEL_PARKING",
        "name": "Parking",
        "description": "Public parking costs USD 72 per day."
      }
    ],
    "sentiment_analysis": {
      "pros": ["Location", "Friendly staff", "Near Times Square"],
      "cons": ["Limited parking", "Expensive breakfast"],
      "categories": [
        {"name": "Location", "rating": 8.3, "description": "..."},
        {"name": "Service", "rating": 7.6, "description": "..."}
      ]
    }
  }
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Hotel ID |
| `name` | string | Hotel name |
| `hotelDescription` | string | Full HTML description |
| `hotelImportantInformation` | string | Important guest info |
| `checkinCheckoutTimes` | object | Check-in/out times |
| `hotelImages` | array | All hotel photos |
| `main_photo` | string | Primary photo URL |
| `starRating` | number | Star rating (1-5) |
| `location` | object | Lat/long coordinates |
| `address` | string | Street address |
| `hotelFacilities` | array | Facility names |
| `rooms` | array | Room types with details |
| `rating` | number | Guest rating |
| `reviewCount` | number | Total reviews |
| `policies` | array | Hotel policies |
| `sentiment_analysis` | object | AI-analyzed review insights |

## Responses

| Code | Description |
|------|-------------|
| 200 | OK - Success |
| 400 | Bad Request |
| 401 | Unauthorized |
