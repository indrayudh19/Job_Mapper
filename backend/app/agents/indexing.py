"""
Agent 5: Indexing Agent
Stores jobs in database and Pinecone vector store.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from .base import BaseAgent
from .geocoding import GeocodedJob
from ..config import get_settings
from ..database import SessionLocal
from ..db_models import JobPostingDB


class IndexingAgent(BaseAgent):
    """
    Indexes jobs in SQLite database and optionally Pinecone.
    """

    def __init__(self):
        self.settings = get_settings()
        self.pinecone_index = None
        self.embeddings = None
        
        # Initialize Pinecone if API key is available
        if self.settings.pinecone_api_key and self.settings.openai_api_key:
            self._init_pinecone()

    def _init_pinecone(self):
        """Initialize Pinecone connection."""
        try:
            from pinecone import Pinecone
            from langchain_openai import OpenAIEmbeddings
            
            pc = Pinecone(api_key=self.settings.pinecone_api_key)
            
            # Create index if it doesn't exist
            index_name = self.settings.pinecone_index_name
            if index_name not in pc.list_indexes().names():
                pc.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
            
            self.pinecone_index = pc.Index(index_name)
            self.embeddings = OpenAIEmbeddings(api_key=self.settings.openai_api_key)
            print(f"Pinecone initialized with index: {index_name}")
            
        except Exception as e:
            print(f"Pinecone initialization failed: {e}")
            self.pinecone_index = None

    @property
    def name(self) -> str:
        return "Indexing Agent"

    async def run(self, geocoded_jobs: list[GeocodedJob]) -> list[dict]:
        """
        Index jobs in database and vector store.
        
        Args:
            geocoded_jobs: List of GeocodedJob from Geocoding Agent
            
        Returns:
            List of indexed job records
        """
        indexed = []
        db = SessionLocal()
        
        try:
            for job in geocoded_jobs:
                job_id = str(uuid.uuid4())
                embedding_id = None
                
                # Generate embedding and store in Pinecone
                if self.pinecone_index and self.embeddings:
                    try:
                        text_to_embed = f"{job.job_title} at {job.company}. {job.description or ''}"
                        embedding = await self.embeddings.aembed_query(text_to_embed)
                        
                        self.pinecone_index.upsert(vectors=[{
                            "id": job_id,
                            "values": embedding,
                            "metadata": {
                                "job_title": job.job_title,
                                "company": job.company,
                                "location": job.location,
                                "apply_url": job.apply_url or ""
                            }
                        }])
                        embedding_id = job_id
                    except Exception as e:
                        print(f"Pinecone indexing error: {e}")
                
                # Store in SQLite database
                db_job = JobPostingDB(
                    id=job_id,
                    job_title=job.job_title,
                    company=job.company,
                    location=job.location,
                    apply_url=job.apply_url or "",
                    lat=job.lat,
                    lng=job.lng,
                    text=job.description,
                    source="pipeline",
                    scraped_at=datetime.utcnow(),
                    embedding_id=embedding_id
                )
                
                db.add(db_job)
                indexed.append({
                    "id": job_id,
                    "job_title": job.job_title,
                    "company": job.company,
                    "location": job.location,
                    "lat": job.lat,
                    "lng": job.lng,
                    "indexed_at": datetime.utcnow().isoformat()
                })
            
            db.commit()
            print(f"Indexed {len(indexed)} jobs to database")
            
        except Exception as e:
            print(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return indexed


# Allow running directly for testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = IndexingAgent()
        test_jobs = [
            GeocodedJob(
                job_title="Software Engineer",
                company="TechCorp",
                location="Bangalore",
                apply_url="https://example.com",
                lat=12.9716,
                lng=77.5946
            )
        ]
        results = await agent.run(test_jobs)
        
        print(f"\nIndexed {len(results)} jobs:\n")
        for r in results:
            print(f"  {r['job_title']} at {r['company']}")
            print(f"    ID: {r['id']}\n")
    
    asyncio.run(test())
