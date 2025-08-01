"""
Basic tests for GenAI Chatbot
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_chat_endpoint_placeholder(client):
    """Test chat endpoint with placeholder response"""
    # Mock the OpenAI API key for testing
    import os
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    response = client.post("/chat", json={
        "message": "Hello, how are you?",
        "user_id": "test_user",
        "session_id": "test_session"
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    assert "confidence" in data
    assert "latency_ms" in data
    assert "tokens_used" in data
    assert "cost" in data
    assert "model" in data
    assert data["intent"] == "general"
    assert data["confidence"] == 0.8

def test_chat_endpoint_invalid_request(client):
    """Test chat endpoint with invalid request"""
    response = client.post("/chat", json={
        "message": ""  # Empty message
    })
    assert response.status_code == 200  # Should still work with empty message

def test_conversation_history_endpoint(client):
    """Test conversation history endpoint"""
    response = client.get("/conversation/test_user/history")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "history" in data
    assert "message_count" in data
    assert data["user_id"] == "test_user"

def test_clear_conversation_endpoint(client):
    """Test clear conversation endpoint"""
    response = client.delete("/conversation/test_user")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_user_stats_endpoint(client):
    """Test user stats endpoint"""
    response = client.get("/stats/test_user")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "message_count" in data
    assert "created_at" in data
    assert "last_activity" in data 