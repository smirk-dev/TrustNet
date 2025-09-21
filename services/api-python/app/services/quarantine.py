"""
Quarantine Service
Handles quarantine room operations for human-AI collaboration.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json

from ..core.database import db_manager
from ..core.cache import cache_manager
from ..core.logging import get_logger
from ..models.schemas import QuarantineItem, UserVerdict, Claim

logger = get_logger(__name__)


class QuarantineService:
    """Service for managing quarantine room operations."""
    
    def __init__(self):
        self.logger = logger
    
    async def create_quarantine_item(
        self, 
        claim_id: str, 
        verdict_id: str, 
        reason: str, 
        confidence_score: float,
        automated_verdict: str
    ) -> QuarantineItem:
        """Create a new quarantine item for human review."""
        try:
            quarantine_data = {
                "claim_id": claim_id,
                "verdict_id": verdict_id,
                "reason": reason,
                "confidence_score": confidence_score,
                "automated_verdict": automated_verdict,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store in database
            quarantine_id = f"quarantine_{claim_id}_{verdict_id}"
            await db_manager.store_analysis(quarantine_id, quarantine_data)
            
            # Create QuarantineItem model
            quarantine_item = QuarantineItem(
                verification_id=claim_id,
                quarantine_item=quarantine_data,
                user_action_required=True,
                verdict_options=["legit", "misleading", "needs_more_info"],
                educational_context=f"This {automated_verdict} claim requires human review with {confidence_score:.2f} confidence."
            )
            
            logger.info(f"Created quarantine item: {quarantine_id}")
            return quarantine_item
            
        except Exception as e:
            logger.error(f"Failed to create quarantine item: {e}")
            raise
    
    def get_educational_context(self, verdict: str) -> Dict[str, Any]:
        """Get educational context for a verdict."""
        try:
            educational_contexts = {
                "misleading": {
                    "explanation": "This content contains misleading information that could deceive readers.",
                    "resources": [
                        "How to identify misleading claims",
                        "Understanding bias in information"
                    ],
                    "examples": ["Common misleading patterns", "Real-world examples"]
                },
                "unverified": {
                    "explanation": "This content cannot be verified with current available evidence.",
                    "resources": [
                        "How to verify information",
                        "Reliable source identification"
                    ],
                    "examples": ["Verification techniques", "Source credibility assessment"]
                },
                "disputed": {
                    "explanation": "This content has conflicting evidence or expert opinions.",
                    "resources": [
                        "Understanding scientific consensus",
                        "Evaluating conflicting evidence"
                    ],
                    "examples": ["Handling uncertainty", "Expert disagreement analysis"]
                }
            }
            
            return educational_contexts.get(verdict.lower(), {
                "explanation": "Content requires human review for accurate assessment.",
                "resources": ["General fact-checking guidelines"],
                "examples": ["Standard verification practices"]
            })
            
        except Exception as e:
            logger.error(f"Failed to get educational context: {e}")
            return {"explanation": "Educational context unavailable", "resources": [], "examples": []}
    
    async def process_user_verdict(
        self, 
        quarantine_id: str, 
        user_verdict: UserVerdict
    ) -> Dict[str, Any]:
        """Process user verdict for quarantine item."""
        try:
            # Get quarantine item
            quarantine_data = await db_manager.get_analysis(quarantine_id)
            if not quarantine_data:
                raise ValueError(f"Quarantine item not found: {quarantine_id}")
            
            # Update with user verdict
            update_data = {
                "user_verdict": user_verdict.user_verdict,
                "user_confidence": user_verdict.confidence,
                "user_reasoning": user_verdict.reasoning,
                "user_expertise": user_verdict.user_expertise.value if user_verdict.user_expertise else "general_public",
                "status": "reviewed",
                "reviewed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await db_manager.update_analysis(quarantine_id, update_data)
            
            result = {
                "status": "processed",
                "quarantine_id": quarantine_id,
                "user_verdict": user_verdict.user_verdict,
                "confidence_improvement": user_verdict.confidence - quarantine_data.get("confidence_score", 0),
                "processed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Processed user verdict for quarantine: {quarantine_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process user verdict: {e}")
            raise
    
    async def update_verdict_with_user_input(
        self, 
        verdict_id: str, 
        user_verdict: UserVerdict
    ) -> bool:
        """Update verdict with user input."""
        try:
            # Get original verdict
            verdict_data = await db_manager.get_analysis(f"verdict_{verdict_id}")
            
            if verdict_data:
                # Update verdict with human input
                update_data = {
                    "human_verdict": user_verdict.user_verdict,
                    "human_confidence": user_verdict.confidence,
                    "human_reasoning": user_verdict.reasoning,
                    "consensus_score": (verdict_data.get("confidence", 0) + user_verdict.confidence) / 2,
                    "updated_by_human": True,
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                await db_manager.update_analysis(f"verdict_{verdict_id}", update_data)
                logger.info(f"Updated verdict with user input: {verdict_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update verdict with user input: {e}")
            return False
    
    async def get_consensus_data(self, verification_id: str) -> Dict[str, Any]:
        """Get consensus data for verification."""
        try:
            # Mock consensus data - in production this would aggregate multiple user inputs
            consensus_data = {
                "verification_id": verification_id,
                "total_reviews": 5,
                "consensus_verdict": "misleading",
                "agreement_percentage": 80.0,
                "confidence_distribution": {
                    "high": 3,
                    "medium": 2,
                    "low": 0
                },
                "reviewer_expertise": {
                    "expert": 2,
                    "knowledgeable": 2,
                    "general": 1
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return consensus_data
            
        except Exception as e:
            logger.error(f"Failed to get consensus data: {e}")
            return {"error": "Consensus data unavailable"}
    
    async def find_similar_resolved_cases(self, claim: str) -> List[Dict[str, Any]]:
        """Find similar resolved cases for pattern learning."""
        try:
            # Mock similar cases - in production this would use semantic search
            similar_cases = [
                {
                    "case_id": "case_001",
                    "claim": "Similar health misinformation claim",
                    "verdict": "misleading",
                    "confidence": 0.92,
                    "resolution_method": "expert_consensus",
                    "similarity_score": 0.85,
                    "resolved_at": "2024-01-15T10:30:00Z"
                },
                {
                    "case_id": "case_002", 
                    "claim": "Related false information about topic",
                    "verdict": "false",
                    "confidence": 0.88,
                    "resolution_method": "fact_check",
                    "similarity_score": 0.78,
                    "resolved_at": "2024-01-10T14:20:00Z"
                }
            ]
            
            return similar_cases
            
        except Exception as e:
            logger.error(f"Failed to find similar cases: {e}")
            return []
    
    def extract_pattern_insights(self, similar_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract pattern insights from similar cases."""
        try:
            if not similar_cases:
                return {"insights": [], "patterns": []}
            
            insights = {
                "common_verdicts": {},
                "average_confidence": 0.0,
                "resolution_methods": {},
                "patterns": [
                    "Similar claims often contain health misinformation",
                    "Expert consensus provides high confidence verdicts",
                    "Fact-checking resources are effective for verification"
                ]
            }
            
            # Analyze verdicts
            for case in similar_cases:
                verdict = case.get("verdict", "unknown")
                insights["common_verdicts"][verdict] = insights["common_verdicts"].get(verdict, 0) + 1
                
                method = case.get("resolution_method", "unknown")
                insights["resolution_methods"][method] = insights["resolution_methods"].get(method, 0) + 1
            
            # Calculate average confidence
            confidences = [case.get("confidence", 0) for case in similar_cases]
            insights["average_confidence"] = sum(confidences) / len(confidences) if confidences else 0.0
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to extract pattern insights: {e}")
            return {"insights": [], "patterns": []}
    
    async def get_community_statistics(self) -> Dict[str, Any]:
        """Get community statistics for quarantine room."""
        try:
            # Mock community statistics - in production this would aggregate real data
            stats = {
                "total_reviews": 1247,
                "active_reviewers": 89,
                "accuracy_rate": 0.94,
                "average_review_time": "4.2 minutes",
                "consensus_rate": 0.87,
                "top_categories": [
                    {"category": "Health", "count": 342},
                    {"category": "Politics", "count": 298},
                    {"category": "Technology", "count": 203},
                    {"category": "Environment", "count": 156}
                ],
                "performance_metrics": {
                    "false_positive_rate": 0.03,
                    "false_negative_rate": 0.05,
                    "reviewer_agreement": 0.89
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get community statistics: {e}")
            return {"error": "Statistics unavailable"}


# Global quarantine service instance
quarantine_service = QuarantineService()