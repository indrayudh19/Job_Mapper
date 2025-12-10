"""
Agent 1: Web Search Agent
Searches for job pages in India using DuckDuckGo.
"""

from typing import Optional
from duckduckgo_search import DDGS
from .base import BaseAgent


class WebSearchAgent(BaseAgent):
    """
    Searches the web for job postings in India.
    Uses DuckDuckGo search (free, no API key required).
    """

    # Default search queries for Indian job market
    DEFAULT_QUERIES = [
        "software engineer jobs India hiring 2024",
        "developer jobs Bangalore hiring",
        "tech jobs Mumbai hiring now",
        "remote jobs India software",
        "startup jobs Delhi NCR",
    ]

    @property
    def name(self) -> str:
        return "Web Search Agent"

    async def run(
        self, 
        query: Optional[str] = None,
        max_results: int = 10
    ) -> list[dict]:
        """
        Search for job postings.
        
        Args:
            query: Search query (uses defaults if None)
            max_results: Maximum results per query
            
        Returns:
            List of search results with title, url, body
        """
        results = []
        queries = [query] if query else self.DEFAULT_QUERIES[:2]  # Limit for rate limiting
        
        with DDGS() as ddgs:
            for q in queries:
                try:
                    search_results = list(ddgs.text(
                        q,
                        region="in-en",  # India, English
                        max_results=max_results
                    ))
                    
                    for result in search_results:
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", ""),
                            "source_query": q
                        })
                except Exception as e:
                    print(f"Search error for '{q}': {e}")
                    continue
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_results = []
        for r in results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique_results.append(r)
        
        return unique_results


# Allow running directly for testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = WebSearchAgent()
        results = await agent.run(max_results=5)
        
        print(f"\nFound {len(results)} results:\n")
        for r in results[:5]:
            print(f"  {r['title']}")
            print(f"    URL: {r['url']}\n")
    
    asyncio.run(test())
