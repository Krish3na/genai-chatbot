#!/bin/bash

# Kubernetes deployment script for GenAI Chatbot
set -e

echo "🚀 Deploying GenAI Chatbot to Kubernetes..."

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build Docker image
echo "📦 Building Docker image..."
docker build -t genai-chatbot:latest .

# Load image to kind/minikube if needed
if command -v kind &> /dev/null; then
    echo "📤 Loading image to kind cluster..."
    kind load docker-image genai-chatbot:latest
elif command -v minikube &> /dev/null; then
    echo "📤 Loading image to minikube cluster..."
    minikube image load genai-chatbot:latest
fi

# Create namespace
echo "🏗️ Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Apply ConfigMap and Secret
echo "🔧 Applying ConfigMap and Secret..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Apply PersistentVolumeClaims
echo "💾 Creating PersistentVolumeClaims..."
kubectl apply -f k8s/persistent-volume-claims.yaml

# Apply Deployment
echo "🚀 Deploying application..."
kubectl apply -f k8s/deployment.yaml

# Apply Service
echo "🌐 Creating service..."
kubectl apply -f k8s/service.yaml

# Apply Ingress (optional)
echo "🌍 Creating ingress..."
kubectl apply -f k8s/ingress.yaml

# Apply HorizontalPodAutoscaler
echo "⚖️ Setting up auto-scaling..."
kubectl apply -f k8s/horizontal-pod-autoscaler.yaml

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/genai-chatbot -n genai-chatbot

echo "✅ Deployment completed successfully!"

# Show deployment status
echo "📊 Deployment status:"
kubectl get pods -n genai-chatbot
kubectl get services -n genai-chatbot
kubectl get ingress -n genai-chatbot

echo ""
echo "🌐 Access your application:"
echo "   - Local: kubectl port-forward svc/genai-chatbot-service 8080:80 -n genai-chatbot"
echo "   - Ingress: http://genai-chatbot.local (add to /etc/hosts)"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: kubectl logs -f deployment/genai-chatbot -n genai-chatbot"
echo "   - Scale up: kubectl scale deployment genai-chatbot --replicas=5 -n genai-chatbot"
echo "   - Delete: kubectl delete namespace genai-chatbot" 