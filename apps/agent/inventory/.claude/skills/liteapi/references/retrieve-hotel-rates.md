# Retrieve Rates for Hotels

Search for hotel rates and availability with real-time pricing.

## Endpoint

```
POST https://api.liteapi.travel/v3.0/hotels/rates
```

## Overview

This is your primary endpoint for finding bookable hotel rooms with real-time pricing. Search across multiple hotels and get detailed rate information including cancellation policies, meal plans, and room types.

## When to Use

- Display hotel listings with prices on search results page
- Show detailed rate options for specific hotels
- Support multi-room bookings for families or groups
- Filter hotels by location, amenities, ratings, or AI-powered semantic search

## What You Get

- **Real-time rates** with availability and pricing
- **Multiple room options** per hotel, sorted by price
- **Complete booking details** including cancellation policies, meal plans, and room types
- **Hotel information** (name, photos, address, ratings) when searching by filters

## Key Features

- **Multiple search methods**: Search by hotel IDs, city/country, coordinates, Place ID, IATA code, or natural language (AI search)
- **Flexible filtering**: Filter by star rating, facilities, hotel chains, accessibility, and more
- **Multi-room support**: Book multiple rooms with different guest configurations in one request
- **Performance optimized**: Default limit of 200 hotels (expandable to 5,000), recommended timeout of 6-12 seconds

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `checkin` | string | Check-in date (YYYY-MM-DD) |
| `checkout` | string | Check-out date (YYYY-MM-DD) |
| `currency` | string | Currency code (e.g., "USD", "EUR") |
| `guestNationality` | string | Guest nationality (ISO 2-letter code) |
| `occupancies` | array | Guest configuration per room |

**Plus one of these location methods:**
- `hotelIds` - Array of hotel IDs
- `countryCode` + `cityName` - City search
- `latitude` + `longitude` + `radius` - Coordinate search
- `placeId` - Place ID search
- `iataCode` - Airport/city code search
- `aiSearch` - Natural language search

## Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `timeout` | integer | Max seconds before timeout (default: 10) |
| `maxRatesPerHotel` | integer | Rates per hotel (1 = cheapest only) |
| `boardType` | string | Filter by meal plan (RO, BB, HB, etc.) |
| `refundableRatesOnly` | boolean | Only show refundable rates |
| `sort` | array | Sorting criteria |
| `roomMapping` | boolean | Enable room mapping |
| `limit` | integer | Max results (default: 200, max: 5000) |
| `offset` | integer | Pagination offset |
| `minRating` | number | Minimum guest rating |
| `minReviewsCount` | integer | Minimum review count |
| `starRating` | array | Filter by star ratings |
| `hotelTypeIds` | array | Filter by hotel types |
| `chainIds` | array | Filter by hotel chains |
| `facilities` | array | Filter by facility IDs |
| `includeHotelData` | boolean | Include hotel metadata |

## Occupancy Object

```json
{
  "adults": 2,
  "children": [5, 8]
}
```

## Example Request

```python
import requests
import os

api_key = os.environ.get('LITEAPI_API_KEY')
url = "https://api.liteapi.travel/v3.0/hotels/rates"

payload = {
    "checkin": "2026-01-15",
    "checkout": "2026-01-20",
    "currency": "EUR",
    "guestNationality": "US",
    "occupancies": [
        {"adults": 2, "children": []}
    ],
    "countryCode": "ES",
    "cityName": "Barcelona",
    "limit": 10,
    "timeout": 10,
    "includeHotelData": True
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
      "hotelId": "lp1897",
      "hotel": {
        "name": "The Manhattan at Times Square",
        "main_photo": "https://...",
        "address": "790 7th Avenue",
        "rating": 5.6
      },
      "roomTypes": [
        {
          "roomTypeId": "GQ2TOLJWGI...",
          "offerId": "GE5ESNBSIZ...",
          "supplier": "nuitee",
          "rates": [
            {
              "rateId": "I42FUVCPJZ...",
              "occupancyNumber": 1,
              "name": "Standard King Room",
              "maxOccupancy": 2,
              "adultCount": 2,
              "childCount": 0,
              "boardType": "RO",
              "boardName": "Room Only",
              "retailRate": {
                "total": [{"amount": 163.66, "currency": "USD"}],
                "suggestedSellingPrice": [{"amount": 191.52, "currency": "USD"}],
                "taxesAndFees": [
                  {"included": true, "description": "City Tax", "amount": 7.87}
                ]
              },
              "cancellationPolicies": {
                "cancelPolicyInfos": [
                  {
                    "cancelTime": "2026-07-30 02:00:00",
                    "amount": 163.66,
                    "currency": "USD",
                    "type": "amount"
                  }
                ],
                "refundableTag": "RFN"
              },
              "paymentTypes": ["NUITEE_PAY", "PROPERTY_PAY"]
            }
          ],
          "offerRetailRate": {"amount": 163.66, "currency": "USD"}
        }
      ]
    }
  ],
  "sandbox": true
}
```

## Board Types

| Code | Description |
|------|-------------|
| `RO` | Room Only |
| `BB` | Bed & Breakfast |
| `HB` | Half Board |
| `FB` | Full Board |
| `AI` | All Inclusive |

## Refundable Tags

| Tag | Description |
|-----|-------------|
| `RFN` | Refundable |
| `NRFN` | Non-Refundable |

## Responses

| Code | Description |
|------|-------------|
| 200 | OK - Success |
| 204 | No Content - No rates available |
| 400 | Bad Request |
