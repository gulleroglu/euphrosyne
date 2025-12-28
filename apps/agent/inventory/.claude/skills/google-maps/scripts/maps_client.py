#!/usr/bin/env python3
"""
Google Maps API client wrapper with authentication and error handling.
"""
import os
import json
import time
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

MAPS_BASE_URL = "https://maps.googleapis.com/maps/api"


class MapsClient:
    """Google Maps API client."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GOOGLE_MAPS_API_KEY environment variable not set. "
                "Get your API key from https://console.cloud.google.com/apis/credentials"
            )

        self.base_url = MAPS_BASE_URL
        self.session = requests.Session()

    def _request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Make API request with retry logic."""
        params["key"] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    # Check for API-level errors
                    status = data.get("status")
                    if status == "OK" or status == "ZERO_RESULTS":
                        return data
                    elif status == "OVER_QUERY_LIMIT":
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)
                            continue
                        raise Exception("API quota exceeded")
                    elif status == "REQUEST_DENIED":
                        raise ValueError(f"Request denied: {data.get('error_message', 'Check API key')}")
                    elif status == "INVALID_REQUEST":
                        raise ValueError(f"Invalid request: {data.get('error_message', 'Check parameters')}")
                    else:
                        raise Exception(f"API error: {status} - {data.get('error_message', '')}")

                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    raise Exception("Rate limit exceeded")

                raise Exception(f"HTTP {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"Request failed: {e}")

        raise Exception("Max retries exceeded")

    def search_places(
        self,
        query: str,
        location: Optional[str] = None,
        radius: int = 5000,
        type: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Search for places using text query.

        Args:
            query: Search query
            location: Center point as "lat,lng"
            radius: Search radius in meters
            type: Place type filter
            language: Language for results

        Returns:
            Places API response
        """
        params = {
            "query": query,
            "language": language
        }

        if location:
            params["location"] = location
            params["radius"] = radius

        if type:
            params["type"] = type

        return self._request("place/textsearch/json", params)

    def nearby_search(
        self,
        location: str,
        radius: int = 5000,
        type: Optional[str] = None,
        keyword: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Search for nearby places.

        Args:
            location: Center point as "lat,lng"
            radius: Search radius in meters
            type: Place type filter
            keyword: Keyword to match
            language: Language for results

        Returns:
            Places API response
        """
        params = {
            "location": location,
            "radius": radius,
            "language": language
        }

        if type:
            params["type"] = type

        if keyword:
            params["keyword"] = keyword

        return self._request("place/nearbysearch/json", params)

    def get_place_details(
        self,
        place_id: str,
        fields: Optional[List[str]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get detailed information about a place.

        Args:
            place_id: Google Place ID
            fields: List of fields to return
            language: Language for results

        Returns:
            Place Details API response
        """
        default_fields = [
            "name", "formatted_address", "formatted_phone_number",
            "opening_hours", "rating", "reviews", "website",
            "price_level", "photos", "geometry"
        ]

        params = {
            "place_id": place_id,
            "fields": ",".join(fields or default_fields),
            "language": language
        }

        return self._request("place/details/json", params)

    def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        departure_time: Optional[str] = None,
        alternatives: bool = False,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get directions between two points.

        Args:
            origin: Starting point
            destination: End point
            mode: Travel mode (driving, walking, bicycling, transit)
            departure_time: Departure time for transit
            alternatives: Return alternative routes
            language: Language for results

        Returns:
            Directions API response
        """
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "alternatives": str(alternatives).lower(),
            "language": language
        }

        if departure_time:
            # Convert ISO format to Unix timestamp
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
                params["departure_time"] = int(dt.timestamp())
            except:
                params["departure_time"] = departure_time

        return self._request("directions/json", params)

    def distance_matrix(
        self,
        origins: List[str],
        destinations: List[str],
        mode: str = "driving",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Calculate distances between multiple origins and destinations.

        Args:
            origins: List of origin points
            destinations: List of destination points
            mode: Travel mode
            language: Language for results

        Returns:
            Distance Matrix API response
        """
        params = {
            "origins": "|".join(origins),
            "destinations": "|".join(destinations),
            "mode": mode,
            "language": language
        }

        return self._request("distancematrix/json", params)


def get_client() -> MapsClient:
    """Get a configured Maps client instance."""
    return MapsClient()


if __name__ == "__main__":
    # Test connection
    try:
        client = get_client()
        print("Google Maps client initialized successfully")
    except Exception as e:
        print(f"Error: {e}")
