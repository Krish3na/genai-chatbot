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

        stage('Validate Code') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'ls -la'
                        sh 'echo "Python files found:"'
                        sh 'find . -name "*.py" | head -10'
                        sh 'echo "Kubernetes files found:"'
                        sh 'find . -name "*.yaml" | head -10'
                    } else {
                        bat 'dir'
                        bat 'echo Python files found:'
                        bat 'dir /s *.py'
                        bat 'echo Kubernetes files found:'
                        bat 'dir /s *.yaml'
                    }
                }
                echo 'Code validation completed'
            }
        }

        stage('Test Application Structure') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "Checking application structure..."
                            if [ -f "app/main.py" ]; then
                                echo "✅ FastAPI app found"
                            else
                                echo "❌ FastAPI app not found"
                                exit 1
                            fi
                            
                            if [ -f "Dockerfile" ]; then
                                echo "✅ Dockerfile found"
                            else
                                echo "❌ Dockerfile not found"
                                exit 1
                            fi
                            
                            if [ -d "k8s" ]; then
                                echo "✅ Kubernetes manifests found"
                            else
                                echo "❌ Kubernetes manifests not found"
                                exit 1
                            fi
                            
                            echo "✅ Application structure is valid"
                        '''
                    } else {
                        bat '''
                            echo Checking application structure...
                            if exist app\\main.py (
                                echo ✅ FastAPI app found
                            ) else (
                                echo ❌ FastAPI app not found
                                exit /b 1
                            )
                            
                            if exist Dockerfile (
                                echo ✅ Dockerfile found
                            ) else (
                                echo ❌ Dockerfile not found
                                exit /b 1
                            )
                            
                            if exist k8s (
                                echo ✅ Kubernetes manifests found
                            ) else (
                                echo ❌ Kubernetes manifests not found
                                exit /b 1
                            )
                            
                            echo ✅ Application structure is valid
                        '''
                    }
                }
                echo 'Application structure validation completed'
            }
        }

        stage('Simulate Build') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "Simulating Docker build..."
                            echo "Would build: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                            echo "Build context: $(pwd)"
                            echo "Dockerfile: $(pwd)/Dockerfile"
                            
                            # Check if Dockerfile is valid
                            if [ -f "Dockerfile" ]; then
                                echo "✅ Dockerfile exists and is readable"
                                head -5 Dockerfile
                            else
                                echo "❌ Dockerfile not found"
                                exit 1
                            fi
                        '''
                    } else {
                        bat '''
                            echo Simulating Docker build...
                            echo Would build: %DOCKER_IMAGE%:%DOCKER_TAG%
                            echo Build context: %cd%
                            echo Dockerfile: %cd%\\Dockerfile
                            
                            if exist Dockerfile (
                                echo ✅ Dockerfile exists and is readable
                                type Dockerfile | findstr /n . | findstr "^1:" | findstr /v ":" | findstr /v "^$"
                            ) else (
                                echo ❌ Dockerfile not found
                                exit /b 1
                            )
                        '''
                    }
                }
                echo 'Build simulation completed'
            }
        }

        stage('Simulate Deployment') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "Simulating Kubernetes deployment..."
                            echo "Would deploy to namespace: ${KUBERNETES_NAMESPACE}"
                            echo "Would update image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                            
                            # Check if k8s manifests exist
                            if [ -d "k8s" ]; then
                                echo "✅ Kubernetes manifests directory found"
                                ls -la k8s/
                            else
                                echo "❌ Kubernetes manifests directory not found"
                                exit 1
                            fi
                        '''
                    } else {
                        bat '''
                            echo Simulating Kubernetes deployment...
                            echo Would deploy to namespace: %KUBERNETES_NAMESPACE%
                            echo Would update image: %DOCKER_IMAGE%:%DOCKER_TAG%
                            
                            if exist k8s (
                                echo ✅ Kubernetes manifests directory found
                                dir k8s
                            ) else (
                                echo ❌ Kubernetes manifests directory not found
                                exit /b 1
                            )
                        '''
                    }
                }
                echo 'Deployment simulation completed'
            }
        }

        stage('Health Check Simulation') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "Simulating health check..."
                            echo "Would check: http://genai-chatbot.local/health"
                            echo "Would check: http://localhost:3000 (Grafana)"
                            echo "Would check: http://localhost:9090 (Prometheus)"
                            
                            # Simulate a successful health check
                            echo "✅ Health check simulation passed"
                        '''
                    } else {
                        bat '''
                            echo Simulating health check...
                            echo Would check: http://genai-chatbot.local/health
                            echo Would check: http://localhost:3000 (Grafana)
                            echo Would check: http://localhost:9090 (Prometheus)
                            
                            echo ✅ Health check simulation passed
                        '''
                    }
                }
                echo 'Health check simulation completed'
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed'
        }
        success {
            echo '🎉 Pipeline succeeded!'
            echo '✅ Code checkout completed'
            echo '✅ Application structure validated'
            echo '✅ Build simulation completed'
            echo '✅ Deployment simulation completed'
            echo '✅ Health check simulation completed'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
} 