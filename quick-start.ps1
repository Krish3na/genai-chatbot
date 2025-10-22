# GenAI Chatbot Quick Start Script for Windows
Write-Host "🚀 Starting GenAI Chatbot Setup..." -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item env.example .env
    Write-Host "⚠️  Please edit .env file and add your OpenAI API key!" -ForegroundColor Red
    Write-Host "   OPENAI_API_KEY=your_actual_api_key_here" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Build and start services
Write-Host "🔨 Building Docker containers..." -ForegroundColor Blue
docker-compose build

Write-Host "🚀 Starting services..." -ForegroundColor Blue
docker-compose up -d

Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service health
Write-Host "🔍 Checking service health..." -ForegroundColor Blue
docker-compose ps

Write-Host ""
Write-Host "✅ Setup complete! Access your services:" -ForegroundColor Green
Write-Host "🌐 Frontend:    http://localhost:3001" -ForegroundColor Cyan
Write-Host "🤖 API:        http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 Grafana:    http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
Write-Host "📈 Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "🧪 MLflow:     http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Magenta
Write-Host "💡 Need help? Check README.md" -ForegroundColor Magenta
