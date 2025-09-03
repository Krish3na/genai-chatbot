# Simple deployment script for GenAI Chatbot with monitoring
Write-Host "Deploying GenAI Chatbot with monitoring stack..." -ForegroundColor Green

# Create namespace
Write-Host "Creating namespace..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml

# Create ConfigMap and Secret
Write-Host "Creating ConfigMap and Secret..." -ForegroundColor Yellow
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy main application
Write-Host "Deploying chatbot application..." -ForegroundColor Yellow
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/deployment-hybrid.yaml

# Deploy Prometheus
Write-Host "Deploying Prometheus..." -ForegroundColor Yellow
kubectl apply -f k8s/prometheus-serviceaccount.yaml
kubectl apply -f k8s/prometheus-configmap.yaml
kubectl apply -f k8s/prometheus-service.yaml
kubectl apply -f k8s/prometheus-deployment.yaml

# Deploy Grafana
Write-Host "Deploying Grafana..." -ForegroundColor Yellow
kubectl apply -f k8s/grafana-service.yaml
kubectl apply -f k8s/grafana-datasources-configmap.yaml
kubectl apply -f k8s/grafana-simple.yaml

# Wait for pods to be ready
Write-Host "Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=genai-chatbot -n genai-chatbot --timeout=120s
kubectl wait --for=condition=ready pod -l app=prometheus -n genai-chatbot --timeout=120s
kubectl wait --for=condition=ready pod -l app=grafana -n genai-chatbot --timeout=120s

# Show status
Write-Host "Deployment completed! Pod status:" -ForegroundColor Green
kubectl get pods -n genai-chatbot

Write-Host "`nTo access the services:" -ForegroundColor Cyan
Write-Host "Chatbot: kubectl port-forward -n genai-chatbot svc/genai-chatbot-service 8080:80" -ForegroundColor White
Write-Host "Prometheus: kubectl port-forward -n genai-chatbot svc/prometheus-service 9090:9090" -ForegroundColor White
Write-Host "Grafana: kubectl port-forward -n genai-chatbot svc/grafana-service 3000:3000" -ForegroundColor White
Write-Host "Grafana credentials: admin/admin" -ForegroundColor White
