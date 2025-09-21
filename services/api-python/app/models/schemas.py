"""
TrustNet Core Data Models
Pydantic models matching the OpenAPI schema specifications.
"""

from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional, Dict, Any, Union, Annotated
from datetime import datetime
from enum import Enum
import uuid


# Enums for consistent values
class LanguageCode(str, Enum):
    """Supported language codes."""
    HINDI = "hi"
    BENGALI = "bn" 
    TELUGU = "te"
    MARATHI = "mr"
    TAMIL = "ta"
    KANNADA = "kn"
    MALAYALAM = "ml"
    GUJARATI = "gu"
    ODIA = "or"
    PUNJABI = "pa"
    URDU = "ur"
    ENGLISH = "en"


class SourceType(str, Enum):
    """Content source types."""
    SOCIAL_MEDIA = "social_media"
    NEWS = "news"
    MESSAGING = "messaging"
    EMAIL = "email"
    WEB = "web"


class RatingType(str, Enum):
    """Verdict rating types."""
    TRUE = "True"
    FALSE = "False"
    MIXTURE = "Mixture"
    UNPROVEN = "Unproven"
    INSUFFICIENT_EVIDENCE = "Insufficient_Evidence"


class EvidenceType(str, Enum):
    """Evidence classification types."""
    SUPPORTING = "supporting"
    REFUTING = "refuting"
    CONTEXTUAL = "contextual"
    NEUTRAL = "neutral"


class UserRating(str, Enum):
    """User feedback rating types."""
    ACCURATE = "accurate"
    INACCURATE = "inaccurate"
    PARTIALLY_ACCURATE = "partially_accurate"


class FeedbackType(str, Enum):
    """Feedback classification types."""
    RATING_DISAGREEMENT = "rating_disagreement"
    MISSING_EVIDENCE = "missing_evidence"
    POOR_EXPLANATION = "poor_explanation"
    FACTUAL_ERROR = "factual_error"


class UserExpertise(str, Enum):
    """User expertise levels."""
    EXPERT = "expert"
    KNOWLEDGEABLE = "knowledgeable"
    GENERAL_PUBLIC = "general_public"


class ManipulationType(str, Enum):
    """Types of manipulation detected."""
    EMOTIONAL_MANIPULATION = "emotional_manipulation"
    UNREALISTIC_INCENTIVE = "unrealistic_incentive"
    TECHNICAL_DECEPTION = "technical_deception"
    SYNTHETIC_MEDIA = "synthetic_media"


class SeverityLevel(str, Enum):
    """Severity levels for manipulation."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Priority(str, Enum):
    """Processing priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


# Base Models
class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class UUIDModel(BaseModel):
    """Base model with UUID identifier."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# Core Data Models
class Claim(UUIDModel, TimestampedModel):
    """Claim data model."""
    text: str = Field(..., min_length=10, max_length=10000)
    urls: Optional[List[HttpUrl]] = Field(default=None, max_length=5)
    images: Optional[List[HttpUrl]] = Field(default=None, max_length=3)
    language: LanguageCode
    script: Optional[str] = None
    source_type: SourceType
    user_segment: Optional[str] = None
    pii_redacted: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }


class Evidence(UUIDModel, TimestampedModel):
    """Evidence data model."""
    claim_id: str = Field(..., description="UUID of the related claim")
    snippet: str = Field(..., max_length=1000)
    source_url: HttpUrl
    source_title: Optional[str] = Field(None, max_length=200)
    source_domain: Optional[str] = None
    relevance_score: float = Field(..., ge=0, le=1)
    evidence_type: EvidenceType
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    language: Optional[LanguageCode] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }


class ManipulationIndicator(BaseModel):
    """Manipulation detection indicator."""
    type: ManipulationType
    severity: SeverityLevel
    description: str
    confidence: float = Field(..., ge=0, le=1)


class DetectionScores(BaseModel):
    """AI detection scores."""
    misinformation_probability: float = Field(..., ge=0, le=1)
    toxicity_score: float = Field(..., ge=0, le=1)
    spam_score: float = Field(..., ge=0, le=1)
    manipulation_score: float = Field(..., ge=0, le=1)


class Verdict(UUIDModel, TimestampedModel):
    """Verdict data model."""
    claim_id: str = Field(..., description="UUID of the related claim")
    rating: RatingType
    confidence_score: float = Field(..., ge=0, le=1)
    rationale: str = Field(..., max_length=2000)
    evidence_ids: List[str] = Field(default_factory=list)
    fact_check_matches: List[Dict[str, Any]] = Field(default_factory=list)
    education_tips: List[str] = Field(default_factory=list)
    manipulation_indicators: List[ManipulationIndicator] = Field(default_factory=list)
    detection_scores: Optional[DetectionScores] = None
    model_version: str
    processing_time_ms: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Feedback(UUIDModel, TimestampedModel):
    """User feedback data model."""
    verdict_id: str = Field(..., description="UUID of the related verdict")
    user_rating: UserRating
    feedback_type: FeedbackType
    comments: Optional[str] = Field(None, max_length=1000)
    user_expertise: UserExpertise = Field(default=UserExpertise.GENERAL_PUBLIC)
    processing_time_ms: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Request/Response Models
class VerificationRequest(BaseModel):
    """Request model for content verification."""
    text: str = Field(..., min_length=10, max_length=10000)
    urls: Optional[List[HttpUrl]] = Field(default=None, max_length=5)
    images: Optional[List[HttpUrl]] = Field(default=None, max_length=3)
    language: Optional[LanguageCode] = Field(default=LanguageCode.ENGLISH)
    source_type: Optional[SourceType] = Field(default=SourceType.WEB)
    priority: Optional[Priority] = Field(default=Priority.NORMAL)
    
    class Config:
        json_encoders = {
            HttpUrl: lambda v: str(v)
        }


class AnalysisRequest(VerificationRequest):
    """Request model for content analysis (alias for verification)."""
    pass


class VerificationQueued(BaseModel):
    """Response when verification is queued."""
    verification_id: str
    status: str = "analyzing"
    message: str
    text_preview: Optional[str] = None
    check_url: str
    estimated_completion: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VerificationCard(BaseModel):
    """Verification result card."""
    credibility_score: float = Field(..., ge=0, le=1)
    rating: RatingType
    confidence: float = Field(..., ge=0, le=1)
    source_analysis: Dict[str, Any] = Field(default_factory=dict)
    alternative_headlines: List[str] = Field(default_factory=list)
    neutral_summary: str
    manipulation_alerts: List[ManipulationIndicator] = Field(default_factory=list)
    education_tips: List[Dict[str, str]] = Field(default_factory=list)


class VerificationComplete(BaseModel):
    """Complete verification response."""
    verification_id: str
    status: str = "completed"
    verification_card: VerificationCard
    processing_time: int
    completed_at: datetime
    note: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class QuarantineRequired(BaseModel):
    """Response when content needs quarantine review."""
    verification_id: str
    status: str = "needs_review"
    quarantine_url: str
    confidence_score: float = Field(..., ge=0, le=1)
    suspicious_indicators: List[str] = Field(default_factory=list)
    message: str


class QuarantineItem(BaseModel):
    """Quarantine item details."""
    verification_id: str
    quarantine_item: Dict[str, Any]
    user_action_required: bool = True
    verdict_options: List[str] = Field(default_factory=lambda: ["legit", "misleading", "needs_more_info"])
    educational_context: str


class UserVerdict(BaseModel):
    """User verdict submission."""
    user_verdict: str = Field(..., pattern="^(legit|misleading|needs_more_info)$")
    confidence: int = Field(..., ge=1, le=5)
    reasoning: Optional[str] = Field(None, max_length=500)
    user_expertise: UserExpertise = Field(default=UserExpertise.GENERAL_PUBLIC)


class FeedbackRequest(BaseModel):
    """Feedback submission request."""
    verdict_id: str
    user_rating: UserRating
    feedback_type: FeedbackType
    comments: Optional[str] = Field(None, max_length=1000)
    user_expertise: UserExpertise = Field(default=UserExpertise.GENERAL_PUBLIC)


class AnalysisResult(BaseModel):
    """Complete analysis result."""
    claim_id: str
    verdict: Verdict
    evidence: List[Evidence] = Field(default_factory=list)
    processing_time_ms: int
    grounding_coverage: float = Field(..., ge=0, le=1)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisQueued(BaseModel):
    """Queued analysis response."""
    claim_id: str
    status: str = Field(default="queued")
    estimated_completion: datetime
    check_url: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClaimResult(BaseModel):
    """Claim lookup result."""
    claim_id: str
    status: str
    claim: Optional[Claim] = None
    verdict: Optional[Verdict] = None
    evidence: List[Evidence] = Field(default_factory=list)
    processing_completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Educational Feed Models
class FeedItem(BaseModel):
    """Educational feed item."""
    id: str
    title: str
    type: str = Field(..., pattern="^(verified_example|debunked_example|education_tip)$")
    summary: str
    original_claim: Optional[str] = None
    verdict: Optional[str] = None
    evidence_summary: Optional[str] = None
    learning_points: List[str] = Field(default_factory=list)
    visual_elements: Dict[str, Any] = Field(default_factory=dict)
    engagement_score: float = Field(default=0.0)
    published_at: datetime
    source_attribution: Optional[str] = None
    category: Optional[str] = Field(None, pattern="^(health|politics|finance|social)$")
    
    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class EducationalFeed(BaseModel):
    """Educational feed response."""
    feed_items: List[FeedItem]
    trending_topics: List[Dict[str, Any]] = Field(default_factory=list)
    total_count: int
    language: LanguageCode
    last_updated: datetime
    feed_metadata: Dict[str, bool] = Field(default_factory=lambda: {
        "user_education_focus": True,
        "real_world_examples": True,
        "proactive_learning": True
    })
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FeedItemDetail(BaseModel):
    """Detailed feed item response."""
    feed_item: Dict[str, Any]
    related_content: List[Dict[str, Any]] = Field(default_factory=list)
    user_actions: Dict[str, bool] = Field(default_factory=lambda: {
        "can_share": True,
        "can_bookmark": True,
        "can_report_error": True
    })


class EngagementFeedback(BaseModel):
    """User engagement feedback on educational content."""
    item_id: str
    user_id: Optional[str] = None
    engagement_type: str = Field(..., pattern="^(like|dislike|share|save|helpful|not_helpful|confusing|learned_something|share_worthy)$")
    feedback_text: Optional[str] = Field(None, max_length=500)
    rating: Optional[int] = Field(None, ge=1, le=5)
    time_spent_seconds: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TrendingPatterns(BaseModel):
    """Trending misinformation patterns."""
    trending_patterns: List[Dict[str, Any]]
    time_range: str
    language: LanguageCode
    generated_at: datetime
    disclaimer: str = "This data is for educational purposes only"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Error Models
class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    message: str
    details: Optional[List[Dict[str, str]]] = None


# Additional Educational and Feedback Models
class TrendingTopic(BaseModel):
    """Trending topic in educational content."""
    id: str
    title: str
    description: str
    category: str
    trend_score: float = Field(..., ge=0, le=1)
    engagement_count: int = Field(default=0, ge=0)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserFeedback(BaseModel):
    """General user feedback on the platform."""
    feedback_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    feedback_type: str = Field(..., pattern="^(bug_report|feature_request|general|content_quality|user_experience)$")
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    priority: Priority = Field(default=Priority.NORMAL)
    status: str = Field(default="submitted", pattern="^(submitted|reviewed|in_progress|resolved|closed)$")
    rating: Optional[int] = Field(None, ge=1, le=5)
    contact_email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Content Analysis Models  
class ContentAnalysisRequest(BaseModel):
    """Request model for detailed content analysis (legacy compatibility)."""
    content: str = Field(..., min_length=10, max_length=10000, description="Content to analyze")
    analysis_type: str = Field(default="comprehensive", pattern="^(quick|comprehensive|deep)$")
    priority: Priority = Field(default=Priority.NORMAL)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ManipulationTechnique(BaseModel):
    """Legacy alias for ManipulationIndicator."""
    type: ManipulationType
    description: str
    confidence: float = Field(..., ge=0, le=1)
    severity: SeverityLevel
    evidence: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TrustScore(BaseModel):
    """Trust score calculation result."""
    overall_score: float = Field(..., ge=0, le=1)
    components: Dict[str, float] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0, le=1)
    factors: List[str] = Field(default_factory=list)
    calculation_method: str = Field(default="weighted_average")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationError(BaseModel):
    """Validation error response."""
    error: str = "validation_error"
    message: str
    field_errors: List[Dict[str, str]] = Field(default_factory=list)