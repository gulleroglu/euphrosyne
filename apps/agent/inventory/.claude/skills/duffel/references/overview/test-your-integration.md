# Integration Testing Guide for Duffel API

## Overview

This documentation provides test scenarios for validating your integration with the Duffel test environment. Use these predefined routes to trigger different flows in your integration and ensure they are handled accordingly.

## Offer Request API Tests

The Offer Request API includes six predefined routes that return consistent, predictable responses:

| Scenario | Route | Expected Outcome |
|----------|-------|------------------|
| **No Flights** | PVD → RAI | No offers will be returned |
| **Hold Orders** | JFK → EWR | Returns offers with `requires_instant_payment=false` |
| **Connecting Flights** | LHR → DXB | Multiple segments demonstrating connections |
| **No Baggage** | BTS → MRU | Offers without baggage for any passengers |
| **Timeout** | STN → LHR | Request guaranteed to timeout |
| **Stops** | DXB → AMS | Single-stop itineraries |

### Example: Testing No Flights Scenario

```python
payload = {
    "data": {
        "slices": [
            {
                "origin": "PVD",
                "destination": "RAI",
                "departure_date": "2025-06-01"
            }
        ],
        "passengers": [{"type": "adult"}],
        "cabin_class": "economy"
    }
}
# Response will have empty offers array
```

## Offer API Tests

Three scenarios validate offer retrieval and state management:

| Scenario | Route | Notes |
|----------|-------|-------|
| **No Additional Services** | BTS → ABV | Requires `return_available_services=true` |
| **Expired Offers** | LGW → LHR | Simulates offer unavailability |
| **Price Changes** | LHR → STN | Demonstrates pricing fluctuations |

## Order Creation Tests

Six test cases cover order lifecycle scenarios:

| Scenario | Route | Expected Behavior |
|----------|-------|-------------------|
| **Creation Failures** | LHR → LGW | Order creation fails |
| **Insufficient Balance** | LGW → STN | Payment rejected |
| **Expired Offers at Booking** | LHR → STN | `offer_expired` error |
| **HTTP 200 Response** | LTN → STN | Successful but delayed info |
| **HTTP 202 Response** | SEN → STN | Accepted but unconfirmed |
| **Webhook Failures** | LCY → STN | `order.creation_failed` notification |

## Payments API Tests

Two scenarios test payment processing delays:

| Response | Route | Behavior |
|----------|-------|----------|
| **200 Success** | LTN → STN | Webhook sent 30s after response |
| **202 Accepted** | SEN → STN | Resolution within an hour |

## Airline-Initiated Changes

Route: **LHR → LTN** creates test orders for validating change notifications.

## Airline Credits

Route: **LTN → SYD** generates orders refundable as airline credits upon cancellation.

## Testing Checklist

### Offer Request Flow
- [ ] Search returns offers successfully
- [ ] Handle empty results gracefully
- [ ] Timeout handling works correctly
- [ ] Connecting flights displayed properly

### Offer Flow
- [ ] Single offer retrieval works
- [ ] Expired offer error handled
- [ ] Price change detection implemented

### Order Flow
- [ ] Order creation succeeds
- [ ] Order creation failure handled
- [ ] Insufficient balance error shown
- [ ] 200/202 response handling correct
- [ ] Webhook listener receives notifications

### Payment Flow
- [ ] Successful payment processed
- [ ] 3D Secure flow works
- [ ] Insufficient funds error shown

## Best Practices

1. **Always retrieve offers before booking** - Captures latest pricing and availability
2. **Handle timeout scenarios** - Graceful degradation in user experience
3. **Implement webhook listeners** - For asynchronous order confirmation
4. **Test error responses** - Including `offer_no_longer_available` error codes
5. **Validate 200/202 HTTP responses** - Different handling for each
6. **Log x-request-id** - For debugging and support requests
