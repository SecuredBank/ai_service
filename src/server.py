"""
SecuredBank AI Service
=========================

FastAPI application for banking AI services
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
from typing import List, Optional
import logging
from core.config import get_settings
from core.security import api_key_auth
from db.db import connectToPostgres
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application Lifecycle
@asynccontextmanager
async def lifecycle(app: FastAPI):
    # Startup
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.version} in {settings.environment} mode")
    
    # Initialize resources (database, models, etc.)
    await connectToPostgres()
    
    yield  # Run the application
    
    # Cleanup
    # await database.disconnect()
    logger.info("Shutting down application")

# Create FastAPI app with Lifecycle
app = FastAPI(
    title="SecuredBank AI Service",
    description="Secure API for banking AI services",
    version=get_settings().version,
    lifecycle=lifecycle,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().backend_cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (public)
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {
        "status": "healthy",
        "service": get_settings().app_name,
        "version": get_settings().version,
        "environment": get_settings().environment,
    }

# Protected root endpoint
@app.get("/", dependencies=[Depends(api_key_auth)])
async def root():
    """Root endpoint that requires API key authentication."""
    return {
        "message": "SecuredBank AI API is running",
        "version": get_settings().version,
        "environment": get_settings().environment,
    }

# Add exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Run the application
if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
    )