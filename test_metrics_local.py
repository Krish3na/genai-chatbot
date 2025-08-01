#!/usr/bin/env python3
"""
Test script for GenAI Chatbot monitoring metrics
"""
import requests
import time
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_chat_request():
    """Test chat endpoint"""
    print("💬 Testing chat endpoint...")
    payload = {
        "message": "Hello, how are you today?",
        "user_id": "test_user_1"
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['response'][:100]}...")
        print(f"Intent: {data['intent']}")
        print(f"Confidence: {data['confidence']}")
        print(f"Tokens Used: {data['tokens_used']}")
        print(f"Cost: ${data['cost']:.6f}")
    print()

def test_rag_request():
    """Test RAG-enabled chat"""
    print("🔍 Testing RAG-enabled chat...")
    payload = {
        "message": "What information do you have about proteins?",
        "user_id": "test_user_2",
        "use_rag": True
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['response'][:100]}...")
        print(f"Sources Used: {data['sources_used']}")
        print(f"Context Length: {data['context_length']}")
    print()

def test_document_upload():
    """Test document upload"""
    print("📄 Testing document upload...")
    files = {'file': ('test_document.txt', 'This is a test document for monitoring.', 'text/plain')}
    response = requests.post(f"{BASE_URL}/upload-document", files=files)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
    print()

def test_knowledge_base_stats():
    """Test knowledge base stats"""
    print("📊 Testing knowledge base stats...")
    response = requests.get(f"{BASE_URL}/knowledge-base/stats")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Documents: {data['total_documents']}")
        print(f"Persist Directory: {data['persist_directory']}")
    print()

def test_metrics():
    """Test metrics endpoint"""
    print("📈 Testing metrics endpoint...")
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        metrics = response.text
        # Look for our custom metrics
        custom_metrics = [
            "genai_chatbot_chat_requests_total",
            "genai_chatbot_tokens_used_total",
            "genai_chatbot_cost_total",
            "genai_chatbot_intent_classifications_total"
        ]
        for metric in custom_metrics:
            if metric in metrics:
                print(f"✅ Found metric: {metric}")
            else:
                print(f"❌ Missing metric: {metric}")
    print()

def test_error_handling():
    """Test error handling"""
    print("⚠️ Testing error handling...")
    # Test invalid endpoint
    response = requests.get(f"{BASE_URL}/invalid-endpoint")
    print(f"Invalid endpoint status: {response.status_code}")
    
    # Test invalid chat request
    payload = {"invalid": "data"}
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Invalid chat request status: {response.status_code}")
    print()

def main():
    """Run all tests"""
    print("🚀 Starting GenAI Chatbot Monitoring Tests")
    print("=" * 50)
    
    try:
        test_health()
        test_chat_request()
        test_rag_request()
        test_document_upload()
        test_knowledge_base_stats()
        test_metrics()
        test_error_handling()
        
        print("✅ All tests completed!")
        print("\n📊 To view metrics in Grafana:")
        print("1. Port forward Grafana: kubectl port-forward svc/grafana-service 3000:3000 -n genai-chatbot")
        print("2. Open http://localhost:3000 in your browser")
        print("3. Login with admin/admin")
        print("4. Look for 'GenAI Chatbot Dashboard'")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the application.")
        print("Make sure the application is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 