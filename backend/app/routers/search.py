"""
Search router - Semantic job search using Pinecone.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from ..vectorstore import get_vector_store

router = APIRouter(prefix="/search", tags=["search"])


class SearchResult(BaseModel):
    """Individual search result."""
    id: str
    score: float
    job_title: str
    company: str
    location: str
    apply_url: str
    lat: float
    lng: float
    text: Optional[str] = None


class SearchResponse(BaseModel):
    """Response from search endpoint."""
    query: str
    results: list[SearchResult]
    total: int


@router.get("", response_model=SearchResponse)
async def semantic_search(
    q: str = Query(..., description="Search query, e.g., 'software developer Bangalore'"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return"),
    location: Optional[str] = Query(None, description="Filter by location")
):
    """
    Semantic search for jobs.
    
    Examples:
    - "software developer fresher roles"
    - "jobs in Bangalore"
    - "data analyst remote"
    """
    vs = get_vector_store()
    
    raw_results = vs.semantic_search(
        query=q,
        top_k=limit,
        location_filter=location
    )
    
    results = []
    for r in raw_results:
        results.append(SearchResult(
            id=r.get("id", ""),
            score=r.get("score", 0.0),
            job_title=r.get("job_title", ""),
            company=r.get("company", ""),
            location=r.get("location", ""),
            apply_url=r.get("apply_url", ""),
            lat=float(r.get("lat", 20.5937)),
            lng=float(r.get("lng", 78.9629)),
            text=r.get("text")
        ))
    
    return SearchResponse(
        query=q,
        results=results,
        total=len(results)
    )


@router.post("/index-sample")
async def index_sample_jobs():
    """
    Index sample jobs from /pins endpoint into Pinecone.
    Call this once to populate the vector store.
    """
    vs = get_vector_store()
    count = vs.index_sample_jobs()
    
    return {
        "message": f"Indexed {count} sample jobs",
        "indexed_count": count
    }


@router.get("/stats")
async def get_stats():
    """Get Pinecone index statistics."""
    vs = get_vector_store()
    return vs.get_index_stats()
