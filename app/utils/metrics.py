"""
Custom Prometheus metrics for GenAI Chatbot
"""
from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# Chat metrics
CHAT_REQUESTS_TOTAL = Counter(
    'genai_chatbot_chat_requests_total',
    'Total number of chat requests',
    ['user_id', 'intent', 'response_type']
)

CHAT_REQUEST_DURATION = Histogram(
    'genai_chatbot_chat_request_duration_seconds',
    'Duration of chat requests',
    ['user_id', 'intent', 'response_type']
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

# Intent classification metrics
INTENT_CLASSIFICATIONS_TOTAL = Counter(
    'genai_chatbot_intent_classifications_total',
    'Total number of intent classifications',
    ['intent', 'confidence_level']
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
    ['file_type']
)

KNOWLEDGE_BASE_DOCUMENTS = Gauge(
    'genai_chatbot_knowledge_base_documents',
    'Number of documents in knowledge base'
)

# Error metrics
ERRORS_TOTAL = Counter(
    'genai_chatbot_errors_total',
    'Total number of errors',
    ['error_type', 'endpoint']
)

# Active conversations metric
ACTIVE_CONVERSATIONS = Gauge(
    'genai_chatbot_active_conversations',
    'Number of active conversations'
)

def record_chat_metrics(user_id: str, intent: str, response_type: str, duration: float, tokens: int, cost: float, model: str, 
                       response: Optional[str] = None, rag_sources: Optional[List[str]] = None, confidence: Optional[float] = None,
                       conversation_id: Optional[str] = None):
    """Record metrics for chat requests"""
    CHAT_REQUESTS_TOTAL.labels(user_id=user_id, intent=intent, response_type=response_type).inc()
    CHAT_REQUEST_DURATION.labels(user_id=user_id, intent=intent, response_type=response_type).observe(duration)
    CHAT_TOKENS_USED.labels(user_id=user_id, model=model, intent=intent).inc(tokens)
    CHAT_COST_TOTAL.labels(user_id=user_id, model=model).inc(cost)
    
    # Log to MLflow if enabled
    try:
        from app.config import settings
        if settings.MLFLOW_ENABLED:
            # Log general chat metrics
            from app.utils.mlflow_tracker import mlflow_tracker
            mlflow_tracker.log_chat_interaction(
                user_message="",  # Will be passed from the actual chat endpoint
                response=response or "",
                intent=intent,
                response_type=response_type,
                duration=duration,
                tokens_used=tokens,
                cost=cost,
                rag_sources=rag_sources,
                confidence=confidence
            )
            
            # Log detailed cost metrics
            from app.utils.mlflow_cost_tracker import MLflowCostTracker
            cost_tracker = MLflowCostTracker()
            cost_tracker.log_conversation_costs(
                tokens_used=tokens,
                cost_usd=cost,
                model=model,
                conversation_id=conversation_id or "unknown",
                user_id=user_id,
                response_type=response_type,
                metadata={
                    "intent": intent,
                    "duration": duration,
                    "confidence": confidence or 0.0,
                    "sources_used": len(rag_sources) if rag_sources else 0
                }
            )
            
            # Log detailed performance metrics
            from app.utils.mlflow_performance_tracker import MLflowPerformanceTracker
            performance_tracker = MLflowPerformanceTracker()
            performance_tracker.log_request_performance(
                response_time=duration,
                request_type=response_type,
                user_id=user_id,
                success=True,  # We'll update this when we implement error tracking
                metadata={
                    "intent": intent,
                    "model": model,
                    "confidence": confidence or 0.0,
                    "sources_used": len(rag_sources) if rag_sources else 0,
                    "tokens_used": tokens
                }
            )
            
            # Log quality metrics
            from app.utils.mlflow_quality_tracker import MLflowQualityTracker
            quality_tracker = MLflowQualityTracker()
            
            # Log intent accuracy (confidence is available)
            if confidence is not None:
                quality_tracker.log_intent_accuracy(
                    intent_predicted=intent,
                    confidence_score=confidence,
                    user_id=user_id
                )
            
            # Log response relevance (estimate based on response type and confidence)
            if response and confidence is not None:
                relevance_score = min(0.95, confidence * 1.2) if response_type == "rag" else confidence
                quality_tracker.log_response_relevance(
                    user_message="",  # Will be passed from actual chat endpoint
                    response=response,
                    relevance_score=relevance_score,
                    intent=intent,
                    response_type=response_type,
                    user_id=user_id
                )
            
            # Log RAG quality if it's a RAG response
            if response_type == "rag" and rag_sources and response:
                # Estimate quality scores based on available data
                context_relevance = min(0.9, confidence * 1.1) if confidence else 0.7
                source_quality = min(0.85, len(rag_sources) * 0.2) if rag_sources else 0.5
                hallucination_score = max(0.05, 0.3 - (confidence * 0.2)) if confidence else 0.2
                
                quality_tracker.log_rag_quality(
                    user_message="",  # Will be passed from actual chat endpoint
                    response=response,
                    sources_used=rag_sources,
                    context_relevance=context_relevance,
                    source_quality=source_quality,
                    hallucination_score=hallucination_score,
                    user_id=user_id
                )
    except Exception as e:
        logger.error(f"Failed to log to MLflow: {e}")

def record_rag_metrics(user_id: str, sources_used: int, context_length: int):
    """Record metrics for RAG requests"""
    RAG_REQUESTS_TOTAL.labels(user_id=user_id).inc()
    RAG_SOURCES_USED.labels(user_id=user_id).observe(sources_used)
    RAG_CONTEXT_LENGTH.labels(user_id=user_id).observe(context_length)

def record_intent_classification(intent: str, confidence: float):
    """Record metrics for intent classification"""
    confidence_level = "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low"
    INTENT_CLASSIFICATIONS_TOTAL.labels(intent=intent, confidence_level=confidence_level).inc()

def record_document_upload(file_type: str, success: bool):
    """Record metrics for document uploads"""
    DOCUMENT_UPLOADS_TOTAL.labels(file_type=file_type, success=success).inc()

def record_document_deletion(file_type: str):
    """Record metrics for document deletions"""
    DOCUMENT_DELETIONS_TOTAL.labels(file_type=file_type).inc()

def update_knowledge_base_documents(count: int):
    """Update the number of documents in knowledge base"""
    KNOWLEDGE_BASE_DOCUMENTS.set(count)

def record_error(error_type: str, endpoint: str, error_message: str = "", status_code: int = 500, 
                 user_id: str = "unknown", stack_trace: str = None):
    """Record error metrics"""
    ERRORS_TOTAL.labels(error_type=error_type, endpoint=endpoint).inc()
    
    # Log to MLflow if enabled
    try:
        from app.config import settings
        if settings.MLFLOW_ENABLED:
            from app.utils.mlflow_error_tracker import MLflowErrorTracker
            error_tracker = MLflowErrorTracker()
            
            error_tracker.log_api_error(
                endpoint=endpoint,
                error_type=error_type,
                error_message=error_message,
                status_code=status_code,
                user_id=user_id,
                stack_trace=stack_trace
            )
    except Exception as e:
        logger.error(f"Failed to log error to MLflow: {e}")

def update_active_conversations(count: int):
    """Update the number of active conversations"""
    ACTIVE_CONVERSATIONS.set(count)

def log_system_metrics_to_mlflow():
    """Log current system metrics to MLflow"""
    try:
        from app.config import settings
        if not settings.MLFLOW_ENABLED:
            return
            
        from app.utils.mlflow_tracker import mlflow_tracker
        
        # Calculate current metrics
        active_conversations = ACTIVE_CONVERSATIONS._value._value
        total_documents = KNOWLEDGE_BASE_DOCUMENTS._value._value
        
        # Calculate error rate (simplified)
        total_errors = sum([metric._value._value for metric in ERRORS_TOTAL._metrics.values()])
        total_requests = sum([metric._value._value for metric in CHAT_REQUESTS_TOTAL._metrics.values()])
        error_rate = total_errors / max(total_requests, 1)
        
        # Calculate average context length (simplified)
        context_samples = [metric._sum._value for metric in RAG_CONTEXT_LENGTH._metrics.values()]
        context_counts = [metric._count._value for metric in RAG_CONTEXT_LENGTH._metrics.values()]
        avg_context_length = sum(context_samples) / max(sum(context_counts), 1)
        
        mlflow_tracker.log_system_metrics(
            active_conversations=active_conversations,
            total_documents=total_documents,
            avg_rag_context_length=avg_context_length,
            error_rate=error_rate
        )
        
    except Exception as e:
        logger.error(f"Failed to log system metrics to MLflow: {e}")

def log_model_performance_to_mlflow(accuracy: float = 0.9, precision: float = 0.85, 
                                   recall: float = 0.88, f1_score: float = 0.86):
    """Log model performance metrics to MLflow"""
    try:
        from app.config import settings
        if not settings.MLFLOW_ENABLED:
            return
            
        from app.utils.mlflow_tracker import mlflow_tracker
        
        # Calculate average response time
        duration_samples = [metric._sum._value for metric in CHAT_REQUEST_DURATION._metrics.values()]
        duration_counts = [metric._count._value for metric in CHAT_REQUEST_DURATION._metrics.values()]
        avg_response_time = sum(duration_samples) / max(sum(duration_counts), 1)
        
        # Get total interactions
        total_interactions = sum([metric._value._value for metric in CHAT_REQUESTS_TOTAL._metrics.values()])
        
        mlflow_tracker.log_model_performance(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            avg_response_time=avg_response_time,
            total_interactions=total_interactions
        )
        
    except Exception as e:
        logger.error(f"Failed to log model performance to MLflow: {e}") 