FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install MLflow and dependencies
RUN pip install mlflow==2.8.1

# Create directory for MLflow data
RUN mkdir -p /mlflow_data/artifacts

# Set working directory
WORKDIR /mlflow_data

# Create startup script with file-based backend
RUN echo '#!/bin/bash\n\
# Create directories\n\
mkdir -p /mlflow_data/artifacts\n\
\n\
# Start MLflow server with file-based backend (simpler than SQLite)\n\
exec mlflow server --backend-store-uri file:///mlflow_data --default-artifact-root /mlflow_data/artifacts --host 0.0.0.0 --port 5000' > /start-mlflow.sh && \
    chmod +x /start-mlflow.sh

# Expose MLflow port
EXPOSE 5000

# Start MLflow server with initialization
CMD ["/start-mlflow.sh"]
