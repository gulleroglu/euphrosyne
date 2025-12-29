# Duffel API Response Handling Documentation

## Overview

Duffel employs standard HTTP status codes to communicate API request outcomes. The platform supports both successful responses and detailed error reporting.

## HTTP Status Codes

### Success Responses

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | New resource successfully created |
| 202 | Accepted | Request accepted; processing ongoing |
| 204 | No Content | Success with no response body |

### Client Error Responses

| Code | Status | Description |
|------|--------|-------------|
| 400 | Bad Request | Invalid or malformed request |
| 401 | Unauthorized | Missing or invalid access token |
| 403 | Forbidden | Valid token lacks required permissions |
| 404 | Not Found | Resource does not exist |
| 406 | Not Acceptable | Requested response format unsupported |
| 422 | Unprocessable Entity | Validation error occurred |
| 429 | Too Many Requests | Rate limit exceeded |

### Server Error Responses

| Code | Status | Guidance |
|------|--------|----------|
| 500 | Internal Server Error | Contact support with `request_id`; don't retry |
| 502 | Bad Gateway | Contact support with `request_id`; don't retry |
| 503 | Service Unavailable | Temporary issue; retry later |
| 504 | Gateway Timeout | Temporary issue; retry later |

## Error Response Structure

Every API error includes:

- **title**: Brief description of what went wrong
- **message**: Detailed explanation in human-readable format
- **documentation_url**: Link to relevant documentation
- **type**: Machine-readable error category
- **code**: Specific error identifier

Example error response:
```json
{
  "errors": [
    {
      "type": "validation_error",
      "title": "Validation Error",
      "message": "The passengers field is required",
      "code": "validation_required",
      "documentation_url": "https://duffel.com/docs/api",
      "source": {
        "field": "passengers",
        "pointer": "/data/passengers"
      }
    }
  ]
}
```

## Error Types

| Type | Meaning |
|------|---------|
| `authentication_error` | Token issues or missing credentials |
| `airline_error` | Error received from airline systems |
| `invalid_state_error` | Attempting action on unsuitable resource |
| `rate_limit_error` | Too many requests sent rapidly |
| `validation_error` | Missing or invalid parameters |
| `invalid_request_error` | Other request-related problems |
| `api_error` | Internal platform issue |

## Common Error Codes

### Authentication & Authorization
- `access_token_not_found`: Token not recognized
- `expired_access_token`: Token has expired
- `insufficient_permissions`: Token lacks required access

### Booking & Order Issues
- `offer_expired`: Selected offer no longer valid
- `offer_no_longer_available`: Offer pricing or availability changed
- `booking_already_attempted`: Booking pending for this rate
- `order_creation_already_attempted`: Don't retry this request

### Validation Errors
- `validation_required`: Required field is blank
- `validation_format`: Field format is invalid
- `validation_length`: Field length out of acceptable range
- `duplicate_passenger_name`: Cannot repeat passenger names

### Payment Issues
- `payment_declined`: Card rejected
- `insufficient_balance`: Wallet lacks funds
- `payment_amount_does_not_match_order_amount`: Payment doesn't match order total

## Order & Booking Creation Responses

### 201 Created Response
Complete resource information returned including the resource ID (e.g., `ord_00009hthhsUZ8W4LxQgkjo` for flights).

### 200 Success Response
Booking confirmed in supplier system but complete data not yet retrieved. Resource appears after processing completes.

### 202 Accepted Response
Request accepted; outcome confirmation pending. Webhook notifications will follow.

**Critical Implementation Detail**: Set HTTP client timeout of at least 130 seconds to avoid timing out before receiving responses from airline and accommodation systems, which can take up to 120 seconds.

## Rate Limiting

When rate limits are exceeded, the API returns a 429 status code with these headers:

- `ratelimit-limit`: Request quota (60 per 60-second period)
- `ratelimit-remaining`: Available requests in current period
- `ratelimit-reset`: When limit resets (RFC 2616 format)

### Handling Rate Limits

```python
import time

def make_request_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        response = func()
        if response.status_code == 429:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
            continue
        return response
    raise Exception("Max retries exceeded")
```

## Error Handling Guidelines

### Expired Offers
When receiving `offer_expired` errors, don't retry the same request. Instead, perform a new search using fresh offers. Monitor the `expires_at` attribute (typically 15-30 minutes validity) before attempting order creation.

### Validation Errors
These require adjusting the request. Responses include a `source` property identifying the exact problematic field.

### Temporary Errors (503, 504)
Safe to retry with exponential backoff; consult Duffel Status page if errors persist.

### Server Errors (500, 502)
Don't retry - contact support with the `request_id`.

## Webhook Notifications

- **Flights**: `order.created` event when order is created
- **Stays**: `stays.booking.created` event when booking is created
- **Failures**: `order.creation_failed` or `stays.booking_creation_failed` notifications
