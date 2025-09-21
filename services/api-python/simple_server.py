"""
Simple TrustNet API for testing frontend integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import time
import random
import asyncio

# Create FastAPI app
app = FastAPI(
    title="TrustNet API",
    description="AI-powered misinformation detection service",
    version="1.0.0-simple"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response Models
class AnalysisRequest(BaseModel):
    content: str
    content_type: str = "text"
    user_id: str = "anonymous"
    metadata: Optional[Dict[str, Any]] = None

class TrustScore(BaseModel):
    overall_score: float
    credibility: float
    bias_score: float
    emotional_manipulation: float
    source_reliability: float

class ManipulationTechnique(BaseModel):
    name: str
    description: str
    confidence: float
    severity: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    trust_score: TrustScore
    analysis_summary: str
    manipulation_techniques: List[ManipulationTechnique]
    educational_content: str
    metadata: Dict[str, Any]
    timestamp: float

# Mock analysis function
def mock_analyze_content(content: str) -> AnalysisResponse:
    """Generate mock analysis results"""
    
    # Generate some realistic mock data
    word_count = len(content.split())
    
    # Determine trust score based on simple heuristics
    if any(word in content.lower() for word in ["breaking", "urgent", "shocking", "unbelievable"]):
        trust_score = random.uniform(0.2, 0.4)
    elif any(word in content.lower() for word in ["according to", "sources", "research", "study"]):
        trust_score = random.uniform(0.7, 0.9)
    else:
        trust_score = random.uniform(0.4, 0.7)
    
    # Generate manipulation techniques based on content
    techniques = []
    if "urgent" in content.lower() or "breaking" in content.lower():
        techniques.append(ManipulationTechnique(
            name="Urgency Manipulation",
            description="Uses urgent language to bypass critical thinking",
            confidence=0.85,
            severity="medium"
        ))
    
    if "shocking" in content.lower() or "unbelievable" in content.lower():
        techniques.append(ManipulationTechnique(
            name="Emotional Appeal",
            description="Uses shock value to create emotional response",
            confidence=0.75,
            severity="high"
        ))
    
    # Educational content based on analysis
    if trust_score < 0.5:
        education = "This content shows warning signs of potential misinformation. Look for credible sources and fact-check claims before sharing."
    elif trust_score > 0.8:
        education = "This content appears credible with good sourcing. Always verify information through multiple independent sources."
    else:
        education = "This content has mixed signals. Cross-reference with other sources to verify accuracy."
    
    return AnalysisResponse(
        analysis_id=f"analysis_{int(time.time())}_{random.randint(1000, 9999)}",
        trust_score=TrustScore(
            overall_score=trust_score,
            credibility=min(1.0, trust_score + random.uniform(-0.1, 0.1)),
            bias_score=random.uniform(0.3, 0.8),
            emotional_manipulation=1.0 - trust_score,
            source_reliability=trust_score * random.uniform(0.8, 1.2)
        ),
        analysis_summary=f"Analysis of {word_count} words reveals trust score of {trust_score:.2f}. " + 
                        ("Content shows signs of manipulation." if trust_score < 0.6 else "Content appears credible."),
        manipulation_techniques=techniques,
        educational_content=education,
        metadata={
            "word_count": word_count,
            "processing_time_ms": random.randint(1200, 2800),
            "sources": ["TrustNet AI Analysis"] if not techniques else ["Flagged for Review"],
            "language": "en"
        },
        timestamp=time.time()
    )

# API Endpoints
@app.get("/")
async def root():
    return {
        "name": "TrustNet API",
        "version": "1.0.0-simple",
        "status": "running",
        "description": "Simplified API for frontend testing"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0-simple",
        "timestamp": time.time()
    }

@app.post("/v1/analysis", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    """Analyze content for misinformation"""
    
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    if len(request.content) > 10000:
        raise HTTPException(status_code=400, detail="Content too long (max 10000 characters)")
    
    # Simulate processing time
    await asyncio.sleep(random.uniform(1.0, 2.5))
    
    # Generate mock analysis
    result = mock_analyze_content(request.content)
    
    return result

@app.get("/v1/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis by ID (mock endpoint)"""
    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "message": "This is a mock endpoint for testing"
    }

if __name__ == "__main__":
    print("🚀 Starting TrustNet Simple API on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)