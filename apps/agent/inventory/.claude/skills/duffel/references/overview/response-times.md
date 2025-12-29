# Duffel API Response Times Documentation

## Overview

The Duffel API functions as a proxy to external airline systems, meaning response times comprise two components:
- Airline API response times
- Duffel overhead/latency

## Default Timeout Behavior

### Search Requests
- Default maximum: 20 seconds
- Extendable via the supplier timeout parameter

### General Operations
- Maximum allowed: 120 seconds
- Includes occasionally slow airline API operations

## Client-Side Recommendations

To prevent timeouts on your end, set your HTTP client timeout "slightly higher" than the API's maximum—approximately **130 seconds** is suggested.

```python
import requests

# Recommended timeout configuration
response = requests.post(
    url,
    json=payload,
    headers=headers,
    timeout=130  # 130 seconds to account for airline delays
)
```

## Performance Optimization

The platform offers parameter options for fine-tuning requests based on your specific needs:

### Supplier Timeout
Control how long to wait for airline responses:
```json
{
  "data": {
    "supplier_timeout": 30,
    "slices": [...],
    "passengers": [...]
  }
}
```

### Max Connections
Limit connection complexity for faster results:
```json
{
  "data": {
    "max_connections": 1,
    "slices": [...],
    "passengers": [...]
  }
}
```

## Expected Response Times

| Operation | Typical Time | Maximum Time |
|-----------|--------------|--------------|
| Flight Search | 5-20 seconds | 30+ seconds |
| Hotel Search | 3-15 seconds | 30+ seconds |
| Get Offer | <1 second | 5 seconds |
| Create Order | 10-60 seconds | 120 seconds |
| Create Booking | 10-60 seconds | 120 seconds |

## Best Practices

1. **Set appropriate timeouts** - Use 130 seconds for order creation
2. **Implement retry logic** - For 503/504 errors with exponential backoff
3. **Cache reference data** - Airlines, airports don't change frequently
4. **Use streaming** - For large result sets when available
5. **Monitor x-request-id** - Track slow requests for debugging
