# GenAI Chatbot Monitoring Setup

## 🎯 Overview

This project includes a complete monitoring stack with **Prometheus** for metrics collection and **Grafana** for visualization. The advanced dashboard provides comprehensive insights into your GenAI chatbot's performance, usage patterns, and system health.

## 📊 What You Get

### **Advanced Dashboard Features:**
- **23 different panels** with various visualizations
- **Real-time metrics** with auto-refresh every 10 seconds
- **Professional thresholds** and alerting capabilities
- **Interactive filtering** by user_id and intent
- **Cost tracking** for AI operations
- **Performance analytics** with heatmaps
- **User behavior insights**
- **System health monitoring**

### **Dashboard Sections:**
1. **System Overview** - Key metrics at a glance
2. **Performance Metrics** - Response time distribution and intent analysis
3. **AI & Cost Metrics** - Token usage, costs, and RAG vs Direct usage
4. **Real-time Analytics** - Time-series data and trends
5. **User Activity** - User engagement and intent distribution
6. **System Health** - Service status, memory, CPU, and connections

## 🚀 Quick Start

### 1. Start Port Forwarding
```powershell
# Stop any existing port forwarding
Get-Process kubectl -ErrorAction SilentlyContinue | Stop-Process -Force

# Start port forwarding for all services
Start-Process kubectl -ArgumentList "port-forward", "-n", "genai-chatbot", "svc/genai-chatbot-service", "8080:80" -WindowStyle Hidden
Start-Process kubectl -ArgumentList "port-forward", "-n", "genai-chatbot", "svc/prometheus-service", "9090:9090" -WindowStyle Hidden
Start-Process kubectl -ArgumentList "port-forward", "-n", "genai-chatbot", "svc/grafana-service", "3000:3000" -WindowStyle Hidden
```

### 2. Generate Test Data
```powershell
# Quick test (20 requests)
.\quick-test.ps1

# Or comprehensive load test (25 requests with detailed reporting)
.\load-test.ps1
```

### 3. Access Dashboards
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Chatbot API**: http://localhost:8080/docs

## 📈 Dashboard Access

### **Grafana Dashboard**
1. Go to http://localhost:3000
2. Login with `admin/admin`
3. Look for **"GenAI Chatbot - Advanced Monitoring"** dashboard
4. If not visible, go to **Dashboards > Browse** and search for it

### **Dashboard Features:**
- **Auto-refresh** every 10 seconds
- **Template variables** for filtering (user_id, intent)
- **Color-coded thresholds** (green/yellow/red)
- **Interactive panels** with drill-down capabilities
- **Annotations** for deployment markers

## 🔍 Prometheus Queries

Use the queries from `prometheus-queries.txt` for custom analysis:

### **Basic Metrics:**
```promql
# Total requests
sum(genai_chatbot_chat_requests_total)

# Requests per second
sum(rate(genai_chatbot_chat_requests_total[5m]))

# Average response time
histogram_quantile(0.5, rate(genai_chatbot_chat_request_duration_seconds_bucket[5m]))

# Error rate
sum(rate(genai_chatbot_errors_total[5m])) / sum(rate(genai_chatbot_chat_requests_total[5m])) * 100
```

### **User Analytics:**
```promql
# Top users
topk(10, sum(genai_chatbot_chat_requests_total) by (user_id))

# User activity rate
sum(rate(genai_chatbot_chat_requests_total[5m])) by (user_id)
```

### **AI & Cost Metrics:**
```promql
# Token usage rate
sum(rate(genai_chatbot_tokens_used_total[5m]))

# Total cost
sum(genai_chatbot_cost_total)

# RAG vs Direct usage
sum(genai_chatbot_chat_requests_total) by (response_type)
```

### **System Health:**
```promql
# Service status
up{job="genai-chatbot"}

# Memory usage (MB)
container_memory_usage_bytes{container="genai-chatbot"} / 1024 / 1024

# CPU usage (%)
rate(container_cpu_usage_seconds_total{container="genai-chatbot"}[5m]) * 100
```

## 🧪 Testing Scripts

### **Quick Test (`quick-test.ps1`)**
- 20 requests with 4 different users
- Tests health and metrics endpoints
- 1-second delays between requests
- Perfect for basic testing

### **Load Test (`load-test.ps1`)**
- 25 requests with 5 different users
- 25 different messages covering various topics
- Random delays (1-3 seconds)
- Detailed success/failure reporting
- Comprehensive endpoint testing

### **Manual Testing**
```powershell
# Single request
$body = @{
    message = "Hello, how are you?"
    user_id = "test_user"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8080/chat" -Method POST -Body $body -ContentType "application/json"
```

## 📋 Available Endpoints

### **Chatbot API:**
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `POST /chat` - Chat endpoint
- `GET /docs` - API documentation

### **Monitoring:**
- **Prometheus**: http://localhost:9090
  - Status > Targets - Check scraping status
  - Graph - Run custom queries
  - Alerts - View alert rules

- **Grafana**: http://localhost:3000
  - Dashboards - View visualizations
  - Explore - Ad-hoc querying
  - Alerting - Configure alerts

## 🎛️ Dashboard Customization

### **Template Variables:**
- **user_id**: Filter by specific users
- **intent**: Filter by detected intents
- **response_type**: Filter by RAG vs Direct responses

### **Time Ranges:**
- **Last 5 minutes**: `[5m]`
- **Last 1 hour**: `[1h]`
- **Last 6 hours**: `[6h]`
- **Last 24 hours**: `[1d]`

### **Adding Custom Panels:**
1. Click **Edit** on the dashboard
2. Add new panel
3. Use queries from `prometheus-queries.txt`
4. Configure visualization type and thresholds

## 🚨 Alerting Examples

### **High Error Rate:**
```promql
sum(rate(genai_chatbot_errors_total[5m])) / sum(rate(genai_chatbot_chat_requests_total[5m])) * 100 > 5
```

### **High Response Time:**
```promql
histogram_quantile(0.95, rate(genai_chatbot_chat_request_duration_seconds_bucket[5m])) > 10
```

### **Service Down:**
```promql
up{job="genai-chatbot"} == 0
```

### **High Load:**
```promql
sum(rate(genai_chatbot_chat_requests_total[5m])) > 50
```

## 🔧 Troubleshooting

### **Dashboard Not Loading:**
1. Check if Grafana pod is running: `kubectl get pods -n genai-chatbot`
2. Check Grafana logs: `kubectl logs -n genai-chatbot deployment/grafana`
3. Verify port forwarding: `netstat -an | findstr 3000`

### **No Data in Prometheus:**
1. Check targets: http://localhost:9090/targets
2. Verify genai-chatbot target is UP (green)
3. Check metrics endpoint: http://localhost:8080/metrics

### **Port Forwarding Issues:**
```powershell
# Stop all kubectl processes
Get-Process kubectl | Stop-Process -Force

# Restart port forwarding
.\start-monitoring.ps1
```

## 📊 Metrics Explained

### **Request Metrics:**
- `genai_chatbot_chat_requests_total` - Total chat requests
- `genai_chatbot_chat_request_duration_seconds` - Response time histogram
- `genai_chatbot_errors_total` - Total errors

### **AI Metrics:**
- `genai_chatbot_tokens_used_total` - Total tokens consumed
- `genai_chatbot_cost_total` - Total cost in USD

### **System Metrics:**
- `container_memory_usage_bytes` - Memory usage
- `container_cpu_usage_seconds_total` - CPU usage
- `up` - Service health status

## 🎉 Success Indicators

### **Dashboard Working:**
- ✅ Grafana loads without errors
- ✅ Dashboard shows "GenAI Chatbot - Advanced Monitoring"
- ✅ Panels display data (not "No data")
- ✅ Auto-refresh updates values

### **Data Collection Working:**
- ✅ Prometheus targets show UP status
- ✅ Metrics endpoint returns data
- ✅ Test scripts complete successfully
- ✅ Dashboard shows increasing request counts

## 📚 Additional Resources

- **Prometheus Query Language**: https://prometheus.io/docs/prometheus/latest/querying/
- **Grafana Documentation**: https://grafana.com/docs/
- **Prometheus Metrics**: https://prometheus.io/docs/concepts/metric_types/

---

**🎯 You now have a production-grade monitoring system for your GenAI chatbot!**
