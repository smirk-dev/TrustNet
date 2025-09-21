"""
Services Package Initialization
Imports all service modules for easy access
"""

from .educational import educational_service
from .analysis import analysis_service
from .manipulation_detection import manipulation_detector
from .feedback import feedback_service
from .community import community_service

__all__ = [
    "educational_service",
    "analysis_service", 
    "manipulation_detector",
    "feedback_service",
    "community_service"
]