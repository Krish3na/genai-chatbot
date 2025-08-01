# Kubernetes Deployment for GenAI Chatbot

This directory contains all the Kubernetes manifests and deployment scripts for the GenAI Chatbot.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ingress       │    │   Service       │    │   Deployment    │
│   (nginx)       │───▶│   (Load Bal.)   │───▶│   (3 replicas)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   PVC           │
                                              │   (Data/Chroma) │
                                              └─────────────────┘
```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `namespace.yaml` | Creates isolated namespace |
| `configmap.yaml` | Environment variables |
| `secret.yaml` | Sensitive data (API keys) |
| `deployment.yaml` | Application deployment |
| `service.yaml` | Load balancer |
| `ingress.yaml` | External access |
| `persistent-volume-claims.yaml` | Data persistence |
| `horizontal-pod-autoscaler.yaml` | Auto-scaling |
| `deploy.sh` | Linux/Mac deployment script |
| `deploy.ps1` | Windows deployment script |

## 🚀 Quick Start

### Prerequisites

1. **Kubernetes Cluster**
   ```bash
   # Option 1: Docker Desktop (Windows/Mac)
   # Enable Kubernetes in Docker Desktop settings

   # Option 2: Minikube
   minikube start

   # Option 3: Kind
   kind create cluster
   ```

2. **kubectl**
   ```bash
   # Install kubectl
   # https://kubernetes.io/docs/tasks/tools/
   ```

3. **Docker**
   ```bash
   # Ensure Docker is running
   docker info
   ```

### Deployment

#### Linux/Mac:
```bash
chmod +x k8s/deploy.sh
./k8s/deploy.sh
```

#### Windows:
```powershell
.\k8s\deploy.ps1
```

#### Manual:
```bash
# Build image
docker build -t genai-chatbot:latest .

# Apply manifests
kubectl apply -f k8s/
```

## 🔧 Configuration

### Update API Key

1. **Encode your API key:**
   ```bash
   echo -n "your-openai-api-key" | base64
   ```

2. **Update `k8s/secret.yaml`:**
   ```yaml
   data:
     OPENAI_API_KEY: "your-base64-encoded-key"
   ```

### Customize Resources

Edit `k8s/deployment.yaml`:
```yaml
resources:
  requests:
    memory: "512Mi"    # Minimum
    cpu: "250m"
  limits:
    memory: "1Gi"      # Maximum
    cpu: "500m"
```

### Auto-scaling

Edit `k8s/horizontal-pod-autoscaler.yaml`:
```yaml
minReplicas: 2        # Minimum pods
maxReplicas: 10       # Maximum pods
averageUtilization: 70 # CPU threshold
```

## 🌐 Access

### Port Forward (Local)
```bash
kubectl port-forward svc/genai-chatbot-service 8080:80 -n genai-chatbot
# Access: http://localhost:8080
```

### Ingress (External)
```bash
# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
127.0.0.1 genai-chatbot.local

# Access: http://genai-chatbot.local
```

## 📊 Monitoring

### Check Status
```bash
# Pods
kubectl get pods -n genai-chatbot

# Services
kubectl get services -n genai-chatbot

# Ingress
kubectl get ingress -n genai-chatbot

# HPA
kubectl get hpa -n genai-chatbot
```

### View Logs
```bash
# All pods
kubectl logs -f deployment/genai-chatbot -n genai-chatbot

# Specific pod
kubectl logs -f <pod-name> -n genai-chatbot
```

### Scale Manually
```bash
# Scale up
kubectl scale deployment genai-chatbot --replicas=5 -n genai-chatbot

# Scale down
kubectl scale deployment genai-chatbot --replicas=1 -n genai-chatbot
```

## 🔄 Updates

### Rolling Update
```bash
# Update image
docker build -t genai-chatbot:v1.1 .
kubectl set image deployment/genai-chatbot genai-chatbot=genai-chatbot:v1.1 -n genai-chatbot
```

### Blue-Green Deployment
```bash
# Deploy new version
kubectl apply -f k8s/deployment-v2.yaml

# Switch traffic
kubectl patch service genai-chatbot-service -p '{"spec":{"selector":{"version":"v2"}}}'
```

## 🧹 Cleanup

### Delete Everything
```bash
kubectl delete namespace genai-chatbot
```

### Delete Specific Resources
```bash
kubectl delete deployment genai-chatbot -n genai-chatbot
kubectl delete service genai-chatbot-service -n genai-chatbot
kubectl delete ingress genai-chatbot-ingress -n genai-chatbot
```

## 🔍 Troubleshooting

### Common Issues

1. **Image Pull Error**
   ```bash
   # Load image to local cluster
   kind load docker-image genai-chatbot:latest
   # or
   minikube image load genai-chatbot:latest
   ```

2. **PVC Pending**
   ```bash
   # Check storage class
   kubectl get storageclass
   
   # Update PVC if needed
   kubectl patch pvc genai-chatbot-data-pvc -p '{"spec":{"storageClassName":"standard"}}'
   ```

3. **Ingress Not Working**
   ```bash
   # Check ingress controller
   kubectl get pods -n ingress-nginx
   
   # Install nginx ingress
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
   ```

### Debug Commands
```bash
# Describe resources
kubectl describe pod <pod-name> -n genai-chatbot
kubectl describe service genai-chatbot-service -n genai-chatbot

# Check events
kubectl get events -n genai-chatbot --sort-by='.lastTimestamp'

# Exec into pod
kubectl exec -it <pod-name> -n genai-chatbot -- /bin/bash
```

## 📈 Production Considerations

### Security
- Use secrets for sensitive data
- Enable RBAC
- Network policies
- Pod security policies

### Monitoring
- Prometheus + Grafana
- Application metrics
- Resource monitoring

### Backup
- PVC snapshots
- Application data backup
- Configuration backup

### High Availability
- Multi-zone deployment
- Load balancer
- Auto-scaling
- Health checks

## 🎯 Next Steps

1. **CI/CD Pipeline** - Jenkins/GitHub Actions
2. **Monitoring** - Prometheus/Grafana
3. **Security** - RBAC, Network Policies
4. **Backup** - Velero for disaster recovery
5. **Advanced Features** - Service Mesh (Istio) 