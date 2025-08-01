#!/bin/bash

# Docker run script for GenAI Chatbot

set -e

echo "🐳 Building GenAI Chatbot Docker image..."

# Build the Docker image
docker build -t genai-chatbot:latest .

echo "✅ Docker image built successfully!"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create a .env file with your OpenAI API key:"
    echo "   OPENAI_API_KEY=your_api_key_here"
    echo ""
    echo "🚀 Starting container without .env file..."
fi

echo "🚀 Starting GenAI Chatbot container..."

# Run the container
docker run -d \
    --name genai-chatbot \
    -p 8000:8000 \
    --env-file .env \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/chroma_db:/app/chroma_db \
    --restart unless-stopped \
    genai-chatbot:latest

echo "✅ Container started successfully!"
echo ""
echo "📊 Container status:"
docker ps --filter name=genai-chatbot

echo ""
echo "🌐 Access your chatbot at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo "💚 Health check at: http://localhost:8000/health"

echo ""
echo "📝 Useful commands:"
echo "   View logs: docker logs genai-chatbot"
echo "   Stop container: docker stop genai-chatbot"
echo "   Remove container: docker rm genai-chatbot"
echo "   Restart container: docker restart genai-chatbot" 