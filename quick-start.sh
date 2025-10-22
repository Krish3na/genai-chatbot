#!/bin/bash

# GenAI Chatbot Quick Start Script
echo "🚀 Starting GenAI Chatbot Setup..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key!"
    echo "   OPENAI_API_KEY=your_actual_api_key_here"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start services
echo "🔨 Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

echo ""
echo "✅ Setup complete! Access your services:"
echo "🌐 Frontend:    http://localhost:3001"
echo "🤖 API:        http://localhost:8000"
echo "📊 Grafana:    http://localhost:3000 (admin/admin)"
echo "📈 Prometheus: http://localhost:9090"
echo "🧪 MLflow:     http://localhost:5000"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "💡 Need help? Check README.md"
