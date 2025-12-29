# Sessions API Documentation

## Overview

The Sessions API enables creation of traveler sessions for search and booking flows. Each session represents a distinct user journey through the search and book experience.

## Base Endpoint

```
https://api.duffel.com/links/sessions
```

---

## Key Characteristics

- Valid for 20 minutes after first use
- Can be accessed up to 24 hours after creation
- One order per session; subsequent visits redirect to confirmation page
- Create a new session for each user booking attempt

---

## Schema

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `reference` | string | Internal identifier (user ID, etc.); max 500 chars |
| `success_url` | string | Redirect URL after successful order creation |
| `failure_url` | string | Redirect URL if unmitigated failure occurs |
| `abandonment_url` | string | Redirect URL if user abandons session |

### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `traveller_currency` | string | ISO 4217 currency code; defaults to account settlement currency |
| `primary_color` | string | Hex color (#RRGGBB) for UI customization |
| `secondary_color` | string | Hex color (#RRGGBB) for UI customization |
| `logo_url` | string | Custom logo URL (max 1000 chars); resized to 16px height |
| `markup_amount` | string | Fixed amount added to final price |
| `markup_currency` | string | Currency for markup_amount (must match settlement currency) |
| `markup_rate` | string | Percentage markup (e.g., "0.01" = 1%) |
| `checkout_display_text` | string | Message at checkout form bottom (max 120 chars) |
| `should_hide_traveller_currency_selector` | boolean | Prevent currency changes; defaults to false |
| `flights` | object | Flight configuration with `enabled` property |
| `stays` | object | Accommodation configuration with `enabled` property |

**Note:** Markup fields apply only to Duffel Flights. To enable both Flights and Stays, provide both objects with `enabled: true`.

---

## Endpoint

### Create Session

**Method:** `POST`
**Endpoint:** `/links/sessions`

#### Example

```python
import requests

url = "https://api.duffel.com/links/sessions"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

payload = {
    "data": {
        "reference": "user_123",
        "success_url": "https://example.com/success",
        "failure_url": "https://example.com/failure",
        "abandonment_url": "https://example.com/abandonment",
        "primary_color": "#000000",
        "markup_amount": "1.00",
        "markup_currency": "GBP",
        "flights": {"enabled": True},
        "stays": {"enabled": True}
    }
}

response = requests.post(url, json=payload, headers=headers)
session = response.json()["data"]
print(f"Session URL: {session['url']}")
```

#### Response

```json
{
  "data": {
    "url": "https://links.duffel.com?token=<TOKEN>"
  }
}
```

The `url` field contains the session link for redirection. If using a custom subdomain, the URL reflects that domain; otherwise defaults to `links.duffel.com`.

---

## Usage Flow

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Duffel-Version": "v2",
    "Content-Type": "application/json"
}

# Create a session for a user
session_url = "https://api.duffel.com/links/sessions"
payload = {
    "data": {
        "reference": "booking_attempt_456",
        "success_url": "https://myapp.com/booking/success",
        "failure_url": "https://myapp.com/booking/failed",
        "abandonment_url": "https://myapp.com/booking/abandoned",
        "traveller_currency": "USD",
        "primary_color": "#3B82F6",
        "flights": {"enabled": True},
        "stays": {"enabled": True}
    }
}

response = requests.post(session_url, json=payload, headers=headers)
session = response.json()["data"]

# Redirect user to the session URL
redirect_url = session["url"]
# User completes booking flow in Duffel Links
# Upon completion, user is redirected to success_url
```

---

## Notes

- Create a new session for each booking attempt
- Sessions expire 20 minutes after first access
- Only one order can be created per session
- Use `reference` to correlate sessions with your internal records
- Markup is applied only to flights, not stays

