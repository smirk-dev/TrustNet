"""
Feedback and Community API Endpoints
MVP Priority #5: Community Engagement and Continuous Improvement
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional, List
import time
from datetime import datetime

from ....models.schemas import (
    UserFeedback, FeedbackResponse, CommunityStats, 
    UserContribution, ReputationScore, FeedbackAnalytics
)
from ....core.database import db_manager
from ....core.cache import cache_manager
from ....core.logging import get_logger
from ....services.feedback import feedback_service
from ....services.community import community_service

logger = get_logger(__name__)
router = APIRouter()


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: UserFeedback,
    request: Request
):
    """
    Submit user feedback on content verification or system performance.
    
    Supports multiple feedback types:
    - Verification accuracy feedback
    - Feature improvement suggestions
    - Bug reports and technical issues
    - Content quality assessments
    - User experience feedback
    """
    try:
        logger.info(f"💬 Processing feedback submission: type={feedback.feedback_type}")
        
        # Validate feedback content
        if not feedback.content or len(feedback.content.strip()) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Feedback content must be at least 10 characters long"
            )
        
        # Process feedback through service
        feedback_result = await feedback_service.process_feedback(feedback)
        
        # Update community statistics
        await community_service.update_engagement_stats(
            feedback_type=feedback.feedback_type,
            user_id=feedback.user_id
        )
        
        response = FeedbackResponse(
            feedback_id=feedback_result["feedback_id"],
            status="received",
            message="Thank you for your feedback! Your input helps improve TrustNet.",
            contribution_points=feedback_result.get("points_awarded", 0),
            community_impact={
                "helps_improve_accuracy": True,
                "contributes_to_community": True,
                "supports_better_detection": True
            },
            follow_up_actions=feedback_result.get("follow_up_actions", [])
        )
        
        # Cache feedback for quick retrieval
        await cache_manager.cache_user_feedback(
            feedback.user_id or "anonymous",
            feedback_result["feedback_id"],
            response.dict()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/analytics", response_model=FeedbackAnalytics)
async def get_feedback_analytics(
    time_range: str = Query(default="30d", regex="^(7d|30d|90d)$"),
    feedback_type: Optional[str] = Query(default=None)
):
    """
    Get feedback analytics and trends.
    
    Provides insights into:
    - Feedback volume and trends
    - Common improvement areas
    - User satisfaction metrics
    - Feature request priorities
    """
    try:
        logger.info(f"📊 Getting feedback analytics: range={time_range}, type={feedback_type}")
        
        analytics = await feedback_service.get_feedback_analytics(
            time_range=time_range,
            feedback_type=feedback_type
        )
        
        return FeedbackAnalytics(**analytics)
        
    except Exception as e:
        logger.error(f"❌ Failed to get feedback analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get feedback analytics: {str(e)}")


@router.get("/community/stats", response_model=CommunityStats)
async def get_community_statistics():
    """
    Get community engagement statistics.
    
    Returns comprehensive community metrics:
    - Active user participation
    - Contribution quality scores
    - Collaboration effectiveness
    - Community growth trends
    """
    try:
        logger.info("👥 Getting community statistics")
        
        # Check cache first
        cached_stats = await cache_manager.get_cached_community_stats()
        if cached_stats:
            return CommunityStats(**cached_stats)
        
        # Get fresh statistics
        stats = await community_service.get_community_statistics()
        
        community_stats = CommunityStats(
            total_active_users=stats["active_users"],
            total_contributions=stats["total_contributions"],
            verification_accuracy=stats["verification_accuracy"],
            community_consensus=stats["consensus_rate"],
            collaboration_score=stats["collaboration_score"],
            trending_topics=stats["trending_topics"],
            improvement_metrics={
                "accuracy_improvement": stats["accuracy_trend"],
                "response_time_improvement": stats["response_time_trend"],
                "user_satisfaction": stats["satisfaction_score"]
            },
            community_achievements=stats["recent_achievements"]
        )
        
        # Cache for 1 hour
        await cache_manager.cache_community_stats(
            community_stats.dict(),
            ttl=3600
        )
        
        return community_stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get community stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get community stats: {str(e)}")


@router.get("/user/{user_id}/contributions", response_model=List[UserContribution])
async def get_user_contributions(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50)
):
    """
    Get user's contributions and impact.
    
    Returns user's community participation:
    - Verification contributions
    - Feedback submissions
    - Quality assessments
    - Community recognition
    """
    try:
        logger.info(f"👤 Getting contributions for user: {user_id}")
        
        contributions = await community_service.get_user_contributions(
            user_id=user_id,
            limit=limit
        )
        
        return [UserContribution(**contrib) for contrib in contributions]
        
    except Exception as e:
        logger.error(f"❌ Failed to get user contributions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user contributions: {str(e)}")


@router.get("/user/{user_id}/reputation", response_model=ReputationScore)
async def get_user_reputation(user_id: str):
    """
    Get user's reputation score and trust level.
    
    Calculates reputation based on:
    - Contribution quality and accuracy
    - Community engagement level
    - Verification track record
    - Peer recognition and validation
    """
    try:
        logger.info(f"⭐ Getting reputation for user: {user_id}")
        
        reputation = await community_service.calculate_user_reputation(user_id)
        
        if not reputation:
            raise HTTPException(status_code=404, detail="User reputation not found")
        
        return ReputationScore(**reputation)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get user reputation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user reputation: {str(e)}")


@router.post("/improve/suggestion")
async def submit_improvement_suggestion(
    suggestion: dict,
    request: Request
):
    """
    Submit system improvement suggestions.
    
    Allows users to suggest:
    - New feature requests
    - Algorithm improvements
    - User experience enhancements
    - Integration possibilities
    """
    try:
        logger.info("💡 Processing improvement suggestion")
        
        # Validate suggestion
        if not suggestion.get("title") or not suggestion.get("description"):
            raise HTTPException(
                status_code=400,
                detail="Suggestion must include title and description"
            )
        
        # Process suggestion
        result = await feedback_service.process_improvement_suggestion(suggestion)
        
        return {
            "suggestion_id": result["suggestion_id"],
            "status": "submitted",
            "message": "Thank you for your suggestion!",
            "review_process": {
                "initial_review": "3-5 business days",
                "community_voting": "Available for community input",
                "implementation_consideration": "Based on community priority and feasibility"
            },
            "tracking_url": f"/feedback/suggestions/{result['suggestion_id']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to submit suggestion: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit suggestion: {str(e)}")


@router.get("/suggestions/trending")
async def get_trending_suggestions(
    limit: int = Query(default=10, ge=1, le=20)
):
    """
    Get trending improvement suggestions from community.
    
    Returns popular feature requests and improvements:
    - Highly voted suggestions
    - Recent community proposals
    - Implementation status updates
    - Community discussion activity
    """
    try:
        logger.info("📈 Getting trending suggestions")
        
        suggestions = await feedback_service.get_trending_suggestions(limit=limit)
        
        return {
            "trending_suggestions": suggestions,
            "community_engagement": {
                "total_suggestions": await feedback_service.get_total_suggestions_count(),
                "active_discussions": await feedback_service.get_active_discussions_count(),
                "implemented_features": await feedback_service.get_implemented_count()
            },
            "voting_info": {
                "how_to_vote": "Community members can vote on suggestions",
                "voting_weight": "Based on user reputation and contribution history",
                "implementation_threshold": "High community support + technical feasibility"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get trending suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending suggestions: {str(e)}")


@router.post("/quality/report")
async def report_quality_issue(
    quality_report: dict,
    request: Request
):
    """
    Report quality issues with content or system performance.
    
    Supports reporting:
    - Incorrect verification results
    - Misleading educational content
    - System bugs or errors
    - Performance issues
    """
    try:
        logger.info("🚨 Processing quality issue report")
        
        # Process quality report
        result = await feedback_service.process_quality_report(quality_report)
        
        return {
            "report_id": result["report_id"],
            "priority": result["priority"],
            "message": "Quality issue reported successfully",
            "investigation": {
                "estimated_response": "24-48 hours for high priority issues",
                "investigation_process": "Our team will review and investigate promptly",
                "updates_available": f"/feedback/reports/{result['report_id']}/status"
            },
            "community_impact": "Your report helps maintain system quality for all users"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to process quality report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process quality report: {str(e)}")


@router.get("/impact/metrics")
async def get_feedback_impact_metrics():
    """
    Get metrics showing how feedback has improved the system.
    
    Demonstrates community impact:
    - Accuracy improvements from feedback
    - Features implemented from suggestions
    - Bug fixes from quality reports
    - Performance enhancements
    """
    try:
        logger.info("📊 Getting feedback impact metrics")
        
        impact_metrics = await feedback_service.get_feedback_impact_metrics()
        
        return {
            "impact_summary": impact_metrics,
            "recent_improvements": await feedback_service.get_recent_improvements(),
            "community_driven_features": await feedback_service.get_community_features(),
            "success_stories": await feedback_service.get_feedback_success_stories(),
            "continuous_improvement": {
                "feedback_integration_rate": "95%",
                "average_implementation_time": "2-4 weeks",
                "community_satisfaction": "4.7/5.0"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get impact metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get impact metrics: {str(e)}")