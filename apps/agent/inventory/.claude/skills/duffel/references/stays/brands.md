# Brands API Documentation

## Overview

The Brands API provides information about hotel brands supported by Duffel Stays, allowing you to retrieve brand details and list all available brands.

## Base Endpoint

```
https://api.duffel.com/stays/brands
```

---

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the brand |
| `name` | string | Name of the brand |

---

## Endpoints

### 1. List Brands

**Method:** `GET`
**Endpoint:** `/stays/brands`

Retrieves all brands supported by Duffel Stays.

#### Example

```python
import requests

url = "https://api.duffel.com/stays/brands"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
brands = response.json()["data"]

for brand in brands:
    print(f"{brand['name']} ({brand['id']})")
```

#### Response

```json
{
  "data": [
    {
      "name": "Duffel Test",
      "id": "bra_0000Alr8BYNsbmDMThHSbI"
    }
  ]
}
```

---

### 2. Get Brand

**Method:** `GET`
**Endpoint:** `/stays/brands/{id}`

Retrieves details for a specific brand by ID.

#### URL Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Brand identifier |

#### Response

```json
{
  "data": {
    "name": "Duffel Test",
    "id": "bra_0000Alr8BYNsbmDMThHSbI"
  }
}
```

---

## Notes

- Brand IDs can be used to filter accommodations
- Brands are associated with accommodations via the `brand` field

