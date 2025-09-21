"""
API v1 Router Configuration
Combines all endpoint modules into a unified API router
"""

from fastapi import APIRouter
from .endpoints import verification, quarantine, feed, analysis, feedback

# Create the main API v1 router
api_router = APIRouter()

# Include all endpoint routers with their respective prefixes and tags
api_router.include_router(
    verification.router,
    prefix="/verify",
    tags=["Verification"],
    responses={
        404: {"description": "Content not found"},
        500: {"description": "Internal server error"}
    }
)

api_router.include_router(
    quarantine.router,
    prefix="/quarantine",
    tags=["Quarantine Room"],
    responses={
        404: {"description": "Quarantine item not found"},
        500: {"description": "Internal server error"}
    }
)

api_router.include_router(
    feed.router,
    prefix="/feed",
    tags=["Educational Feed"],
    responses={
        404: {"description": "Feed content not found"},
        500: {"description": "Internal server error"}
    }
)

api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["Content Analysis"],
    responses={
        404: {"description": "Analysis not found"},
        500: {"description": "Internal server error"}
    }
)

api_router.include_router(
    feedback.router,
    prefix="/feedback",
    tags=["Community Feedback"],
    responses={
        404: {"description": "Feedback not found"},
        500: {"description": "Internal server error"}
    }
)