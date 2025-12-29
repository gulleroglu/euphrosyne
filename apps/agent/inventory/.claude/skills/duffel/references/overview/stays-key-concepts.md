# Stays Key Concepts - Duffel Documentation

## Overview

To effectively use the Duffel Stays API, developers need to understand several foundational concepts. This guide introduces the essential building blocks for creating accommodation booking products.

## Data Model

Duffel employs a unified data structure across all Stays endpoints consisting of three primary components:

### Accommodation
The physical property where guests will stay. This encompasses descriptive details such as location, imagery, written descriptions, and available amenities.

### Room
The specific sleeping space being reserved. Includes the room name, bed arrangement details, and visual representations.

### Rate
The booking terms and conditions, encompassing service inclusions, cancellation terms, payment specifications, and hotel policies.

## Distinguishing Rates

Rates differentiate based on specific characteristics defined by accommodation providers to match varying traveler preferences. When evaluating how to present options to customers, consider these distinguishing factors:

- **Cancellation Policy** — Refund eligibility upon cancellation
- **Board Type** — Included meals and beverages
- **Payment Method** — Accepted payment forms
- **Loyalty Programme** — Point-earning opportunities and member benefits
- **Price** — Total cost including taxes and fees
- **Rate Code** — Alphanumeric identifier for negotiated rates

Identical rates across multiple sources result in Duffel retaining only the lowest-priced option by default.

### Cancellation Policy Details

Three refund categories exist:

- **Fully refundable** — Complete reimbursement upon cancellation
- **Partially refundable** — Partial reimbursement upon cancellation
- **Non-refundable** — No reimbursement available

Refund eligibility typically evolves as check-in approaches, expressed through a cancellation timeline showing applicable terms at different booking stages.

### Board Type
Specifies meal and beverage inclusions within the rate pricing. Complete supported options appear in the API documentation.

Board types include:
- `room_only` - No meals included
- `breakfast` - Breakfast included
- `half_board` - Breakfast and dinner
- `full_board` - All meals included
- `all_inclusive` - All meals, drinks, and amenities

### Payment Method
Identifies acceptable payment forms. This characteristic guides your platform decisions rather than customer-facing presentation.

### Loyalty Programme
Enables customers to accumulate points during bookings and access member perks (complimentary internet, extended checkout, promotional items). Not all rates support loyalty earning for every property.

### Price
The comprehensive room cost covering all nights, all guests, base rates, taxes, and applicable fees due at booking.

### Rate Code
Serves as a distinct identifier for specific negotiated rate arrangements.

---

## API Flow

1. **Search** - Find available accommodations by location and dates
2. **Get Search Results** - Retrieve accommodation options with rates
3. **Create Quote** - Lock in a specific rate for booking
4. **Create Booking** - Complete the reservation with guest details

## Key Parameters

### Search Request
```json
{
  "data": {
    "location": {
      "geographic_coordinates": {
        "latitude": 43.7384,
        "longitude": 7.4246
      },
      "radius": 10
    },
    "check_in_date": "2025-05-23",
    "check_out_date": "2025-05-25",
    "rooms": 1,
    "guests": [
      { "type": "adult" }
    ]
  }
}
```

### Location Options
- Geographic coordinates with radius (km)
- Google Place ID
- IATA airport code

### Guest Types
- `adult` - Primary guest
- `child` - With age specification

## Accommodation Object

Key fields returned:
- `id` - Unique identifier
- `name` - Property name
- `rating` - Star rating (1-5)
- `review_score` - Guest review average
- `review_count` - Number of reviews
- `location` - Address and coordinates
- `amenities` - Available facilities
- `photos` - Property images
