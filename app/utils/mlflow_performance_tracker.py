"""
MLflow Performance Metrics Tracker
"""
import mlflow
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
from prometheus_client.core import REGISTRY
from .metrics import CHAT_REQUEST_DURATION, CHAT_REQUESTS_TOTAL

logger = logging.getLogger(__name__)

class MLflowPerformanceTracker:
    """Tracks performance-related metrics in MLflow"""
    
    def __init__(self, experiment_name: str = "genai-chatbot-performance"):
        self.experiment_name = experiment_name
        try:
            # Set tracking URI to our MLflow server
            mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000'))
            # Get or create the experiment
            self.experiment = mlflow.get_experiment_by_name(experiment_name)
            if not self.experiment:
                mlflow.create_experiment(experiment_name)
            logger.info(f"MLflow performance tracking initialized for experiment: {experiment_name}")
        except Exception as e:
            logger.error(f"Failed to initialize MLflow performance tracking: {e}")
            raise

    def log_request_performance(
        self,
        response_time: float,
        request_type: str,  # 'direct' or 'rag'
        user_id: str,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log performance metrics for a single request"""
        try:
            with mlflow.start_run(run_name=f"request_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # Log metrics
                mlflow.log_metric("response_time_seconds", response_time)
                mlflow.log_metric("request_success", 1 if success else 0)
                
                # Log parameters
                mlflow.log_param("request_type", request_type)
                mlflow.log_param("user_id", user_id)
                
                # Log tags
                mlflow.set_tag("tracking_type", "request_performance")
                
                # Log additional metadata if provided
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(key, value)
                        else:
                            mlflow.log_param(key, str(value))
                
                logger.info(f"Logged performance metrics for request from {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to log performance metrics: {e}")
            
    def log_batch_performance(
        self,
        time_period: str,  # e.g., 'hourly', 'daily'
        request_counts: Dict[str, int],  # e.g., {'direct': 10, 'rag': 5}
        avg_response_times: Dict[str, float],  # e.g., {'direct': 0.5, 'rag': 1.2}
        success_rates: Dict[str, float],  # e.g., {'direct': 0.98, 'rag': 0.95}
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log aggregated performance metrics"""
        try:
            with mlflow.start_run(run_name=f"batch_performance_{time_period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # Log request counts
                for req_type, count in request_counts.items():
                    mlflow.log_metric(f"{req_type}_requests_total", count)
                
                # Log average response times
                for req_type, avg_time in avg_response_times.items():
                    mlflow.log_metric(f"{req_type}_avg_response_time", avg_time)
                
                # Log success rates
                for req_type, rate in success_rates.items():
                    mlflow.log_metric(f"{req_type}_success_rate", rate)
                
                # Calculate overall metrics
                total_requests = sum(request_counts.values())
                weighted_avg_response_time = sum(
                    avg_time * request_counts[req_type] / total_requests
                    for req_type, avg_time in avg_response_times.items()
                ) if total_requests > 0 else 0
                
                mlflow.log_metric("total_requests", total_requests)
                mlflow.log_metric("overall_avg_response_time", weighted_avg_response_time)
                
                # Log parameters
                mlflow.log_param("time_period", time_period)
                
                # Log tags
                mlflow.set_tag("tracking_type", "batch_performance")
                mlflow.set_tag("batch_period", time_period)
                
                # Log additional metadata
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(key, value)
                        else:
                            mlflow.log_param(key, str(value))
                            
                logger.info(f"Logged batch performance metrics for {time_period} period")
                
        except Exception as e:
            logger.error(f"Failed to log batch performance metrics: {e}")
            
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate current performance metrics from Prometheus"""
        try:
            # Get request durations
            direct_durations = []
            rag_durations = []
            
            for metric in CHAT_REQUEST_DURATION._metrics.values():
                response_type = metric.labels.get('response_type', '')
                if response_type == 'direct':
                    direct_durations.append(metric._sum._value)
                elif response_type == 'rag':
                    rag_durations.append(metric._sum._value)
            
            # Get request counts
            direct_count = 0
            rag_count = 0
            
            for metric in CHAT_REQUESTS_TOTAL._metrics.values():
                response_type = metric.labels.get('response_type', '')
                if response_type == 'direct':
                    direct_count += metric._value._value
                elif response_type == 'rag':
                    rag_count += metric._value._value
            
            # Calculate averages
            avg_direct_time = sum(direct_durations) / len(direct_durations) if direct_durations else 0
            avg_rag_time = sum(rag_durations) / len(rag_durations) if rag_durations else 0
            
            return {
                'request_counts': {
                    'direct': direct_count,
                    'rag': rag_count
                },
                'avg_response_times': {
                    'direct': avg_direct_time,
                    'rag': avg_rag_time
                },
                'success_rates': {
                    'direct': 1.0,  # We'll need to implement error tracking to make this accurate
                    'rag': 1.0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {e}")
            return {
                'request_counts': {'direct': 0, 'rag': 0},
                'avg_response_times': {'direct': 0, 'rag': 0},
                'success_rates': {'direct': 0, 'rag': 0}
            }
