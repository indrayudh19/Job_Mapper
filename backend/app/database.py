"""
Database configuration and session management.
Uses SQLite for development - can be migrated to PostgreSQL later.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file path
SQLITE_DATABASE_URL = "sqlite:///./jobs.db"

# Create engine with SQLite-specific settings
engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    Ensures proper cleanup after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    Call this on application startup.
    """
    from . import db_models  # Import to register models
    Base.metadata.create_all(bind=engine)
