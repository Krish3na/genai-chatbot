# PowerShell deployment script for GenAI Chatbot Kubernetes deployment

Write-Host "Deploying GenAI Chatbot to Kubernetes..." -ForegroundColor Green

# Check if kubectl is installed
try {
    kubectl version --client | Out-Null
    Write-Host "kubectl found" -ForegroundColor Green
} catch {
    Write-Host "kubectl is not installed. Please install kubectl first." -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t genai-chatbot:latest .

# Try to load image to kind/minikube (optional)
Write-Host "Attempting to load image to cluster..." -ForegroundColor Yellow
try {
    kind load docker-image genai-chatbot:latest
    Write-Host "Image loaded to kind cluster" -ForegroundColor Green
} catch {
    try {
        minikube image load genai-chatbot:latest
        Write-Host "Image loaded to minikube cluster" -ForegroundColor Green
    } catch {
        Write-Host "Could not load image to cluster (this is OK for Docker Desktop)" -ForegroundColor Yellow
    }
}

# Create namespace
Write-Host "Creating namespace..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml

# Apply ConfigMap and Secret
Write-Host "Applying ConfigMap and Secret..." -ForegroundColor Yellow
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Apply PersistentVolumeClaims
Write-Host "Creating PersistentVolumeClaims..." -ForegroundColor Yellow
kubectl apply -f k8s/persistent-volume-claims.yaml

# Apply Deployment
Write-Host "Deploying application..." -ForegroundColor Yellow
kubectl apply -f k8s/deployment.yaml

# Apply Service
Write-Host "Creating service..." -ForegroundColor Yellow
kubectl apply -f k8s/service.yaml

# Apply Ingress
Write-Host "Creating ingress..." -ForegroundColor Yellow
kubectl apply -f k8s/ingress.yaml

# Apply HorizontalPodAutoscaler
Write-Host "Setting up auto-scaling..." -ForegroundColor Yellow
kubectl apply -f k8s/horizontal-pod-autoscaler.yaml

# Wait for deployment to be ready
Write-Host "Waiting for deployment to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=available --timeout=300s deployment/genai-chatbot -n genai-chatbot

Write-Host "Deployment completed successfully!" -ForegroundColor Green

# Show deployment status
Write-Host "Deployment status:" -ForegroundColor Cyan
kubectl get pods -n genai-chatbot
kubectl get services -n genai-chatbot
kubectl get ingress -n genai-chatbot

Write-Host ""
Write-Host "Access your application:" -ForegroundColor Green
Write-Host "   - Local: kubectl port-forward svc/genai-chatbot-service 8080:80 -n genai-chatbot" -ForegroundColor White
Write-Host "   - Ingress: http://genai-chatbot.local (add to hosts file)" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "   - View logs: kubectl logs -f deployment/genai-chatbot -n genai-chatbot" -ForegroundColor White
Write-Host "   - Scale up: kubectl scale deployment genai-chatbot --replicas=5 -n genai-chatbot" -ForegroundColor White
Write-Host "   - Delete: kubectl delete namespace genai-chatbot" -ForegroundColor White 