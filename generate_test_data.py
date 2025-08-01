#!/usr/bin/env python3
"""
Generate test data for GenAI Chatbot monitoring
"""
import requests
import time
import json
import random
from typing import Dict, Any

BASE_URL = "http://genai-chatbot.local"  # Using Ingress URL

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def generate_chat_requests():
    """Generate multiple chat requests to create metrics"""
    print("💬 Generating chat requests...")
    
    messages = [
        "Hello, how are you?",
        "What is machine learning?",
        "Tell me about Python programming",
        "How does RAG work?",
        "What are the benefits of Kubernetes?",
        "Explain microservices architecture",
        "What is the difference between AI and ML?",
        "How do neural networks work?",
        "Tell me about Docker containers",
        "What is CI/CD pipeline?"
    ]
    
    for i in range(20):
        message = random.choice(messages)
        user_id = f"test_user_{i % 5}"
        
        payload = {
            "message": message,
            "user_id": user_id
        }
        
        try:
            response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Request {i+1}: {message[:30]}... (Tokens: {result.get('tokens_used', 'N/A')})")
            else:
                print(f"❌ Request {i+1}: Failed with status {response.status_code}")
        except Exception as e:
            print(f"❌ Request {i+1}: Error - {e}")
        
        # Add some delay between requests
        time.sleep(2)
    
    print()

def test_document_upload():
    """Test document upload to generate KB metrics"""
    print("📄 Testing document upload...")
    
    # Create a test document
    test_content = """
    This is a test document about artificial intelligence.
    AI is a branch of computer science that aims to create intelligent machines.
    Machine learning is a subset of AI that enables computers to learn without being explicitly programmed.
    Deep learning is a type of machine learning based on artificial neural networks.
    """
    
    files = {
        'file': ('test_ai_document.txt', test_content, 'text/plain')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/upload-document", files=files)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document uploaded: {result.get('filename', 'N/A')}")
        else:
            print(f"❌ Upload failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Upload error: {e}")
    
    print()

def test_knowledge_base_stats():
    """Test knowledge base stats"""
    print("📊 Testing knowledge base stats...")
    try:
        response = requests.get(f"{BASE_URL}/knowledge-base/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ KB Stats: {stats}")
        else:
            print(f"❌ Stats failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")
    
    print()

def test_metrics_endpoint():
    """Test metrics endpoint"""
    print("📈 Testing metrics endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        if response.status_code == 200:
            metrics = response.text
            # Look for our custom metrics
            if "genai_chatbot" in metrics:
                print("✅ Custom metrics found!")
                # Show some key metrics
                lines = metrics.split('\n')
                for line in lines:
                    if "genai_chatbot" in line and ("total" in line or "duration" in line):
                        print(f"   {line}")
            else:
                print("❌ No custom metrics found")
        else:
            print(f"❌ Metrics failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Metrics error: {e}")
    
    print()

def main():
    """Main function to generate test data"""
    print("🚀 Generating test data for GenAI Chatbot monitoring...")
    print("=" * 60)
    
    # Test health first
    test_health()
    
    # Generate chat requests
    generate_chat_requests()
    
    # Test document upload
    test_document_upload()
    
    # Test knowledge base stats
    test_knowledge_base_stats()
    
    # Test metrics endpoint
    test_metrics_endpoint()
    
    print("🎉 Test data generation complete!")
    print("📊 Check your Grafana dashboard for visualizations!")
    print("🔗 Grafana URL: http://localhost:3000")
    print("🔗 Prometheus URL: http://localhost:9090")

if __name__ == "__main__":
    main() 