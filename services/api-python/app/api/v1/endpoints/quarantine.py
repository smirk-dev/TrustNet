"""
Quarantine Room API Endpoints  
MVP Priority #2: Human-AI Collaboration Interface
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import time
from datetime import datetime

from ....models.schemas import (
    QuarantineItem, UserVerdict, ErrorResponse
)
from ....core.database import db_manager
from ....core.logging import get_logger
from ....services.quarantine import quarantine_service

logger = get_logger(__name__)
router = APIRouter()


@router.get("/{verification_id}", response_model=QuarantineItem)
async def get_quarantine_item(verification_id: str):
    """
    Get quarantine item details for user review.
    
    Provides all necessary information for users to make informed decisions
    about uncertain content, including:
    - Original content with highlighted suspicious areas
    - AI's uncertainty explanation
    - Context questions for user consideration
    - Similar claims for comparison
    """
    try:
        logger.info(f"🏠 Getting quarantine item: {verification_id}")
        
        # Get claim and verdict from database
        claim = await db_manager.get_claim(verification_id)
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        verdict = await db_manager.get_verdict_by_claim(verification_id)
        if not verdict:
            raise HTTPException(status_code=404, detail="Verdict not found")
        
        # Get evidence for context
        evidence = await db_manager.get_evidence_by_claim(verification_id)
        
        # Create quarantine item details
        quarantine_item = await quarantine_service.create_quarantine_item(
            claim, verdict, evidence
        )
        
        return QuarantineItem(
            verification_id=verification_id,
            quarantine_item=quarantine_item,
            user_action_required=True,
            verdict_options=["legit", "misleading", "needs_more_info"],
            educational_context=quarantine_service.get_educational_context(verdict)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get quarantine item: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get quarantine item: {str(e)}")


@router.post("/{verification_id}/verdict")
async def submit_quarantine_verdict(
    verification_id: str,
    user_verdict: UserVerdict,
    request: Request
):
    """
    Submit user judgment on quarantined content.
    
    Records user decisions and reasoning for uncertain content, enabling:
    - Community wisdom aggregation
    - AI model improvement through human feedback
    - Transparent decision-making process
    - Educational value for other users
    """
    try:
        logger.info(f"⚖️ User verdict submission for: {verification_id}")
        
        # Validate that claim exists and is in quarantine
        claim = await db_manager.get_claim(verification_id)
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        verdict = await db_manager.get_verdict_by_claim(verification_id)
        if not verdict:
            raise HTTPException(status_code=404, detail="Verdict not found")
        
        # Ensure this content actually needs quarantine review
        if verdict.confidence_score >= 0.65:
            raise HTTPException(
                status_code=400, 
                detail="This content doesn't require quarantine review"
            )
        
        # Process user verdict
        result = await quarantine_service.process_user_verdict(
            verification_id,
            user_verdict,
            claim,
            verdict
        )
        
        # Update verdict with user input if needed
        if result["should_update_verdict"]:
            await quarantine_service.update_verdict_with_user_input(
                verdict.id,
                user_verdict,
                result["consensus_data"]
            )
        
        return {
            "verdict_id": result["verdict_id"],
            "message": "Thank you for your contribution to community verification!",
            "contribution_impact": result["impact_message"],
            "quarantine_resolved": result["resolved"],
            "consensus_reached": result.get("consensus_reached", False),
            "confidence_improvement": result.get("confidence_improvement", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to submit quarantine verdict: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit verdict: {str(e)}")


@router.get("/{verification_id}/consensus")
async def get_quarantine_consensus(verification_id: str):
    """
    Get current consensus data for quarantined content.
    
    Shows aggregated user opinions and reasoning to help users understand
    community wisdom and make informed decisions.
    """
    try:
        logger.info(f"📊 Getting consensus data for: {verification_id}")
        
        # Get consensus data from quarantine service
        consensus_data = await quarantine_service.get_consensus_data(verification_id)
        
        if not consensus_data:
            raise HTTPException(status_code=404, detail="No consensus data found")
        
        return consensus_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get consensus data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get consensus data: {str(e)}")


@router.get("/{verification_id}/similar")
async def get_similar_quarantine_cases(verification_id: str):
    """
    Get similar cases that have been resolved through quarantine.
    
    Provides educational examples of how similar content was evaluated
    by the community to help users learn detection patterns.
    """
    try:
        logger.info(f"🔍 Getting similar cases for: {verification_id}")
        
        # Get claim to analyze similarity
        claim = await db_manager.get_claim(verification_id)
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        # Find similar resolved cases
        similar_cases = await quarantine_service.find_similar_resolved_cases(claim)
        
        return {
            "similar_cases": similar_cases,
            "educational_value": "Learn from how the community evaluated similar content",
            "pattern_insights": quarantine_service.extract_pattern_insights(similar_cases)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get similar cases: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get similar cases: {str(e)}")


@router.get("/stats/community")
async def get_quarantine_community_stats():
    """
    Get community statistics for quarantine room effectiveness.
    
    Shows metrics like accuracy rates, consensus patterns, and 
    learning outcomes to demonstrate quarantine room value.
    """
    try:
        logger.info("📈 Getting quarantine community stats")
        
        stats = await quarantine_service.get_community_statistics()
        
        return {
            "total_quarantine_cases": stats["total_cases"],
            "resolved_cases": stats["resolved_cases"],
            "consensus_accuracy": stats["consensus_accuracy"],
            "average_confidence_improvement": stats["confidence_improvement"],
            "top_contributors": stats["top_contributors"],
            "learning_metrics": {
                "users_improved_detection": stats["users_improved"],
                "pattern_recognition_accuracy": stats["pattern_accuracy"],
                "cross_platform_application": stats["spillover_effect"]
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get community stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get community stats: {str(e)}")