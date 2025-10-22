FROM python:3.11-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy frontend files (from current directory)
COPY . /app/frontend/

# Set working directory to frontend
WORKDIR /app/frontend

# Expose port
EXPOSE 3001

# Start Python HTTP server
CMD ["python", "-m", "http.server", "3001"]
