# Authentication

All requests to LiteAPI must be authenticated using an API key.

## API Key Authentication

You can find your API key in the LiteAPI dashboard. An account provides analytics and management for all bookings through the attached API keys.

### Header Format

Include the `X-API-Key` header in your HTTP requests:

```
X-API-Key: YOUR_API_KEY
```

### Example Request

```python
import requests

api_key = 'YOUR_API_KEY'
url = 'https://api.liteapi.travel/v3.0/data/hotels?countryCode=IT&cityName=Rome'
headers = {
    'X-API-Key': api_key
}

response = requests.get(url, headers=headers)
data = response.json()
print(data)
```

### cURL Example

```bash
curl -X GET "https://api.liteapi.travel/v3.0/data/hotels?countryCode=IT&cityName=Rome" \
  -H "X-API-Key: YOUR_API_KEY"
```

## Sandbox API Key

To help you get started quickly, LiteAPI provides a sandbox API key for testing purposes.

> **Note:** This key has limited permissions and can only be used for sandbox testing.

**Sandbox API Key:**
```
sand_c0155ab8-c683-4f26-8f94-b5e92c5797b9
```

### Example Request Using Sandbox API Key

```bash
curl -X GET "https://api.liteapi.travel/v3.0/data/hotels?countryCode=IT&cityName=Rome" \
  -H "X-API-Key: sand_c0155ab8-c683-4f26-8f94-b5e92c5797b9"
```

## Security Best Practices

1. **Keep your API key secure** - Do not expose it in client-side code
2. **Rotate your API keys regularly** - Periodically generate new keys
3. **Use environment variables** - Store API keys in environment variables, not in code

```python
import os

api_key = os.environ.get('LITEAPI_API_KEY')
```

## Environment Variable

```bash
export LITEAPI_API_KEY=your_api_key_here
```
