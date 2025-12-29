# Autocomplete (New) API Documentation

## Overview

"Autocomplete (New) is a web service that returns place predictions and query predictions in response to an HTTP request." It supports matching on full words, substrings, place names, addresses, and plus codes, enabling real-time suggestions as users type.

The service returns two prediction types:
- **Place predictions**: Businesses, addresses, and points of interest
- **Query predictions**: Alternative search terms (optional)

## Request Format

**Endpoint:** `https://places.googleapis.com/v1/places:autocomplete`

**Method:** HTTP POST with JSON body

Example request:
```json
{
  "input": "pizza",
  "locationBias": {
    "circle": {
      "center": {
        "latitude": 37.7937,
        "longitude": -122.3965
      },
      "radius": 500.0
    }
  }
}
```

## Required Parameters

| Parameter | Description |
|-----------|-------------|
| `input` | Text string for searching (full words, substrings, place names, addresses, plus codes) |

## Optional Parameters

| Parameter | Description |
|-----------|-------------|
| `includedPrimaryTypes` | Restrict results to up to five specified place types |
| `includePureServiceAreaBusinesses` | Include businesses without physical locations (true/false) |
| `includeQueryPredictions` | Include query predictions in response (true/false) |
| `includedRegionCodes` | Array of up to 15 country codes to limit results |
| `inputOffset` | Zero-based Unicode character offset for cursor position |
| `languageCode` | IETF BCP-47 language code for results |
| `locationBias` | Circle or rectangle area to bias results toward |
| `locationRestriction` | Circle or rectangle area to restrict results within |
| `origin` | Latitude/longitude for calculating distance to predictions |
| `regionCode` | ccTLD two-character code for response formatting |
| `sessionToken` | User string grouping calls into sessions for billing |
| `FieldMask` (HTTP Header) | Comma-separated fields to return |

## Location Definition Formats

**Circle:**
```json
{
  "circle": {
    "center": {
      "latitude": 37.7749,
      "longitude": -122.4194
    },
    "radius": 5000.0
  }
}
```

**Rectangle:**
```json
{
  "rectangle": {
    "low": {
      "latitude": 40.477398,
      "longitude": -74.259087
    },
    "high": {
      "latitude": 40.91618,
      "longitude": -73.70018
    }
  }
}
```

## Response Structure

```json
{
  "suggestions": [
    {
      "placePrediction": {
        "place": "places/ChIJ5YQQf1GHhYARPKG7WLIaOko",
        "placeId": "ChIJ5YQQf1GHhYARPKG7WLIaOko",
        "text": {
          "text": "Amoeba Music, Haight Street, San Francisco, CA, USA",
          "matches": [
            {
              "endOffset": 6
            }
          ]
        },
        "structuredFormat": {
          "mainText": {
            "text": "Amoeba Music",
            "matches": [{"endOffset": 6}]
          },
          "secondaryText": {
            "text": "Haight Street, San Francisco, CA, USA"
          }
        },
        "types": ["store", "establishment"],
        "distanceMeters": 3012
      }
    },
    {
      "queryPrediction": {
        "text": {
          "text": "Amoeba Music",
          "matches": [{"endOffset": 6}]
        }
      }
    }
  ]
}
```

## Key Constraints

- Maximum 5 total predictions returned (place or query combination)
- Query predictions unavailable when `includedRegionCodes` is set
- Cannot use both `locationBias` and `locationRestriction` simultaneously
- Circle radius must be 0.0-50000.0 meters; for restrictions, must exceed 0.0
- `distanceMeters` omitted for routes and distances under 1 meter

## Cost Optimization

Consider these approaches:

1. **Widget Implementation**: Use JavaScript, Android, or iOS widgets with built-in session management
2. **Programmatic with Sessions**: Use session tokens for grouped requests and Place Details calls
3. **Programmatic without Sessions**: Call Geocoding API instead if users select predictions within 4 requests average
4. **Delay Strategy**: Wait until 3-4 characters typed to reduce request volume

"Use field masks in Place Details (New) and Autocomplete (New) widgets to return only the fields you need."

## Performance Best Practices

- Add country restrictions and location biasing
- Bias to map viewport when accompanying a map display
- Fall back to Geocoding API when users reject all predictions
- Use Geocoding for subpremise addresses (apartments/units within buildings)
