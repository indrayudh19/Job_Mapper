"""
Hacker News "Who's Hiring" thread scraper.
Scrapes job postings from monthly HN hiring threads.
"""

import re
from bs4 import BeautifulSoup
from .base import BaseScraper
from ..models import JobPostingCreate


class HNHiringScraper(BaseScraper):
    """
    Scraper for Hacker News "Who's Hiring" monthly threads.
    These threads contain real job postings from tech companies.
    """

    # Recent "Who's Hiring" thread - December 2024
    # Can be updated to latest thread ID
    THREAD_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    
    # Default to a recent hiring thread
    DEFAULT_THREAD_ID = 42575537  # December 2024 Who's Hiring

    @property
    def source_name(self) -> str:
        return "hackernews"

    def _extract_company_from_comment(self, text: str) -> str:
        """Extract company name from HN comment (usually first line)."""
        if not text:
            return "Unknown Company"
        
        # First line usually has company name
        first_line = text.split('\n')[0].strip()
        
        # Remove common patterns
        first_line = re.sub(r'\s*\|.*', '', first_line)  # Remove after |
        first_line = re.sub(r'\s*-.*', '', first_line)   # Remove after -
        first_line = re.sub(r'\(.*?\)', '', first_line)  # Remove parentheses
        
        return first_line[:100] if first_line else "Unknown Company"

    def _extract_location(self, text: str) -> str:
        """Extract location from comment text."""
        if not text:
            return "Remote"
        
        # Common location patterns
        location_patterns = [
            r'(?:Location|Based in|Office in)[:\s]+([^|\n]+)',
            r'(Remote|On-?site|Hybrid)',
            r'(San Francisco|New York|London|Berlin|India|Bangalore|Mumbai|Delhi)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:100]
        
        return "Remote"

    def _extract_url(self, text: str) -> str:
        """Extract apply URL from comment."""
        if not text:
            return ""
        
        # Find URLs in text
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Prefer job/career URLs
        for url in urls:
            if any(keyword in url.lower() for keyword in ['job', 'career', 'apply', 'hire', 'lever', 'greenhouse']):
                return url
        
        return urls[0] if urls else ""

    def scrape(self, thread_id: int = None, limit: int = 20) -> list[JobPostingCreate]:
        """
        Scrape job postings from a HN "Who's Hiring" thread.
        
        Args:
            thread_id: HN item ID of the hiring thread
            limit: Maximum number of jobs to return
            
        Returns:
            List of JobPostingCreate objects
        """
        jobs = []
        thread_id = thread_id or self.DEFAULT_THREAD_ID
        
        # Fetch the thread to get comment IDs
        thread_url = self.THREAD_URL.format(item_id=thread_id)
        thread_data = self.fetch_json(thread_url)
        
        if not thread_data:
            print(f"Failed to fetch HN thread {thread_id}")
            return jobs

        comment_ids = thread_data.get("kids", [])[:limit]
        
        for comment_id in comment_ids:
            comment_url = self.THREAD_URL.format(item_id=comment_id)
            comment_data = self.fetch_json(comment_url)
            
            if not comment_data or comment_data.get("deleted"):
                continue
            
            text = comment_data.get("text", "")
            if not text:
                continue
            
            # Parse HTML entities
            soup = BeautifulSoup(text, 'html.parser')
            clean_text = soup.get_text()
            
            try:
                company = self._extract_company_from_comment(clean_text)
                location = self._extract_location(clean_text)
                apply_url = self._extract_url(text)
                
                if not apply_url:
                    # Use HN comment as fallback
                    apply_url = f"https://news.ycombinator.com/item?id={comment_id}"
                
                job_posting = JobPostingCreate(
                    job_title="Software Engineer",  # HN jobs are usually engineering
                    company=company,
                    location=location,
                    apply_url=apply_url,
                    lat=20.5937,  # Default to India center
                    lng=78.9629,
                    text=clean_text[:2000],  # Limit text length
                    source=self.source_name
                )
                jobs.append(job_posting)
            except Exception as e:
                print(f"Error parsing HN comment {comment_id}: {e}")
                continue

        return jobs


# Allow running directly for testing
if __name__ == "__main__":
    scraper = HNHiringScraper()
    jobs = scraper.scrape(limit=5)
    
    print(f"\nScraped {len(jobs)} jobs from Hacker News:\n")
    for job in jobs:
        print(f"  {job.job_title} at {job.company}")
        print(f"    Location: {job.location}")
        print(f"    URL: {job.apply_url}\n")
