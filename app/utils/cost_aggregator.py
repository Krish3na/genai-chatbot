"""
Aggregates cost metrics for batch logging to MLflow
"""
from datetime import datetime, timedelta
from typing import Dict, Any
import logging
from prometheus_client.core import REGISTRY
from .metrics import CHAT_TOKENS_USED, CHAT_COST_TOTAL
from .mlflow_cost_tracker import MLflowCostTracker

logger = logging.getLogger(__name__)

def aggregate_costs(time_period: str = 'hourly') -> Dict[str, Any]:
    """
    Aggregate cost metrics from Prometheus for the specified time period
    """
    # Get all metrics
    total_tokens = sum([metric._value._value for metric in CHAT_TOKENS_USED._metrics.values()])
    total_cost = sum([metric._value._value for metric in CHAT_COST_TOTAL._metrics.values()])
    
    # Count unique conversations (simplified - using unique user_ids)
    unique_users = set()
    for metric in CHAT_TOKENS_USED._metrics:
        user_id = metric.labels.get('user_id')
        if user_id:
            unique_users.add(user_id)
    
    return {
        'total_tokens': total_tokens,
        'total_cost': total_cost,
        'num_conversations': len(unique_users)
    }

def log_batch_costs(time_period: str = 'hourly'):
    """
    Log aggregated cost metrics to MLflow
    """
    try:
        # Get aggregated metrics
        metrics = aggregate_costs(time_period)
        
        # Add timestamp info
        now = datetime.now()
        metrics['timestamp'] = now.isoformat()
        if time_period == 'hourly':
            metrics['period_start'] = (now - timedelta(hours=1)).isoformat()
        elif time_period == 'daily':
            metrics['period_start'] = (now - timedelta(days=1)).isoformat()
        
        # Log to MLflow
        cost_tracker = MLflowCostTracker()
        cost_tracker.log_batch_costs(
            total_tokens=metrics['total_tokens'],
            total_cost=metrics['total_cost'],
            time_period=time_period,
            num_conversations=metrics['num_conversations'],
            metadata={
                'period_start': metrics['period_start'],
                'period_end': metrics['timestamp']
            }
        )
        
        logger.info(f"Successfully logged batch costs for {time_period} period")
        
    except Exception as e:
        logger.error(f"Failed to log batch costs: {e}")

def schedule_cost_logging():
    """
    Schedule periodic cost logging
    This should be called when the application starts
    """
    import threading
    import time
    
    def log_costs_periodically():
        while True:
            try:
                # Log hourly costs
                log_batch_costs('hourly')
                # Sleep for 1 hour
                time.sleep(3600)
            except Exception as e:
                logger.error(f"Error in cost logging thread: {e}")
                # Sleep for 5 minutes before retrying
                time.sleep(300)
    
    # Start the logging thread
    cost_logging_thread = threading.Thread(target=log_costs_periodically, daemon=True)
    cost_logging_thread.start()
    logger.info("Cost logging scheduler started")
