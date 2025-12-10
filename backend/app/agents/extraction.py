"""
Agent 3: Extraction Agent
Uses LLM to extract structured job data from raw text.
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from .base import BaseAgent
from ..config import get_settings


class ExtractedJob(BaseModel):
    """Structured job data extracted by LLM."""
    job_title: str = Field(description="The job title/position")
    company: str = Field(description="The company name")
    location: str = Field(description="Job location (city, state, or Remote)")
    apply_url: Optional[str] = Field(default=None, description="URL to apply")
    description: Optional[str] = Field(default=None, description="Brief job description")


class ExtractionAgent(BaseAgent):
    """
    Extracts structured job information from raw text using OpenAI.
    """

    EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
        ("system", """You are a job posting extractor. Extract job information from the provided text.
Focus on finding:
- Job title/position name
- Company name
- Location (city in India, or "Remote")
- Application URL if present
- Brief description (1-2 sentences)

If information is not found, use reasonable defaults or leave empty.
Respond ONLY with valid JSON matching the required format."""),
        ("human", "Extract job posting information from this text:\n\n{text}")
    ])

    def __init__(self):
        settings = get_settings()
        self.llm = None
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",  # Cost-effective model
                temperature=0,
                api_key=settings.openai_api_key
            )

    @property
    def name(self) -> str:
        return "Extraction Agent"

    async def run(self, scraped_content: list[dict]) -> list[ExtractedJob]:
        """
        Extract structured job data from scraped content.
        
        Args:
            scraped_content: List of dicts with 'content' key from Scraper Agent
            
        Returns:
            List of ExtractedJob objects
        """
        if not self.llm:
            print("Warning: OpenAI API key not configured. Using mock extraction.")
            return self._mock_extract(scraped_content)
        
        extracted_jobs = []
        
        for item in scraped_content:
            content = item.get("content", "")
            if not content:
                continue
            
            try:
                # Use structured output
                structured_llm = self.llm.with_structured_output(ExtractedJob)
                result = await structured_llm.ainvoke(
                    self.EXTRACTION_PROMPT.format_messages(text=content[:3000])
                )
                
                # Add URL from original if not extracted
                if not result.apply_url:
                    result.apply_url = item.get("url", "")
                
                extracted_jobs.append(result)
                
            except Exception as e:
                print(f"Extraction error: {e}")
                continue
        
        return extracted_jobs

    def _mock_extract(self, scraped_content: list[dict]) -> list[ExtractedJob]:
        """Mock extraction when API key is not available."""
        jobs = []
        for item in scraped_content:
            jobs.append(ExtractedJob(
                job_title=item.get("title", "Software Engineer"),
                company="Unknown Company",
                location="India",
                apply_url=item.get("url", ""),
                description=item.get("snippet", "")[:200]
            ))
        return jobs


# Allow running directly for testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = ExtractionAgent()
        test_content = [{
            "content": "Software Engineer at TechCorp. Location: Bangalore, India. Apply at techcorp.com/careers",
            "url": "https://example.com",
            "title": "Test Job"
        }]
        results = await agent.run(test_content)
        
        print(f"\nExtracted {len(results)} jobs:\n")
        for job in results:
            print(f"  {job.job_title} at {job.company}")
            print(f"    Location: {job.location}\n")
    
    asyncio.run(test())
