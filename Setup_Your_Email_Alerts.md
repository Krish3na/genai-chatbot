# 📧 Email Alert Setup for saikrishna.sriram3@gmail.com

## 🎯 **Quick Setup (5 minutes)**

Your email `saikrishna.sriram3@gmail.com` is already configured as the default recipient! You just need to set up the sender credentials.

### **Step 1: Get Gmail App Password**

1. **Go to Google Account Settings**:
   - Visit: https://myaccount.google.com/security
   - Sign in with your Gmail account

2. **Enable 2-Step Verification** (if not already enabled):
   - Find "2-Step Verification" 
   - Follow the setup process

3. **Generate App Password**:
   - Search for "App passwords" in settings
   - Click "App passwords"
   - Select "Mail" as the app
   - Select "Other" for device and enter "MLflow Alerts"
   - **Copy the 16-character password** (like: `abcd efgh ijkl mnop`)

### **Step 2: Configure Your System**

#### **Option A: Using the Setup Script (Recommended)**
```bash
python setup_email_alerts.py
```
This will guide you through the entire process!

#### **Option B: Manual Configuration**
Create a `.env` file in your project root:

```bash
# Email Alert Configuration
EMAIL_ALERTS_ENABLED=true
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-16-char-app-password
ALERT_RECIPIENTS=saikrishna.sriram3@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### **Step 3: Test Your Setup**

#### **Test via API**:
```bash
curl -X POST http://localhost:8000/alerts/test-email
```

#### **Test via Python Script**:
```bash
python email_alert_example.py
```

## 🚨 **What You'll Receive**

### **Email Alerts Will Be Sent For:**

#### **🔴 CRITICAL Alerts** (Immediate Action Required):
- Response time > 5 seconds
- Model accuracy < 75%
- Error rate > 15%
- Daily cost > $50
- Cost per interaction > $0.05

#### **🟡 WARNING Alerts** (Monitor Closely):
- Response time > 3 seconds  
- Model accuracy < 85%
- Error rate > 5%
- Daily cost > $10
- Cost per interaction > $0.01

### **Sample Email You'll Receive:**

```
Subject: MLflow Alert - 2 issues detected

🚨 MLflow Alert Report

The following issues were detected in your GenAI Chatbot:

🔴 CRITICAL | Performance: Response Time
   Value: 5.2s | Threshold: 5.0s
   Message: Response time (5.2s) exceeds critical threshold

🟡 WARNING | Cost: Daily Cost  
   Value: $12.50 | Threshold: $10.00
   Message: Daily cost ($12.50) exceeds warning threshold

Check your MLflow dashboard for more details: http://localhost:5000
```

## 🔧 **API Endpoints**

Your chatbot now has these email-related endpoints:

### **Check Email Configuration**:
```bash
curl http://localhost:8000/alerts/email-config
```

### **Send Test Email**:
```bash
curl -X POST http://localhost:8000/alerts/test-email
```

### **Check Alert Status** (includes email status):
```bash
curl http://localhost:8000/alerts/status
```

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **"Authentication failed"**
- ✅ Make sure 2-Step Verification is enabled
- ✅ Use App Password, not your regular Gmail password
- ✅ App Password should be 16 characters with spaces

#### **"Connection refused"**
- ✅ Check internet connection
- ✅ Gmail SMTP might be blocked by firewall
- ✅ Try port 465 instead of 587

#### **"Email not received"**
- ✅ Check spam/junk folder
- ✅ Verify recipient email address
- ✅ Gmail might have delivery delays

### **Test Your Configuration**:
```python
# Quick test
import os
os.environ["EMAIL_ALERTS_ENABLED"] = "true"
os.environ["SENDER_EMAIL"] = "your-email@gmail.com"
os.environ["SENDER_PASSWORD"] = "your-app-password"

# Run test
python -c "
from app.utils.mlflow_alerts import alert_system
test_alerts = [{'type': 'WARNING', 'category': 'Test', 'metric': 'Setup', 'value': 'OK', 'threshold': 'N/A', 'message': 'Test email!', 'timestamp': '2025-01-03'}]
alert_system.send_alerts({'test': test_alerts})
print('Test email sent!')
"
```

## 🎉 **What Happens Next**

Once configured:

1. **✅ Automatic Monitoring**: System checks every 5-60 minutes
2. **📧 Smart Alerts**: Only sends emails for real issues
3. **📊 Rich Reports**: Beautiful HTML emails with details
4. **🔗 Quick Access**: Direct links to MLflow dashboard
5. **⚙️ Easy Management**: Update thresholds via API

## 🚀 **Your Email Alert System is Ready!**

- **Recipient**: `saikrishna.sriram3@gmail.com` ✅
- **Smart Thresholds**: Performance, Cost, Quality ✅  
- **Beautiful Emails**: HTML formatted reports ✅
- **API Integration**: Full control via endpoints ✅
- **24/7 Monitoring**: Automated background checks ✅

**You now have enterprise-grade email alerting for your GenAI Chatbot!** 🎯

---

## 📞 **Need Help?**

If you encounter issues:
1. Check the troubleshooting section above
2. Run `python setup_email_alerts.py` for guided setup
3. Test with `python email_alert_example.py`
4. Check logs in your chatbot console

**Your monitoring system is now complete and professional!** 🚀
