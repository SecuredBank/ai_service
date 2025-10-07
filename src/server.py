"""
SecuredBank AI Service
=========================

FastAPI application for banking AI services with MongoDB and JWT authentication
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
import logging
import uvicorn

from core.config import get_settings
from db.mongo import connect_to_mongo, close_mongo_connection, db
from middleware.auth_middleware import JWTBearer, RateLimiter
from controllers import auth_controllers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Application Lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.version} in {settings.environment} mode")
    
    try:
        # Initialize MongoDB connection
        await connect_to_mongo()
        logger.info("Connected to MongoDB")
        
        # Create indexes
        await db.db.users.create_index("email", unique=True)
        await db.db.users.create_index("username", unique=True)
        logger.info("Database indexes created")
        
        yield  # Run the application
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        # Cleanup
        await close_mongo_connection()
        logger.info("Application shutdown complete")

# Create FastAPI app with Lifecycle
app = FastAPI(
    title="SecuredBank AI Service",
    description="Secure API for banking AI services with JWT authentication",
    version=get_settings().version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json" if get_settings().environment != "production" else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().backend_cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
app.add_middleware(RateLimiter, times=100, seconds=60)  # 100 requests per minute

# Include routers
app.include_router(
    auth_controllers.router,
    prefix="/api/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
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