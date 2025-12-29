# Nearby Search (New) - Google Places API Documentation

## Overview

The Nearby Search (New) feature enables location-based place discovery across multiple platforms. This API accepts POST requests to find places based on geographic location and type filters.

## API Endpoint

```
https://places.googleapis.com/v1/places:searchNearby
```

**Request Method:** POST only

## Required Parameters

### FieldMask
Controls which data fields return in responses. This parameter significantly impacts billing costs.

**Specification methods:**
- URL parameter: `$fields` or `fields`
- HTTP header: `X-Goog-FieldMask`

**Example:**
```
X-Goog-FieldMask: places.displayName,places.formattedAddress
```

**Field Categories by SKU:**

**Nearby Search Pro SKU fields:**
- Basic info: `displayName`, `id`, `name`, `types`, `location`
- Address data: `formattedAddress`, `shortFormattedAddress`, `postalAddress`, `addressComponents`, `adrFormatAddress`
- Additional: `photos`, `plusCode`, `viewport`, `googleMapsUri`, `businessStatus`, `utcOffsetMinutes`

**Nearby Search Enterprise SKU fields:**
- Contact: `nationalPhoneNumber`, `internationalPhoneNumber`, `websiteUri`
- Reviews: `rating`, `userRatingCount`
- Hours: `regularOpeningHours`, `currentOpeningHours`
- Pricing: `priceLevel`, `priceRange`

**Nearby Search Enterprise + Atmosphere SKU fields:**
- Amenities: `allowsDogs`, `restroom`, `parkingOptions`, `outdoorSeating`
- Services: `delivery`, `dineIn`, `takeout`, `curbsidePickup`, `reservable`
- Food attributes: `servesBeer`, `servesWine`, `servesCoffee`, `servesBreakfast`, `servesDessert`
- Content: `reviews`, `editorialSummary`, `generativeSummary`

### locationRestriction
Defines the search radius using a circular boundary.

**Required specifications:**
- Center point: `latitude` and `longitude`
- Radius: 0.0 to 50,000.0 meters (default: 0.0, must be > 0.0)

**Example:**
```json
"locationRestriction": {
  "circle": {
    "center": {
      "latitude": 37.7937,
      "longitude": -122.3965
    },
    "radius": 500.0
  }
}
```

## Optional Parameters

### Type Filtering

**includedTypes / excludedTypes:**
- Filter by any place types (up to 50 each)
- A place can have multiple type associations
- Example: restaurant with types `"seafood_restaurant"`, `"restaurant"`, `"food"`

**includedPrimaryTypes / excludedPrimaryTypes:**
- Filter by primary type only (one per place)
- Example primary types: `"mexican_restaurant"`, `"steak_house"`

**Type interaction rules:**
- When specifying a general type like `"restaurant"`, results may include more specific subtypes
- Combining filters: "When you specify `includedTypes` and `excludedPrimaryTypes`, returned places provide the included services but do not operate primarily as the excluded type"

### languageCode
Specifies result language. Defaults to `en` if omitted.

**Behavior:**
- Street addresses return in local language, transliterated if needed
- Other addresses use preferred language
- Uses closest match if preferred language unavailable

### maxResultCount
Number of results to return (1-20 inclusive). Default: 20.

### rankPreference
Result sorting option:
- `POPULARITY` (default): Orders by popularity
- `DISTANCE`: Ascending order by distance from specified location

### regionCode
Two-character CLDR code controlling address formatting. Omits country code from `formattedAddress` when country matches region code.

## Request Examples

### Basic Restaurant Search
```bash
curl -X POST -d '{
  "includedTypes": ["restaurant"],
  "maxResultCount": 10,
  "locationRestriction": {
    "circle": {
      "center": {
        "latitude": 37.7937,
        "longitude": -122.3965
      },
      "radius": 500.0
    }
  }
}' \
-H 'Content-Type: application/json' \
-H "X-Goog-Api-Key: API_KEY" \
-H "X-Goog-FieldMask: places.displayName" \
https://places.googleapis.com/v1/places:searchNearby
```

### Multiple Types with Extended Data
```bash
curl -X POST -d '{
  "includedTypes": ["liquor_store", "convenience_store"],
  "maxResultCount": 10,
  "locationRestriction": {
    "circle": {
      "center": {
        "latitude": 37.7937,
        "longitude": -122.3965
      },
      "radius": 1000.0
    }
  }
}' \
-H 'Content-Type: application/json' \
-H "X-Goog-Api-Key: API_KEY" \
-H "X-Goog-FieldMask: places.displayName,places.primaryType,places.types" \
https://places.googleapis.com/v1/places:searchNearby
```

### Type Exclusion with Distance Ranking
```bash
curl -X POST -d '{
  "includedTypes": ["school"],
  "excludedTypes": ["primary_school"],
  "maxResultCount": 10,
  "locationRestriction": {
    "circle": {
      "center": {
        "latitude": 37.7937,
        "longitude": -122.3965
      },
      "radius": 1000.0
    }
  },
  "rankPreference": "DISTANCE"
}' \
-H 'Content-Type: application/json' \
-H "X-Goog-Api-Key: API_KEY" \
-H "X-Goog-FieldMask: places.displayName" \
https://places.googleapis.com/v1/places:searchNearby
```

### Address Descriptors (Landmarks & Areas)
```bash
curl -X POST -d '{
  "maxResultCount": 5,
  "locationRestriction": {
    "circle": {
      "center": {
        "latitude": 37.321328,
        "longitude": -121.946275
      },
      "radius": 1000
    }
  },
  "includedTypes": ["restaurant", "cafe"],
  "rankPreference": "POPULARITY"
}' \
-H 'Content-Type: application/json' \
-H "X-Goog-Api-Key: API_KEY" \
-H "X-Goog-FieldMask: places.displayName,places.addressDescriptor" \
https://places.googleapis.com/v1/places:searchNearby
```

## Response Format

```json
{
  "places": [
    {
      "displayName": {
        "text": "Place Name",
        "languageCode": "en"
      },
      "formattedAddress": "Address",
      "types": ["type1", "type2"],
      "websiteUri": "https://example.com"
    }
  ]
}
```

The `places` array contains all matching results. Each place object follows the `Place` resource schema, with returned fields determined by the FieldMask specification.

## Regional Compliance Note

For European Economic Area developers, effective July 8, 2025, the Google Maps Platform EEA Terms of Service apply.
