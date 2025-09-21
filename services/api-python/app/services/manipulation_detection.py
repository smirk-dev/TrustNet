"""
Manipulation Detection Service
Specialized service for detecting manipulation techniques in content
"""

from typing import List, Dict
from datetime import datetime

from ..core.logging import get_logger
from ..models.schemas import ManipulationTechnique

logger = get_logger(__name__)


class ManipulationDetector:
    """Service for detecting manipulation techniques in content."""
    
    async def detect_techniques(self, content: str, deep_analysis: bool = False) -> List[ManipulationTechnique]:
        """Detect manipulation techniques in content."""
        try:
            logger.info(f"🎭 Detecting manipulation techniques (deep={deep_analysis})")
            
            techniques = []
            
            # Emotional manipulation detection
            emotional_keywords = ["shocking", "urgent", "exposed", "revealed", "secret", "hidden"]
            emotional_score = sum(1 for keyword in emotional_keywords if keyword.lower() in content.lower())
            
            if emotional_score > 0:
                techniques.append(ManipulationTechnique(
                    technique_id="emotional_manipulation",
                    technique_name="Emotional Manipulation",
                    description="Uses emotionally charged language to bypass critical thinking",
                    confidence_score=min(0.9, 0.3 + (emotional_score * 0.15)),
                    indicators=["emotionally charged words", "urgency language", "sensational claims"],
                    severity="medium" if emotional_score < 3 else "high",
                    detection_method="keyword_analysis",
                    mitigation_advice=[
                        "Take a moment to analyze the emotional content",
                        "Look for factual evidence beyond emotional appeals",
                        "Consider why this content is trying to make you feel this way"
                    ]
                ))
            
            # False urgency detection
            urgency_keywords = ["urgent", "immediate", "now", "quickly", "before it's too late"]
            urgency_score = sum(1 for keyword in urgency_keywords if keyword.lower() in content.lower())
            
            if urgency_score > 0:
                techniques.append(ManipulationTechnique(
                    technique_id="false_urgency",
                    technique_name="False Urgency",
                    description="Creates artificial time pressure to prevent careful consideration",
                    confidence_score=min(0.85, 0.4 + (urgency_score * 0.1)),
                    indicators=["time pressure language", "urgent calls to action", "deadline emphasis"],
                    severity="medium",
                    detection_method="linguistic_analysis",
                    mitigation_advice=[
                        "Legitimate information rarely requires immediate action",
                        "Take time to verify urgent claims",
                        "Be suspicious of artificial deadlines"
                    ]
                ))
            
            # Authority manipulation detection
            authority_keywords = ["experts say", "studies show", "doctors recommend", "scientists confirm"]
            authority_score = sum(1 for keyword in authority_keywords if keyword.lower() in content.lower())
            
            if authority_score > 0:
                techniques.append(ManipulationTechnique(
                    technique_id="false_authority",
                    technique_name="False Authority Claims",
                    description="Cites vague or non-existent authorities to add credibility",
                    confidence_score=min(0.8, 0.3 + (authority_score * 0.12)),
                    indicators=["vague authority references", "unnamed experts", "unsourced studies"],
                    severity="high",
                    detection_method="authority_claim_analysis",
                    mitigation_advice=[
                        "Look for specific names and credentials",
                        "Verify studies and expert claims",
                        "Check if authorities are relevant to the topic"
                    ]
                ))
            
            # Social proof manipulation
            social_keywords = ["everyone", "nobody", "most people", "millions", "viral"]
            social_score = sum(1 for keyword in social_keywords if keyword.lower() in content.lower())
            
            if social_score > 0:
                techniques.append(ManipulationTechnique(
                    technique_id="false_social_proof",
                    technique_name="False Social Proof",
                    description="Claims widespread belief or participation without evidence",
                    confidence_score=min(0.75, 0.25 + (social_score * 0.15)),
                    indicators=["bandwagon appeals", "popularity claims", "peer pressure"],
                    severity="medium",
                    detection_method="social_claim_analysis",
                    mitigation_advice=[
                        "Question claims about what 'everyone' believes",
                        "Look for actual data behind popularity claims",
                        "Consider that widespread belief doesn't equal truth"
                    ]
                ))
            
            # If deep analysis requested, add more sophisticated techniques
            if deep_analysis:
                techniques.extend(await self._deep_analysis_techniques(content))
            
            return techniques
            
        except Exception as e:
            logger.error(f"❌ Manipulation detection failed: {e}")
            return []
    
    async def _deep_analysis_techniques(self, content: str) -> List[ManipulationTechnique]:
        """Perform deep analysis for advanced manipulation techniques."""
        advanced_techniques = []
        
        # Logical fallacy detection
        fallacy_patterns = {
            "strawman": ["nobody said", "you claim", "people like you"],
            "ad_hominem": ["those people", "typical", "what do you expect"],
            "false_dichotomy": ["either", "only two", "must choose"]
        }
        
        for fallacy_type, patterns in fallacy_patterns.items():
            if any(pattern in content.lower() for pattern in patterns):
                advanced_techniques.append(ManipulationTechnique(
                    technique_id=f"logical_fallacy_{fallacy_type}",
                    technique_name=f"Logical Fallacy: {fallacy_type.replace('_', ' ').title()}",
                    description=f"Uses {fallacy_type.replace('_', ' ')} logical fallacy to mislead",
                    confidence_score=0.7,
                    indicators=[f"{fallacy_type} pattern detected"],
                    severity="high",
                    detection_method="logical_fallacy_analysis",
                    mitigation_advice=[
                        "Identify the logical structure of the argument",
                        "Look for missing premises or invalid conclusions",
                        "Consider alternative explanations"
                    ]
                ))
        
        # Statistical manipulation detection
        stat_keywords = ["statistics show", "data proves", "numbers don't lie", "research indicates"]
        if any(keyword in content.lower() for keyword in stat_keywords):
            advanced_techniques.append(ManipulationTechnique(
                technique_id="statistical_manipulation",
                technique_name="Statistical Manipulation",
                description="Misuses statistics or data to support false claims",
                confidence_score=0.65,
                indicators=["unsourced statistics", "misleading data presentation"],
                severity="high",
                detection_method="statistical_analysis",
                mitigation_advice=[
                    "Ask for the source of statistics",
                    "Look for context and methodology",
                    "Check if the data actually supports the claim"
                ]
            ))
        
        return advanced_techniques


# Global instance
manipulation_detector = ManipulationDetector()