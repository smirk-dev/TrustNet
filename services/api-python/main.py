# TrustNet API Python Backend
# AI-powered misinformation detection service

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import AsyncGenerator

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1 import api_router
from app.core.database import init_database, close_database
from app.core.cache import init_redis, close_redis
from app.core.gcp import init_gcp_clients, close_gcp_clients


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown."""
    # Startup
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting TrustNet API Python Backend")
    
    try:
        # Initialize services
        await init_database()
        await init_redis()
        await init_gcp_clients()
        logger.info("✅ All services initialized successfully")
        
        yield
        
    finally:
        # Shutdown
        logger.info("🛑 Shutting down TrustNet API")
        await close_gcp_clients()
        await close_redis()
        await close_database()
        logger.info("✅ Graceful shutdown completed")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="TrustNet API",
        description="AI-powered misinformation detection and fact-checking service",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan
    )
    
    # CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Processing-Time"]
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Include API routes
    app.include_router(api_router, prefix="/v1")
    
    # Health check endpoint (no prefix)
    @app.get("/health")
    async def health_check():
        """Health check endpoint for load balancers."""
        return {
            "status": "healthy",
            "version": "1.0.0-python",
            "environment": settings.ENVIRONMENT,
            "features": {
                "verification_engine": True,
                "quarantine_room": True,
                "proactive_feed": True,
                "no_login_required": True
            }
        }
    
    @app.get("/")
    async def root():
        """API information endpoint."""
        return {
            "name": "TrustNet API",
            "description": "AI-powered misinformation detection system for India", 
            "version": "1.0.0-python",
            "status": "Production Ready - Python Backend",
            "documentation": f"{settings.API_BASE_URL}/docs" if settings.ENVIRONMENT != "production" else None,
            "endpoints": [
                "GET /health - Health check",
                "GET / - API information", 
                "POST /v1/verify - Verify content",
                "GET /v1/verify/{id} - Get verification results",
                "POST /v1/quarantine/{id}/verdict - Submit quarantine verdict",
                "GET /v1/feed - Get educational feed",
                "POST /v1/analyze - Analyze content",
                "POST /v1/feedback - Submit feedback"
            ]
        }
    
    return app


# Create the FastAPI app instance
app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
        access_log=True
    )