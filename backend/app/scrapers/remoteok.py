"""
RemoteOK job scraper.
Scrapes remote job listings from remoteok.com
"""

from bs4 import BeautifulSoup
from .base import BaseScraper
from ..models import JobPostingCreate


class RemoteOKScraper(BaseScraper):
    """
    Scraper for RemoteOK - a remote job board.
    Uses their JSON API endpoint for easier parsing.
    """

    BASE_URL = "https://remoteok.com/api"

    @property
    def source_name(self) -> str:
        return "remoteok"

    def scrape(self, limit: int = 20) -> list[JobPostingCreate]:
        """
        Scrape job listings from RemoteOK.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of JobPostingCreate objects
        """
        jobs = []
        
        # RemoteOK provides a JSON API
        data = self.fetch_json(self.BASE_URL)
        
        if not data:
            print("Failed to fetch RemoteOK data")
            return jobs

        # First item is usually metadata, skip it
        job_listings = data[1:limit + 1] if len(data) > 1 else []

        for job in job_listings:
            try:
                # Extract location - default to Remote if not specified
                location = job.get("location", "Remote")
                if not location:
                    location = "Remote"

                # Create job posting
                job_posting = JobPostingCreate(
                    job_title=job.get("position", "Unknown Position"),
                    company=job.get("company", "Unknown Company"),
                    location=location,
                    apply_url=f"https://remoteok.com/remote-jobs/{job.get('slug', '')}",
                    lat=20.5937,  # Default to India center - will be geocoded later
                    lng=78.9629,
                    text=job.get("description", ""),
                    source=self.source_name
                )
                jobs.append(job_posting)
            except Exception as e:
                print(f"Error parsing job: {e}")
                continue

        return jobs


# Allow running directly for testing
if __name__ == "__main__":
    scraper = RemoteOKScraper()
    jobs = scraper.scrape(limit=5)
    
    print(f"\nScraped {len(jobs)} jobs from RemoteOK:\n")
    for job in jobs:
        print(f"  {job.job_title} at {job.company}")
        print(f"    Location: {job.location}")
        print(f"    URL: {job.apply_url}\n")
