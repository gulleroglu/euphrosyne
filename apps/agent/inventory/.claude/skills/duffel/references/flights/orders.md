# Duffel Orders API Documentation

## Overview

The Orders API enables flight booking management after selecting an offer. Orders require offer ID, payment details, and passenger information.

## Schema

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Duffel's unique identifier (e.g., `ord_00009hthhsUZ8W4LxQgkjo`) |
| `booking_reference` | string | Airline's PNR reference |
| `type` | enum | `"instant"` or `"hold"` |
| `total_amount` | string | Total price including taxes |
| `total_currency` | string | ISO 4217 currency code |
| `base_amount` | string (nullable) | Price excluding taxes |
| `tax_amount` | string (nullable) | Tax amount |
| `payment_status` | object | Payment info: `awaiting_payment`, `paid_at`, `payment_required_by` |
| `available_actions` | string[] | Possible actions: `"cancel"`, `"change"`, `"update"` |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `synced_at` | datetime | Last sync with airline |
| `slices` | list | Flight segments |
| `passengers` | list | Traveling passengers |
| `services` | list | Booked services (seats, baggage) |
| `void_window_ends_at` | datetime (nullable) | Full refund deadline |
| `live_mode` | boolean | Production or test mode |
| `metadata` | object (nullable) | Custom key-value pairs |

---

## List Orders

**Endpoint:** `GET https://api.duffel.com/air/orders`

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Records per page (1-200, default 50) |
| `after` | string | Pagination cursor |
| `before` | string | Pagination cursor |
| `booking_reference` | string | Filter by exact PNR |
| `offer_id` | string | Filter by offer ID |
| `awaiting_payment` | boolean | Filter by payment status |
| `sort` | enum | Sort by field (prefix `-` for descending) |
| `owner_id[]` | string[] | Filter by airline IDs |
| `origin_id[]` | string[] | Filter by origin |
| `destination_id[]` | string[] | Filter by destination |
| `departing_at` | object | Filter by departure datetime |
| `arriving_at` | object | Filter by arrival datetime |
| `created_at` | object | Filter by creation datetime |
| `passenger_name[]` | string[] | Filter by passenger names |
| `requires_action` | boolean | Filter orders with pending changes |

---

## Create an Order

**Endpoint:** `POST https://api.duffel.com/air/orders`

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `selected_offers` | string[] | ✓ | Single offer ID to book |
| `passengers` | list | ✓ | Passenger details |
| `payments` | list | ✓* | Payment details (omit for hold) |
| `type` | enum | | `"instant"` (default) or `"hold"` |
| `services` | list | | Services to add |
| `metadata` | object | | Custom key-value pairs |

*Required for instant orders; omit for hold orders

### Passenger Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Passenger ID from offer |
| `given_name` | string | ✓ | First name |
| `family_name` | string | ✓ | Last name |
| `email` | string | ✓ | Email address |
| `born_on` | string | ✓ | Date of birth (YYYY-MM-DD) |
| `title` | string | | mr, mrs, ms, miss, dr |
| `gender` | string | | m or f |
| `phone_number` | string | | E.164 format |

### Payment Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | ✓ | `balance`, `card`, `arc_bsp_cash` |
| `amount` | string | ✓ | Payment amount |
| `currency` | string | ✓ | ISO 4217 code |

### Request Example

```bash
curl -X POST "https://api.duffel.com/air/orders" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Duffel-Version: v2" \
  -d '{
    "data": {
      "type": "instant",
      "selected_offers": ["off_00009htyDGjIfajdNBZRlw"],
      "passengers": [
        {
          "id": "pas_00009hj8USM7Ncg31cBCLL",
          "given_name": "Amelia",
          "family_name": "Earhart",
          "email": "amelia@example.com",
          "born_on": "1987-07-24",
          "title": "mrs",
          "gender": "f",
          "phone_number": "+442080160509"
        }
      ],
      "payments": [
        {
          "type": "balance",
          "amount": "90.80",
          "currency": "GBP"
        }
      ]
    }
  }'
```

---

## Get Single Order

**Endpoint:** `GET https://api.duffel.com/air/orders/{id}`

Returns full order details including booking reference, itinerary, and payment status.

---

## Update Order

**Endpoint:** `PATCH https://api.duffel.com/air/orders/{id}`

Update metadata on an existing order.

---

## Key Notes

- Airlines limit orders to ≤ 9 passengers
- Show full operating carrier name for each segment during confirmation
- Orders sync with airline systems; `synced_at` within 1 minute = current
- Metadata supports operational tracking (max 50 pairs, 40 char keys, 500 char values)

## Order Types

| Type | Description |
|------|-------------|
| `instant` | Immediate booking with payment |
| `hold` | Reserve without immediate payment |

## Available Actions

| Action | Description |
|--------|-------------|
| `cancel` | Cancel the order |
| `change` | Modify the itinerary |
| `update` | Update passenger details |
