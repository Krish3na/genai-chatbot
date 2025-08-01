# Quick fix script for Kubernetes deployment issues

Write-Host "Fixing Kubernetes deployment issues..." -ForegroundColor Green

# Delete existing PVCs
Write-Host "Deleting existing PVCs..." -ForegroundColor Yellow
kubectl delete pvc genai-chatbot-data-pvc genai-chatbot-chroma-pvc -n genai-chatbot --ignore-not-found=true

# Delete existing secret
Write-Host "Deleting existing secret..." -ForegroundColor Yellow
kubectl delete secret genai-chatbot-secrets -n genai-chatbot --ignore-not-found=true

# Create new secret (replace with your actual API key)
Write-Host "Creating new secret..." -ForegroundColor Yellow
kubectl create secret generic genai-chatbot-secrets --from-literal=OPENAI_API_KEY="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" -n genai-chatbot

# Apply updated PVCs
Write-Host "Applying updated PVCs..." -ForegroundColor Yellow
kubectl apply -f k8s/persistent-volume-claims.yaml

# Restart deployment
Write-Host "Restarting deployment..." -ForegroundColor Yellow
kubectl rollout restart deployment/genai-chatbot -n genai-chatbot

# Wait for deployment to be ready
Write-Host "Waiting for deployment to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=available --timeout=300s deployment/genai-chatbot -n genai-chatbot

Write-Host "Fix completed!" -ForegroundColor Green

# Show status
Write-Host "Current status:" -ForegroundColor Cyan
kubectl get pods -n genai-chatbot 