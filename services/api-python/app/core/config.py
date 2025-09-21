"""
TrustNet Configuration Management
Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    API_NAME: str = "TrustNet API"
    API_VERSION: str = "1.0.0"
    API_BASE_URL: str = "http://localhost:8000"
    PORT: int = 8000
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Frontend app port (from package.json)
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://127.0.0.1:5173",  # Alternative localhost  
        "http://127.0.0.1:8080",  # Alternative localhost
        "https://trustnet.dev",   # Production frontend
        "https://api.trustnet.dev"  # Production API
    ]
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_CLOUD_REGION: str = "asia-south1"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Firestore Configuration
    FIRESTORE_DATABASE: str = "trustnet-db"
    FIRESTORE_EMULATOR_HOST: Optional[str] = None
    
    # Vertex AI Configuration
    VERTEX_AI_LOCATION: str = "asia-south1"
    VERTEX_SEARCH_INDEX: str = "evidence-corpus"
    VERTEX_MODEL_NAME: str = "gemini-1.5-pro"
    
    # Pub/Sub Configuration
    PUBSUB_TOPIC_ANALYSIS: str = "content-analysis"
    PUBSUB_TOPIC_EVIDENCE: str = "evidence-retrieval"
    PUBSUB_TOPIC_FACTCHECK: str = "fact-check-lookup"
    PUBSUB_TOPIC_VERDICTS: str = "verdict-updates"
    
    # External API Keys
    FACT_CHECK_API_KEY: Optional[str] = None
    WEB_RISK_API_KEY: Optional[str] = None
    PERSPECTIVE_API_KEY: Optional[str] = None
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    CACHE_TTL_SECONDS: int = 3600  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 3600  # 1 hour
    
    # ML Configuration
    MAX_TEXT_LENGTH: int = 10000
    MAX_URLS_PER_REQUEST: int = 5
    MAX_IMAGES_PER_REQUEST: int = 3
    CONFIDENCE_THRESHOLD: float = 0.65  # Below this goes to quarantine
    
    # Processing Configuration
    MAX_PROCESSING_TIME_SECONDS: int = 30
    ASYNC_PROCESSING_THRESHOLD: int = 5000  # Text length for async processing
    
    # Monitoring & Logging
    LOG_LEVEL: str = "INFO"
    STRUCTURED_LOGGING: bool = True
    ENABLE_METRICS: bool = True
    
    # Development Flags
    MOCK_GOOGLE_SERVICES: bool = False
    DEVELOPMENT_MODE: bool = True
    ENABLE_API_DOCS: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings