# Duffel API: Making Requests Documentation

## Overview

The Duffel API requires several foundational components for successful integration. All interactions demand an access token, specific headers, and JSON formatting.

## Authentication

Every API request requires an access token included in the `Authorization` header:

```
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

Access tokens are created via your dashboard and can be configured as either read-only or read-write depending on your needs.

## API Versioning

Include the `Duffel-Version` header with each request to specify which API version you're targeting:

```
Duffel-Version: v2
```

Refer to the dedicated Versioning documentation for comprehensive version management details.

## MIME Types & Content Headers

**For responses:** The API returns JSON with UTF-8 encoding. Include this required header:

```
Accept: application/json
```

**For requests:** When sending request bodies (POST/PUT operations), specify:

```
Content-Type: application/json
```

## Required Headers Summary

```python
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

## Response Compression

To enable compression for large responses, send:

```
Accept-Encoding: gzip
```

Most HTTP clients automatically decompress responses with this configuration enabled.

## Tracking & Debugging

**Request ID:** All responses include an `x-request-id` header for unique request identification. Save this for support interactions.

**Client Correlation ID:** Optionally send `x-client-correlation-id` to track requests using your own identifiers. When omitted, it defaults to matching the `x-request-id` value.

## Example Request

```python
import requests

url = "https://api.duffel.com/air/offer_requests"

headers = {
    "Authorization": "Bearer duffel_live_xxx",
    "Duffel-Version": "v2",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

payload = {
    "data": {
        "slices": [
            {
                "origin": "LHR",
                "destination": "JFK",
                "departure_date": "2025-05-01"
            }
        ],
        "passengers": [
            {"type": "adult"}
        ],
        "cabin_class": "economy"
    }
}

response = requests.post(url, json=payload, headers=headers)
```

## Base URL

All API requests should be made to:

```
https://api.duffel.com
```

## API Endpoints

### Flights
- `POST /air/offer_requests` - Search for flights
- `GET /air/offers/{id}` - Get offer details
- `POST /air/orders` - Create booking

### Stays
- `POST /stays/search` - Search for accommodations
- `GET /stays/search_results/{id}` - Get search results
- `POST /stays/quotes` - Create quote
- `POST /stays/bookings` - Create booking
