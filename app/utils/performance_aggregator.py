"""
Aggregates performance metrics for batch logging to MLflow
"""
from datetime import datetime
import logging
import threading
import time
from typing import Dict, Any
from .mlflow_performance_tracker import MLflowPerformanceTracker

logger = logging.getLogger(__name__)

def log_batch_performance(time_period: str = 'hourly'):
    """
    Log aggregated performance metrics to MLflow
    """
    try:
        # Get performance metrics
        performance_tracker = MLflowPerformanceTracker()
        metrics = performance_tracker.calculate_performance_metrics()
        
        # Add timestamp info
        now = datetime.now()
        metrics['timestamp'] = now.isoformat()
        
        # Log to MLflow
        performance_tracker.log_batch_performance(
            time_period=time_period,
            request_counts=metrics['request_counts'],
            avg_response_times=metrics['avg_response_times'],
            success_rates=metrics['success_rates'],
            metadata={
                'timestamp': metrics['timestamp']
            }
        )
        
        logger.info(f"Successfully logged batch performance for {time_period} period")
        
    except Exception as e:
        logger.error(f"Failed to log batch performance: {e}")

def schedule_performance_logging():
    """
    Schedule periodic performance logging
    This should be called when the application starts
    """
    def log_performance_periodically():
        while True:
            try:
                # Log hourly performance
                log_batch_performance('hourly')
                # Sleep for 1 hour
                time.sleep(3600)
            except Exception as e:
                logger.error(f"Error in performance logging thread: {e}")
                # Sleep for 5 minutes before retrying
                time.sleep(300)
    
    # Start the logging thread
    performance_logging_thread = threading.Thread(
        target=log_performance_periodically,
        daemon=True
    )
    performance_logging_thread.start()
    logger.info("Performance logging scheduler started")
