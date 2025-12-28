# Duffel API Reference

## Overview

Duffel provides a unified API for flights and accommodation booking.

- **Base URL**: `https://api.duffel.com`
- **API Version**: v2
- **Auth**: Bearer token (`DUFFEL_API_KEY`)

## Flight Offer Requests

### Create Offer Request

**Endpoint**: `POST /air/offer_requests`

**Request Body**:
```json
{
  "data": {
    "slices": [
      {
        "origin": "JFK",
        "destination": "CDG",
        "departure_date": "2025-03-15"
      }
    ],
    "passengers": [
      {"type": "adult"},
      {"type": "adult"}
    ],
    "cabin_class": "economy",
    "max_connections": 1
  }
}
```

**Response**:
```json
{
  "data": {
    "id": "orq_xxx",
    "offers": [
      {
        "id": "off_xxx",
        "total_amount": "684.00",
        "total_currency": "USD",
        "slices": [
          {
            "origin": {"iata_code": "JFK"},
            "destination": {"iata_code": "CDG"},
            "duration": "PT7H15M",
            "segments": [...]
          }
        ]
      }
    ]
  }
}
```

### Cabin Classes
- `economy`
- `premium_economy`
- `business`
- `first`

### Passenger Types
- `adult` (12+ years)
- `child` (2-11 years)
- `infant_without_seat` (0-2 years)

## Stays API

### Search Stays

**Endpoint**: `POST /stays/search`

**Request Body**:
```json
{
  "data": {
    "location": {
      "geographic_coordinates": {
        "latitude": 48.8566,
        "longitude": 2.3522
      },
      "radius": 10
    },
    "check_in_date": "2025-03-15",
    "check_out_date": "2025-03-20",
    "rooms": 1,
    "guests": [
      {"type": "adult"},
      {"type": "adult"}
    ]
  }
}
```

**Response**:
```json
{
  "data": {
    "results": [
      {
        "id": "acc_xxx",
        "name": "Hotel Example",
        "rating": 4,
        "address": {
          "line_1": "123 Example St",
          "city": "Paris",
          "country_code": "FR"
        },
        "amenities": ["wifi", "pool", "gym"],
        "rates": [
          {
            "id": "rat_xxx",
            "total_amount": "1500.00",
            "total_currency": "EUR",
            "cancellation_policy": {
              "free_cancellation": true,
              "free_cancellation_before": "2025-03-13"
            }
          }
        ]
      }
    ]
  }
}
```

## Error Handling

### Error Response Format
```json
{
  "errors": [
    {
      "code": "invalid_request",
      "message": "Origin airport not found",
      "type": "validation_error"
    }
  ]
}
```

### Common Error Codes
- `invalid_request` - Request validation failed
- `authentication_failed` - Invalid API key
- `rate_limit_exceeded` - Too many requests
- `not_found` - Resource not found

## Rate Limits

- 100 requests per minute per API key
- 429 response when exceeded
- Use exponential backoff for retries

## Documentation

Full API docs: https://duffel.com/docs/api
