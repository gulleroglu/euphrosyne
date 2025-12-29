# Place IDs Documentation

## Introduction

Place IDs uniquely identify locations in the Google Places database and across Google Maps. These identifiers are textual and variable in length, with no maximum limit.

**Example Place IDs:**
- `ChIJgUbEo8cfqokR5lP9_Wh_DaM`
- `GhIJQWDl0CIeQUARxks3icF8U8A`
- Long-form IDs for addresses and intersections

## Key Characteristics

- Available for most locations including businesses, landmarks, parks, and intersections
- "It is possible for the same place or location to have multiple different place IDs"
- May change over time due to database updates
- Can be reused across multiple Google Maps Platform APIs

## Finding Place IDs

You can locate a Place ID through:

1. **Place ID Finder tool** - Interactive search interface available in the documentation
2. **Places API searches** - Use Text Search (New) or Place Search (Legacy) requests
3. **Maps JavaScript API** - Places library search functionality

## Using Place IDs

Place IDs are accepted across these services:

- Geocoding API and Directions API
- Routes API and Distance Matrix API
- Places API (New and Legacy)
- Maps Embed API
- Maps URLs
- Roads API

## Retrieving Place Details

Once obtained, use a Place ID in a Details request to fetch comprehensive place information without repeating the original search.

## Storing Place IDs

"Place IDs are **exempt from** the caching restrictions" in the Terms of Service, allowing indefinite storage.

### Refreshing Stored IDs

Best practice: Refresh Place IDs older than 12 months by making a Place Details request with only the ID field specified—"at no charge."

## Error Codes

**`INVALID_REQUEST`**: The Place ID is malformed, truncated, or corrupted.

**`NOT_FOUND`**: The Place ID is obsolete, typically due to business closure, relocation, or database updates.

*Note: Obsolete IDs may briefly appear in autocomplete responses after removal from the database.*
