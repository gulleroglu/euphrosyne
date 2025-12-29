# Google Places API - Text Search (New) Documentation

## Overview

The Text Search (New) API enables searching for places based on text queries like "pizza in New York" or "shoe stores near Ottawa". The service returns a list of matching places with optional location biasing.

**Maximum Results:** Text Search returns up to 60 results across all pages.

## Request Format

**Endpoint:** `https://places.googleapis.com/v1/places:searchText`

**Method:** HTTP POST

**Example Request:**
```bash
curl -X POST -d '{
  "textQuery": "Spicy Vegetarian Food in Sydney, Australia"
}' \
-H 'Content-Type: application/json' \
-H 'X-Goog-Api-Key: API_KEY' \
-H 'X-Goog-FieldMask: places.displayName,places.formattedAddress,places.priceLevel' \
'https://places.googleapis.com/v1/places:searchText'
```

## Response Format

Returns a JSON object with a `places` array containing `Place` objects:

```json
{
  "places": [
    {
      "object (Place)"
    }
  ]
}
```

Each `Place` object contains details specified by the FieldMask.

## Required Parameters

### textQuery
The text string to search. Examples: "restaurant", "123 Main Street", "Best place to visit in San Francisco"

**Not intended for:**
- Ambiguous multi-concept queries
- Postal addresses with non-geographic elements (C/O, P.O. Box)
- Unavailable business names in locations
- Historical place names
- Coordinates in lat/long format

### FieldMask
Specifies returned data fields via `X-Goog-FieldMask` header or `$fields` URL parameter.

**Format:** `places.fieldName,places.anotherField`

**Wildcard:** Use `*` to retrieve all fields (discouraged in production)

**SKU Categories:**

| SKU | Fields |
|-----|--------|
| **Essentials ID Only** | `places.attributions`, `places.id`, `places.name`, `nextPageToken`, `places.movedPlace`, `places.movedPlaceId` |
| **Pro** | `places.accessibilityOptions`, `places.addressComponents`, `places.displayName`, `places.formattedAddress`, `places.location`, `places.photos`, `places.types`, `places.primaryType`, `places.viewport` (and others) |
| **Enterprise** | `places.currentOpeningHours`, `places.rating`, `places.priceLevel`, `places.websiteUri`, `places.nationalPhoneNumber` (and others) |
| **Enterprise + Atmosphere** | `places.reviews`, `places.allowsDogs`, `places.delivery`, `places.dineIn`, `places.editorialSummary`, `places.parkingOptions`, `places.reservable`, `places.takeout` (and others) |

## Optional Parameters

### includedType
Filters results to a specific place type. Only one type permitted. Examples: `"bar"`, `"pharmacy"`

**Note:** Type filtering may not apply to address-specific queries but typically applies to categorical ones.

### includePureServiceAreaBusinesses
Boolean. When `true`, includes businesses without physical locations (delivery services, mobile businesses).

### languageCode
Returns results in specified language. Defaults to `en` if not supplied.

### locationBias
Specifies a preferred search area (biases results but allows outside results).

**Circle format:**
```json
"locationBias": {
  "circle": {
    "center": {"latitude": 37.7937, "longitude": -122.3965},
    "radius": 500.0
  }
}
```

**Rectangle format:**
```json
"locationBias": {
  "rectangle": {
    "low": {"latitude": 40.477398, "longitude": -74.259087},
    "high": {"latitude": 40.91618, "longitude": -73.70018}
  }
}
```

### locationRestriction
Rectangular viewport restricting categorical queries to specified region (results must be within bounds).

### pageSize
Number of results per page (1-20). Defaults to 20. Returns `nextPageToken` for pagination.

### pageToken
Token from previous response's `nextPageToken` for accessing subsequent pages.

### priceLevels
Array of acceptable price levels: `PRICE_LEVEL_INEXPENSIVE`, `PRICE_LEVEL_MODERATE`, `PRICE_LEVEL_EXPENSIVE`, `PRICE_LEVEL_VERY_EXPENSIVE`

### rankPreference
For categorical queries, choose `RELEVANCE` (default) or `DISTANCE` ranking.

### regionCode
Two-character CLDR code affecting response formatting and search bias. Omits country name from `formattedAddress` when it matches region.

### strictTypeFiltering
Boolean. When `true` with `includedType`, only exact type matches returned.

### minRating
Filters to places with ratings >= this value (0.0-5.0, increments of 0.5).

### openNow
Boolean. When `true`, returns only currently open businesses.

### evOptions
EV charging filters:
- `connectorTypes`: Array of connector types (`EV_CONNECTOR_TYPE_J1772`, `EV_CONNECTOR_TYPE_TESLA`, etc.)
- `minimumChargingRateKw`: Minimum charging rate in kilowatts

## Examples

### Basic Search
```bash
curl -X POST -d '{
  "textQuery": "Spicy Vegetarian Food in Sydney, Australia"
}' \
-H 'Content-Type: application/json' \
-H 'X-Goog-Api-Key: API_KEY' \
-H 'X-Goog-FieldMask: places.displayName,places.formattedAddress' \
'https://places.googleapis.com/v1/places:searchText'
```

### Price Level Filtering
```bash
curl -X POST -d '{
  "textQuery": "Spicy Vegetarian Food in Sydney, Australia",
  "priceLevels": ["PRICE_LEVEL_INEXPENSIVE", "PRICE_LEVEL_MODERATE"]
}' \
-H 'X-Goog-FieldMask: places.displayName,places.priceLevel' \
...
```

### Location Restriction
```bash
curl -X POST -d '{
  "textQuery": "vegetarian food",
  "pageSize": 10,
  "locationRestriction": {
    "rectangle": {
      "low": {"latitude": 40.477398, "longitude": -74.259087},
      "high": {"latitude": 40.91618, "longitude": -73.70018}
    }
  }
}' \
...
```

### Location Bias with Circle
```bash
curl -X POST -d '{
  "textQuery": "vegetarian food",
  "openNow": true,
  "pageSize": 10,
  "locationBias": {
    "circle": {
      "center": {"latitude": 37.7937, "longitude": -122.3965},
      "radius": 500.0
    }
  }
}' \
...
```

### EV Charging Search
```bash
curl -X POST -d '{
  "textQuery": "EV Charging Station Mountain View",
  "pageSize": 4,
  "evOptions": {
    "minimumChargingRateKw": 10,
    "connectorTypes": ["EV_CONNECTOR_TYPE_J1772", "EV_CONNECTOR_TYPE_TESLA"]
  }
}' \
-H 'X-Goog-FieldMask: places.displayName,places.evChargeOptions' \
...
```

### Service Area Businesses
```bash
curl -X POST -d '{
  "textQuery": "plumber San Francisco",
  "includePureServiceAreaBusinesses": true
}' \
-H 'X-Goog-FieldMask: places.displayName,places.formattedAddress' \
...
```

### Pagination
**First page:**
```bash
curl -X POST -d '{
  "textQuery": "pizza in New York",
  "pageSize": 5
}' \
-H 'X-Goog-FieldMask: places.id,nextPageToken' \
...
```

**Next page (using token):**
```bash
curl -X POST -d '{
  "textQuery": "pizza in New York",
  "pageSize": 5,
  "pageToken": "AeCrKXsZWzNVbPzO-MRWPu52jWO_..."
}' \
...
```

## Key Constraints

- All parameters except `pageSize` and `pageToken` must remain consistent across paginated requests
- `locationBias` can be overridden by explicit locations in `textQuery`
- If neither `locationBias` nor `locationRestriction` specified, API defaults to IP-based biasing
- No spaces allowed in FieldMask lists
