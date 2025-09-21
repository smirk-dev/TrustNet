"""
Educational Feed API Endpoints
MVP Priority #3: Proactive Homepage Feed
"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional
import time
from datetime import datetime

from ....models.schemas import (
    EducationalFeed, FeedItemDetail, EngagementFeedback, 
    TrendingPatterns, LanguageCode
)
from ....core.database import db_manager
from ....core.cache import cache_manager
from ....core.logging import get_logger
from ....services.educational import educational_service

logger = get_logger(__name__)
router = APIRouter()


@router.get("", response_model=EducationalFeed)
async def get_educational_feed(
    language: LanguageCode = Query(default=LanguageCode.ENGLISH, description="Content language"),
    limit: int = Query(default=10, ge=1, le=20, description="Number of items to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    category: Optional[str] = Query(default=None, description="Filter by category (health, politics, finance, social)")
):
    """
    Get educational content feed for homepage.
    
    Provides curated educational content including:
    - Real-world verified and debunked examples  
    - Interactive learning opportunities
    - Trending misinformation patterns
    - Skill-building exercises
    """
    try:
        logger.info(f"📚 Getting educational feed: lang={language}, limit={limit}, offset={offset}")
        
        # Check cache first
        cache_key = f"{language}_{limit}_{offset}_{category or 'all'}"
        cached_feed = await cache_manager.get_cached_educational_feed(cache_key)
        
        if cached_feed:
            logger.info("✅ Returning cached educational feed")
            return EducationalFeed(**cached_feed)
        
        # Get educational content from database/service
        feed_items = await educational_service.get_feed_items(
            language=language.value,
            limit=limit,
            offset=offset,
            category=category
        )
        
        # Get trending topics
        trending_topics = await educational_service.get_trending_topics(
            language=language.value
        )
        
        # Create feed response
        educational_feed = EducationalFeed(
            feed_items=feed_items,
            trending_topics=trending_topics,
            total_count=await educational_service.get_total_feed_count(language.value, category),
            language=language,
            last_updated=datetime.utcnow(),
            feed_metadata={
                "user_education_focus": True,
                "real_world_examples": True,
                "proactive_learning": True
            }
        )
        
        # Cache the result
        await cache_manager.cache_educational_feed(
            cache_key, 
            educational_feed.dict(), 
            ttl=1800  # 30 minutes
        )
        
        return educational_feed
        
    except Exception as e:
        logger.error(f"❌ Failed to get educational feed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get educational feed: {str(e)}")


@router.get("/{item_id}", response_model=FeedItemDetail)
async def get_feed_item_detail(item_id: str):
    """
    Get detailed educational content item.
    
    Provides comprehensive analysis including:
    - Step-by-step fact-checking methodology
    - Evidence chain with source analysis
    - Manipulation technique breakdown
    - Red flags and verification steps
    """
    try:
        logger.info(f"📖 Getting detailed feed item: {item_id}")
        
        # Get detailed item from educational service
        feed_item_detail = await educational_service.get_item_detail(item_id)
        
        if not feed_item_detail:
            raise HTTPException(status_code=404, detail="Feed item not found")
        
        # Get related content
        related_content = await educational_service.get_related_content(item_id)
        
        return FeedItemDetail(
            feed_item=feed_item_detail,
            related_content=related_content,
            user_actions={
                "can_share": True,
                "can_bookmark": True,
                "can_report_error": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get feed item detail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get feed item detail: {str(e)}")


@router.post("/{item_id}/engagement")
async def submit_feed_engagement(
    item_id: str,
    engagement: EngagementFeedback,
    request: Request
):
    """
    Submit engagement feedback on educational content.
    
    Records user interactions to improve content quality and personalization:
    - Helpfulness ratings
    - Learning outcomes
    - Content quality feedback
    - Time spent analysis
    """
    try:
        logger.info(f"👍 Recording engagement for feed item: {item_id}")
        
        # Validate that feed item exists
        feed_item = await educational_service.get_item_basic(item_id)
        if not feed_item:
            raise HTTPException(status_code=404, detail="Feed item not found")
        
        # Process engagement feedback
        engagement_result = await educational_service.process_engagement(
            item_id,
            engagement
        )
        
        return {
            "engagement_id": engagement_result["engagement_id"],
            "message": "Thank you for your feedback!",
            "contribution": "Your feedback helps improve content quality for all users",
            "learning_progress": engagement_result.get("learning_progress"),
            "recommendations": engagement_result.get("recommended_content", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to submit engagement: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit engagement: {str(e)}")


@router.get("/trends/patterns", response_model=TrendingPatterns)
async def get_trending_patterns(
    language: LanguageCode = Query(default=LanguageCode.ENGLISH),
    time_range: str = Query(default="7d", regex="^(7d|30d)$", description="Time range: 7d or 30d")
):
    """
    Get trending misinformation patterns (educational).
    
    Provides insights into current misinformation trends for educational purposes:
    - Common manipulation techniques
    - Emerging threat patterns
    - Detection tips and red flags
    - Related topic clusters
    """
    try:
        logger.info(f"📊 Getting trending patterns: lang={language}, range={time_range}")
        
        # Get trending patterns from service
        patterns_data = await educational_service.get_trending_patterns(
            language=language.value,
            time_range=time_range
        )
        
        return TrendingPatterns(**patterns_data)
        
    except Exception as e:
        logger.error(f"❌ Failed to get trending patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending patterns: {str(e)}")


@router.get("/categories/available")
async def get_available_categories():
    """
    Get available content categories.
    
    Returns list of available categories for filtering educational content.
    """
    try:
        categories = await educational_service.get_available_categories()
        
        return {
            "categories": categories,
            "descriptions": {
                "health": "Medical misinformation and health-related false claims",
                "politics": "Political misinformation and electoral manipulation", 
                "finance": "Financial scams and investment fraud",
                "social": "Social issues and community-related misinformation"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@router.get("/learning/progress")
async def get_learning_progress(
    user_id: Optional[str] = Query(default=None, description="User identifier for progress tracking")
):
    """
    Get user learning progress and achievements.
    
    Tracks educational progress including:
    - Manipulation detection skill improvement
    - Content categories mastered
    - Learning streaks and achievements
    - Recommended next steps
    """
    try:
        if not user_id:
            # Return general learning metrics for anonymous users
            return {
                "anonymous_user": True,
                "general_metrics": await educational_service.get_general_learning_metrics(),
                "message": "Sign up to track your personal learning progress"
            }
        
        # Get personalized learning progress
        progress = await educational_service.get_user_learning_progress(user_id)
        
        return progress
        
    except Exception as e:
        logger.error(f"❌ Failed to get learning progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get learning progress: {str(e)}")


@router.post("/content/suggest")
async def suggest_educational_content(
    suggestion: dict,
    request: Request
):
    """
    Submit suggestions for new educational content.
    
    Allows community to suggest new misinformation examples or educational topics.
    """
    try:
        logger.info("💡 New content suggestion received")
        
        # Process content suggestion
        result = await educational_service.process_content_suggestion(suggestion)
        
        return {
            "suggestion_id": result["suggestion_id"],
            "message": "Thank you for your suggestion!",
            "status": "under_review",
            "estimated_review_time": "3-5 business days"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to process suggestion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process suggestion: {str(e)}")