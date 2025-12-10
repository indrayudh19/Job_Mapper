"""
Base scraper class with common HTTP handling and error management.
"""

import time
import requests
from abc import ABC, abstractmethod
from typing import Optional
from ..models import JobPostingCreate


class BaseScraper(ABC):
    """
    Abstract base class for job scrapers.
    Provides common functionality for HTTP requests and rate limiting.
    """

    # Default headers to mimic a browser
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize the scraper.
        
        Args:
            rate_limit: Minimum seconds between requests
        """
        self.rate_limit = rate_limit
        self.last_request_time: float = 0
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limit."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

    def fetch(self, url: str, headers: Optional[dict] = None) -> Optional[str]:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch
            headers: Optional additional headers
            
        Returns:
            HTML content or None if failed
        """
        self._wait_for_rate_limit()
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            self.last_request_time = time.time()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def fetch_json(self, url: str, headers: Optional[dict] = None) -> Optional[dict]:
        """
        Fetch JSON content from a URL.
        
        Args:
            url: URL to fetch
            headers: Optional additional headers
            
        Returns:
            JSON data or None if failed
        """
        self._wait_for_rate_limit()
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            self.last_request_time = time.time()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this scraper's source."""
        pass

    @abstractmethod
    def scrape(self) -> list[JobPostingCreate]:
        """
        Scrape job postings from the source.
        
        Returns:
            List of JobPostingCreate objects
        """
        pass
