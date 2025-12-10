"""
India Job Map - FastAPI Backend

Main application entry point with CORS configuration
for frontend communication.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import pins, search
from .database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - initializes database on startup."""
    init_db()
    yield


# Create FastAPI application
app = FastAPI(
    title="India Job Map API",
    description="Backend API for the India Job Map agentic system",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for frontend communication
# Allow requests from Vite dev server (default port 5173)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pins.router)
app.include_router(search.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "India Job Map API is running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "api": "India Job Map",
        "version": "0.1.0"
    }
