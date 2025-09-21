"""
TrustNet API v1 Router
Main router for all API endpoints.
"""

from fastapi import APIRouter

from .endpoints import verification, quarantine, feed, analysis, feedback

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(verification.router, prefix="/verify", tags=["verification"])
api_router.include_router(quarantine.router, prefix="/quarantine", tags=["quarantine"])
api_router.include_router(feed.router, prefix="/feed", tags=["educational-feed"])
api_router.include_router(analysis.router, prefix="/analyze", tags=["analysis"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])