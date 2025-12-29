# Test Mode Documentation

## Overview

Test mode provides a sandbox environment for risk-free API integration development. Test mode is a 'sandbox' which lets you use the Duffel API risk-free, with no danger of spending any money or booking flights you don't want!

## Creating Test Tokens

To access test mode, developers must create a testing access token via the dashboard while in "Developer test mode" status.

Test tokens are easily identifiable - they start with `duffel_test_`

Access is segregated by token type:
- **Test tokens** only access test mode resources
- **Live tokens** only access production resources

```python
# Test token example
DUFFEL_API_KEY = "duffel_test_abc123..."

# Live token example
DUFFEL_API_KEY = "duffel_live_xyz789..."
```

## Airline Sandboxes

External airline sandbox environments have limitations:
- May experience maintenance outages
- Flight availability can be depleted by other users' bookings
- Creates inconsistent testing experiences

## Duffel Airways

To address sandbox reliability concerns, Duffel provides its own test airline: **Duffel Airways** (IATA code: `ZZ`).

### Capabilities

From Duffel Airways offers, testers can:
- Select from multiple fare brands (business class)
- List available ancillary services (baggage)
- Access seat maps with pricing details
- Create, cancel, and modify orders
- Confirm refunds and alternative flights

### Trade-offs

In test mode, Duffel Airways is much more reliable than other airlines, but this comes with a significant trade-off: you won't see realistic flight schedules or prices.

## Test Card Numbers

Payment testing uses dedicated test cards—real card details are prohibited in test mode. All test cards accept:
- Any 3-digit CVC
- Any future expiration date

### Available Test Cards

| Card Number | Country | Result |
|-------------|---------|--------|
| 4000 0082 6000 0000 | Great Britain | Success |
| 4000 0037 2000 0005 | Ireland | Success |
| 4000 0003 6000 0006 | Australia | Success |
| 4242 4242 4242 4242 | USA | Success |
| 4000 0000 0000 3220 | USA | 3D Secure triggered |
| 4000 0000 0000 9995 | USA | Insufficient funds |

**Note:** Test cards are exclusively for Duffel Payments use.

## Environment Detection

```python
def is_test_mode(api_key: str) -> bool:
    return api_key.startswith("duffel_test_")

# Usage
if is_test_mode(DUFFEL_API_KEY):
    print("Running in test mode")
else:
    print("Running in production")
```

## Best Practices

1. **Never use live tokens in development** - Always use test tokens
2. **Never use test tokens in production** - They won't work anyway
3. **Use Duffel Airways (ZZ)** - For consistent, reliable testing
4. **Store tokens securely** - Use environment variables
5. **Test edge cases** - Use the test routes for specific scenarios
