"""
MLflow Quality Metrics Tracker
"""
import mlflow
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MLflowQualityTracker:
    """Tracks quality-related metrics in MLflow"""
    
    def __init__(self, experiment_name: str = "genai-chatbot-quality"):
        self.experiment_name = experiment_name
        try:
            # Set tracking URI to our MLflow server
            mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000'))
            # Get or create the experiment
            self.experiment = mlflow.get_experiment_by_name(experiment_name)
            if not self.experiment:
                mlflow.create_experiment(experiment_name)
            logger.info(f"MLflow quality tracking initialized for experiment: {experiment_name}")
        except Exception as e:
            logger.error(f"Failed to initialize MLflow quality tracking: {e}")
            raise

    def log_intent_accuracy(self, 
                           intent_predicted: str, 
                           intent_actual: Optional[str] = None,
                           confidence_score: float = 0.0,
                           user_id: str = "default",
                           timestamp: Optional[datetime] = None):
        """Log intent classification accuracy"""
        try:
            timestamp = timestamp or datetime.now()
            
            with mlflow.start_run(run_name=f"intent_accuracy_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
                # Log parameters
                mlflow.log_param("intent_predicted", intent_predicted)
                if intent_actual:
                    mlflow.log_param("intent_actual", intent_actual)
                mlflow.log_param("user_id", user_id)
                mlflow.log_param("timestamp", timestamp.isoformat())
                
                # Log metrics
                mlflow.log_metric("confidence_score", confidence_score)
                if intent_actual:
                    accuracy = 1.0 if intent_predicted == intent_actual else 0.0
                    mlflow.log_metric("intent_accuracy", accuracy)
                
                # Log tags
                mlflow.set_tag("metric_type", "quality")
                mlflow.set_tag("quality_aspect", "intent_classification")
                mlflow.set_tag("user_id", user_id)
                
                logger.info(f"Logged intent accuracy: {intent_predicted} (confidence: {confidence_score})")
                
        except Exception as e:
            logger.error(f"Failed to log intent accuracy to MLflow: {e}")

    def log_response_relevance(self,
                              user_message: str,
                              response: str,
                              relevance_score: float,
                              intent: str,
                              response_type: str,
                              user_id: str = "default",
                              timestamp: Optional[datetime] = None):
        """Log response relevance quality metrics"""
        try:
            timestamp = timestamp or datetime.now()
            
            with mlflow.start_run(run_name=f"response_relevance_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
                # Log parameters
                mlflow.log_param("intent", intent)
                mlflow.log_param("response_type", response_type)
                mlflow.log_param("user_id", user_id)
                mlflow.log_param("timestamp", timestamp.isoformat())
                mlflow.log_param("message_length", len(user_message))
                mlflow.log_param("response_length", len(response))
                
                # Log metrics
                mlflow.log_metric("relevance_score", relevance_score)
                mlflow.log_metric("message_word_count", len(user_message.split()))
                mlflow.log_metric("response_word_count", len(response.split()))
                
                # Log text artifacts
                mlflow.log_text(user_message, "user_message.txt")
                mlflow.log_text(response, "response.txt")
                
                # Log tags
                mlflow.set_tag("metric_type", "quality")
                mlflow.set_tag("quality_aspect", "response_relevance")
                mlflow.set_tag("intent", intent)
                mlflow.set_tag("response_type", response_type)
                mlflow.set_tag("user_id", user_id)
                
                logger.info(f"Logged response relevance: {relevance_score} for {response_type} response")
                
        except Exception as e:
            logger.error(f"Failed to log response relevance to MLflow: {e}")

    def log_rag_quality(self,
                       user_message: str,
                       response: str,
                       sources_used: List[str],
                       context_relevance: float,
                       source_quality: float,
                       hallucination_score: float,
                       user_id: str = "default",
                       timestamp: Optional[datetime] = None):
        """Log RAG-specific quality metrics"""
        try:
            timestamp = timestamp or datetime.now()
            
            with mlflow.start_run(run_name=f"rag_quality_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
                # Log parameters
                mlflow.log_param("user_id", user_id)
                mlflow.log_param("timestamp", timestamp.isoformat())
                mlflow.log_param("sources_count", len(sources_used))
                mlflow.log_param("message_length", len(user_message))
                mlflow.log_param("response_length", len(response))
                
                # Log metrics
                mlflow.log_metric("context_relevance", context_relevance)
                mlflow.log_metric("source_quality", source_quality)
                mlflow.log_metric("hallucination_score", hallucination_score)
                mlflow.log_metric("sources_used_count", len(sources_used))
                
                # Calculate derived metrics
                factuality_score = 1.0 - hallucination_score
                overall_rag_quality = (context_relevance + source_quality + factuality_score) / 3.0
                
                mlflow.log_metric("factuality_score", factuality_score)
                mlflow.log_metric("overall_rag_quality", overall_rag_quality)
                
                # Log text artifacts
                mlflow.log_text(user_message, "user_message.txt")
                mlflow.log_text(response, "response.txt")
                mlflow.log_text("\n".join(sources_used), "sources_used.txt")
                
                # Log tags
                mlflow.set_tag("metric_type", "quality")
                mlflow.set_tag("quality_aspect", "rag_quality")
                mlflow.set_tag("response_type", "rag")
                mlflow.set_tag("user_id", user_id)
                
                logger.info(f"Logged RAG quality: overall={overall_rag_quality:.3f}, sources={len(sources_used)}")
                
        except Exception as e:
            logger.error(f"Failed to log RAG quality to MLflow: {e}")

    def log_user_satisfaction(self,
                             user_id: str,
                             session_id: str,
                             satisfaction_score: float,
                             feedback_text: Optional[str] = None,
                             interaction_count: int = 1,
                             timestamp: Optional[datetime] = None):
        """Log user satisfaction metrics"""
        try:
            timestamp = timestamp or datetime.now()
            
            with mlflow.start_run(run_name=f"user_satisfaction_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
                # Log parameters
                mlflow.log_param("user_id", user_id)
                mlflow.log_param("session_id", session_id)
                mlflow.log_param("timestamp", timestamp.isoformat())
                mlflow.log_param("interaction_count", interaction_count)
                
                # Log metrics
                mlflow.log_metric("satisfaction_score", satisfaction_score)
                mlflow.log_metric("interactions_in_session", interaction_count)
                
                # Log feedback if provided
                if feedback_text:
                    mlflow.log_text(feedback_text, "user_feedback.txt")
                    mlflow.log_param("has_feedback", True)
                    mlflow.log_metric("feedback_length", len(feedback_text))
                else:
                    mlflow.log_param("has_feedback", False)
                
                # Log tags
                mlflow.set_tag("metric_type", "quality")
                mlflow.set_tag("quality_aspect", "user_satisfaction")
                mlflow.set_tag("user_id", user_id)
                mlflow.set_tag("session_id", session_id)
                
                logger.info(f"Logged user satisfaction: {satisfaction_score} for user {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to log user satisfaction to MLflow: {e}")

    def calculate_quality_metrics(self) -> Dict[str, Any]:
        """Calculate aggregated quality metrics from recent runs"""
        try:
            # This would typically query MLflow for recent runs and calculate aggregates
            # For now, return placeholder metrics
            return {
                "avg_intent_accuracy": 0.85,
                "avg_response_relevance": 0.78,
                "avg_rag_quality": 0.82,
                "avg_user_satisfaction": 0.76,
                "total_quality_interactions": 0
            }
        except Exception as e:
            logger.error(f"Failed to calculate quality metrics: {e}")
            return {}

    def log_batch_quality(self, 
                         time_period: str,
                         quality_metrics: Dict[str, Any]):
        """Log aggregated quality metrics for a time period"""
        try:
            timestamp = datetime.now()
            
            with mlflow.start_run(run_name=f"quality_batch_{time_period}_{timestamp.strftime('%Y%m%d_%H%M')}"):
                # Log parameters
                mlflow.log_param("time_period", time_period)
                mlflow.log_param("batch_type", "quality_aggregation")
                mlflow.log_param("timestamp", timestamp.isoformat())
                
                # Log all quality metrics
                for metric_name, value in quality_metrics.items():
                    if isinstance(value, (int, float)):
                        mlflow.log_metric(f"batch_{metric_name}", value)
                
                # Log tags
                mlflow.set_tag("metric_type", "quality")
                mlflow.set_tag("quality_aspect", "batch_aggregation")
                mlflow.set_tag("time_period", time_period)
                
                logger.info(f"Logged batch quality metrics for {time_period}")
                
        except Exception as e:
            logger.error(f"Failed to log batch quality metrics to MLflow: {e}")
