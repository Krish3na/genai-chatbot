"""
Alert Scheduler for MLflow Monitoring
Runs periodic checks and sends alerts when thresholds are exceeded
"""
import asyncio
import logging
import schedule
import time
from datetime import datetime
from threading import Thread
from typing import Dict, Any

from app.utils.mlflow_alerts import alert_system
from app.config import settings

logger = logging.getLogger(__name__)

class AlertScheduler:
    """Scheduler for running MLflow alerts"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the alert scheduler"""
        if self.running:
            logger.warning("Alert scheduler is already running")
            return
            
        self.running = True
        
        # Schedule different types of checks
        schedule.every(5).minutes.do(self._run_performance_checks)
        schedule.every(15).minutes.do(self._run_error_checks)
        schedule.every(1).hours.do(self._run_cost_checks)
        schedule.every(1).hours.do(self._run_comprehensive_check)
        
        # Start scheduler in background thread
        self.thread = Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("Alert scheduler started")
        
    def stop(self):
        """Stop the alert scheduler"""
        self.running = False
        schedule.clear()
        logger.info("Alert scheduler stopped")
        
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in alert scheduler: {e}")
                time.sleep(60)  # Wait longer on error
                
    def _run_performance_checks(self):
        """Run performance-focused checks"""
        try:
            logger.debug("Running performance checks...")
            alerts = alert_system.check_performance_alerts(time_window_hours=1)
            
            if alerts:
                alert_system.send_alerts({"performance": alerts})
                logger.info(f"Sent {len(alerts)} performance alerts")
            else:
                logger.debug("No performance alerts")
                
        except Exception as e:
            logger.error(f"Error in performance checks: {e}")
            
    def _run_error_checks(self):
        """Run error-focused checks"""
        try:
            logger.debug("Running error checks...")
            alerts = alert_system.check_error_alerts(time_window_hours=1)
            
            if alerts:
                alert_system.send_alerts({"errors": alerts})
                logger.info(f"Sent {len(alerts)} error alerts")
            else:
                logger.debug("No error alerts")
                
        except Exception as e:
            logger.error(f"Error in error checks: {e}")
            
    def _run_cost_checks(self):
        """Run cost-focused checks"""
        try:
            logger.debug("Running cost checks...")
            alerts = alert_system.check_cost_alerts(time_window_hours=24)
            
            if alerts:
                alert_system.send_alerts({"cost": alerts})
                logger.info(f"Sent {len(alerts)} cost alerts")
            else:
                logger.debug("No cost alerts")
                
        except Exception as e:
            logger.error(f"Error in cost checks: {e}")
            
    def _run_comprehensive_check(self):
        """Run all checks together"""
        try:
            logger.debug("Running comprehensive alert check...")
            all_alerts = alert_system.run_all_checks()
            
            # Count total alerts
            total_alerts = sum(len(alerts) for alerts in all_alerts.values())
            
            if total_alerts > 0:
                alert_system.send_alerts(all_alerts)
                logger.info(f"Sent {total_alerts} alerts across all categories")
                
                # Log summary
                summary = {}
                for category, alerts in all_alerts.items():
                    if alerts:
                        summary[category] = len(alerts)
                        
                logger.info(f"Alert summary: {summary}")
            else:
                logger.debug("No alerts in comprehensive check")
                
        except Exception as e:
            logger.error(f"Error in comprehensive check: {e}")

# Global scheduler instance
scheduler = AlertScheduler()

def start_alert_monitoring():
    """Start the alert monitoring system"""
    # TEMPORARILY DISABLED FOR PERFORMANCE - MLflow timestamp issues
    logger.info("MLflow alert monitoring temporarily disabled for performance")
    # if settings.MLFLOW_ENABLED:
    #     scheduler.start()
    #     logger.info("MLflow alert monitoring started")
    # else:
    #     logger.info("MLflow disabled, skipping alert monitoring")
        
def stop_alert_monitoring():
    """Stop the alert monitoring system"""
    scheduler.stop()
