"""
MLflow Alert System for GenAI Chatbot
Monitors key metrics and sends alerts when thresholds are exceeded
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import json

import mlflow
from mlflow.tracking import MlflowClient

from app.config import settings

logger = logging.getLogger(__name__)

class MLflowAlerts:
    """Alert system for MLflow metrics monitoring"""
    
    def __init__(self):
        # Set MLflow tracking URI before creating client
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        self.client = MlflowClient()
        self.experiment_name = settings.MLFLOW_EXPERIMENT_NAME
        
        # Alert thresholds (customize these based on your needs)
        self.thresholds = {
            # Performance thresholds
            "response_time_warning": 3.0,      # seconds
            "response_time_critical": 5.0,     # seconds
            
            # Quality thresholds
            "accuracy_warning": 0.85,          # 85%
            "accuracy_critical": 0.75,         # 75%
            "confidence_warning": 0.7,         # 70%
            "confidence_critical": 0.5,        # 50%
            
            # Cost thresholds
            "cost_per_interaction_warning": 0.01,   # $0.01
            "cost_per_interaction_critical": 0.05,  # $0.05
            "daily_cost_warning": 10.0,             # $10/day
            "daily_cost_critical": 50.0,            # $50/day
            
            # Error thresholds
            "error_rate_warning": 0.05,        # 5%
            "error_rate_critical": 0.15,       # 15%
            
            # Usage thresholds
            "tokens_per_interaction_warning": 500,
            "tokens_per_interaction_critical": 1000,
        }
        
        # Alert channels
        self.alert_handlers = []
        
    def add_alert_handler(self, handler: Callable):
        """Add custom alert handler (email, Slack, etc.)"""
        self.alert_handlers.append(handler)
        
    def check_performance_alerts(self, time_window_hours: int = 1) -> List[Dict]:
        """Check for performance-related alerts"""
        alerts = []
        
        try:
            # Get recent runs
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return alerts
                
            # Calculate time window
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=f"attributes.start_time >= '{int(start_time.timestamp() * 1000)}'",
                max_results=100
            )
            
            if runs.empty:
                return alerts
                
            # Check response time
            if 'metrics.response_duration_seconds' in runs.columns:
                avg_response_time = runs['metrics.response_duration_seconds'].mean()
                max_response_time = runs['metrics.response_duration_seconds'].max()
                
                if avg_response_time > self.thresholds["response_time_critical"]:
                    alerts.append({
                        "type": "CRITICAL",
                        "category": "Performance",
                        "metric": "Average Response Time",
                        "value": f"{avg_response_time:.2f}s",
                        "threshold": f"{self.thresholds['response_time_critical']}s",
                        "message": f"Average response time ({avg_response_time:.2f}s) exceeds critical threshold",
                        "timestamp": datetime.now().isoformat()
                    })
                elif avg_response_time > self.thresholds["response_time_warning"]:
                    alerts.append({
                        "type": "WARNING",
                        "category": "Performance", 
                        "metric": "Average Response Time",
                        "value": f"{avg_response_time:.2f}s",
                        "threshold": f"{self.thresholds['response_time_warning']}s",
                        "message": f"Average response time ({avg_response_time:.2f}s) exceeds warning threshold",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            # Check accuracy
            if 'metrics.accuracy' in runs.columns:
                avg_accuracy = runs['metrics.accuracy'].mean()
                
                if avg_accuracy < self.thresholds["accuracy_critical"]:
                    alerts.append({
                        "type": "CRITICAL",
                        "category": "Quality",
                        "metric": "Model Accuracy",
                        "value": f"{avg_accuracy:.2%}",
                        "threshold": f"{self.thresholds['accuracy_critical']:.2%}",
                        "message": f"Model accuracy ({avg_accuracy:.2%}) below critical threshold",
                        "timestamp": datetime.now().isoformat()
                    })
                elif avg_accuracy < self.thresholds["accuracy_warning"]:
                    alerts.append({
                        "type": "WARNING",
                        "category": "Quality",
                        "metric": "Model Accuracy", 
                        "value": f"{avg_accuracy:.2%}",
                        "threshold": f"{self.thresholds['accuracy_warning']:.2%}",
                        "message": f"Model accuracy ({avg_accuracy:.2%}) below warning threshold",
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")
            
        return alerts
        
    def check_cost_alerts(self, time_window_hours: int = 24) -> List[Dict]:
        """Check for cost-related alerts"""
        alerts = []
        
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return alerts
                
            # Get recent runs
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=f"attributes.start_time >= '{int(start_time.timestamp() * 1000)}'",
                max_results=1000
            )
            
            if runs.empty:
                return alerts
                
            # Check cost per interaction
            if 'metrics.cost_usd' in runs.columns:
                avg_cost = runs['metrics.cost_usd'].mean()
                total_cost = runs['metrics.cost_usd'].sum()
                
                if avg_cost > self.thresholds["cost_per_interaction_critical"]:
                    alerts.append({
                        "type": "CRITICAL",
                        "category": "Cost",
                        "metric": "Cost Per Interaction",
                        "value": f"${avg_cost:.4f}",
                        "threshold": f"${self.thresholds['cost_per_interaction_critical']:.4f}",
                        "message": f"Average cost per interaction (${avg_cost:.4f}) exceeds critical threshold",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                # Check daily cost (for 24-hour window)
                if time_window_hours == 24:
                    if total_cost > self.thresholds["daily_cost_critical"]:
                        alerts.append({
                            "type": "CRITICAL",
                            "category": "Cost",
                            "metric": "Daily Cost",
                            "value": f"${total_cost:.2f}",
                            "threshold": f"${self.thresholds['daily_cost_critical']:.2f}",
                            "message": f"Daily cost (${total_cost:.2f}) exceeds critical threshold",
                            "timestamp": datetime.now().isoformat()
                        })
                    elif total_cost > self.thresholds["daily_cost_warning"]:
                        alerts.append({
                            "type": "WARNING",
                            "category": "Cost",
                            "metric": "Daily Cost",
                            "value": f"${total_cost:.2f}",
                            "threshold": f"${self.thresholds['daily_cost_warning']:.2f}",
                            "message": f"Daily cost (${total_cost:.2f}) exceeds warning threshold",
                            "timestamp": datetime.now().isoformat()
                        })
                        
        except Exception as e:
            logger.error(f"Error checking cost alerts: {e}")
            
        return alerts
        
    def check_error_alerts(self, time_window_hours: int = 1) -> List[Dict]:
        """Check for error-related alerts"""
        alerts = []
        
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return alerts
                
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=f"attributes.start_time >= '{int(start_time.timestamp() * 1000)}'",
                max_results=100
            )
            
            if runs.empty:
                return alerts
                
            # Check error rate
            if 'metrics.error_rate_percent' in runs.columns:
                avg_error_rate = runs['metrics.error_rate_percent'].mean() / 100  # Convert to decimal
                
                if avg_error_rate > self.thresholds["error_rate_critical"]:
                    alerts.append({
                        "type": "CRITICAL",
                        "category": "Reliability",
                        "metric": "Error Rate",
                        "value": f"{avg_error_rate:.2%}",
                        "threshold": f"{self.thresholds['error_rate_critical']:.2%}",
                        "message": f"Error rate ({avg_error_rate:.2%}) exceeds critical threshold",
                        "timestamp": datetime.now().isoformat()
                    })
                elif avg_error_rate > self.thresholds["error_rate_warning"]:
                    alerts.append({
                        "type": "WARNING",
                        "category": "Reliability",
                        "metric": "Error Rate",
                        "value": f"{avg_error_rate:.2%}",
                        "threshold": f"{self.thresholds['error_rate_warning']:.2%}",
                        "message": f"Error rate ({avg_error_rate:.2%}) exceeds warning threshold",
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            logger.error(f"Error checking error alerts: {e}")
            
        return alerts
        
    def run_all_checks(self) -> Dict[str, List[Dict]]:
        """Run all alert checks and return results"""
        return {
            "performance": self.check_performance_alerts(),
            "cost": self.check_cost_alerts(),
            "errors": self.check_error_alerts()
        }
        
    def send_alerts(self, alerts: Dict[str, List[Dict]]):
        """Send alerts through configured channels"""
        all_alerts = []
        for category, alert_list in alerts.items():
            all_alerts.extend(alert_list)
            
        if not all_alerts:
            logger.info("No alerts to send")
            return
            
        # Send through all configured handlers
        for handler in self.alert_handlers:
            try:
                handler(all_alerts)
            except Exception as e:
                logger.error(f"Failed to send alert through handler: {e}")
                
        # Log alerts
        for alert in all_alerts:
            logger.warning(f"ALERT [{alert['type']}] {alert['category']}: {alert['message']}")

# Alert handlers
def console_alert_handler(alerts: List[Dict]):
    """Print alerts to console"""
    print("\n" + "="*60)
    print("🚨 MLFLOW ALERTS")
    print("="*60)
    
    for alert in alerts:
        icon = "🔴" if alert['type'] == 'CRITICAL' else "🟡"
        print(f"{icon} [{alert['type']}] {alert['category']}")
        print(f"   Metric: {alert['metric']}")
        print(f"   Value: {alert['value']} (Threshold: {alert['threshold']})")
        print(f"   Message: {alert['message']}")
        print(f"   Time: {alert['timestamp']}")
        print("-" * 60)
        
def email_alert_handler(alerts: List[Dict], 
                       smtp_server: str = "smtp.gmail.com",
                       smtp_port: int = 587,
                       sender_email: str = "",
                       sender_password: str = "",
                       recipient_emails: List[str] = []):
    """Send alerts via email"""
    if not sender_email or not recipient_emails:
        logger.warning("Email alerts not configured")
        return
        
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipient_emails)
        msg['Subject'] = f"MLflow Alert - {len(alerts)} issues detected"
        
        # Create HTML body
        html_body = """
        <html>
        <body>
        <h2>🚨 MLflow Alert Report</h2>
        <p>The following issues were detected in your GenAI Chatbot:</p>
        <table border="1" style="border-collapse: collapse;">
        <tr>
            <th>Type</th>
            <th>Category</th>
            <th>Metric</th>
            <th>Value</th>
            <th>Threshold</th>
            <th>Message</th>
        </tr>
        """
        
        for alert in alerts:
            color = "#ffebee" if alert['type'] == 'CRITICAL' else "#fff3e0"
            html_body += f"""
            <tr style="background-color: {color};">
                <td>{alert['type']}</td>
                <td>{alert['category']}</td>
                <td>{alert['metric']}</td>
                <td>{alert['value']}</td>
                <td>{alert['threshold']}</td>
                <td>{alert['message']}</td>
            </tr>
            """
            
        html_body += """
        </table>
        <p><em>Check your MLflow dashboard for more details: http://localhost:5000</em></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Alert email sent to {len(recipient_emails)} recipients")
        
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")

# Global alert system instance
alert_system = MLflowAlerts()

# Add console handler by default
alert_system.add_alert_handler(console_alert_handler)

# Configure email alerts if enabled
def setup_email_alerts():
    """Setup email alerts based on configuration"""
    try:
        from app.config import settings
        
        if settings.EMAIL_ALERTS_ENABLED and settings.SENDER_EMAIL:
            recipient_emails = [email.strip() for email in settings.ALERT_RECIPIENTS.split(",")]
            
            def configured_email_handler(alerts):
                return email_alert_handler(
                    alerts,
                    smtp_server=settings.SMTP_SERVER,
                    smtp_port=settings.SMTP_PORT,
                    sender_email=settings.SENDER_EMAIL,
                    sender_password=settings.SENDER_PASSWORD,
                    recipient_emails=recipient_emails
                )
            
            alert_system.add_alert_handler(configured_email_handler)
            logger.info(f"Email alerts configured for: {recipient_emails}")
        else:
            logger.info("Email alerts not configured (disabled or missing credentials)")
            
    except Exception as e:
        logger.error(f"Failed to setup email alerts: {e}")

# Setup email alerts on import
setup_email_alerts()
