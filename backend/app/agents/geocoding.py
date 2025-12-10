"""
Agent 4: Geocoding Agent
Converts location strings to lat/lng coordinates using Nominatim.
"""

from typing import Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
from .base import BaseAgent
from .extraction import ExtractedJob


class GeocodedJob(ExtractedJob):
    """Job with geocoded coordinates."""
    lat: float = 20.5937  # Default: India center
    lng: float = 78.9629


class GeocodingAgent(BaseAgent):
    """
    Geocodes job locations to lat/lng coordinates.
    Uses Nominatim (OpenStreetMap) - free, no API key required.
    """

    # Cache for common Indian cities
    CITY_CACHE = {
        "bangalore": (12.9716, 77.5946),
        "bengaluru": (12.9716, 77.5946),
        "mumbai": (19.0760, 72.8777),
        "delhi": (28.6139, 77.2090),
        "new delhi": (28.6139, 77.2090),
        "hyderabad": (17.3850, 78.4867),
        "chennai": (13.0827, 80.2707),
        "pune": (18.5204, 73.8567),
        "kolkata": (22.5726, 88.3639),
        "gurgaon": (28.4595, 77.0266),
        "gurugram": (28.4595, 77.0266),
        "noida": (28.5355, 77.3910),
        "ahmedabad": (23.0225, 72.5714),
        "jaipur": (26.9124, 75.7873),
        "remote": (20.5937, 78.9629),  # India center for remote
        "india": (20.5937, 78.9629),
    }

    def __init__(self):
        self.geolocator = Nominatim(user_agent="india-job-map")

    @property
    def name(self) -> str:
        return "Geocoding Agent"

    async def run(self, extracted_jobs: list[ExtractedJob]) -> list[GeocodedJob]:
        """
        Add coordinates to extracted jobs.
        
        Args:
            extracted_jobs: List of ExtractedJob from Extraction Agent
            
        Returns:
            List of GeocodedJob with lat/lng
        """
        geocoded_jobs = []
        
        for job in extracted_jobs:
            lat, lng = await self._geocode_location(job.location)
            
            geocoded_job = GeocodedJob(
                job_title=job.job_title,
                company=job.company,
                location=job.location,
                apply_url=job.apply_url,
                description=job.description,
                lat=lat,
                lng=lng
            )
            geocoded_jobs.append(geocoded_job)
        
        return geocoded_jobs

    async def _geocode_location(self, location: str) -> Tuple[float, float]:
        """Geocode a location string to coordinates."""
        if not location:
            return 20.5937, 78.9629  # Default: India center
        
        # Normalize location
        location_lower = location.lower().strip()
        
        # Check cache first
        for key, coords in self.CITY_CACHE.items():
            if key in location_lower:
                return coords
        
        # Try Nominatim for unknown locations
        try:
            time.sleep(1)  # Rate limiting for Nominatim
            result = self.geolocator.geocode(f"{location}, India", timeout=10)
            if result:
                return (result.latitude, result.longitude)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Geocoding error for '{location}': {e}")
        
        # Default to India center
        return 20.5937, 78.9629


# Allow running directly for testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = GeocodingAgent()
        test_jobs = [
            ExtractedJob(
                job_title="Developer",
                company="Test Corp",
                location="Bangalore",
                apply_url="https://example.com"
            ),
            ExtractedJob(
                job_title="Engineer",
                company="Remote Inc",
                location="Remote",
                apply_url="https://example.com"
            )
        ]
        results = await agent.run(test_jobs)
        
        print(f"\nGeocoded {len(results)} jobs:\n")
        for job in results:
            print(f"  {job.job_title} at {job.company}")
            print(f"    Location: {job.location} -> ({job.lat}, {job.lng})\n")
    
    asyncio.run(test())
