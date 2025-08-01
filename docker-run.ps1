# PowerShell script to build and run GenAI Chatbot Docker container
param(
    [switch]$Rebuild
)

Write-Host "Building GenAI Chatbot Docker image..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your OpenAI API key:" -ForegroundColor Yellow
    Write-Host "OPENAI_API_KEY=your_actual_openai_api_key_here" -ForegroundColor Yellow
    exit 1
}

# Stop and remove existing container if it exists
$existingContainer = docker ps -a --filter "name=genai-chatbot" --format "table {{.Names}}" | Select-String "genai-chatbot"
if ($existingContainer) {
    Write-Host "Stopping existing container..." -ForegroundColor Yellow
    docker stop genai-chatbot
    docker rm genai-chatbot
}

# Build Docker image
if ($Rebuild) {
    Write-Host "Rebuilding Docker image..." -ForegroundColor Green
    docker build --no-cache -t genai-chatbot:latest .
} else {
    Write-Host "Building Docker image..." -ForegroundColor Green
    docker build -t genai-chatbot:latest .
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Starting GenAI Chatbot container..." -ForegroundColor Green

# Run container
docker run -d --name genai-chatbot -p 8000:8000 --env-file .env -v ${PWD}/data:/app/data -v ${PWD}/chroma_db:/app/chroma_db genai-chatbot:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host "Container started successfully!" -ForegroundColor Green
    
    # Wait a moment for container to start
    Start-Sleep -Seconds 3
    
    # Check container status
    Write-Host "Container status:" -ForegroundColor Cyan
    docker ps --filter "name=genai-chatbot"
    
    Write-Host ""
    Write-Host "Access your chatbot at: http://localhost:8000" -ForegroundColor Green
    Write-Host "API documentation at: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "Health check at: http://localhost:8000/health" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "   View logs: docker logs genai-chatbot" -ForegroundColor White
    Write-Host "   Stop container: docker stop genai-chatbot" -ForegroundColor White
    Write-Host "   Remove container: docker rm genai-chatbot" -ForegroundColor White
    Write-Host "   Restart container: docker restart genai-chatbot" -ForegroundColor White
    Write-Host "   Rebuild and restart: .\docker-run.ps1 -Rebuild" -ForegroundColor White
} else {
    Write-Host "Error: Failed to start container!" -ForegroundColor Red
} 