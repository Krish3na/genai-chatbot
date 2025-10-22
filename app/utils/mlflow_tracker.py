"""
MLflow integration for GenAI Chatbot
Tracks experiments, model performance, and metrics
"""
import os
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

from app.config import settings

logger = logging.getLogger(__name__)

class MLflowTracker:
    """MLflow tracking integration for GenAI Chatbot"""
    
    def __init__(self):
        """Initialize MLflow tracker"""
        self.experiment_name = settings.MLFLOW_EXPERIMENT_NAME
        self.tracking_uri = settings.MLFLOW_TRACKING_URI
        
        # Set MLflow tracking URI
        mlflow.set_tracking_uri(self.tracking_uri)
        self.client = MlflowClient()
        
        # Create or get experiment
        self._setup_experiment()
        
        # Current run tracking
        self.current_run = None
        
    def _setup_experiment(self):
        """Set up MLflow experiment"""
        try:
            # Try to get existing experiment
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                # Create new experiment
                experiment_id = mlflow.create_experiment(
                    name=self.experiment_name,
                    tags={
                        "project": "genai-chatbot",
                        "version": "1.0.0",
                        "created_at": datetime.now().isoformat()
                    }
                )
                logger.info(f"Created MLflow experiment: {self.experiment_name} (ID: {experiment_id})")
            else:
                logger.info(f"Using existing MLflow experiment: {self.experiment_name}")
                
            # Set the experiment as active
            mlflow.set_experiment(self.experiment_name)
            
        except Exception as e:
            logger.error(f"Failed to setup MLflow experiment: {e}")
            
    def start_run(self, run_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> str:
        """Start a new MLflow run"""
        try:
            if not run_name:
                run_name = f"chatbot_run_{int(time.time())}"
                
            default_tags = {
                "environment": os.getenv("ENVIRONMENT", "development"),
                "model": settings.OPENAI_MODEL,
                "started_at": datetime.now().isoformat()
            }
            
            if tags:
                default_tags.update(tags)
                
            self.current_run = mlflow.start_run(run_name=run_name, tags=default_tags)
            logger.info(f"Started MLflow run: {run_name} (ID: {self.current_run.info.run_id})")
            return self.current_run.info.run_id
            
        except Exception as e:
            logger.error(f"Failed to start MLflow run: {e}")
            return ""
            
    def end_run(self):
        """End the current MLflow run"""
        try:
            if self.current_run:
                mlflow.end_run()
                logger.info(f"Ended MLflow run: {self.current_run.info.run_id}")
                self.current_run = None
        except Exception as e:
            logger.error(f"Failed to end MLflow run: {e}")
            
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics to MLflow"""
        try:
            if self.current_run:
                for key, value in metrics.items():
                    mlflow.log_metric(key, value, step=step)
                logger.debug(f"Logged metrics: {metrics}")
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")
            
    def log_params(self, params: Dict[str, Any]):
        """Log parameters to MLflow"""
        try:
            if self.current_run:
                mlflow.log_params(params)
                logger.debug(f"Logged parameters: {params}")
        except Exception as e:
            logger.error(f"Failed to log parameters: {e}")
            
    def log_chat_interaction(self, 
                           user_message: str,
                           response: str,
                           intent: str,
                           response_type: str,
                           duration: float,
                           tokens_used: int,
                           cost: float,
                           rag_sources: Optional[List[str]] = None,
                           confidence: Optional[float] = None):
        """Log a complete chat interaction"""
        try:
            if not self.current_run:
                self.start_run()
                
            # Log interaction metrics
            metrics = {
                "response_duration_seconds": duration,
                "tokens_used": tokens_used,
                "cost_usd": cost,
                "intent_confidence": confidence or 0.0,
                "rag_sources_count": len(rag_sources) if rag_sources else 0
            }
            self.log_metrics(metrics)
            
            # Log interaction details as tags/artifacts
            interaction_data = {
                "user_message_length": len(user_message),
                "response_length": len(response),
                "intent": intent,
                "response_type": response_type,
                "timestamp": datetime.now().isoformat()
            }
            
            if rag_sources:
                interaction_data["rag_sources"] = ", ".join(rag_sources)
                
            # Log as artifact (for detailed analysis)
            artifact_path = f"interactions/interaction_{int(time.time())}.json"
            mlflow.log_dict(interaction_data, artifact_path)
            
            logger.debug(f"Logged chat interaction with {tokens_used} tokens, cost ${cost:.4f}")
            
        except Exception as e:
            logger.error(f"Failed to log chat interaction: {e}")
            
    def log_model_performance(self, 
                            accuracy: float,
                            precision: float,
                            recall: float,
                            f1_score: float,
                            avg_response_time: float,
                            total_interactions: int):
        """Log model performance metrics"""
        try:
            if not self.current_run:
                self.start_run(run_name="model_performance_evaluation")
                
            performance_metrics = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "avg_response_time_seconds": avg_response_time,
                "total_interactions": total_interactions,
                "evaluation_timestamp": time.time()
            }
            
            self.log_metrics(performance_metrics)
            logger.info(f"Logged model performance: Accuracy={accuracy:.3f}, F1={f1_score:.3f}")
            
        except Exception as e:
            logger.error(f"Failed to log model performance: {e}")
            
    def log_system_metrics(self, 
                          active_conversations: int,
                          total_documents: int,
                          avg_rag_context_length: float,
                          error_rate: float):
        """Log system-level metrics"""
        try:
            if not self.current_run:
                self.start_run(run_name="system_metrics")
                
            system_metrics = {
                "active_conversations": active_conversations,
                "knowledge_base_documents": total_documents,
                "avg_rag_context_length": avg_rag_context_length,
                "error_rate_percent": error_rate * 100,
                "system_timestamp": time.time()
            }
            
            self.log_metrics(system_metrics)
            logger.debug(f"Logged system metrics: {system_metrics}")
            
        except Exception as e:
            logger.error(f"Failed to log system metrics: {e}")
            
    def log_experiment_config(self, config: Dict[str, Any]):
        """Log experiment configuration"""
        try:
            if not self.current_run:
                self.start_run(run_name="experiment_config")
                
            # Log configuration parameters
            config_params = {
                "openai_model": config.get("model", settings.OPENAI_MODEL),
                "max_tokens": config.get("max_tokens", settings.OPENAI_MAX_TOKENS),
                "temperature": config.get("temperature", settings.OPENAI_TEMPERATURE),
                "rag_top_k": config.get("rag_top_k", settings.RAG_TOP_K),
                "similarity_threshold": config.get("similarity_threshold", settings.RAG_SIMILARITY_THRESHOLD),
                "intent_threshold": config.get("intent_threshold", settings.INTENT_CONFIDENCE_THRESHOLD)
            }
            
            self.log_params(config_params)
            
            # Log full config as artifact
            mlflow.log_dict(config, "config/experiment_config.json")
            logger.info("Logged experiment configuration")
            
        except Exception as e:
            logger.error(f"Failed to log experiment config: {e}")
            
    def get_experiment_runs(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get runs from the current experiment"""
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return []
                
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                max_results=max_results,
                order_by=["start_time DESC"]
            )
            
            return runs.to_dict('records') if not runs.empty else []
            
        except Exception as e:
            logger.error(f"Failed to get experiment runs: {e}")
            return []
            
    def get_best_run(self, metric_name: str = "f1_score") -> Optional[Dict[str, Any]]:
        """Get the best run based on a metric"""
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return None
                
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=[f"metrics.{metric_name} DESC"],
                max_results=1
            )
            
            return runs.iloc[0].to_dict() if not runs.empty else None
            
        except Exception as e:
            logger.error(f"Failed to get best run: {e}")
            return None
            
    def cleanup_old_runs(self, keep_last_n: int = 50):
        """Clean up old runs to save storage"""
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return
                
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["start_time DESC"]
            )
            
            if len(runs) > keep_last_n:
                old_runs = runs.iloc[keep_last_n:]
                for _, run in old_runs.iterrows():
                    self.client.delete_run(run['run_id'])
                    
                logger.info(f"Cleaned up {len(old_runs)} old runs")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old runs: {e}")

# Global MLflow tracker instance
mlflow_tracker = MLflowTracker()

