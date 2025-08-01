#!/usr/bin/env python3
"""
Simple test script for the GenAI Chatbot API
"""
import requests
import json

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    try:
        data = {
            "message": "Hello, how are you?",
            "user_id": "test_user"
        }
        response = requests.post("http://localhost:8000/chat", json=data)
        print(f"✅ Chat endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing GenAI Chatbot API...")
    print("=" * 50)
    
    health_ok = test_health()
    print()
    chat_ok = test_chat()
    
    print("=" * 50)
    if health_ok and chat_ok:
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("❌ Some tests failed. Check the server logs for details.") 