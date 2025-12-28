#!/usr/bin/env python3
"""
Duffel API client wrapper with authentication and error handling.
"""
import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List

# Load environment variables from .env file in revision folder
project_root = Path(__file__).parent.parent.parent.parent.parent
env_file = project_root / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)
else:
    # Try parent directories
    for parent in [project_root.parent, project_root.parent.parent]:
        env_file = parent / ".env"
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
            break

DUFFEL_API_URL = "https://api.duffel.com"
DUFFEL_API_VERSION = "v2"


class DuffelClient:
    """Duffel API client with authentication and retry logic."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DUFFEL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DUFFEL_API_KEY environment variable not set. "
                "Get your API key from https://app.duffel.com/tokens"
            )

        self.base_url = DUFFEL_API_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Duffel-Version": DUFFEL_API_VERSION,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Make API request with retry logic."""
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=60
                )

                if response.status_code == 200 or response.status_code == 201:
                    return response.json()

                if response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = 2 ** attempt
                    print(f"Rate limited, waiting {wait_time}s...", file=__import__('sys').stderr)
                    time.sleep(wait_time)
                    continue

                if response.status_code == 401:
                    raise ValueError("Invalid API key. Check your DUFFEL_API_KEY.")

                if response.status_code >= 500:
                    # Server error - retry
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue

                # Parse error response
                try:
                    error_data = response.json()
                    errors = error_data.get("errors", [])
                    if errors:
                        error_msg = errors[0].get("message", str(response.text))
                    else:
                        error_msg = str(response.text)
                except:
                    error_msg = response.text

                raise Exception(f"API Error {response.status_code}: {error_msg}")

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"Request failed: {e}")

        raise Exception("Max retries exceeded")

    def create_offer_request(
        self,
        slices: List[Dict],
        passengers: List[Dict],
        cabin_class: str = "economy",
        max_connections: int = 1
    ) -> Dict[str, Any]:
        """
        Create a flight offer request.

        Args:
            slices: List of flight slices with origin, destination, departure_date
            passengers: List of passenger objects with type (adult, child, infant)
            cabin_class: Cabin class preference
            max_connections: Maximum number of connections

        Returns:
            Offer request response with offers
        """
        data = {
            "data": {
                "slices": slices,
                "passengers": passengers,
                "cabin_class": cabin_class,
                "max_connections": max_connections
            }
        }

        return self._request("POST", "air/offer_requests", data=data)

    def get_offer(self, offer_id: str) -> Dict[str, Any]:
        """Get details for a specific offer."""
        return self._request("GET", f"air/offers/{offer_id}")

    def search_stays(
        self,
        location: Dict,
        check_in_date: str,
        check_out_date: str,
        rooms: int = 1,
        adults: int = 2
    ) -> Dict[str, Any]:
        """
        Search for hotel/stay accommodations.

        Args:
            location: Dict with latitude, longitude or location name
            check_in_date: Check-in date (YYYY-MM-DD)
            check_out_date: Check-out date (YYYY-MM-DD)
            rooms: Number of rooms
            adults: Number of adults

        Returns:
            Stays search response
        """
        data = {
            "data": {
                "location": location,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "rooms": rooms,
                "guests": [{"type": "adult"} for _ in range(adults)]
            }
        }

        return self._request("POST", "stays/search", data=data)

    def get_stay_rate(self, rate_id: str) -> Dict[str, Any]:
        """Get details for a specific stay rate."""
        return self._request("GET", f"stays/rates/{rate_id}")


def get_client() -> DuffelClient:
    """Get a configured Duffel client instance."""
    return DuffelClient()


if __name__ == "__main__":
    # Test connection
    try:
        client = get_client()
        print("Duffel client initialized successfully")
    except Exception as e:
        print(f"Error: {e}")
