# Flights Key Concepts Documentation

## Overview

The Duffel API requires understanding several foundational concepts for flight search and booking operations.

### Core Components

**Offer Request**: A search query describing passengers and their desired travel. As stated in the documentation, "An offer request describes the passengers and where and when they want to travel (in the form of a list of slices)." It may include additional filters like cabin class preferences.

**Slice**: Represents a single journey segment between an origin and destination. You specify locations using IATA codes—either airport codes (e.g., `LHR` for London Heathrow) or city codes (e.g., `NYC` for New York). An offer request contains one or more slices.

**Offer**: The API "sends the search to a range of airlines, and come back to you with a series of offers." Each offer represents a purchasable flight bundle at a specific price meeting your criteria. Airlines may return multiple offers.

**Segment**: An individual flight within a slice. Direct routes have one segment; indirect routes have multiple segments with connections. "All lists of slices and segments will be ordered by those departing first."

**Order**: Created after selecting an offer, requiring passenger details (name, date of birth) and payment information.

---

## Trip Type Examples

### One-Way Direct
- Two passengers: LHR → NYC (May 1st)
- Single segment: LHR to JFK on British Airways flight BA117
- Cost: £1,532

### One-Way Indirect
- Two passengers: LHR → NYC (May 1st)
- Two segments: LHR→BOS (VS4011), then BOS→LGA (VS3277)
- Cost: £482

### Return Direct
- One passenger: LON ↔ YTO (May 1st–8th)
- Outbound: LGW→YYZ on WestJet WS4
- Return: YYZ→LGW on WestJet WS3
- Cost: £431

### Return Indirect
- One passenger: LON ↔ YTO (May 1st–8th)
- Outbound: LHR→YYZ on Air Canada AC869
- Return: YYZ→ORD→LHR (Air Canada AC509 and AC5364)
- Cost: £396

### Multi-City Direct
- One passenger: LON→JFK (May 1st), NYC→SFO (May 4th), SFO→LON (May 8th)
- Three segments via British Airways and partner airlines
- Cost: £763

---

## API Flow

1. **Create Offer Request** - Define passengers and slices
2. **Receive Offers** - Get available flight options with prices
3. **Select Offer** - Choose the desired flight option
4. **Create Order** - Book with passenger details and payment

## Key Parameters

### Offer Request
```json
{
  "data": {
    "slices": [
      {
        "origin": "LHR",
        "destination": "JFK",
        "departure_date": "2025-05-01"
      }
    ],
    "passengers": [
      { "type": "adult" }
    ],
    "cabin_class": "economy"
  }
}
```

### Slice Fields
- `origin` - IATA airport or city code
- `destination` - IATA airport or city code
- `departure_date` - Date in YYYY-MM-DD format

### Passenger Types
- `adult` - 12+ years
- `child` - 2-11 years
- `infant_without_seat` - Under 2 years

### Cabin Classes
- `economy`
- `premium_economy`
- `business`
- `first`
