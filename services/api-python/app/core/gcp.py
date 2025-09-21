"""
Google Cloud Platform Integration
Manages connections to Firestore, Vertex AI, Pub/Sub, DLP, and Web Risk.
"""

from typing import Optional, Dict, Any
import asyncio
import logging
from google.cloud import firestore
from google.cloud import aiplatform
from google.cloud import pubsub_v1

# Try to import DLP and WebRisk, fall back to None if not available
try:
    from google.cloud import dlp_v2
except ImportError:
    dlp_v2 = None

try:
    from google.cloud.webrisk_v1 import WebRiskServiceClient
except ImportError:
    WebRiskServiceClient = None

from google.api_core import exceptions as gcp_exceptions

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)

# Global client instances
_firestore_client: Optional[firestore.AsyncClient] = None
_pubsub_publisher: Optional[pubsub_v1.PublisherClient] = None
_pubsub_subscriber: Optional[pubsub_v1.SubscriberClient] = None
_dlp_client: Optional[Any] = None  # Using Any for optional DLP client
_webrisk_client: Optional[Any] = None  # Using Any for optional WebRisk client


class GCPClientManager:
    """Manager for Google Cloud Platform clients."""
    
    def __init__(self):
        self.initialized = False
        self.mock_mode = settings.MOCK_GOOGLE_SERVICES
    
    async def initialize(self):
        """Initialize all GCP clients."""
        if self.initialized:
            return
        
        logger.info("🔧 Initializing Google Cloud clients...")
        
        try:
            if self.mock_mode:
                logger.info("🎭 Running in mock mode - using mock GCP clients")
                await self._init_mock_clients()
            else:
                await self._init_real_clients()
            
            self.initialized = True
            logger.info("✅ Google Cloud clients initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize GCP clients: {e}")
            # Fallback to mock mode if real clients fail
            if not self.mock_mode:
                logger.warning("🔄 Falling back to mock mode")
                self.mock_mode = True
                await self._init_mock_clients()
                self.initialized = True
    
    async def _init_real_clients(self):
        """Initialize real GCP clients."""
        global _firestore_client, _pubsub_publisher, _pubsub_subscriber, _dlp_client, _webrisk_client
        
        # Initialize Vertex AI
        if settings.GOOGLE_CLOUD_PROJECT_ID:
            aiplatform.init(
                project=settings.GOOGLE_CLOUD_PROJECT_ID,
                location=settings.VERTEX_AI_LOCATION
            )
        
        # Initialize Firestore
        _firestore_client = firestore.AsyncClient(
            project=settings.GOOGLE_CLOUD_PROJECT_ID,
            database=settings.FIRESTORE_DATABASE
        )
        
        # Initialize Pub/Sub
        _pubsub_publisher = pubsub_v1.PublisherClient()
        _pubsub_subscriber = pubsub_v1.SubscriberClient()
        
        # Initialize DLP (if available)
        if dlp_v2:
            _dlp_client = dlp_v2.DlpServiceClient()
        
        # Initialize Web Risk (if available)
        if WebRiskServiceClient:
            _webrisk_client = WebRiskServiceClient()
    
    async def _init_mock_clients(self):
        """Initialize mock clients for development."""
        global _firestore_client, _pubsub_publisher, _pubsub_subscriber, _dlp_client, _webrisk_client
        
        # Use mock implementations
        _firestore_client = MockFirestoreClient()
        _pubsub_publisher = MockPubSubPublisher()
        _pubsub_subscriber = MockPubSubSubscriber()
        _dlp_client = MockDLPClient()
        _webrisk_client = MockWebRiskClient()
    
    async def close(self):
        """Close all GCP clients."""
        if not self.initialized:
            return
        
        logger.info("🔒 Closing Google Cloud clients...")
        
        try:
            if not self.mock_mode and _firestore_client:
                await _firestore_client.close()
            
            # Other clients are synchronous and don't need explicit closing
            self.initialized = False
            logger.info("✅ Google Cloud clients closed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error closing GCP clients: {e}")


# Mock clients for development
class MockFirestoreClient:
    """Mock Firestore client for development."""
    
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
    
    def collection(self, name: str):
        return MockFirestoreCollection(name, self._data)
    
    async def close(self):
        pass


class MockFirestoreCollection:
    """Mock Firestore collection."""
    
    def __init__(self, name: str, data: Dict[str, Dict[str, Any]]):
        self.name = name
        self._data = data
        if name not in self._data:
            self._data[name] = {}
    
    def document(self, doc_id: str):
        return MockFirestoreDocument(self.name, doc_id, self._data)
    
    async def add(self, data: Dict[str, Any]):
        doc_id = f"mock_{len(self._data[self.name])}"
        self._data[self.name][doc_id] = data
        return (None, MockFirestoreDocument(self.name, doc_id, self._data))
    
    def stream(self):
        # Return async generator
        async def _stream():
            for doc_id, doc_data in self._data[self.name].items():
                yield MockFirestoreDocument(self.name, doc_id, self._data, doc_data)
        return _stream()


class MockFirestoreDocument:
    """Mock Firestore document."""
    
    def __init__(self, collection: str, doc_id: str, data: Dict[str, Dict[str, Any]], doc_data: Dict[str, Any] = None):
        self.collection = collection
        self.id = doc_id
        self._data = data
        self._doc_data = doc_data
    
    async def get(self):
        return MockDocumentSnapshot(
            self.collection, 
            self.id, 
            self._data[self.collection].get(self.id)
        )
    
    async def set(self, data: Dict[str, Any]):
        self._data[self.collection][self.id] = data
    
    async def update(self, data: Dict[str, Any]):
        if self.id in self._data[self.collection]:
            self._data[self.collection][self.id].update(data)
        else:
            self._data[self.collection][self.id] = data
    
    async def delete(self):
        if self.id in self._data[self.collection]:
            del self._data[self.collection][self.id]
    
    def to_dict(self):
        return self._doc_data or self._data[self.collection].get(self.id, {})


class MockDocumentSnapshot:
    """Mock Firestore document snapshot."""
    
    def __init__(self, collection: str, doc_id: str, data: Dict[str, Any]):
        self.id = doc_id
        self._data = data or {}
        self.exists = data is not None
    
    def to_dict(self):
        return self._data


class MockPubSubPublisher:
    """Mock Pub/Sub publisher."""
    
    def __init__(self):
        self._messages = []
    
    def topic_path(self, project: str, topic: str):
        return f"projects/{project}/topics/{topic}"
    
    def publish(self, topic: str, data: bytes, **attrs):
        self._messages.append({
            "topic": topic,
            "data": data,
            "attributes": attrs
        })
        return MockFuture("mock_message_id")


class MockPubSubSubscriber:
    """Mock Pub/Sub subscriber."""
    
    def subscription_path(self, project: str, subscription: str):
        return f"projects/{project}/subscriptions/{subscription}"


class MockDLPClient:
    """Mock DLP client."""
    
    def inspect_content(self, request):
        # Return mock inspection result
        return MockDLPResponse()


class MockDLPResponse:
    """Mock DLP response."""
    
    def __init__(self):
        self.result = MockDLPResult()


class MockDLPResult:
    """Mock DLP result."""
    
    def __init__(self):
        self.findings = []  # No PII found in mock mode


class MockWebRiskClient:
    """Mock Web Risk client."""
    
    def search_uris(self, request):
        # Return mock safe result
        return MockWebRiskResponse()


class MockWebRiskResponse:
    """Mock Web Risk response."""
    
    def __init__(self):
        self.threat = None  # No threats found in mock mode


class MockFuture:
    """Mock future for async operations."""
    
    def __init__(self, result):
        self._result = result
    
    def result(self):
        return self._result


# Global client manager instance
_client_manager = GCPClientManager()


async def init_gcp_clients():
    """Initialize GCP clients."""
    await _client_manager.initialize()


async def close_gcp_clients():
    """Close GCP clients."""
    await _client_manager.close()


def get_firestore_client() -> firestore.AsyncClient:
    """Get Firestore client."""
    if not _client_manager.initialized:
        raise RuntimeError("GCP clients not initialized")
    return _firestore_client


def get_pubsub_publisher() -> pubsub_v1.PublisherClient:
    """Get Pub/Sub publisher client."""
    if not _client_manager.initialized:
        raise RuntimeError("GCP clients not initialized")
    return _pubsub_publisher


def get_pubsub_subscriber() -> pubsub_v1.SubscriberClient:
    """Get Pub/Sub subscriber client."""
    if not _client_manager.initialized:
        raise RuntimeError("GCP clients not initialized")
    return _pubsub_subscriber


def get_dlp_client() -> dlp_v2.DlpServiceClient:
    """Get DLP client."""
    if not _client_manager.initialized:
        raise RuntimeError("GCP clients not initialized")
    return _dlp_client


def get_webrisk_client() -> webrisk_v1.WebRiskServiceClient:
    """Get Web Risk client."""
    if not _client_manager.initialized:
        raise RuntimeError("GCP clients not initialized")
    return _webrisk_client


def is_mock_mode() -> bool:
    """Check if running in mock mode."""
    return _client_manager.mock_mode