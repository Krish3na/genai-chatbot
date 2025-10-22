"""
Aggregates error metrics for batch logging to MLflow
"""
from datetime import datetime, timedelta
import logging
import threading
import time
from typing import Dict, Any, List
from .mlflow_error_tracker import MLflowErrorTracker

logger = logging.getLogger(__name__)

def log_batch_errors(time_period: str = 'hourly'):
    """
    Log aggregated error metrics to MLflow
    """
    try:
        # Get error metrics
        error_tracker = MLflowErrorTracker()
        metrics = error_tracker.calculate_error_metrics()
        
        # Add timestamp info
        now = datetime.now()
        metrics['timestamp'] = now.isoformat()
        
        # Log to MLflow
        error_tracker.log_batch_errors(
            time_period=time_period,
            error_metrics=metrics
        )
        
        logger.info(f"Successfully logged batch error metrics for {time_period}")
        
    except Exception as e:
        logger.error(f"Failed to log batch error metrics: {e}")

def schedule_error_logging():
    """
    Schedule periodic error metrics logging
    """
    def error_logging_worker():
        while True:
            try:
                # Log hourly error metrics
                log_batch_errors('hourly')
                
                # Wait for 1 hour
                time.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in error logging worker: {e}")
                # Wait 5 minutes before retrying
                time.sleep(300)
    
    # Start the error logging thread
    error_thread = threading.Thread(target=error_logging_worker, daemon=True)
    error_thread.start()
    logger.info("Error metrics logging scheduler started")

def detect_performance_anomalies(current_metrics: Dict[str, float], 
                                historical_averages: Dict[str, float],
                                thresholds: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Detect performance anomalies by comparing current metrics to historical averages
    """
    anomalies = []
    
    for metric_name, current_value in current_metrics.items():
        if metric_name not in historical_averages:
            continue
            
        expected_value = historical_averages[metric_name]
        threshold = thresholds.get(metric_name, 0.2)  # Default 20% threshold
        
        # Calculate percentage difference
        if expected_value > 0:
            diff_pct = abs(current_value - expected_value) / expected_value
            
            if diff_pct > threshold:
                anomaly = {
                    'metric_name': metric_name,
                    'current_value': current_value,
                    'expected_value': expected_value,
                    'difference_pct': diff_pct * 100,
                    'threshold_breached': f"{threshold * 100}%",
                    'severity': 'high' if diff_pct > 0.5 else 'medium'
                }
                anomalies.append(anomaly)
    
    return anomalies

def analyze_error_patterns(error_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze error logs to identify patterns and trends
    """
    if not error_logs:
        return {
            'total_errors': 0,
            'error_types': {},
            'error_trends': {},
            'most_common_errors': [],
            'error_rate_by_hour': {}
        }
    
    # Count error types
    error_types = {}
    for error in error_logs:
        error_type = error.get('error_type', 'unknown')
        error_types[error_type] = error_types.get(error_type, 0) + 1
    
    # Find most common errors
    most_common = sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Analyze error trends by hour
    error_rate_by_hour = {}
    for error in error_logs:
        timestamp = error.get('timestamp')
        if timestamp:
            try:
                hour = datetime.fromisoformat(timestamp).hour
                error_rate_by_hour[hour] = error_rate_by_hour.get(hour, 0) + 1
            except:
                continue
    
    return {
        'total_errors': len(error_logs),
        'error_types': error_types,
        'most_common_errors': most_common,
        'error_rate_by_hour': error_rate_by_hour,
        'unique_error_types': len(error_types)
    }

def calculate_system_health_score(metrics: Dict[str, Any]) -> float:
    """
    Calculate overall system health score based on various metrics
    """
    try:
        # Base score
        health_score = 100.0
        
        # Deduct points for errors
        total_errors = metrics.get('total_errors', 0)
        error_penalty = min(50, total_errors * 2)  # Max 50 points deduction for errors
        health_score -= error_penalty
        
        # Deduct points for high error rate
        error_rate = metrics.get('error_rate', 0.0)
        if error_rate > 0.05:  # More than 5% error rate
            rate_penalty = min(30, (error_rate - 0.05) * 1000)  # Scale penalty
            health_score -= rate_penalty
        
        # Deduct points for performance degradations
        perf_degradations = metrics.get('performance_degradations', 0)
        perf_penalty = min(20, perf_degradations * 5)
        health_score -= perf_penalty
        
        # Ensure score is between 0 and 100
        health_score = max(0.0, min(100.0, health_score))
        
        return health_score
        
    except Exception as e:
        logger.error(f"Failed to calculate system health score: {e}")
        return 50.0  # Return neutral score on error

def detect_critical_issues(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect critical issues that require immediate attention
    """
    critical_issues = []
    
    # High error rate
    error_rate = metrics.get('error_rate', 0.0)
    if error_rate > 0.1:  # More than 10% error rate
        critical_issues.append({
            'type': 'high_error_rate',
            'severity': 'critical',
            'description': f'Error rate is {error_rate:.2%}, exceeding 10% threshold',
            'metric_value': error_rate,
            'threshold': 0.1
        })
    
    # System errors
    system_errors = metrics.get('system_errors', 0)
    if system_errors > 5:  # More than 5 system errors
        critical_issues.append({
            'type': 'system_errors',
            'severity': 'high',
            'description': f'{system_errors} system errors detected',
            'metric_value': system_errors,
            'threshold': 5
        })
    
    # Model errors
    model_errors = metrics.get('model_errors', 0)
    if model_errors > 10:  # More than 10 model errors
        critical_issues.append({
            'type': 'model_errors',
            'severity': 'medium',
            'description': f'{model_errors} model errors detected',
            'metric_value': model_errors,
            'threshold': 10
        })
    
    # Low system health score
    health_score = calculate_system_health_score(metrics)
    if health_score < 70:
        critical_issues.append({
            'type': 'low_health_score',
            'severity': 'high' if health_score < 50 else 'medium',
            'description': f'System health score is {health_score:.1f}, below 70 threshold',
            'metric_value': health_score,
            'threshold': 70
        })
    
    return critical_issues
