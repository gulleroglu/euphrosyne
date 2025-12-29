# Getting Started With LiteAPI

Learn how to quickly get up and running with LiteAPI. Follow these steps to start making API calls in minutes.

## Step 1: Sign Up

1. Create an account on the [LiteAPI platform](https://liteapi.travel)
2. Obtain your API key from the dashboard

## Step 2: Authentication

Use your API key to authenticate your requests. See the [Authentication](authentication.md) section for more details.

## Step 3: Making Your First API Call

Example code to fetch hotels by city:

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

## Step 4: Explore the API

Browse the [API Reference](endpoints-overview.md) and Booking workflow to see all available endpoints and their functionalities.

## Quick Links

| Resource | Description |
|----------|-------------|
| [Authentication](authentication.md) | API key setup and security |
| [Endpoints Overview](endpoints-overview.md) | All available API endpoints |
| [Hotel Search](retrieve-a-list-of-hotels.md) | Search for hotels |
| [Hotel Rates](retrieve-hotel-rates.md) | Get pricing and availability |
