# Pagination Documentation

## Overview

The Duffel API implements cursor-based pagination for list endpoints. List endpoints return a limited number of results per request, with navigation controlled through query parameters.

## Default Behavior

By default, the API returns 50 results per page, but you can set this to any number between 1 and 200 using the `?limit` query parameter.

Example request with custom limit:
```
https://api.duffel.com/air/airports?limit=200
```

## Response Structure

Each list response includes a `meta` object containing pagination information:

```json
{
  "meta": {
    "after": "g2wAAAACbQAAABBBZXJvbWlzdC1LaGFya2l2bQAAAB=",
    "before": null,
    "limit": 50
  },
  "data": [...]
}
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `limit` | Number of results per page (1-200, default: 50) |
| `after` | Cursor token for fetching the next page of results |
| `before` | Cursor token for previous page (nullable) |

## Navigation Logic

- When `meta.after` is `null`, no additional results exist
- When `meta.after` contains a value, results remain available beyond the current page
- To retrieve the next page, append `?after=${meta.after}` to the request URL
- Repeat this process until `meta.after` returns `null`

## Example: Paginating Through Results

```python
import requests

def get_all_airports(api_key):
    all_airports = []
    url = "https://api.duffel.com/air/airports"
    params = {"limit": 200}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Duffel-Version": "v2",
        "Accept": "application/json"
    }

    while True:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        all_airports.extend(data.get("data", []))

        after_cursor = data.get("meta", {}).get("after")
        if after_cursor is None:
            break

        params["after"] = after_cursor

    return all_airports
```

## Supported Endpoints

This pagination approach applies to all list APIs, including:
- List offer requests
- List airports
- List airlines
- List orders
- List bookings
