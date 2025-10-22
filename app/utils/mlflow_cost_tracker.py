import mlflow
import os
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MLflowCostTracker:
    """Tracks cost-related metrics in MLflow"""
    
    def __init__(self, experiment_name: str = "genai-chatbot-costs"):
        self.experiment_name = experiment_name
        try:
            # Set tracking URI to our MLflow server
            mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000'))
            # Get or create the experiment
            self.experiment = mlflow.get_experiment_by_name(experiment_name)
            if not self.experiment:
                mlflow.create_experiment(experiment_name)
            logger.info(f"MLflow cost tracking initialized for experiment: {experiment_name}")
        except Exception as e:
            logger.error(f"Failed to initialize MLflow cost tracking: {e}")
            raise

    def log_conversation_costs(
        self,
        tokens_used: int,
        cost_usd: float,
        model: str,
        conversation_id: str,
        user_id: str,
        response_type: str = "direct",  # 'direct' or 'rag'
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log costs for a single conversation"""
        try:
            with mlflow.start_run(run_name=f"cost_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # Log metrics
                mlflow.log_metric("tokens_used", tokens_used)
                mlflow.log_metric("cost_usd", cost_usd)
                mlflow.log_metric("tokens_per_dollar", tokens_used / cost_usd if cost_usd > 0 else 0)
                
                # Log parameters
                mlflow.log_param("model", model)
                mlflow.log_param("response_type", response_type)
                
                # Log tags
                mlflow.set_tag("conversation_id", conversation_id)
                mlflow.set_tag("user_id", user_id)
                mlflow.set_tag("tracking_type", "cost")
                
                # Log additional metadata if provided
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(key, value)
                        else:
                            mlflow.log_param(key, str(value))
                
                logger.info(f"Logged cost metrics for conversation {conversation_id}")
                
        except Exception as e:
            logger.error(f"Failed to log cost metrics: {e}")
            # Don't raise the exception - we don't want to break the main application flow
            # but we do want to log the error
            
    def log_batch_costs(
        self,
        total_tokens: int,
        total_cost: float,
        time_period: str,  # e.g., 'hourly', 'daily'
        num_conversations: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log aggregated cost metrics for multiple conversations"""
        try:
            with mlflow.start_run(run_name=f"batch_costs_{time_period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # Log core metrics
                mlflow.log_metric("total_tokens", total_tokens)
                mlflow.log_metric("total_cost_usd", total_cost)
                mlflow.log_metric("average_tokens_per_conversation", total_tokens / num_conversations if num_conversations > 0 else 0)
                mlflow.log_metric("average_cost_per_conversation", total_cost / num_conversations if num_conversations > 0 else 0)
                mlflow.log_metric("num_conversations", num_conversations)
                
                # Log parameters
                mlflow.log_param("time_period", time_period)
                
                # Log tags
                mlflow.set_tag("tracking_type", "batch_cost")
                mlflow.set_tag("batch_period", time_period)
                
                # Log additional metadata
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(key, value)
                        else:
                            mlflow.log_param(key, str(value))
                            
                logger.info(f"Logged batch cost metrics for {time_period} period")
                
        except Exception as e:
            logger.error(f"Failed to log batch cost metrics: {e}")
