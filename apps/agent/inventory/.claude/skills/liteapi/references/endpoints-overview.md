# Endpoints Overview

The LiteAPI v3 provides endpoints categorized into four main sections: Hotel Data API, Search API, Booking API, and Loyalty API.

## Base URL

```
https://api.liteapi.travel/v3.0
```

## Booking Base URL

```
https://book.liteapi.travel/v3.0
```

---

## Hotel Data API

### Hotels

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/data/hotels` | Retrieve a list of hotels |
| GET | `/data/hotel` | Get detailed information about a specific hotel |
| GET | `/data/reviews` | Access reviews for a specific hotel |
| GET | `/data/hotels/semantic-search` | AI-powered semantic hotel search (Beta) |

### Reference Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/data/cities` | Fetch a list of cities within a specified country |
| GET | `/data/countries` | Obtain a list of all countries |
| GET | `/data/currencies` | Retrieve a list of supported currencies |
| GET | `/data/iataCodes` | Get IATA codes for airports and cities |
| GET | `/data/facilities` | List the hotel facilities |
| GET | `/data/hotelTypes` | List of hotel types |
| GET | `/data/chains` | List of hotel chains |
| GET | `/data/places` | Search for places |

---

## Search API

### Room Rates

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hotels/rates` | Request room rates for hotels with full details |
| POST | `/hotels/min-rates` | Get minimum rates for quick price comparisons |

---

## Booking API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rates/prebook` | Create checkout session and obtain transaction ID |
| POST | `/rates/book` | Confirm booking with transaction ID |
| GET | `/prebooks/{prebookId}` | Retrieve prebook details |
| GET | `/bookings` | Retrieve a list of all bookings |
| GET | `/bookings/{bookingId}` | Get details of a specific booking |
| PUT | `/bookings/{bookingId}` | Cancel a specific booking |
| PUT | `/bookings/{bookingId}/amend` | Modify guest information |

---

## Loyalty API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/guests` | Fetch all guests with loyalty info |
| GET | `/guests/{guestId}` | Fetch specific guest details |
| GET | `/guests/{guestId}/bookings` | Get all bookings for a guest |
| GET | `/guests/{guestId}/loyalty-points` | Get loyalty points balance |
| POST | `/guests/{guestId}/loyalty-points/redeem` | Redeem loyalty points |
| POST | `/loyalties` | Enable the loyalty program |
| PUT | `/loyalties` | Update loyalty program settings |
| GET | `/loyalties` | Get loyalty program settings |

---

## Voucher API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/vouchers` | Create a voucher |
| GET | `/vouchers` | List all vouchers |
| GET | `/vouchers/{voucherId}` | Get specific voucher |
| PUT | `/vouchers/{id}` | Update voucher |
| PUT | `/vouchers/{id}/status` | Update voucher status |
| DELETE | `/vouchers` | Delete voucher |

---

## Analytics API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analytics/weekly` | Weekly analytics |
| POST | `/analytics/report` | Detailed reports |
| POST | `/analytics/markets` | Market analytics |
| POST | `/analytics/hotels` | Top booked hotels |

---

## Booking Flow Summary

```
1. Search Hotels     →  GET  /data/hotels
2. Get Rates         →  POST /hotels/rates
3. Create Prebook    →  POST /rates/prebook
4. Complete Booking  →  POST /rates/book
5. Manage Booking    →  GET/PUT /bookings/{id}
```
