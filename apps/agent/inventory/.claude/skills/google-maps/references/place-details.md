# Place Details (New) - Google Places API Documentation

## Overview

The Place Details API retrieves comprehensive information about a specific location using its unique place ID. According to the documentation, "The Place Details API returns comprehensive information about a place, such as its address, phone number, ratings, and reviews, using a unique place ID."

## Obtaining Place IDs

Place IDs can be acquired through several methods:
- Text Search (New)
- Nearby Search (New)
- Geocoding API
- Routes API
- Address Validation API
- Place Autocomplete (New)

## Request Format

### Basic Request Structure

```
GET https://places.googleapis.com/v1/places/PLACE_ID
```

### Example with curl

```bash
curl -X GET -H 'Content-Type: application/json' \
-H "X-Goog-Api-Key: API_KEY" \
-H "X-Goog-FieldMask: id,displayName" \
https://places.googleapis.com/v1/places/ChIJj61dQgK6j4AR4GeTYWZsKWw
```

## Required Parameters

### FieldMask (Required)

A response field mask specifies which data fields to return. Pass it via:
- URL parameter: `$fields` or `fields`
- HTTP header: `X-Goog-FieldMask`

**Example:**
```
X-Goog-FieldMask: displayName,formattedAddress
```

**Important:** The documentation states "There is no default list of returned fields in the response. If you omit the field mask, the method returns an error."

Use wildcard to retrieve all fields:
```
X-Goog-FieldMask: *
```

### Place ID (Required)

A unique textual identifier returned from search operations. The resource name format is `places/PLACE_ID`.

## Optional Parameters

### languageCode
Specifies the language for returned results. Defaults to `en` if omitted.

### regionCode
Two-character CLDR code for response formatting. Affects whether country names appear in `formattedAddress`.

### sessionToken
User-generated string tracking Autocomplete sessions for billing purposes. Pass tokens from Autocomplete into subsequent Place Details calls.

## Field Categories & Billing SKUs

### Essentials IDs Only SKU
- `attributions`
- `id`
- `moved_place`
- `moved_place_id`
- `name`
- `photos`

### Essentials SKU
- `addressComponents`
- `addressDescriptor`
- `adrFormatAddress`
- `formattedAddress`
- `location`
- `plusCode`
- `postalAddress`
- `shortFormattedAddress`
- `types`
- `viewport`

### Pro SKU
- `accessibilityOptions`
- `businessStatus`
- `containingPlaces`
- `displayName`
- `googleMapsLinks`
- `googleMapsUri`
- `iconBackgroundColor`
- `iconMaskBaseUri`
- `primaryType`
- `primaryTypeDisplayName`
- `pureServiceAreaBusiness`
- `subDestinations`
- `utcOffsetMinutes`

### Enterprise SKU
- `currentOpeningHours`
- `currentSecondaryOpeningHours`
- `internationalPhoneNumber`
- `nationalPhoneNumber`
- `priceLevel`
- `priceRange`
- `rating`
- `regularOpeningHours`
- `regularSecondaryOpeningHours`
- `userRatingCount`
- `websiteUri`

### Enterprise + Atmosphere SKU
- `allowsDogs`
- `curbsidePickup`
- `delivery`
- `dineIn`
- `editorialSummary`
- `evChargeAmenitySummary`
- `evChargeOptions`
- `fuelOptions`
- `generativeSummary`
- `goodForChildren`
- `goodForGroups`
- `goodForWatchingSports`
- `liveMusic`
- `menuForChildren`
- `neighborhoodSummary`
- `parkingOptions`
- `paymentOptions`
- `outdoorSeating`
- `reservable`
- `restroom`
- `reviews`
- `reviewSummary`
- `routingSummaries`
- `servesBeer`
- `servesBreakfast`
- `servesBrunch`
- `servesCocktails`
- `servesCoffee`
- `servesDessert`
- `servesDinner`
- `servesLunch`
- `servesVegetarianFood`
- `servesWine`
- `takeout`

## Response Format

Responses return a `Place` object in JSON format:

```json
{
  "name": "places/ChIJkR8FdQNB0VQRm64T_lv1g1g",
  "id": "ChIJkR8FdQNB0VQRm64T_lv1g1g",
  "displayName": {
    "text": "Trinidad"
  }
}
```

## Example Responses

### Basic Example

**Request:**
```bash
curl -X GET -H 'Content-Type: application/json' \
-H "X-Goog-Api-Key: API_KEY" \
-H "X-Goog-FieldMask: id,displayName" \
https://places.googleapis.com/v1/places/ChIJj61dQgK6j4AR4GeTYWZsKWw
```

**Response:**
```json
{
  "id": "ChIJj61dQgK6j4AR4GeTYWZsKWw",
  "displayName": {
    "text": "Googleplex",
    "languageCode": "en"
  }
}
```

### Extended Example with Address

**Request:**
```bash
curl -X GET -H 'Content-Type: application/json' \
-H "X-Goog-Api-Key: API_KEY" \
-H "X-Goog-FieldMask: id,displayName,formattedAddress,plusCode" \
https://places.googleapis.com/v1/places/ChIJj61dQgK6j4AR4GeTYWZsKWw
```

**Response:**
```json
{
  "id": "ChIJj61dQgK6j4AR4GeTYWZsKWw",
  "formattedAddress": "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA",
  "plusCode": {
    "globalCode": "849VCWC7+RW",
    "compoundCode": "CWC7+RW Mountain View, CA, USA"
  },
  "displayName": {
    "text": "Googleplex",
    "languageCode": "en"
  }
}
```

## Special Features

### Address Descriptors

Address descriptors provide relational information about a location, including nearby landmarks and containing areas. This feature is "generally available for customers in India and are experimental elsewhere."

**Request:**
```bash
curl -X GET https://places.googleapis.com/v1/places/ChIJ8WvuSB7Lj4ARFyHppkxDRQ4 \
-H 'Content-Type: application/json' \
-H "X-Goog-Api-Key: API_KEY" \
-H "X-Goog-FieldMask: name,displayName,addressDescriptor"
```

Response includes landmarks array (with name, placeId, displayName, types, spatialRelationship, straightLineDistanceMeters) and areas array (with containment relationships).

### Moved Places

When a business location has permanently closed or relocated, the API returns relevant information:

```json
{
  "id": "ChIJUfQdGInVzkwRzAjmjzWB7CQ",
  "businessStatus": "CLOSED_PERMANENTLY",
  "displayName": {
    "text": "Marche IGA St-Canut",
    "languageCode": "en"
  },
  "movedPlace": "places/ChIJ36QT7n8qz0wRDqVZ_UBlUlQ",
  "movedPlaceId": "ChIJ36QT7n8qz0wRDqVZ_UBlUlQ"
}
```

For multiple relocations, chain Place Details requests using the `movedPlace` field from each response until reaching the current location (indicated by absence of `movedPlace` in response).
