"""
SQLAlchemy ORM models for database persistence.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime
from .database import Base
import uuid


class JobPostingDB(Base):
    """
    SQLAlchemy model for job postings stored in the database.
    """
    __tablename__ = "job_postings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False, index=True)
    apply_url = Column(String(500), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    text = Column(Text, nullable=True)  # Full job description
    source = Column(String(255), nullable=True)  # Where job was found
    scraped_at = Column(DateTime, nullable=True)  # When job was scraped
    embedding_id = Column(String(255), nullable=True)  # Pinecone vector ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<JobPosting {self.job_title} at {self.company}>"
