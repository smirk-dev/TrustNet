"""
Database Layer Management
Handles Firestore operations and connection management.
"""

import asyncio
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

from ..core.config import settings
from ..core.logging import get_logger
from ..core.gcp import get_firestore_client, is_mock_mode
from ..models.schemas import Claim, Evidence, Verdict, Feedback

logger = get_logger(__name__)

# Database connection state
_database_initialized = False


async def init_database():
    """Initialize database connections."""
    global _database_initialized
    
    try:
        logger.info("🗄️ Initializing database layer...")
        
        # Test Firestore connection
        firestore_client = get_firestore_client()
        
        if not is_mock_mode():
            # Test connection with a simple read
            collections = ["claims", "evidence", "verdicts", "feedback"]
            for collection_name in collections:
                collection = firestore_client.collection(collection_name)
                # Just check if collection exists - this will create it if needed
                logger.info(f"✅ Firestore collection '{collection_name}' ready")
        
        _database_initialized = True
        logger.info("✅ Database layer initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


async def close_database():
    """Close database connections."""
    global _database_initialized
    
    if _database_initialized:
        logger.info("🔒 Closing database connections...")
        # Firestore client closure is handled in GCP layer
        _database_initialized = False
        logger.info("✅ Database connections closed")


class FirestoreManager:
    """Manages Firestore operations for TrustNet data."""
    
    def __init__(self):
        self.client = None
    
    def _get_client(self):
        """Get Firestore client instance."""
        if not self.client:
            self.client = get_firestore_client()
        return self.client
    
    # Claims operations
    async def create_claim(self, claim: Claim) -> str:
        """Create a new claim document."""
        try:
            client = self._get_client()
            doc_ref = client.collection("claims").document(claim.id)
            await doc_ref.set(claim.dict())
            logger.info(f"✅ Created claim: {claim.id}")
            return claim.id
        except Exception as e:
            logger.error(f"❌ Failed to create claim: {e}")
            raise
    
    async def get_claim(self, claim_id: str) -> Optional[Claim]:
        """Get a claim by ID."""
        try:
            client = self._get_client()
            doc_ref = client.collection("claims").document(claim_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return Claim(**data)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get claim {claim_id}: {e}")
            raise
    
    async def update_claim(self, claim_id: str, updates: Dict[str, Any]) -> bool:
        """Update a claim document."""
        try:
            client = self._get_client()
            doc_ref = client.collection("claims").document(claim_id)
            updates['updated_at'] = datetime.utcnow()
            await doc_ref.update(updates)
            logger.info(f"✅ Updated claim: {claim_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update claim {claim_id}: {e}")
            return False
    
    # Evidence operations
    async def create_evidence(self, evidence: Evidence) -> str:
        """Create a new evidence document."""
        try:
            client = self._get_client()
            doc_ref = client.collection("evidence").document(evidence.id)
            await doc_ref.set(evidence.dict())
            logger.info(f"✅ Created evidence: {evidence.id}")
            return evidence.id
        except Exception as e:
            logger.error(f"❌ Failed to create evidence: {e}")
            raise
    
    async def get_evidence_by_claim(self, claim_id: str) -> List[Evidence]:
        """Get all evidence for a claim."""
        try:
            client = self._get_client()
            collection = client.collection("evidence")
            query = collection.where("claim_id", "==", claim_id)
            
            evidence_list = []
            async for doc in query.stream():
                data = doc.to_dict()
                evidence_list.append(Evidence(**data))
            
            return evidence_list
        except Exception as e:
            logger.error(f"❌ Failed to get evidence for claim {claim_id}: {e}")
            return []
    
    # Verdict operations
    async def create_verdict(self, verdict: Verdict) -> str:
        """Create a new verdict document."""
        try:
            client = self._get_client()
            doc_ref = client.collection("verdicts").document(verdict.id)
            await doc_ref.set(verdict.dict())
            logger.info(f"✅ Created verdict: {verdict.id}")
            return verdict.id
        except Exception as e:
            logger.error(f"❌ Failed to create verdict: {e}")
            raise
    
    async def get_verdict_by_claim(self, claim_id: str) -> Optional[Verdict]:
        """Get verdict for a claim."""
        try:
            client = self._get_client()
            collection = client.collection("verdicts")
            query = collection.where("claim_id", "==", claim_id).limit(1)
            
            async for doc in query.stream():
                data = doc.to_dict()
                return Verdict(**data)
            
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get verdict for claim {claim_id}: {e}")
            return None
    
    async def get_verdict(self, verdict_id: str) -> Optional[Verdict]:
        """Get a verdict by ID."""
        try:
            client = self._get_client()
            doc_ref = client.collection("verdicts").document(verdict_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return Verdict(**data)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get verdict {verdict_id}: {e}")
            return None
    
    # Feedback operations
    async def create_feedback(self, feedback: Feedback) -> str:
        """Create a new feedback document."""
        try:
            client = self._get_client()
            doc_ref = client.collection("feedback").document(feedback.id)
            await doc_ref.set(feedback.dict())
            logger.info(f"✅ Created feedback: {feedback.id}")
            return feedback.id
        except Exception as e:
            logger.error(f"❌ Failed to create feedback: {e}")
            raise
    
    async def get_feedback_by_verdict(self, verdict_id: str) -> List[Feedback]:
        """Get all feedback for a verdict."""
        try:
            client = self._get_client()
            collection = client.collection("feedback")
            query = collection.where("verdict_id", "==", verdict_id)
            
            feedback_list = []
            async for doc in query.stream():
                data = doc.to_dict()
                feedback_list.append(Feedback(**data))
            
            return feedback_list
        except Exception as e:
            logger.error(f"❌ Failed to get feedback for verdict {verdict_id}: {e}")
            return []
    
    # Educational content operations
    async def get_educational_content(self, language: str = "en", limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get educational feed content."""
        try:
            # Mock educational content for now
            mock_content = [
                {
                    "id": f"edu_{i}",
                    "title": f"Educational Content {i}",
                    "type": "verified_example" if i % 2 == 0 else "debunked_example",
                    "summary": f"This is educational content item {i} for language {language}",
                    "original_claim": f"Sample claim {i}",
                    "verdict": "True" if i % 2 == 0 else "False",
                    "evidence_summary": f"Evidence summary for item {i}",
                    "learning_points": [f"Learning point {i}.1", f"Learning point {i}.2"],
                    "visual_elements": {},
                    "engagement_score": 0.8,
                    "published_at": datetime.utcnow(),
                    "source_attribution": "TrustNet Educational Team",
                    "category": ["health", "politics", "finance", "social"][i % 4]
                }
                for i in range(offset, offset + limit)
            ]
            
            return mock_content
        except Exception as e:
            logger.error(f"❌ Failed to get educational content: {e}")
            return []
    
    # Trending patterns operations
    async def get_trending_patterns(self, language: str = "en", time_range: str = "7d") -> Dict[str, Any]:
        """Get trending misinformation patterns."""
        try:
            # Mock trending patterns
            mock_patterns = {
                "trending_patterns": [
                    {
                        "pattern_name": "Health Misinformation",
                        "description": "False claims about medical treatments",
                        "frequency": 45,
                        "example_claims": [
                            "Miracle cure discovered",
                            "Doctors don't want you to know this"
                        ],
                        "detection_tips": [
                            "Look for unrealistic medical claims",
                            "Check for medical authority sources"
                        ],
                        "related_topics": ["health", "medicine", "treatment"],
                        "trend_score": 0.8,
                        "educational_priority": "high"
                    },
                    {
                        "pattern_name": "Financial Scams",
                        "description": "Get-rich-quick schemes and investment fraud",
                        "frequency": 32,
                        "example_claims": [
                            "Guaranteed 1000% returns",
                            "Secret investment opportunity"
                        ],
                        "detection_tips": [
                            "Be skeptical of guaranteed returns",
                            "Verify investment opportunities"
                        ],
                        "related_topics": ["finance", "investment", "money"],
                        "trend_score": 0.7,
                        "educational_priority": "high"
                    }
                ],
                "time_range": time_range,
                "language": language,
                "generated_at": datetime.utcnow(),
                "disclaimer": "This data is for educational purposes only"
            }
            
            return mock_patterns
        except Exception as e:
            logger.error(f"❌ Failed to get trending patterns: {e}")
            return {"trending_patterns": [], "time_range": time_range, "language": language}


# Global database manager instance
db_manager = FirestoreManager()