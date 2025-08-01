# GenAI Chatbot Deployment Script
param(
    [switch]$Build,
    [switch]$Deploy,
    [switch]$Test,
    [switch]$All
)

Write-Host "GenAI Chatbot Deployment Script" -ForegroundColor Green

if ($Build -or $All) {
    Write-Host "Building Docker image..." -ForegroundColor Yellow
    docker build -t genai-chatbot:latest .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker image built successfully!" -ForegroundColor Green
    } else {
        Write-Host "Docker build failed!" -ForegroundColor Red
        exit 1
    }
}

if ($Deploy -or $All) {
    Write-Host "Deploying to Kubernetes..." -ForegroundColor Yellow
    
    kubectl set image deployment/genai-chatbot genai-chatbot=genai-chatbot:latest -n genai-chatbot
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Deployment updated!" -ForegroundColor Green
        
        Write-Host "Waiting for rollout to complete..." -ForegroundColor Yellow
        kubectl rollout status deployment/genai-chatbot -n genai-chatbot
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Deployment completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "Deployment failed!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Deployment update failed!" -ForegroundColor Red
        exit 1
    }
}

if ($Test -or $All) {
    Write-Host "Running health checks..." -ForegroundColor Yellow
    
    Start-Sleep -Seconds 30
    
    try {
        $response = Invoke-WebRequest -Uri "http://genai-chatbot.local/health" -Method GET
        if ($response.StatusCode -eq 200) {
            Write-Host "Health check passed!" -ForegroundColor Green
        } else {
            Write-Host "Health check failed!" -ForegroundColor Red
        }
    } catch {
        Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    try {
        $body = @{
            message = "Hello, this is a test message"
            user_id = "deployment_test"
        } | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "http://genai-chatbot.local/chat" -Method POST -Body $body -ContentType "application/json"
        if ($response.StatusCode -eq 200) {
            Write-Host "Chat endpoint test passed!" -ForegroundColor Green
        } else {
            Write-Host "Chat endpoint test failed!" -ForegroundColor Red
        }
    } catch {
        Write-Host "Chat endpoint test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "Deployment script completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Monitoring URLs:" -ForegroundColor Cyan
Write-Host "   - Application: http://genai-chatbot.local" -ForegroundColor White
Write-Host "   - Grafana: http://localhost:3000" -ForegroundColor White
Write-Host "   - Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "   - Jenkins: http://localhost:8080" -ForegroundColor White 