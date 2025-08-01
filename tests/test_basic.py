"""
Basic tests for GenAI Chatbot
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200

def test_metrics_endpoint():
    """Test the metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Should contain Prometheus metrics
    assert "prometheus" in response.text.lower()

def test_chat_endpoint():
    """Test the chat endpoint with a simple message"""
    response = client.post("/chat", json={
        "message": "Hello, this is a test",
        "user_id": "test_user"
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent_description" in data

def test_intents_info():
    """Test the intents info endpoint"""
    response = client.get("/intents/info")
    assert response.status_code == 200
    data = response.json()
    assert "intents" in data

def test_knowledge_base_stats():
    """Test the knowledge base stats endpoint"""
    response = client.get("/knowledge-base/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data 