"""
Aggregates quality metrics for batch logging to MLflow
"""
from datetime import datetime
import logging
import threading
import time
from typing import Dict, Any
from .mlflow_quality_tracker import MLflowQualityTracker

logger = logging.getLogger(__name__)

def log_batch_quality(time_period: str = 'hourly'):
    """
    Log aggregated quality metrics to MLflow
    """
    try:
        # Get quality metrics
        quality_tracker = MLflowQualityTracker()
        metrics = quality_tracker.calculate_quality_metrics()
        
        # Add timestamp info
        now = datetime.now()
        metrics['timestamp'] = now.isoformat()
        
        # Log to MLflow
        quality_tracker.log_batch_quality(
            time_period=time_period,
            quality_metrics=metrics
        )
        
        logger.info(f"Successfully logged batch quality metrics for {time_period}")
        
    except Exception as e:
        logger.error(f"Failed to log batch quality metrics: {e}")

def schedule_quality_logging():
    """
    Schedule periodic quality metrics logging
    """
    def quality_logging_worker():
        while True:
            try:
                # Log hourly quality metrics
                log_batch_quality('hourly')
                
                # Wait for 1 hour
                time.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in quality logging worker: {e}")
                # Wait 5 minutes before retrying
                time.sleep(300)
    
    # Start the quality logging thread
    quality_thread = threading.Thread(target=quality_logging_worker, daemon=True)
    quality_thread.start()
    logger.info("Quality metrics logging scheduler started")

def calculate_intent_accuracy(predicted_intents: list, actual_intents: list) -> float:
    """
    Calculate intent classification accuracy
    """
    if not predicted_intents or not actual_intents or len(predicted_intents) != len(actual_intents):
        return 0.0
    
    correct = sum(1 for p, a in zip(predicted_intents, actual_intents) if p == a)
    return correct / len(predicted_intents)

def calculate_response_relevance(user_messages: list, responses: list, relevance_scores: list) -> Dict[str, float]:
    """
    Calculate response relevance statistics
    """
    if not relevance_scores:
        return {
            'avg_relevance': 0.0,
            'min_relevance': 0.0,
            'max_relevance': 0.0,
            'total_responses': 0
        }
    
    return {
        'avg_relevance': sum(relevance_scores) / len(relevance_scores),
        'min_relevance': min(relevance_scores),
        'max_relevance': max(relevance_scores),
        'total_responses': len(relevance_scores)
    }

def calculate_rag_quality_metrics(rag_interactions: list) -> Dict[str, float]:
    """
    Calculate RAG-specific quality metrics
    """
    if not rag_interactions:
        return {
            'avg_context_relevance': 0.0,
            'avg_source_quality': 0.0,
            'avg_factuality': 0.0,
            'avg_sources_used': 0.0,
            'total_rag_interactions': 0
        }
    
    context_relevance = [r.get('context_relevance', 0.0) for r in rag_interactions]
    source_quality = [r.get('source_quality', 0.0) for r in rag_interactions]
    factuality = [1.0 - r.get('hallucination_score', 0.0) for r in rag_interactions]
    sources_used = [len(r.get('sources_used', [])) for r in rag_interactions]
    
    return {
        'avg_context_relevance': sum(context_relevance) / len(context_relevance) if context_relevance else 0.0,
        'avg_source_quality': sum(source_quality) / len(source_quality) if source_quality else 0.0,
        'avg_factuality': sum(factuality) / len(factuality) if factuality else 0.0,
        'avg_sources_used': sum(sources_used) / len(sources_used) if sources_used else 0.0,
        'total_rag_interactions': len(rag_interactions)
    }

def calculate_user_satisfaction_metrics(satisfaction_data: list) -> Dict[str, float]:
    """
    Calculate user satisfaction statistics
    """
    if not satisfaction_data:
        return {
            'avg_satisfaction': 0.0,
            'min_satisfaction': 0.0,
            'max_satisfaction': 0.0,
            'satisfaction_distribution': {},
            'total_feedback_count': 0
        }
    
    scores = [s.get('score', 0.0) for s in satisfaction_data]
    
    # Calculate satisfaction distribution (1-5 scale)
    distribution = {}
    for score in scores:
        bucket = int(score) if score > 0 else 1
        bucket = min(5, max(1, bucket))  # Clamp to 1-5 range
        distribution[bucket] = distribution.get(bucket, 0) + 1
    
    return {
        'avg_satisfaction': sum(scores) / len(scores) if scores else 0.0,
        'min_satisfaction': min(scores) if scores else 0.0,
        'max_satisfaction': max(scores) if scores else 0.0,
        'satisfaction_distribution': distribution,
        'total_feedback_count': len(satisfaction_data)
    }
