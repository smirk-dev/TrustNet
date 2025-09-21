# Simple test to verify the basic setup is working
print("🔍 Testing core imports and basic functionality...")

# Test 1: Basic FastAPI import
try:
    from fastapi import FastAPI
    print("✅ FastAPI import successful")
except Exception as e:
    print(f"❌ FastAPI import failed: {e}")

# Test 2: Pydantic import and basic model
try:
    from pydantic import BaseModel, Field
    
    class TestModel(BaseModel):
        text: str = Field(..., min_length=1, max_length=100)
        score: float = Field(..., ge=0, le=1)
    
    # Test the model
    test_data = TestModel(text="Hello world", score=0.85)
    print("✅ Pydantic v2 models working")
    print(f"   Test data: {test_data}")
except Exception as e:
    print(f"❌ Pydantic test failed: {e}")

# Test 3: Google Cloud imports
try:
    from google.cloud import firestore
    print("✅ Google Cloud Firestore import successful")
except Exception as e:
    print(f"❌ Google Cloud Firestore import failed: {e}")

try:
    from google.cloud import aiplatform
    print("✅ Google Cloud AI Platform import successful")
except Exception as e:
    print(f"❌ Google Cloud AI Platform import failed: {e}")

# Test 4: Core app schemas
try:
    from app.models.schemas import VerificationRequest, AnalysisRequest
    
    # Test creating a request
    request = VerificationRequest(text="This is a test claim about something")
    print("✅ Core schemas import and creation successful")
    print(f"   Test request: {request.text[:50]}...")
except Exception as e:
    print(f"❌ Core schemas test failed: {e}")

# Test 5: Core GCP module
try:
    from app.core.gcp import init_gcp_clients, get_firestore_client
    print("✅ Core GCP module imports successful")
except Exception as e:
    print(f"❌ Core GCP module import failed: {e}")

print("\n🏁 Basic setup testing completed!")
print("✅ Ready for development and testing")