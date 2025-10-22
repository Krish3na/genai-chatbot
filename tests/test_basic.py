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

def test_metrics_endpoint(client):
    """Test the metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Should contain Prometheus metrics
    assert "genai_chatbot" in response.text.lower()

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
    # First create a conversation by sending a message
    client.post("/chat", json={
        "message": "Test message",
        "user_id": "test_user_clear",
        "session_id": "test_session"
    })
    
    # Now test clearing it
    response = client.delete("/conversation/test_user_clear")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_user_stats_endpoint(client):
    """Test user stats endpoint"""
    # First create some activity by sending a message
    client.post("/chat", json={
        "message": "Test message for stats",
        "user_id": "test_user_stats",
        "session_id": "test_session"
    })
    
    # Now test getting stats
    response = client.get("/stats/test_user_stats")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "message_count" in data

def test_intents_info(client):
    """Test the intents info endpoint"""
    response = client.get("/intents/info")
    assert response.status_code == 200
    data = response.json()
    assert "available_intents" in data
    assert "total_intents" in data
    assert "auto_classification" in data

def test_knowledge_base_stats(client):
    """Test the knowledge base stats endpoint"""
    response = client.get("/knowledge-base/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "persist_directory" in data
    assert "collection_name" in data

def test_available_documents(client):
    """Test the available documents endpoint"""
    response = client.get("/documents/available")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total_count" in data

def test_test_endpoint(client):
    """Test the simple test endpoint"""
    response = client.get("/test")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "timestamp" in data
    assert "status" in data
    assert data["status"] == "ok"
