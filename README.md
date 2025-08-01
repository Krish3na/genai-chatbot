# 🚀 Production-Grade GenAI Chatbot

A comprehensive, production-ready GenAI Chatbot built with modern technologies including OpenAI GPT-4, LangChain, Docker, Kubernetes, Jenkins CI/CD, and Prometheus/Grafana monitoring.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   OpenAI GPT-4  │
│   (Web/Mobile)  │◄──►│   Application   │◄──►│   LLM Service   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ChromaDB      │    │   LangChain     │    │   Intent        │
│   Vector Store  │◄──►│   RAG Pipeline  │◄──►│   Classifier    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ Features

### 🤖 Core AI Features
- **OpenAI GPT-4 Integration**: Advanced language model for intelligent responses
- **RAG (Retrieval-Augmented Generation)**: Enhanced responses with document context
- **Intent Classification**: Smart routing of user queries
- **Conversation Management**: Multi-turn dialogue support
- **Document Processing**: PDF and text file support

### 🐳 Production Features
- **Docker Containerization**: Consistent deployment across environments
- **Kubernetes Orchestration**: Scalable, resilient deployment
- **Jenkins CI/CD**: Automated testing and deployment pipeline
- **GitHub Actions**: Alternative CI/CD workflow
- **Monitoring & Observability**: Prometheus metrics + Grafana dashboards

### 📊 Monitoring & Observability
- **Custom Metrics**: Chat requests, tokens, costs, RAG performance
- **Real-time Dashboards**: Grafana visualization
- **Health Checks**: Application and infrastructure monitoring
- **Performance Tracking**: Response times, error rates

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Kubernetes cluster (minikube/kind)
- Poetry (Python package manager)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd GenAI_Chatbot
poetry install
```

### 2. Environment Configuration
Create a `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Local Development
```bash
# Run locally
poetry run python run.py

# Or with Docker
./docker-run.ps1
```

### 4. Kubernetes Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Access the application
# Add to hosts file: 127.0.0.1 genai-chatbot.local
# Then visit: http://genai-chatbot.local
```

## 📋 API Endpoints

### Core Endpoints
- `GET /` - Application info
- `GET /health` - Health check
- `GET /docs` - API documentation
- `POST /chat` - Main chat endpoint

### RAG Endpoints
- `POST /upload-document` - Upload documents
- `GET /knowledge-base/stats` - KB statistics
- `DELETE /knowledge-base/clear` - Clear KB
- `POST /knowledge-base/initialize` - Initialize KB

### Monitoring Endpoints
- `GET /metrics` - Prometheus metrics
- `GET /intents/info` - Intent classification info

## 🐳 Docker

### Build Image
```bash
docker build -t genai-chatbot:latest .
```

### Run Container
```bash
docker run -d --name genai-chatbot -p 8000:8000 --env-file .env \
  -v ${PWD}/data:/app/data -v ${PWD}/chroma_db:/app/chroma_db \
  genai-chatbot:latest
```

## ☸️ Kubernetes

### Deploy All Components
```bash
kubectl apply -f k8s/
```

### Access URLs
- **Application**: `http://genai-chatbot.local`
- **Grafana**: `http://localhost:3000` (admin/admin)
- **Prometheus**: `http://localhost:9090`
- **Jenkins**: `http://localhost:8080` (admin/admin123)

## 🔄 CI/CD Pipeline

### Jenkins Pipeline
The `Jenkinsfile` includes:
- Code checkout
- Dependency installation
- Testing
- Code quality checks
- Docker build
- Kubernetes deployment
- Health checks

### GitHub Actions
The `.github/workflows/ci-cd.yml` provides:
- Automated testing
- Code quality checks
- Docker image building
- Deployment automation

## 📊 Monitoring

### Custom Metrics
- `genai_chatbot_chat_requests_total` - Total chat requests
- `genai_chatbot_tokens_used_total` - Token consumption
- `genai_chatbot_cost_total` - Cost tracking
- `genai_chatbot_rag_requests_total` - RAG performance
- `genai_chatbot_intent_classifications_total` - Intent analysis

### Grafana Dashboards
- Real-time chat metrics
- Token usage and costs
- RAG performance
- System health monitoring

## 🧪 Testing

### Run Tests
```bash
poetry run pytest tests/ -v
```

### API Testing
```bash
python test_api.py
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_MODEL` - Model name (default: gpt-4)
- `OPENAI_TEMPERATURE` - Response creativity (default: 0.7)
- `OPENAI_MAX_TOKENS` - Max response length (default: 1000)

### Kubernetes Config
- ConfigMaps for application settings
- Secrets for sensitive data
- Persistent volumes for data storage

## 📈 Scaling

### Horizontal Pod Autoscaler
```bash
kubectl apply -f k8s/horizontal-pod-autoscaler.yaml
```

### Load Balancing
- Kubernetes service load balancing
- Ingress controller routing
- Multiple pod replicas

## 🛡️ Security

### Best Practices
- Environment variables for secrets
- Kubernetes secrets management
- Container security scanning
- Network policies (configurable)

## 📝 Development

### Project Structure
```
GenAI_Chatbot/
├── app/                    # Main application
│   ├── chains/            # LangChain pipelines
│   ├── intents/           # Intent classification
│   ├── retriever/         # RAG components
│   └── utils/             # Utilities
├── k8s/                   # Kubernetes manifests
├── tests/                 # Test suite
├── data/                  # Sample documents
└── docs/                  # Documentation
```

### Adding Features
1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Create pull request

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Create GitHub issue
- Check documentation
- Review logs and metrics

---

**Built with ❤️ using modern DevOps practices** 