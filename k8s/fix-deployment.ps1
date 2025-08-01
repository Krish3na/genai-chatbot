# Fix deployment script for GenAI Chatbot
Write-Host "Fixing GenAI Chatbot deployment..." -ForegroundColor Green

# Delete existing deployment
kubectl delete deployment genai-chatbot -n genai-chatbot

# Create secret with your API key
# Replace YOUR_API_KEY_HERE with your actual OpenAI API key
kubectl create secret generic genai-chatbot-secrets --from-literal=OPENAI_API_KEY="YOUR_API_KEY_HERE" -n genai-chatbot

# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -n genai-chatbot

Write-Host "Deployment fixed!" -ForegroundColor Green 