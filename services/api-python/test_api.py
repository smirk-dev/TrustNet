"""
Simple API Test Script
Test the TrustNet Python backend endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_VERSION = "v1"

def test_health_check():
    """Test the health check endpoint."""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            data = response.json()
            print(f"   API Name: {data.get('name')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_verification_endpoint():
    """Test the content verification endpoint."""
    print("\n🔍 Testing verification endpoint...")
    try:
        payload = {
            "content": "This is a test message to verify the API is working correctly.",
            "content_type": "text",
            "priority": "normal",
            "metadata": {
                "source": "api_test",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/{API_VERSION}/verify",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Verification endpoint working")
            data = response.json()
            print(f"   Verification ID: {data.get('verification_id')}")
            print(f"   Status: {data.get('status')}")
            return data.get('verification_id')
        else:
            print(f"❌ Verification endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Verification endpoint error: {e}")
        return None

def test_get_verification_result(verification_id):
    """Test getting verification results."""
    if not verification_id:
        print("\n⏭️  Skipping verification result test (no verification ID)")
        return False
    
    print(f"\n📊 Testing verification result for ID: {verification_id}")
    try:
        response = requests.get(f"{BASE_URL}/{API_VERSION}/verify/{verification_id}")
        
        if response.status_code == 200:
            print("✅ Verification result endpoint working")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Verification result failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Verification result error: {e}")
        return False

def test_educational_feed():
    """Test the educational feed endpoint."""
    print("\n📚 Testing educational feed...")
    try:
        response = requests.get(f"{BASE_URL}/{API_VERSION}/feed?limit=3")
        
        if response.status_code == 200:
            print("✅ Educational feed working")
            data = response.json()
            print(f"   Feed items count: {len(data.get('feed_items', []))}")
            print(f"   Language: {data.get('language')}")
            return True
        else:
            print(f"❌ Educational feed failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Educational feed error: {e}")
        return False

def test_analysis_endpoint():
    """Test the content analysis endpoint."""
    print("\n🔬 Testing analysis endpoint...")
    try:
        payload = {
            "content": "BREAKING: Shocking revelation that will change everything!",
            "analysis_type": "comprehensive",
            "priority": "normal"
        }
        
        response = requests.post(
            f"{BASE_URL}/{API_VERSION}/analysis/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Analysis endpoint working")
            data = response.json()
            print(f"   Analysis ID: {data.get('analysis_id')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Analysis endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analysis endpoint error: {e}")
        return False

def test_feedback_endpoint():
    """Test the feedback submission endpoint."""
    print("\n💬 Testing feedback endpoint...")
    try:
        payload = {
            "feedback_type": "verification_accuracy",
            "content": "The API test worked perfectly! Great job on the implementation.",
            "rating": 5,
            "user_id": "test_user",
            "metadata": {
                "test_run": True,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/{API_VERSION}/feedback/submit",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Feedback endpoint working")
            data = response.json()
            print(f"   Feedback ID: {data.get('feedback_id')}")
            print(f"   Points awarded: {data.get('contribution_points')}")
            return True
        else:
            print(f"❌ Feedback endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Feedback endpoint error: {e}")
        return False

def main():
    """Run all API tests."""
    print("🚀 TrustNet Python Backend API Test")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(test_health_check())
    results.append(test_root_endpoint())
    
    verification_id = test_verification_endpoint()
    results.append(verification_id is not None)
    results.append(test_get_verification_result(verification_id))
    
    results.append(test_educational_feed())
    results.append(test_analysis_endpoint())
    results.append(test_feedback_endpoint())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 Next steps:")
    print("1. View API documentation: http://localhost:8000/docs")
    print("2. Try the interactive API explorer")
    print("3. Integrate with your frontend application")

if __name__ == "__main__":
    main()