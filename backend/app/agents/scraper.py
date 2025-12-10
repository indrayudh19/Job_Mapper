"""
Agent 2: Scraper Agent
Scrapes job content from URLs using existing scrapers.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
from .base import BaseAgent


class ScraperAgent(BaseAgent):
    """
    Scrapes job posting content from URLs.
    Uses requests + BeautifulSoup for simple HTML parsing.
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    @property
    def name(self) -> str:
        return "Scraper Agent"

    async def run(self, urls: list[dict]) -> list[dict]:
        """
        Scrape content from URLs.
        
        Args:
            urls: List of dicts with 'url' key from Web Search Agent
            
        Returns:
            List of scraped content with text
        """
        scraped = []
        
        for item in urls[:10]:  # Limit to prevent too many requests
            url = item.get("url", "")
            if not url:
                continue
            
            content = await self._scrape_url(url)
            if content:
                scraped.append({
                    "url": url,
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "content": content,
                })
        
        return scraped

    async def _scrape_url(self, url: str) -> Optional[str]:
        """Scrape text content from a single URL."""
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Get text content
            text = soup.get_text(separator="\n", strip=True)
            
            # Limit text length
            return text[:5000] if text else None
            
        except Exception as e:
            print(f"Scrape error for {url}: {e}")
            return None


# Allow running directly for testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = ScraperAgent()
        test_urls = [
            {"url": "https://remoteok.com/remote-jobs", "title": "RemoteOK Jobs"}
        ]
        results = await agent.run(test_urls)
        
        print(f"\nScraped {len(results)} pages:\n")
        for r in results:
            print(f"  {r['title']}")
            print(f"    Content length: {len(r['content'])} chars\n")
    
    asyncio.run(test())
