"""
Secure configuration management using pydantic-settings.
Loads API keys from .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # OpenAI
    openai_api_key: str = ""
    
    # Pinecone
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "india-jobs"
    
    # Vector DB choice
    use_local_vectordb: bool = False
    
    # Database
    database_url: str = "sqlite:///./jobs.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reading .env multiple times.
    """
    return Settings()
