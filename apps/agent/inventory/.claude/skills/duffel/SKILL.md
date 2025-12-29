---
name: duffel
description: "Duffel API for flights and hotel bookings. Routes to appropriate reference docs based on user request type."
---

# Duffel Skill

Comprehensive travel booking API covering flights, hotel stays, and embedded booking sessions.

## Quick Navigation

**What do you want to do?**

| Task | Go To |
|------|-------|
| Search flights | [Flights: Offer Requests](#search-flights) |
| Book a flight | [Flights: Orders](#book-flight) |
| Change/cancel flight | [Flights: Order Changes](#manage-flight) |
| Search hotels | [Stays: Search](#search-hotels) |
| Book a hotel | [Stays: Bookings](#book-hotel) |
| Embedded booking UI | [Links: Sessions](#embedded-sessions) |

---

## Environment Variables

```
DUFFEL_API_KEY=duffel_live_xxx  # Required for all API calls
```

## Request Headers (All Endpoints)

```
Authorization: Bearer <DUFFEL_API_KEY>
Duffel-Version: v2
Content-Type: application/json
```

---

# Flights API

## Search Flights

**Goal:** Find available flights for a route and dates

**Flow:** Create Offer Request → Get Offers

| Step | Reference |
|------|-----------|
| 1. Create offer request | `references/flights/offer-requests.md` |
| 2. Browse returned offers | `references/flights/offers.md` |
| 3. View seat maps (optional) | `references/flights/seat-maps.md` |

**Key Concepts:** `references/overview/flights-key-concepts.md`
- Slices = journey legs (outbound, return)
- Segments = individual flights within a slice
- IATA codes for airports/cities

### Quick Example

```python
# Search one-way LHR → JFK
payload = {
    "data": {
        "slices": [{
            "origin": "LHR",
            "destination": "JFK",
            "departure_date": "2025-06-01"
        }],
        "passengers": [{"type": "adult"}],
        "cabin_class": "economy"
    }
}
# POST https://api.duffel.com/air/offer_requests
```

---

## Book Flight

**Goal:** Create a confirmed flight booking from a selected offer

**Flow:** Select Offer → Create Order → Process Payment

| Step | Reference |
|------|-----------|
| 1. Select offer from search | `references/flights/offers.md` |
| 2. Create order with passenger details | `references/flights/orders.md` |
| 3. Process payment | `references/flights/payments.md` |

### Quick Example

```python
# Book selected offer
payload = {
    "data": {
        "selected_offers": ["off_xxx"],
        "passengers": [{
            "id": "pas_xxx",
            "given_name": "Amelia",
            "family_name": "Earhart",
            "born_on": "1990-01-01",
            "email": "amelia@example.com",
            "phone_number": "+14155551234",
            "gender": "f"
        }],
        "type": "instant",
        "payments": [{
            "type": "balance",
            "amount": "150.00",
            "currency": "GBP"
        }]
    }
}
# POST https://api.duffel.com/air/orders
```

---

## Manage Flight

**Goal:** Change or cancel an existing flight booking

| Action | Reference |
|--------|-----------|
| Cancel order | `references/flights/order-cancellations.md` |
| Request change | `references/flights/order-change-requests.md` |
| Get change options | `references/flights/order-change-offers.md` |
| Confirm change | `references/flights/order-changes.md` |
| Handle airline changes | `references/flights/airline-initiated-changes.md` |

### Additional Flights References

| Topic | Reference |
|-------|-----------|
| Batch searches | `references/flights/batch-offer-requests.md` |
| Multi-step bookings | `references/flights/partial-offer-requests.md` |
| Airline credits | `references/flights/airline-credits.md` |

---

# Stays API (Hotels)

## Search Hotels

**Goal:** Find available hotels in a location

**Flow:** Search → Fetch Rates → Create Quote

| Step | Reference |
|------|-----------|
| 1. Search by location | `references/stays/search.md` |
| 2. Fetch rates for result | `references/stays/search-result.md` |
| 3. Create quote (locks price) | `references/stays/quotes.md` |

**Key Concepts:** `references/overview/stays-key-concepts.md`
- Search returns cheapest rate per property
- Fetch rates for full room/rate details
- Quote confirms final price before booking

### Quick Example

```python
# Search hotels in Monaco
payload = {
    "data": {
        "rooms": 1,
        "guests": [{"type": "adult"}, {"type": "adult"}],
        "check_in_date": "2025-06-01",
        "check_out_date": "2025-06-05",
        "location": {
            "geographic_coordinates": {
                "latitude": 43.7384,
                "longitude": 7.4246
            },
            "radius": 10
        }
    }
}
# POST https://api.duffel.com/stays/search
```

---

## Book Hotel

**Goal:** Create a confirmed hotel booking from a quote

**Flow:** Quote → Booking

| Step | Reference |
|------|-----------|
| 1. Have valid quote | `references/stays/quotes.md` |
| 2. Create booking | `references/stays/bookings.md` |
| 3. Payment instructions (optional) | `references/stays/booking-payment-instructions.md` |

### Quick Example

```python
# Book from quote
payload = {
    "data": {
        "quote_id": "quo_xxx",
        "email": "guest@example.com",
        "phone_number": "+442080160509",
        "guests": [{
            "given_name": "Amelia",
            "family_name": "Earhart"
        }]
    }
}
# POST https://api.duffel.com/stays/bookings
```

---

## Hotel Data & Utilities

| Topic | Reference |
|-------|-----------|
| Accommodation details | `references/stays/accommodation.md` |
| Guest reviews | `references/stays/accommodation-reviews.md` |
| Hotel brands | `references/stays/brands.md` |
| Loyalty programmes | `references/stays/accommodation-loyalty-programmes.md` |
| Negotiated rates | `references/stays/negotiated-rates.md` |

---

# Links API (Embedded Booking)

## Embedded Sessions

**Goal:** Create white-labeled booking session for end users

| Step | Reference |
|------|-----------|
| Create session | `references/links/sessions.md` |

### Quick Example

```python
# Create booking session
payload = {
    "data": {
        "reference": "user_123",
        "success_url": "https://myapp.com/success",
        "failure_url": "https://myapp.com/failure",
        "abandonment_url": "https://myapp.com/abandoned",
        "flights": {"enabled": True},
        "stays": {"enabled": True}
    }
}
# POST https://api.duffel.com/links/sessions
# Returns URL to redirect user to
```

---

# API Fundamentals

| Topic | Reference |
|-------|-----------|
| Making requests | `references/overview/making-requests.md` |
| Response handling | `references/overview/response-handling.md` |
| Pagination | `references/overview/pagination.md` |
| Response times | `references/overview/response-times.md` |
| Test mode | `references/overview/test-mode.md` |
| Testing integration | `references/overview/test-your-integration.md` |

---

# Available Scripts

### search_hotels.py

Search hotels and output flat list for inventory building.

```bash
python3 .claude/skills/duffel/scripts/search_hotels.py \
  --city "Monaco" \
  --country "Monaco" \
  --check-in "2025-05-23" \
  --check-out "2025-05-25" \
  --radius 15 \
  --output "files/content/accommodations/duffel_hotels.json"
```

---

# Decision Tree

```
User Request
│
├── "Search/find flights" ──────────► references/flights/offer-requests.md
├── "Book a flight" ────────────────► references/flights/orders.md
├── "Cancel flight" ────────────────► references/flights/order-cancellations.md
├── "Change flight" ────────────────► references/flights/order-change-requests.md
│
├── "Search/find hotels" ───────────► references/stays/search.md
├── "Book a hotel" ─────────────────► references/stays/bookings.md
├── "Cancel hotel" ─────────────────► references/stays/bookings.md (cancel action)
├── "Hotel reviews" ────────────────► references/stays/accommodation-reviews.md
│
├── "Embedded booking" ─────────────► references/links/sessions.md
│
├── "How does Duffel work?" ────────► references/overview/flights-key-concepts.md
│                                     references/overview/stays-key-concepts.md
└── "API errors/pagination" ────────► references/overview/response-handling.md
                                      references/overview/pagination.md
```

---

# Complete Booking Flows

## Flight Booking (End-to-End)

```
1. offer-requests.md    → Search flights
2. offers.md            → Select offer
3. seat-maps.md         → Select seats (optional)
4. orders.md            → Create order with passengers
5. payments.md          → Process payment
```

## Hotel Booking (End-to-End)

```
1. search.md            → Search hotels by location
2. search-result.md     → Fetch all rates for hotel
3. quotes.md            → Lock in price with quote
4. bookings.md          → Create booking with guest info
```

