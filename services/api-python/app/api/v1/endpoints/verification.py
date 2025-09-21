"""
Content Verification API Endpoints
MVP Priority #1: Automated Verification Engine
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Union, List
import asyncio
import hashlib
import time
from datetime import datetime, timedelta

from ....models.schemas import (
    VerificationRequest, VerificationQueued, VerificationComplete, 
    QuarantineRequired, ClaimResult, ErrorResponse
)
from ....core.database import db_manager
from ....core.cache import cache_manager
from ....core.logging import get_logger
from ....services.analysis import analysis_service
from ....models.schemas import Claim, LanguageCode, SourceType

logger = get_logger(__name__)
router = APIRouter()


def create_text_hash(text: str) -> str:
    """Create hash of text for caching."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


@router.post("/", response_model=Union[VerificationQueued, VerificationComplete])
async def verify_content(
    request: VerificationRequest,
    background_tasks: BackgroundTasks,
    http_request: Request
):
    """
    Submit content for automated verification (MVP Core Feature).
    
    This endpoint accepts content for misinformation analysis and returns either:
    - Immediate results for simple content
    - Queued response for complex content requiring deeper analysis
    """
    start_time = time.time()
    
    try:
        logger.info(f"🔍 New verification request for text: {request.text[:100]}...")
        
        # Create text hash for caching
        text_hash = create_text_hash(request.text)
        
        # Check cache first
        cached_result = await cache_manager.get_cached_analysis(text_hash)
        if cached_result:
            logger.info(f"✅ Returning cached result for hash: {text_hash}")
            processing_time = int((time.time() - start_time) * 1000)
            
            return VerificationComplete(
                verification_id=cached_result["verification_id"],
                verification_card=cached_result["verification_card"],
                processing_time=processing_time,
                completed_at=datetime.utcnow(),
                note="Retrieved from cache"
            )
        
        # Create claim object
        claim = Claim(
            text=request.text,
            urls=request.urls,
            language=request.language or LanguageCode.ENGLISH,
            source_type=request.source_type or SourceType.WEB
        )
        
        # Store claim in database
        await db_manager.create_claim(claim)
        
        # Determine if we should process synchronously or asynchronously
        should_queue = (
            len(request.text) > 5000 or  # Long text
            (request.urls and len(request.urls) > 2) or  # Multiple URLs
            request.priority == "high"  # High priority always gets queued for thorough analysis
        )
        
        if should_queue:
            # Queue for background processing
            background_tasks.add_task(
                process_verification_async,
                claim.id,
                text_hash
            )
            
            return VerificationQueued(
                verification_id=claim.id,
                message="Content analysis in progress (DEVELOPMENT MODE)",
                text_preview=request.text[:100] + "..." if len(request.text) > 100 else request.text,
                check_url=f"/v1/verify/{claim.id}",
                estimated_completion=datetime.utcnow() + timedelta(seconds=30)
            )
        else:
            # Process immediately
            result = await analysis_service.analyze_content(claim)
            processing_time = int((time.time() - start_time) * 1000)
            
            # Cache the result
            cache_data = {
                "verification_id": claim.id,
                "verification_card": result.dict()
            }
            await cache_manager.cache_analysis_result(text_hash, cache_data, ttl=3600)
            
            return VerificationComplete(
                verification_id=claim.id,
                verification_card=result,
                processing_time=processing_time,
                completed_at=datetime.utcnow(),
                note="Processed in real-time"
            )
    
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.get("/{verification_id}", response_model=Union[VerificationComplete, QuarantineRequired, ClaimResult])
async def get_verification_result(verification_id: str):
    """
    Get verification results or quarantine status.
    
    Returns the status and results of a verification request, including:
    - Completed analysis with verification card
    - Quarantine status if content needs human review
    - Processing status if still analyzing
    """
    try:
        logger.info(f"📋 Getting verification result for: {verification_id}")
        
        # Get claim from database
        claim = await db_manager.get_claim(verification_id)
        if not claim:
            raise HTTPException(status_code=404, detail="Verification not found")
        
        # Get verdict
        verdict = await db_manager.get_verdict_by_claim(verification_id)
        
        if verdict:
            # Check if verdict indicates quarantine is needed
            if verdict.confidence_score < 0.65:  # Low confidence threshold
                return QuarantineRequired(
                    verification_id=verification_id,
                    quarantine_url=f"/v1/quarantine/{verification_id}",
                    confidence_score=verdict.confidence_score,
                    suspicious_indicators=[
                        indicator.description for indicator in verdict.manipulation_indicators
                    ],
                    message="Content requires human review due to uncertain AI analysis"
                )
            else:
                # Return completed verification
                verification_card = await analysis_service.create_verification_card(verdict)
                
                return VerificationComplete(
                    verification_id=verification_id,
                    verification_card=verification_card,
                    processing_time=verdict.processing_time_ms or 0,
                    completed_at=verdict.created_at,
                    note="Analysis completed successfully"
                )
        else:
            # Still processing
            return ClaimResult(
                claim_id=verification_id,
                status="processing",
                claim=claim,
                verdict=None,
                evidence=[],
                processing_completed_at=None
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get verification result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get verification result: {str(e)}")


async def process_verification_async(claim_id: str, text_hash: str):
    """Background task for processing verification requests."""
    try:
        logger.info(f"🔄 Starting async verification processing for: {claim_id}")
        
        # Get claim from database
        claim = await db_manager.get_claim(claim_id)
        if not claim:
            logger.error(f"❌ Claim not found for async processing: {claim_id}")
            return
        
        # Perform analysis
        result = await analysis_service.analyze_content(claim)
        
        # Cache the result
        cache_data = {
            "verification_id": claim_id,
            "verification_card": result.dict()
        }
        await cache_manager.cache_analysis_result(text_hash, cache_data, ttl=3600)
        
        logger.info(f"✅ Async verification completed for: {claim_id}")
        
    except Exception as e:
        logger.error(f"❌ Async verification failed for {claim_id}: {e}")