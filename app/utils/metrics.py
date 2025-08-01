"""
Custom Prometheus metrics for GenAI Chatbot
"""
from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Dict, Any

# Chat metrics
CHAT_REQUESTS_TOTAL = Counter(
    'genai_chatbot_chat_requests_total',
    'Total number of chat requests',
    ['user_id', 'intent', 'response_type']
)

CHAT_REQUEST_DURATION = Histogram(
    'genai_chatbot_chat_request_duration_seconds',
    'Duration of chat requests',
    ['user_id', 'intent']
)

CHAT_TOKENS_USED = Counter(
    'genai_chatbot_tokens_used_total',
    'Total tokens used in chat responses',
    ['user_id', 'model', 'intent']
)

CHAT_COST_TOTAL = Counter(
    'genai_chatbot_cost_total',
    'Total cost of chat requests',
    ['user_id', 'model']
)

# RAG metrics
RAG_REQUESTS_TOTAL = Counter(
    'genai_chatbot_rag_requests_total',
    'Total number of RAG requests',
    ['user_id']
)

RAG_SOURCES_USED = Histogram(
    'genai_chatbot_rag_sources_used',
    'Number of sources used in RAG responses',
    ['user_id']
)

RAG_CONTEXT_LENGTH = Histogram(
    'genai_chatbot_rag_context_length',
    'Length of context used in RAG responses',
    ['user_id']
)

# Document management metrics
DOCUMENT_UPLOADS_TOTAL = Counter(
    'genai_chatbot_document_uploads_total',
    'Total number of document uploads',
    ['file_type', 'success']
)

DOCUMENT_DELETIONS_TOTAL = Counter(
    'genai_chatbot_document_deletions_total',
    'Total number of document deletions',
    ['file_type', 'success']
)

KNOWLEDGE_BASE_DOCUMENTS = Gauge(
    'genai_chatbot_knowledge_base_documents',
    'Number of documents in knowledge base'
)

# Intent classification metrics
INTENT_CLASSIFICATIONS_TOTAL = Counter(
    'genai_chatbot_intent_classifications_total',
    'Total number of intent classifications',
    ['intent', 'confidence_level']
)

# Error metrics
ERRORS_TOTAL = Counter(
    'genai_chatbot_errors_total',
    'Total number of errors',
    ['error_type', 'endpoint']
)

# System metrics
ACTIVE_CONVERSATIONS = Gauge(
    'genai_chatbot_active_conversations',
    'Number of active conversations'
)

def record_chat_metrics(
    user_id: str,
    intent: str,
    response_type: str,
    duration: float,
    tokens: int,
    cost: float,
    model: str
):
    """Record metrics for a chat request"""
    print(f"DEBUG: Recording chat metrics - user_id: {user_id}, intent: {intent}, response_type: {response_type}")
    CHAT_REQUESTS_TOTAL.labels(user_id=user_id, intent=intent, response_type=response_type).inc()
    CHAT_REQUEST_DURATION.labels(user_id=user_id, intent=intent).observe(duration)
    CHAT_TOKENS_USED.labels(user_id=user_id, model=model, intent=intent).inc(tokens)
    CHAT_COST_TOTAL.labels(user_id=user_id, model=model).inc(cost)
    print(f"DEBUG: Chat metrics recorded successfully")

def record_rag_metrics(
    user_id: str,
    sources_used: int,
    context_length: int
):
    """Record metrics for RAG requests"""
    RAG_REQUESTS_TOTAL.labels(user_id=user_id).inc()
    RAG_SOURCES_USED.labels(user_id=user_id).observe(sources_used)
    RAG_CONTEXT_LENGTH.labels(user_id=user_id).observe(context_length)

def record_document_upload(file_type: str, success: bool):
    """Record metrics for document uploads"""
    DOCUMENT_UPLOADS_TOTAL.labels(file_type=file_type, success=str(success)).inc()

def record_document_deletion(file_type: str, success: bool):
    """Record metrics for document deletions"""
    DOCUMENT_DELETIONS_TOTAL.labels(file_type=file_type, success=str(success)).inc()

def update_knowledge_base_documents(count: int):
    """Update the number of documents in knowledge base"""
    KNOWLEDGE_BASE_DOCUMENTS.set(count)

def record_intent_classification(intent: str, confidence: float):
    """Record metrics for intent classification"""
    confidence_level = "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low"
    INTENT_CLASSIFICATIONS_TOTAL.labels(intent=intent, confidence_level=confidence_level).inc()

def record_error(error_type: str, endpoint: str):
    """Record error metrics"""
    ERRORS_TOTAL.labels(error_type=error_type, endpoint=endpoint).inc()

def update_active_conversations(count: int):
    """Update the number of active conversations"""
    ACTIVE_CONVERSATIONS.set(count) 