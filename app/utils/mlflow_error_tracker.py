"""
MLflow Error Detection and Tracking
"""
import mlflow
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
import traceback

logger = logging.getLogger(__name__)

class MLflowErrorTracker:
    """Tracks errors and issues in MLflow"""
    
    def __init__(self, experiment_name: str = "genai-chatbot-errors"):
        self.experiment_name = experiment_name
        try:
            # Set tracking URI to our MLflow server
            mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000'))
            # Get or create the experiment
            self.experiment = mlflow.get_experiment_by_name(experiment_name)
            if not self.experiment:
                mlflow.create_experiment(experiment_name)
            logger.info(f"MLflow error tracking initialized for experiment: {experiment_name}")
        except Exception as e:
            logger.error(f"Failed to initialize MLflow error tracking: {e}")
            raise

    def log_api_error(self,
                     endpoint: str,
                     error_type: str,
                     error_message: str,
                     status_code: int,
                     user_id: str = "unknown",
                     request_data: Optional[Dict] = None,
                     stack_trace: Optional[str] = None,
                     timestamp: Optional[datetime] = None):
        """Log API errors"""
        try:
            timestamp = timestamp or datetime.now()
            
            with mlflow.start_run(run_name=f"api_error_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
                # Log parameters
                mlflow.log_param("endpoint", endpoint)
                mlflow.log_param("error_type", error_type)
                mlflow.log_param("status_code", status_code)
                mlflow.log_param("user_id", user_id)
                mlflow.log_param("timestamp", timestamp.isoformat())
                
                # Log metrics
                mlflow.log_metric("error_severity", self._get_error_severity(status_code))
                mlflow.log_metric("status_code_numeric", status_code)
                
                # Log error details as artifacts
                mlflow.log_text(error_message, "error_message.txt")
                if stack_trace:
                    mlflow.log_text(stack_trace, "stack_trace.txt")
                if request_data:
                    mlflow.log_text(str(request_data), "request_data.txt")
                
                # Log tags
                mlflow.set_tag("error_category", "api_error")
                mlflow.set_tag("endpoint", endpoint)
                mlflow.set_tag("error_type", error_type)
                mlflow.set_tag("user_id", user_id)
                mlflow.set_tag("severity", self._get_severity_label(status_code))
                
                logger.info(f"Logged API error: {error_type} on {endpoint} (status: {status_code})")
                
        except Exception as e:
            logger.error(f"Failed to log API error to MLflow: {e}")

    def log_model_error(self,
                       model_name: str,
                       error_type: str,
                       error_message: str,
                       input_data: Optional[str] = None,
                       user_id: str = "unknown",
                       tokens_used: int = 0,
                       timestamp: Optional[datetime] = None):
        """Log model-specific errors (OpenAI, etc.)"""
        try:
            timestamp = timestamp or datetime.now()
            
            with mlflow.start_run(run_name=f"model_error_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
                # Log parameters
                mlflow.log_param("model_name", model_name)
                mlflow.log_param("error_type", error_type)
                mlflow.log_param("user_id", user_id)
                mlflow.log_param("timestamp", timestamp.isoformat())
                mlflow.log_param("tokens_used", tokens_used)
                
                # Log metrics
                mlflow.log_metric("model_error_severity", self._get_model_error_severity(error_type))
                mlflow.log_metric("tokens_wasted", tokens_used)
                
                # Log error details as artifacts
                mlflow.log_text(error_message, "error_message.txt")
                if input_data:
                    mlflow.log_text(input_data, "input_data.txt")
                
                # Log tags
                mlflow.set_tag("error_category", "model_error")
                mlflow.set_tag("model_name", model_name)
                mlflow.set_tag("error_type", error_type)
                mlflow.set_tag("user_id", user_id)
                
                logger.info(f"Logged model error: {error_type} for {model_name}")
                
        except Exception as e:
            logger.error(f"Failed to log model error to MLflow: {e}")

    def log_system_error(self,
                        component: str,
                        error_type: str,
                        error_message: str,
                        severity: str = "medium",
                        system_metrics: Optional[Dict] = None,
                        stack_trace: Optional[str] = None,
                        timestamp: Optional[datetime] = None):
        """Log system-level errors"""
        try:
            timestamp = timestamp or datetime.now()
            
            with mlflow.start_run(run_name=f"system_error_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
                # Log parameters
                mlflow.log_param("component", component)
                mlflow.log_param("error_type", error_type)
                mlflow.log_param("severity", severity)
                mlflow.log_param("timestamp", timestamp.isoformat())
                
                # Log metrics
                severity_score = {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(severity.lower(), 2)
                mlflow.log_metric("system_error_severity", severity_score)
                
                if system_metrics:
                    for metric_name, value in system_metrics.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(f"system_{metric_name}", value)
                
                # Log error details as artifacts
                mlflow.log_text(error_message, "error_message.txt")
                if stack_trace:
                    mlflow.log_text(stack_trace, "stack_trace.txt")
                
                # Log tags
                mlflow.set_tag("error_category", "system_error")
                mlflow.set_tag("component", component)
                mlflow.set_tag("error_type", error_type)
                mlflow.set_tag("severity", severity)
                
                logger.info(f"Logged system error: {error_type} in {component} (severity: {severity})")
                
        except Exception as e:
            logger.error(f"Failed to log system error to MLflow: {e}")

    def log_data_quality_issue(self,
                              data_source: str,
                              issue_type: str,
                              description: str,
                              affected_records: int = 0,
                              data_sample: Optional[str] = None,
                              timestamp: Optional[datetime] = None):
        """Log data quality issues"""
        try:
            timestamp = timestamp or datetime.now()
            
            with mlflow.start_run(run_name=f"data_quality_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
                # Log parameters
                mlflow.log_param("data_source", data_source)
                mlflow.log_param("issue_type", issue_type)
                mlflow.log_param("timestamp", timestamp.isoformat())
                
                # Log metrics
                mlflow.log_metric("affected_records", affected_records)
                issue_severity = min(3.0, max(1.0, affected_records / 100))  # Scale based on affected records
                mlflow.log_metric("data_quality_severity", issue_severity)
                
                # Log issue details as artifacts
                mlflow.log_text(description, "issue_description.txt")
                if data_sample:
                    mlflow.log_text(data_sample, "data_sample.txt")
                
                # Log tags
                mlflow.set_tag("error_category", "data_quality")
                mlflow.set_tag("data_source", data_source)
                mlflow.set_tag("issue_type", issue_type)
                
                logger.info(f"Logged data quality issue: {issue_type} in {data_source}")
                
        except Exception as e:
            logger.error(f"Failed to log data quality issue to MLflow: {e}")

    def log_performance_degradation(self,
                                   metric_name: str,
                                   current_value: float,
                                   expected_value: float,
                                   threshold_breached: str,
                                   component: str = "system",
                                   timestamp: Optional[datetime] = None):
        """Log performance degradation events"""
        try:
            timestamp = timestamp or datetime.now()
            
            with mlflow.start_run(run_name=f"perf_degradation_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
                # Log parameters
                mlflow.log_param("metric_name", metric_name)
                mlflow.log_param("component", component)
                mlflow.log_param("threshold_breached", threshold_breached)
                mlflow.log_param("timestamp", timestamp.isoformat())
                
                # Log metrics
                mlflow.log_metric("current_value", current_value)
                mlflow.log_metric("expected_value", expected_value)
                
                # Calculate degradation percentage
                degradation_pct = abs((current_value - expected_value) / expected_value * 100)
                mlflow.log_metric("degradation_percentage", degradation_pct)
                
                # Severity based on degradation
                severity_score = min(4.0, degradation_pct / 25)  # 25% = severity 1, 100% = severity 4
                mlflow.log_metric("performance_degradation_severity", severity_score)
                
                # Log tags
                mlflow.set_tag("error_category", "performance_degradation")
                mlflow.set_tag("metric_name", metric_name)
                mlflow.set_tag("component", component)
                mlflow.set_tag("threshold_breached", threshold_breached)
                
                logger.info(f"Logged performance degradation: {metric_name} = {current_value} (expected: {expected_value})")
                
        except Exception as e:
            logger.error(f"Failed to log performance degradation to MLflow: {e}")

    def _get_error_severity(self, status_code: int) -> float:
        """Convert HTTP status code to severity score"""
        if status_code >= 500:
            return 4.0  # Critical
        elif status_code >= 400:
            return 2.0  # Medium
        else:
            return 1.0  # Low

    def _get_severity_label(self, status_code: int) -> str:
        """Convert HTTP status code to severity label"""
        if status_code >= 500:
            return "critical"
        elif status_code >= 400:
            return "medium"
        else:
            return "low"

    def _get_model_error_severity(self, error_type: str) -> float:
        """Convert model error type to severity score"""
        critical_errors = ["authentication_error", "quota_exceeded", "model_unavailable"]
        high_errors = ["rate_limit_exceeded", "context_length_exceeded"]
        medium_errors = ["invalid_request", "timeout"]
        
        if error_type.lower() in critical_errors:
            return 4.0
        elif error_type.lower() in high_errors:
            return 3.0
        elif error_type.lower() in medium_errors:
            return 2.0
        else:
            return 1.0

    def calculate_error_metrics(self) -> Dict[str, Any]:
        """Calculate aggregated error metrics from recent runs"""
        try:
            # This would typically query MLflow for recent error runs and calculate aggregates
            # For now, return placeholder metrics
            return {
                "total_errors": 0,
                "api_errors": 0,
                "model_errors": 0,
                "system_errors": 0,
                "data_quality_issues": 0,
                "performance_degradations": 0,
                "avg_error_severity": 0.0,
                "error_rate": 0.0,
                "mtbf": 0.0  # Mean Time Between Failures
            }
        except Exception as e:
            logger.error(f"Failed to calculate error metrics: {e}")
            return {}

    def log_batch_errors(self, 
                        time_period: str,
                        error_metrics: Dict[str, Any]):
        """Log aggregated error metrics for a time period"""
        try:
            timestamp = datetime.now()
            
            with mlflow.start_run(run_name=f"error_batch_{time_period}_{timestamp.strftime('%Y%m%d_%H%M')}"):
                # Log parameters
                mlflow.log_param("time_period", time_period)
                mlflow.log_param("batch_type", "error_aggregation")
                mlflow.log_param("timestamp", timestamp.isoformat())
                
                # Log all error metrics
                for metric_name, value in error_metrics.items():
                    if isinstance(value, (int, float)):
                        mlflow.log_metric(f"batch_{metric_name}", value)
                
                # Log tags
                mlflow.set_tag("error_category", "batch_aggregation")
                mlflow.set_tag("time_period", time_period)
                
                logger.info(f"Logged batch error metrics for {time_period}")
                
        except Exception as e:
            logger.error(f"Failed to log batch error metrics to MLflow: {e}")
