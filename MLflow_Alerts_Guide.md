# 🚨 MLflow Alerts & Monitoring System

## 🎯 **What You Now Have**

Your GenAI Chatbot now includes **enterprise-grade alerting** that monitors:

### **📊 Performance Alerts**
- **Response Time**: Warns if responses > 3s, critical if > 5s
- **Model Accuracy**: Warns if < 85%, critical if < 75%
- **Intent Confidence**: Warns if < 70%, critical if < 50%

### **💰 Cost Alerts**
- **Per Interaction**: Warns if > $0.01, critical if > $0.05
- **Daily Spend**: Warns if > $10/day, critical if > $50/day
- **Token Usage**: Warns if > 500 tokens, critical if > 1000 tokens

### **🐛 Error Alerts**
- **Error Rate**: Warns if > 5%, critical if > 15%
- **API Failures**: Immediate alerts for authentication issues
- **System Health**: Monitors overall system stability

## 🚀 **How to Use Your Alert System**

### **1. 📱 Alert Dashboard**
Open `alert_dashboard.html` in your browser for a beautiful real-time dashboard:
```bash
# Open in browser
start alert_dashboard.html
```

**Features:**
- ✅ Real-time alert monitoring
- 📊 Visual status cards
- 🔄 Auto-refresh every 30 seconds
- 🎯 Direct links to MLflow
- ⚙️ Threshold management

### **2. 🔌 API Endpoints**

Your chatbot now has these new endpoints:

#### **Check Alerts**
```bash
curl http://localhost:8000/alerts/check
```

#### **View Thresholds**
```bash
curl http://localhost:8000/alerts/thresholds
```

#### **Update Thresholds**
```bash
curl -X POST http://localhost:8000/alerts/thresholds \
  -H "Content-Type: application/json" \
  -d '{"response_time_warning": 2.0}'
```

#### **System Status**
```bash
curl http://localhost:8000/alerts/status
```

### **3. 🤖 Automated Monitoring**

The system automatically runs:
- **Every 5 minutes**: Performance checks
- **Every 15 minutes**: Error rate checks  
- **Every hour**: Cost analysis
- **Every hour**: Comprehensive health check

## 🛠️ **Testing Your Alert System**

Run the test script to see alerts in action:
```bash
python test_alerts.py
```

This will:
1. ✅ Check system status
2. 📊 Display current thresholds
3. 🔍 Run immediate alert checks
4. ⚙️ Test threshold updates
5. 💬 Generate test interactions
6. 📈 Show final alert status

## 🎛️ **Customizing Thresholds**

### **Default Thresholds:**
```python
{
    "response_time_warning": 3.0,      # seconds
    "response_time_critical": 5.0,     # seconds
    "accuracy_warning": 0.85,          # 85%
    "accuracy_critical": 0.75,         # 75%
    "cost_per_interaction_warning": 0.01,   # $0.01
    "cost_per_interaction_critical": 0.05,  # $0.05
    "daily_cost_warning": 10.0,             # $10/day
    "daily_cost_critical": 50.0,            # $50/day
    "error_rate_warning": 0.05,        # 5%
    "error_rate_critical": 0.15,       # 15%
}
```

### **Update via API:**
```python
import requests

new_thresholds = {
    "response_time_warning": 2.0,  # More sensitive
    "daily_cost_warning": 5.0      # Lower cost limit
}

response = requests.post(
    "http://localhost:8000/alerts/thresholds",
    json=new_thresholds
)
```

## 📧 **Adding Email Alerts**

To enable email notifications, modify `app/utils/mlflow_alerts.py`:

```python
from app.utils.mlflow_alerts import alert_system, email_alert_handler

# Configure email
alert_system.add_alert_handler(
    lambda alerts: email_alert_handler(
        alerts,
        sender_email="your-email@gmail.com",
        sender_password="your-app-password",
        recipient_emails=["admin@company.com"]
    )
)
```

## 🔔 **Alert Types Explained**

### **🟡 WARNING Alerts**
- System is degraded but functional
- Monitor closely, no immediate action required
- Examples: Slightly slow responses, minor accuracy drop

### **🔴 CRITICAL Alerts**
- System requires immediate attention
- User experience is significantly impacted
- Examples: Very slow responses, high error rates, excessive costs

## 📊 **Integration with Existing Tools**

### **MLflow Dashboard**
- All alerts are based on MLflow metrics
- Click "Open MLflow" in dashboard to see detailed data
- Alerts complement your existing MLflow tracking

### **Prometheus & Grafana**
- Alerts use the same metrics as Prometheus
- Can be integrated with Grafana alerting
- Provides additional layer of monitoring

## 🎯 **Business Value**

### **Cost Control**
- Prevents surprise AI bills
- Alerts before costs spiral out of control
- Tracks cost per interaction trends

### **Performance Monitoring**
- Ensures fast user experience
- Detects performance degradation early
- Monitors model quality over time

### **Reliability**
- Immediate notification of system issues
- Proactive error detection
- Maintains high availability

## 🚀 **Production Deployment**

For production, consider:

1. **Email Notifications**: Set up SMTP for email alerts
2. **Slack Integration**: Add Slack webhook for team notifications
3. **PagerDuty**: Integrate with incident management
4. **Custom Thresholds**: Adjust based on your SLAs
5. **Alert Suppression**: Prevent alert fatigue

## 🛡️ **What This Gives You**

✅ **Enterprise-grade monitoring** like Netflix, Uber, Microsoft
✅ **Proactive issue detection** before users complain
✅ **Cost control** to prevent budget overruns
✅ **Performance optimization** insights
✅ **24/7 automated monitoring** without manual intervention
✅ **Beautiful dashboards** for stakeholders
✅ **API-first design** for custom integrations

---

## 🎉 **Your System is Now Production-Ready!**

You've built a professional AI monitoring system that:
- **Tracks everything** that matters
- **Alerts intelligently** when issues arise
- **Scales automatically** as you grow
- **Integrates seamlessly** with your existing tools

**This is exactly what enterprise AI teams use!** 🚀
