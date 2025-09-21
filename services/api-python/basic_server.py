"""
Basic TrustNet API for testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import time
import random

app = FastAPI(title="TrustNet API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:3000", 
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    content: str
    content_type: str = "text"
    user_id: str = "anonymous"

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

@app.get("/")
def root():
    return {"message": "TrustNet API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/v1/analysis")
def analyze_content(request: AnalysisRequest):
    # Simple mock analysis
    score = random.uniform(0.3, 0.9)
    
    techniques = []
    if "urgent" in request.content.lower():
        techniques.append(ManipulationTechnique(
            name="Urgency Manipulation",
            description="Uses urgent language",
            confidence=0.8,
            severity="medium"
        ))
    
    return AnalysisResponse(
        analysis_id=f"test_{int(time.time())}",
        trust_score=TrustScore(
            overall_score=score,
            credibility=score,
            bias_score=0.5,
            emotional_manipulation=1.0 - score,
            source_reliability=score
        ),
        analysis_summary=f"Mock analysis result with trust score {score:.2f}",
        manipulation_techniques=techniques,
        educational_content="This is educational content about misinformation detection.",
        metadata={
            "word_count": len(request.content.split()),
            "sources": ["Mock Source"]
        },
        timestamp=time.time()
    )