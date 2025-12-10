"""
Pydantic models for the India Job Map API.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobPin(BaseModel):
    """Model representing a job pin on the map."""
    
    id: str
    company_name: str
    job_title: str
    latitude: float
    longitude: float
    job_url: str
    location_name: str
    description: Optional[str] = None


class JobPinResponse(BaseModel):
    """Response model for the /pins endpoint."""
    
    pins: list[JobPin]
    total: int


class JobPosting(BaseModel):
    """
    Comprehensive job posting model for database storage and API.
    Fields match the flowchart: job_title, company, location, apply_url, lat, lng, text
    """
    
    id: Optional[str] = None
    job_title: str
    company: str
    location: str
    apply_url: str
    lat: float
    lng: float
    text: Optional[str] = None  # Full job description
    source: Optional[str] = None  # Where job was found (e.g., "linkedin", "indeed")
    scraped_at: Optional[datetime] = None
    embedding_id: Optional[str] = None  # Pinecone vector ID for RAG
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Allow ORM model conversion


class JobPostingCreate(BaseModel):
    """Model for creating new job postings."""
    
    job_title: str
    company: str
    location: str
    apply_url: str
    lat: float
    lng: float
    text: Optional[str] = None
    source: Optional[str] = None


class JobPostingResponse(BaseModel):
    """Response model for job posting endpoints."""
    
    postings: list[JobPosting]
    total: int
