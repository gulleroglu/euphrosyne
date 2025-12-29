# Duffel Stays Bookings API Documentation

## Overview

A booking represents a reservation for one or more rooms at an accommodation, created from a quote and containing guest information.

## Base URL

```
https://api.duffel.com/stays/bookings
```

---

## Endpoints

### 1. Create a Booking

**Method:** `POST`
**Endpoint:** `/stays/bookings`

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `quote_id` | string | The quote ID to book |
| `email` | string | Lead guest's email address |
| `phone_number` | string | Lead guest's phone (E.164 format) |
| `guests` | array | List of guests (minimum one required) |

#### Guest Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `given_name` | string | Yes | Guest's first name |
| `family_name` | string | Yes | Guest's last name |

#### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `users` | string[] | Customer user IDs for access |
| `loyalty_programme_account_number` | string | Loyalty account number |
| `accommodation_special_requests` | string | Special requests |
| `metadata` | object | Custom key-value pairs |
| `payment` | object | Payment details (omit for balance) |

#### Request Example

```python
import requests

url = "https://api.duffel.com/stays/bookings"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

payload = {
    "data": {
        "quote_id": "quo_0000AS0NZdKjjnnHZmSUbI",
        "email": "guest@example.com",
        "phone_number": "+442080160509",
        "guests": [
            {
                "given_name": "Amelia",
                "family_name": "Earhart"
            }
        ],
        "accommodation_special_requests": "Late check-in requested"
    }
}

response = requests.post(url, json=payload, headers=headers)
booking = response.json()["data"]
print(f"Booking reference: {booking['reference']}")
```

---

### 2. Get Booking

**Method:** `GET`
**Endpoint:** `/stays/bookings/{id}`

---

### 3. List Bookings

**Method:** `GET`
**Endpoint:** `/stays/bookings`

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Records per page (1-200) |
| `after` | string | Pagination cursor |
| `before` | string | Pagination cursor |
| `user_id` | string | Filter by customer user ID |

---

### 4. Update Booking

**Method:** `PATCH`
**Endpoint:** `/stays/bookings/{id}`

Update user access permissions:

```json
{
  "data": {
    "users": ["usr_001", "usr_002"]
  }
}
```

---

### 5. Cancel Booking

**Method:** `POST`
**Endpoint:** `/stays/bookings/{booking_id}/actions/cancel`

Returns booking with status "cancelled" and `cancelled_at` timestamp.

---

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique booking identifier |
| `status` | enum | "confirmed" or "cancelled" |
| `reference` | string | Accommodation's booking reference |
| `check_in_date` | date | ISO 8601 check-in date |
| `check_out_date` | date | ISO 8601 check-out date |
| `confirmed_at` | datetime | Booking creation timestamp |
| `cancelled_at` | datetime (nullable) | Cancellation timestamp |
| `email` | string | Lead guest email |
| `phone_number` | string | Lead guest phone |
| `rooms` | number | Number of rooms booked |
| `guests` | array | Guest information |
| `accommodation` | object | Full accommodation details |
| `total_amount` | string | Total booking cost |
| `total_currency` | string | ISO 4217 currency code |

---

## Complete Booking Flow

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

# Step 1: Search for accommodation
search_url = "https://api.duffel.com/stays/search"
search_payload = {
    "data": {
        "rooms": 1,
        "guests": [{"type": "adult"}],
        "check_in_date": "2025-06-01",
        "check_out_date": "2025-06-05",
        "location": {
            "geographic_coordinates": {"latitude": 43.7384, "longitude": 7.4246},
            "radius": 10
        }
    }
}
search_response = requests.post(search_url, json=search_payload, headers=headers)
results = search_response.json()["data"]["results"]

# Step 2: Fetch rates for selected accommodation
result_id = results[0]["id"]
rates_url = f"https://api.duffel.com/stays/search_results/{result_id}/actions/fetch_all_rates"
rates_response = requests.post(rates_url, headers=headers)
rooms = rates_response.json()["data"]["accommodation"]["rooms"]
rate_id = rooms[0]["rates"][0]["id"]

# Step 3: Create quote
quote_url = "https://api.duffel.com/stays/quotes"
quote_payload = {"data": {"rate_id": rate_id}}
quote_response = requests.post(quote_url, json=quote_payload, headers=headers)
quote = quote_response.json()["data"]

# Step 4: Create booking
booking_url = "https://api.duffel.com/stays/bookings"
booking_payload = {
    "data": {
        "quote_id": quote["id"],
        "email": "guest@example.com",
        "phone_number": "+442080160509",
        "guests": [{"given_name": "Amelia", "family_name": "Earhart"}]
    }
}
booking_response = requests.post(booking_url, json=booking_payload, headers=headers)
booking = booking_response.json()["data"]

print(f"Booked! Reference: {booking['reference']}")
```

## Notes

- Phone numbers must be in E.164 format (e.g., +442080160509)
- At least one guest is required
- Quote must not be expired when creating booking
- Cancelled bookings cannot be reinstated
