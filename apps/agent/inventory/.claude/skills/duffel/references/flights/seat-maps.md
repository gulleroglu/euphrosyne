# Seat Maps API Documentation

## Overview

The Seat Maps endpoint enables customers to select aircraft seats during order creation. Seat maps provide detailed cabin layout data including seat availability, pricing, and restrictions.

**Key Limitations:**
- Seat selection only supported during order creation, not after
- Seat cancellation after booking is not supported
- Not available for all airlines

## Endpoint

```
GET https://api.duffel.com/air/seat_maps
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `offer_id` | string | Yes | Duffel's unique identifier for the offer |

### Request Example

```bash
curl -X GET --compressed "https://api.duffel.com/air/seat_maps?offer_id=off_00009htYpSCXrwaB9DnUm0" \
  -H "Accept-Encoding: gzip" \
  -H "Accept: application/json" \
  -H "Duffel-Version: v2" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

## Response Schema

### Root Object

| Field | Type | Description |
|-------|------|-------------|
| `data` | array | List of seat maps, one per segment |

### Seat Map Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Duffel's unique seat map identifier |
| `segment_id` | string | Associated segment identifier |
| `slice_id` | string | Associated slice identifier |
| `cabins` | array | List of cabin sections ordered by deck level |

### Cabin Object

| Field | Type | Description |
|-------|------|-------------|
| `cabin_class` | enum | "first", "business", "premium_economy", or "economy" |
| `deck` | integer | 0 (main) or 1 (upper deck) |
| `aisles` | integer | 1 or 2; determines section division |
| `rows` | array | Rows ordered front-to-back |
| `wings` | object | Wing position indices (nullable) |

### Row Object

| Field | Type | Description |
|-------|------|-------------|
| `sections` | array | Divided by aisles; contains elements |

### Seat Element

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | "seat" |
| `designator` | string | Row/column identifier (e.g., "14B") |
| `available_services` | array | Pricing data per passenger (empty = unavailable) |
| `disclosures` | array | Seat restrictions/conditions |
| `name` | string | Seat description (nullable) |

### Seat Service Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Service identifier |
| `passenger_id` | string | Associated passenger |
| `total_amount` | string | Price including taxes |
| `total_currency` | string | ISO 4217 currency code |

### Other Element Types

| Type | Description |
|------|-------------|
| `bassinet` | Child's cradle |
| `empty` | Padding space |
| `exit_row` | Wide area near exits |
| `lavatory` | Passenger restroom |
| `galley` | Food preparation area |
| `closet` | Storage compartment |
| `stairs` | Multi-deck access |
| `restricted_seat_general` | Booking-restricted seat |

## Example Response

```json
{
  "data": [
    {
      "id": "sea_00003hthlsHZ8W4LxXjkzo",
      "segment_id": "seg_00009htYpSCXrwaB9Dn456",
      "slice_id": "sli_00009htYpSCXrwaB9Dn123",
      "cabins": [
        {
          "cabin_class": "economy",
          "deck": 0,
          "aisles": 2,
          "rows": [
            {
              "sections": [
                {
                  "elements": [
                    {
                      "type": "seat",
                      "designator": "1A",
                      "available_services": [
                        {
                          "id": "ase_00009UhD4ongolulWAAA1A",
                          "passenger_id": "pas_00009hj8USM7Ncg31cAAA",
                          "total_amount": "30.00",
                          "total_currency": "GBP"
                        }
                      ],
                      "disclosures": []
                    }
                  ]
                }
              ]
            }
          ],
          "wings": {
            "first_row_index": 1,
            "last_row_index": 2
          }
        }
      ]
    }
  ]
}
```

## Important Notes

- Each passenger can select one seat per segment maximum
- Multiple passengers cannot select the same seat
- Seat selection is optional per passenger
- Total order cost = offer price + selected seat services

## Display Recommendations

- Use consistent static width for seats, empty spaces, and bassinets
- Other elements should fill available space, center-aligned
- Display letters on individual seats rather than column headers
