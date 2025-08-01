# PowerShell script to deploy monitoring stack
param(
    [switch]$SkipPrometheus,
    [switch]$SkipGrafana
)

Write-Host "Deploying GenAI Chatbot Monitoring Stack..." -ForegroundColor Green

# Check if namespace exists
$namespace = kubectl get namespace genai-chatbot --ignore-not-found
if (-not $namespace) {
    Write-Host "Creating namespace..." -ForegroundColor Yellow
    kubectl apply -f k8s/namespace.yaml
}

# Deploy Prometheus
if (-not $SkipPrometheus) {
    Write-Host "Deploying Prometheus..." -ForegroundColor Green
    kubectl apply -f k8s/prometheus-configmap.yaml
    kubectl apply -f k8s/prometheus-deployment.yaml
    kubectl apply -f k8s/prometheus-service.yaml
    
    Write-Host "Waiting for Prometheus to be ready..." -ForegroundColor Yellow
    kubectl wait --for=condition=ready pod -l app=prometheus -n genai-chatbot --timeout=120s
}

# Deploy Grafana
if (-not $SkipGrafana) {
    Write-Host "Deploying Grafana..." -ForegroundColor Green
    kubectl apply -f k8s/grafana-configmap.yaml
    kubectl apply -f k8s/grafana-dashboard-configmap.yaml
    kubectl apply -f k8s/grafana-deployment.yaml
    kubectl apply -f k8s/grafana-service.yaml
    
    Write-Host "Waiting for Grafana to be ready..." -ForegroundColor Yellow
    kubectl wait --for=condition=ready pod -l app=grafana -n genai-chatbot --timeout=120s
}

Write-Host "Monitoring stack deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  Prometheus: kubectl port-forward svc/prometheus-service 9090:9090 -n genai-chatbot" -ForegroundColor White
Write-Host "  Grafana: kubectl port-forward svc/grafana-service 3000:3000 -n genai-chatbot" -ForegroundColor White
Write-Host ""
Write-Host "Grafana Credentials:" -ForegroundColor Cyan
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin" -ForegroundColor White 