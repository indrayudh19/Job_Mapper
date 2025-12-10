"""
Vector Store Service - Pinecone integration for semantic job search.
Generates OpenAI embeddings and stores jobs in Pinecone.
"""

from typing import Optional
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from .config import get_settings
from .models import JobPosting


class VectorStore:
    """
    Manages Pinecone vector database for semantic job search.
    """

    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536
    INDEX_NAME = "india-jobs"

    def __init__(self):
        self.settings = get_settings()
        self.pc: Optional[Pinecone] = None
        self.index = None
        self.openai_client: Optional[OpenAI] = None
        
        self._initialize()

    def _initialize(self):
        """Initialize Pinecone and OpenAI clients."""
        if not self.settings.openai_api_key:
            print("Warning: OpenAI API key not configured")
            return
        
        if not self.settings.pinecone_api_key:
            print("Warning: Pinecone API key not configured")
            return
        
        try:
            # Initialize OpenAI
            self.openai_client = OpenAI(api_key=self.settings.openai_api_key)
            
            # Initialize Pinecone
            self.pc = Pinecone(api_key=self.settings.pinecone_api_key)
            
            # Create index if it doesn't exist
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.INDEX_NAME not in existing_indexes:
                print(f"Creating Pinecone index: {self.INDEX_NAME}")
                self.pc.create_index(
                    name=self.INDEX_NAME,
                    dimension=self.EMBEDDING_DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            self.index = self.pc.Index(self.INDEX_NAME)
            print(f"Pinecone initialized: {self.INDEX_NAME}")
            
        except Exception as e:
            print(f"Vector store initialization error: {e}")

    def generate_embedding(self, text: str) -> Optional[list[float]]:
        """
        Generate embedding for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.openai_client:
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=text[:8000]  # Limit text length
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            return None

    def upsert_job(self, job_id: str, job: JobPosting) -> bool:
        """
        Store a job posting in Pinecone.
        
        Args:
            job_id: Unique job identifier
            job: JobPosting object
            
        Returns:
            True if successful
        """
        if not self.index:
            return False
        
        # Create text for embedding
        text_to_embed = f"{job.job_title} at {job.company}. Location: {job.location}. {job.text or ''}"
        
        embedding = self.generate_embedding(text_to_embed)
        if not embedding:
            return False
        
        try:
            self.index.upsert(vectors=[{
                "id": job_id,
                "values": embedding,
                "metadata": {
                    "job_title": job.job_title,
                    "company": job.company,
                    "location": job.location,
                    "apply_url": job.apply_url or "",
                    "lat": job.lat,
                    "lng": job.lng,
                    "text": (job.text or "")[:1000]  # Limit metadata size
                }
            }])
            return True
        except Exception as e:
            print(f"Upsert error: {e}")
            return False

    def semantic_search(
        self, 
        query: str, 
        top_k: int = 10,
        location_filter: Optional[str] = None
    ) -> list[dict]:
        """
        Search for jobs semantically similar to query.
        
        Args:
            query: Search query (e.g., "software developer fresher Bangalore")
            top_k: Number of results to return
            location_filter: Optional location to filter by
            
        Returns:
            List of job results with scores
        """
        if not self.index:
            return []
        
        embedding = self.generate_embedding(query)
        if not embedding:
            return []
        
        try:
            # Build filter if location specified
            filter_dict = None
            if location_filter:
                filter_dict = {"location": {"$eq": location_filter}}
            
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            jobs = []
            for match in results.matches:
                job = {
                    "id": match.id,
                    "score": match.score,
                    **match.metadata
                }
                jobs.append(job)
            
            return jobs
            
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def index_sample_jobs(self) -> int:
        """
        Index the sample jobs from /pins endpoint for testing.
        
        Returns:
            Number of jobs indexed
        """
        from .routers.pins import SAMPLE_PINS
        
        count = 0
        for pin in SAMPLE_PINS:
            job = JobPosting(
                id=pin.id,
                job_title=pin.job_title,
                company=pin.company_name,
                location=pin.location_name,
                apply_url=pin.job_url,
                lat=pin.latitude,
                lng=pin.longitude,
                text=pin.description
            )
            
            if self.upsert_job(pin.id, job):
                count += 1
                print(f"  Indexed: {pin.job_title} at {pin.company_name}")
        
        return count

    def get_index_stats(self) -> dict:
        """Get statistics about the Pinecone index."""
        if not self.index:
            return {"error": "Index not initialized"}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_name": self.INDEX_NAME
            }
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


# Allow running directly for testing
if __name__ == "__main__":
    vs = get_vector_store()
    
    print("\n=== Vector Store Test ===\n")
    
    # Check stats
    stats = vs.get_index_stats()
    print(f"Index stats: {stats}")
    
    # Index sample jobs
    print("\nIndexing sample jobs...")
    count = vs.index_sample_jobs()
    print(f"Indexed {count} jobs")
    
    # Test search
    print("\nSearching for 'software developer Bangalore'...")
    results = vs.semantic_search("software developer Bangalore", top_k=3)
    for r in results:
        print(f"  [{r['score']:.3f}] {r['job_title']} at {r['company']} - {r['location']}")
