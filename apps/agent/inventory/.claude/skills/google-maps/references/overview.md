# Places API Overview

## Introduction

The Places API is a service that processes HTTP requests for location data through various methods. It returns formatted location data and imagery regarding establishments, geographic locations, or prominent points of interest.

**Note:** Google Maps Platform offers separate versions for Android, iOS, and JavaScript platforms. It's recommended to use the version specific to your development platform.

## Why Use Places API (New)

Create location-aware features to make detailed location data accessible to users. The data is built on one of the most accurate, up-to-date, and comprehensive place models available. Example use cases include:

- Display rental properties within major metropolitan areas with city-specific targeting
- Include place information in delivery status notifications
- Show parks in an area with user-submitted photos and reviews
- Provide trip planners with contact information, reviews, and pricing for establishments along routes

**Important:** Places API (New) is the current version. The legacy Places API is no longer available for new enablement.

## Capabilities

The Places API (New) enables the following features:

- **Place Search** - Results from different query types including text input, nearby locations, and categorical queries
- **Autocomplete** - Features for text queries or categorical search types
- **Detailed Information** - Customizable details including operating hours, summaries, reviews, and photos
- **Photo Integration** - High-quality images for locations

## How It Works

Places API (New) accepts standard URL requests with specific service endpoints like `/places` or `places:searchText`, returning JSON responses. It supports authorization via API key or OAuth tokens.

Example request:
```
https://places.googleapis.com/v1/places/[PLACE_ID]?fields=addressComponents&key=[YOUR_KEY]
```

## Getting Started Steps

1. **Setup** - Complete Google Cloud project setup and learn API key usage
2. **Text Search** - Issue a text search using Text Search (New)
3. **Place Details** - Use place IDs to retrieve Place Details (New)
4. **Photos** - Access Place Photos (New) for place imagery
