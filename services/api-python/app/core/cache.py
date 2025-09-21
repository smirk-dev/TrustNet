"""
Redis Cache Management
Handles caching operations for improved performance.
"""

import json
import asyncio
import logging
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)

# Cache connection state
_redis_client: Optional[Any] = None
_cache_initialized = False


async def init_redis():
    """Initialize Redis cache connection."""
    global _redis_client, _cache_initialized
    
    try:
        logger.info("⚡ Initializing Redis cache...")
        
        if settings.DEVELOPMENT_MODE:
            # Use mock cache in development
            _redis_client = MockRedisClient()
            logger.info("🎭 Using mock Redis cache for development")
        else:
            # Use real Redis in production
            import aioredis
            _redis_client = aioredis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            
            # Test connection
            await _redis_client.ping()
            logger.info("✅ Connected to Redis successfully")
        
        _cache_initialized = True
        logger.info("✅ Redis cache initialized successfully")
        
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed, using mock cache: {e}")
        # Fallback to mock cache
        _redis_client = MockRedisClient()
        _cache_initialized = True


async def close_redis():
    """Close Redis cache connection."""
    global _redis_client, _cache_initialized
    
    if _cache_initialized and _redis_client:
        try:
            if hasattr(_redis_client, 'close'):
                await _redis_client.close()
            logger.info("✅ Redis cache connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Redis connection: {e}")
        finally:
            _redis_client = None
            _cache_initialized = False


class MockRedisClient:
    """Mock Redis client for development and testing."""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, datetime] = {}
    
    async def ping(self):
        return True
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if key in self._expiry and self._expiry[key] < datetime.utcnow():
            # Key expired
            del self._data[key]
            del self._expiry[key]
            return None
        
        return self._data.get(key)
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in cache."""
        self._data[key] = value
        if ex:
            self._expiry[key] = datetime.utcnow() + timedelta(seconds=ex)
        return True
    
    async def delete(self, key: str) -> int:
        """Delete key from cache."""
        deleted = 0
        if key in self._data:
            del self._data[key]
            deleted += 1
        if key in self._expiry:
            del self._expiry[key]
        return deleted
    
    async def exists(self, key: str) -> int:
        """Check if key exists."""
        if key in self._expiry and self._expiry[key] < datetime.utcnow():
            # Key expired
            del self._data[key]
            del self._expiry[key]
            return 0
        
        return 1 if key in self._data else 0
    
    async def close(self):
        """Close connection."""
        pass


class CacheManager:
    """Manages caching operations for TrustNet."""
    
    def __init__(self):
        self.default_ttl = settings.CACHE_TTL_SECONDS
    
    def _get_client(self):
        """Get Redis client instance."""
        if not _cache_initialized:
            raise RuntimeError("Cache not initialized")
        return _redis_client
    
    def _make_key(self, prefix: str, identifier: str) -> str:
        """Create cache key with prefix."""
        return f"trustnet:{prefix}:{identifier}"
    
    async def get_json(self, prefix: str, identifier: str) -> Optional[Dict[str, Any]]:
        """Get JSON data from cache."""
        try:
            client = self._get_client()
            key = self._make_key(prefix, identifier)
            data = await client.get(key)
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"Cache get failed for {prefix}:{identifier}: {e}")
            return None
    
    async def set_json(self, prefix: str, identifier: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set JSON data in cache."""
        try:
            client = self._get_client()
            key = self._make_key(prefix, identifier)
            json_data = json.dumps(data, default=str)
            ttl = ttl or self.default_ttl
            
            await client.set(key, json_data, ex=ttl)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for {prefix}:{identifier}: {e}")
            return False
    
    async def delete(self, prefix: str, identifier: str) -> bool:
        """Delete data from cache."""
        try:
            client = self._get_client()
            key = self._make_key(prefix, identifier)
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Cache delete failed for {prefix}:{identifier}: {e}")
            return False
    
    async def exists(self, prefix: str, identifier: str) -> bool:
        """Check if key exists in cache."""
        try:
            client = self._get_client()
            key = self._make_key(prefix, identifier)
            result = await client.exists(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Cache exists check failed for {prefix}:{identifier}: {e}")
            return False
    
    # Specific cache operations for TrustNet
    async def cache_claim(self, claim_id: str, claim_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache claim data."""
        return await self.set_json("claim", claim_id, claim_data, ttl)
    
    async def get_cached_claim(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get cached claim data."""
        return await self.get_json("claim", claim_id)
    
    async def cache_verdict(self, claim_id: str, verdict_data: Dict[str, Any], ttl: int = 7200) -> bool:
        """Cache verdict data."""
        return await self.set_json("verdict", claim_id, verdict_data, ttl)
    
    async def get_cached_verdict(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get cached verdict data."""
        return await self.get_json("verdict", claim_id)
    
    async def cache_evidence(self, claim_id: str, evidence_data: List[Dict[str, Any]], ttl: int = 3600) -> bool:
        """Cache evidence data."""
        return await self.set_json("evidence", claim_id, {"evidence": evidence_data}, ttl)
    
    async def get_cached_evidence(self, claim_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached evidence data."""
        data = await self.get_json("evidence", claim_id)
        return data.get("evidence") if data else None
    
    async def cache_analysis_result(self, text_hash: str, result_data: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache analysis result by text hash."""
        return await self.set_json("analysis", text_hash, result_data, ttl)
    
    async def get_cached_analysis(self, text_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result."""
        return await self.get_json("analysis", text_hash)
    
    async def cache_educational_feed(self, language: str, feed_data: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache educational feed data."""
        return await self.set_json("feed", language, feed_data, ttl)
    
    async def get_cached_educational_feed(self, language: str) -> Optional[Dict[str, Any]]:
        """Get cached educational feed."""
        return await self.get_json("feed", language)
    
    async def cache_trust_score(self, content_hash: str, trust_score: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache trust score by content hash."""
        return await self.set_json("trust_score", content_hash, trust_score, ttl)
    
    async def get_cached_trust_score(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached trust score."""
        return await self.get_json("trust_score", content_hash)
    
    async def invalidate_claim(self, claim_id: str) -> bool:
        """Invalidate all cache entries for a claim."""
        try:
            await self.delete("claim", claim_id)
            await self.delete("verdict", claim_id)
            await self.delete("evidence", claim_id)
            return True
        except Exception as e:
            logger.warning(f"Cache invalidation failed for claim {claim_id}: {e}")
            return False


# Global cache manager instance
cache_manager = CacheManager()