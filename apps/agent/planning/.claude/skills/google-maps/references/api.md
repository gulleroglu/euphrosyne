# Google Maps API Reference

## Overview

Google Maps Platform provides APIs for maps, places, and routes.

- **Base URL**: `https://maps.googleapis.com/maps/api`
- **Auth**: API key parameter (`key=YOUR_API_KEY`)

## Places API

### Text Search

**Endpoint**: `GET /place/textsearch/json`

**Parameters**:
- `query` (required): Search query
- `location`: Latitude,longitude
- `radius`: Search radius in meters (max 50000)
- `type`: Place type filter
- `key`: API key

**Response**:
```json
{
  "status": "OK",
  "results": [
    {
      "place_id": "ChIJxyz...",
      "name": "Louvre Museum",
      "formatted_address": "Rue de Rivoli, 75001 Paris, France",
      "geometry": {
        "location": {"lat": 48.8606, "lng": 2.3376}
      },
      "rating": 4.7,
      "user_ratings_total": 150234,
      "price_level": 2,
      "opening_hours": {"open_now": true},
      "types": ["museum", "tourist_attraction", "point_of_interest"]
    }
  ]
}
```

### Place Types
- `tourist_attraction`
- `museum`
- `restaurant`
- `cafe`
- `bar`
- `park`
- `church`
- `art_gallery`
- `shopping_mall`
- `airport`
- `train_station`

## Directions API

**Endpoint**: `GET /directions/json`

**Parameters**:
- `origin` (required): Starting point
- `destination` (required): End point
- `mode`: driving, walking, bicycling, transit
- `departure_time`: Unix timestamp (for transit)
- `alternatives`: true/false
- `key`: API key

**Response**:
```json
{
  "status": "OK",
  "routes": [
    {
      "summary": "A1",
      "legs": [
        {
          "distance": {"text": "25.3 km", "value": 25300},
          "duration": {"text": "45 mins", "value": 2700},
          "start_address": "CDG Airport",
          "end_address": "Hotel, Paris",
          "steps": [
            {
              "html_instructions": "Head south on...",
              "distance": {"text": "0.5 km", "value": 500},
              "duration": {"text": "5 mins", "value": 300},
              "travel_mode": "DRIVING",
              "transit_details": {...}
            }
          ]
        }
      ]
    }
  ]
}
```

## Distance Matrix API

**Endpoint**: `GET /distancematrix/json`

**Parameters**:
- `origins` (required): Pipe-separated origins
- `destinations` (required): Pipe-separated destinations
- `mode`: Travel mode
- `key`: API key

**Response**:
```json
{
  "status": "OK",
  "origin_addresses": ["Hotel, Paris"],
  "destination_addresses": ["Louvre Museum", "Eiffel Tower"],
  "rows": [
    {
      "elements": [
        {
          "status": "OK",
          "distance": {"text": "2.5 km", "value": 2500},
          "duration": {"text": "30 mins", "value": 1800}
        },
        {
          "status": "OK",
          "distance": {"text": "4.2 km", "value": 4200},
          "duration": {"text": "50 mins", "value": 3000}
        }
      ]
    }
  ]
}
```

## Error Handling

### Status Values
- `OK` - Request successful
- `ZERO_RESULTS` - No results found
- `OVER_QUERY_LIMIT` - Quota exceeded
- `REQUEST_DENIED` - Invalid API key or disabled API
- `INVALID_REQUEST` - Missing required parameters

### Rate Limits
- Varies by API and billing account
- Use exponential backoff for retries

## Documentation

Full API docs: https://developers.google.com/maps/documentation
