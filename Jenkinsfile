pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'genai-chatbot'
        DOCKER_TAG = 'latest'
        KUBERNETES_NAMESPACE = 'genai-chatbot'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checkout completed'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'poetry install --only main'
                    } else {
                        bat 'poetry install --only main'
                    }
                }
                echo 'Dependencies installed'
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'poetry run pytest tests/ -v'
                    } else {
                        bat 'poetry run pytest tests/ -v'
                    }
                }
                echo 'Tests completed'
            }
        }
        
        stage('Code Quality') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'poetry run black --check app/'
                        sh 'poetry run isort --check-only app/'
                        sh 'poetry run mypy app/'
                    } else {
                        bat 'poetry run black --check app/'
                        bat 'poetry run isort --check-only app/'
                        bat 'poetry run mypy app/'
                    }
                }
                echo 'Code quality checks passed'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    if (isUnix()) {
                        sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    } else {
                        bat "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    }
                }
                echo 'Docker image built successfully'
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    if (isUnix()) {
                        sh "kubectl set image deployment/genai-chatbot genai-chatbot=${DOCKER_IMAGE}:${DOCKER_TAG} -n ${KUBERNETES_NAMESPACE}"
                        sh "kubectl rollout status deployment/genai-chatbot -n ${KUBERNETES_NAMESPACE}"
                    } else {
                        bat "kubectl set image deployment/genai-chatbot genai-chatbot=${DOCKER_IMAGE}:${DOCKER_TAG} -n ${KUBERNETES_NAMESPACE}"
                        bat "kubectl rollout status deployment/genai-chatbot -n ${KUBERNETES_NAMESPACE}"
                    }
                }
                echo 'Deployment completed successfully'
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'sleep 30'
                        sh 'curl -f http://genai-chatbot.local/health || exit 1'
                    } else {
                        bat 'timeout /t 30'
                        bat 'curl -f http://genai-chatbot.local/health || exit 1'
                    }
                }
                echo 'Health check passed'
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
} 