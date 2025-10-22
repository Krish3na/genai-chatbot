# GenAI Chatbot - Kubernetes Monitoring Setup

This directory contains the complete monitoring stack for the GenAI Chatbot, including automatic dashboard provisioning and metrics collection.

## 🚀 Quick Start

### Automated Setup (Recommended)

Run the automated setup script to deploy everything:

```powershell
# Navigate to the k8s directory
cd k8s

# Run the automated setup
.\automated-monitoring-setup.ps1
```

This will automatically:
- Deploy Prometheus with custom configuration
- Deploy Grafana with pre-configured dashboards
- Set up automatic metrics collection
- Configure port-forwarding for local access
- Test the setup

### Manual Setup

If you prefer manual setup, follow these steps:

1. **Create namespace:**
   ```bash
   kubectl apply -f namespace.yaml
   ```

2. **Deploy storage:**
   ```bash
   kubectl apply -f persistent-volume-claims.yaml
   ```

3. **Deploy Prometheus:**
   ```bash
   kubectl apply -f prometheus-serviceaccount.yaml
   kubectl apply -f prometheus-configmap.yaml
   kubectl apply -f prometheus-deployment.yaml
   kubectl apply -f prometheus-service.yaml
   ```

4. **Deploy Grafana:**
   ```bash
   kubectl apply -f grafana-datasources-configmap.yaml
   kubectl apply -f grafana-dashboard-complete.yaml
   kubectl apply -f grafana-deployment-final.yaml
   kubectl apply -f grafana-service.yaml
   ```

5. **Deploy ingress (optional):**
   ```bash
   kubectl apply -f monitoring-ingress.yaml
   ```

## 📊 Access Information

After deployment, access the monitoring tools:

### Grafana Dashboard
- **URL:** http://localhost:3000
- **Username:** admin
- **Password:** admin123
- **Features:**
  - Automatic dashboard provisioning
  - Real-time metrics visualization
  - Pre-configured GenAI Chatbot dashboard
  - Response time monitoring
  - Token usage tracking
  - Error rate alerts
  - RAG performance metrics
  - Cost tracking

### Prometheus Metrics
- **URL:** http://localhost:9090
- **Features:**
  - Raw metrics collection
  - Query interface
  - Alert rules
  - Service discovery

## 📈 Available Metrics

The monitoring stack collects the following metrics:

### Chat Metrics
- `genai_chatbot_chat_requests_total` - Total chat requests
- `genai_chatbot_chat_request_duration_seconds` - Response time
- `genai_chatbot_tokens_used_total` - Token usage
- `genai_chatbot_cost_total` - Cost tracking

### RAG Metrics
- `genai_chatbot_rag_requests_total` - RAG requests
- `genai_chatbot_rag_sources_used` - Sources used
- `genai_chatbot_rag_context_length` - Context length

### Document Metrics
- `genai_chatbot_document_uploads_total` - Document uploads
- `genai_chatbot_document_deletions_total` - Document deletions
- `genai_chatbot_knowledge_base_documents` - Document count

### System Metrics
- `genai_chatbot_active_conversations` - Active conversations
- `genai_chatbot_intent_classifications_total` - Intent classifications
- `genai_chatbot_errors_total` - Error tracking

## 🎯 Dashboard Features

The Grafana dashboard includes:

### Real-time Monitoring
- **Chat Requests per Second** - Live request rate
- **Response Time (95th percentile)** - Performance monitoring
- **Token Usage Rate** - Cost optimization
- **Error Rate** - System health

### Performance Analytics
- **Response Time Over Time** - Trend analysis
- **Chat Requests by Intent** - Usage patterns
- **RAG Performance** - Knowledge base effectiveness
- **Cost Tracking** - Budget monitoring

### System Health
- **Active Conversations** - User engagement
- **Knowledge Base Documents** - Content management
- **Document Uploads** - Content activity
- **Intent Classification** - AI accuracy

## 🔧 Configuration Files

### Prometheus Configuration
- `prometheus-configmap.yaml` - Scraping rules and alerting
- `prometheus-deployment.yaml` - Deployment configuration
- `prometheus-service.yaml` - Service exposure

### Grafana Configuration
- `grafana-dashboard-complete.yaml` - Complete dashboard with all metrics
- `grafana-datasources-configmap.yaml` - Prometheus data source
- `grafana-deployment-final.yaml` - Deployment with auto-provisioning

### Storage
- `persistent-volume-claims.yaml` - Persistent storage for metrics and dashboards

## 🧪 Testing

Generate test traffic to populate the dashboard:

```bash
# Run the test script
python test_metrics.py
```

This will:
- Send test requests to the chatbot
- Generate metrics for the dashboard
- Verify endpoint accessibility
- Create sample data for visualization

## 🚨 Alerts

The monitoring stack includes pre-configured alerts:

- **High Error Rate** - When error rate > 0.1/sec
- **High Response Time** - When 95th percentile > 5 seconds
- **High Token Usage** - When usage > 1000 tokens/sec
- **Service Down** - When chatbot service is unavailable

## 🔍 Troubleshooting

### Common Issues

1. **Dashboard not loading:**
   - Check if Grafana pod is running: `kubectl get pods -n genai-chatbot`
   - Verify port-forwarding: `kubectl port-forward service/grafana-service 3000:3000 -n genai-chatbot`

2. **No metrics appearing:**
   - Check Prometheus targets: http://localhost:9090/targets
   - Verify chatbot service is running
   - Check metrics endpoint: `curl http://localhost:8000/metrics`

3. **Port-forwarding issues:**
   - Kill existing port-forwards: `Get-Process kubectl | Stop-Process`
   - Restart port-forwarding manually

### Useful Commands

   ```bash
# Check pod status
kubectl get pods -n genai-chatbot

# Check services
kubectl get services -n genai-chatbot

# View logs
kubectl logs deployment/grafana -n genai-chatbot
kubectl logs deployment/prometheus -n genai-chatbot

# Access pods directly
kubectl exec -it deployment/grafana -n genai-chatbot -- /bin/sh
```

## 📝 Customization

### Adding New Metrics

1. Add metrics to `app/utils/metrics.py`
2. Update the dashboard in `grafana-dashboard-complete.yaml`
3. Redeploy the dashboard: `kubectl apply -f grafana-dashboard-complete.yaml`

### Modifying Alerts

Edit `prometheus-configmap.yaml` and redeploy:
```bash
kubectl apply -f prometheus-configmap.yaml
```

### Custom Dashboards

Create new dashboard JSON and add to `grafana-dashboard-complete.yaml`.

## 🎉 Success!

Once deployed, you'll have:
- ✅ Automatic dashboard provisioning
- ✅ Real-time metrics collection
- ✅ Performance monitoring
- ✅ Cost tracking
- ✅ Error alerting
- ✅ RAG performance analytics

The monitoring stack will automatically collect and visualize all GenAI chatbot metrics without manual intervention! 