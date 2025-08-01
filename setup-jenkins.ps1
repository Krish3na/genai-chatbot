# Jenkins CI/CD Setup Script for GenAI Chatbot
Write-Host "Setting up Jenkins CI/CD Pipeline..." -ForegroundColor Green

Write-Host ""
Write-Host "Step 1: Access Jenkins" -ForegroundColor Yellow
Write-Host "1. Open your browser and go to: http://localhost:8080" -ForegroundColor White
Write-Host "2. Login with: admin / admin123" -ForegroundColor White
Write-Host "3. Complete the initial setup if prompted" -ForegroundColor White

Write-Host ""
Write-Host "Step 2: Create New Pipeline" -ForegroundColor Yellow
Write-Host "1. Click 'New Item'" -ForegroundColor White
Write-Host "2. Enter name: 'genai-chatbot-pipeline'" -ForegroundColor White
Write-Host "3. Select 'Pipeline'" -ForegroundColor White
Write-Host "4. Click 'OK'" -ForegroundColor White

Write-Host ""
Write-Host "Step 3: Configure Pipeline" -ForegroundColor Yellow
Write-Host "1. In the pipeline configuration:" -ForegroundColor White
Write-Host "   - Description: 'Production-grade GenAI Chatbot CI/CD Pipeline'" -ForegroundColor White
Write-Host "   - Pipeline Definition: 'Pipeline script from SCM'" -ForegroundColor White
Write-Host "   - SCM: 'Git'" -ForegroundColor White
Write-Host "   - Repository URL: 'https://github.com/YOUR_USERNAME/genai-chatbot.git'" -ForegroundColor White
Write-Host "   - Branch: '*/master'" -ForegroundColor White
Write-Host "   - Script Path: 'Jenkinsfile'" -ForegroundColor White

Write-Host ""
Write-Host "Step 4: Build Triggers" -ForegroundColor Yellow
Write-Host "1. Poll SCM: 'H/5 * * * *' (every 5 minutes)" -ForegroundColor White
Write-Host "2. Or use GitHub webhooks for automatic builds" -ForegroundColor White

Write-Host ""
Write-Host "Step 5: Save and Build" -ForegroundColor Yellow
Write-Host "1. Click 'Save'" -ForegroundColor White
Write-Host "2. Click 'Build Now'" -ForegroundColor White
Write-Host "3. Monitor the build in the console output" -ForegroundColor White

Write-Host ""
Write-Host "Step 6: Verify Deployment" -ForegroundColor Yellow
Write-Host "After successful build, verify:" -ForegroundColor White
Write-Host "1. Application: http://genai-chatbot.local" -ForegroundColor White
Write-Host "2. Health check: http://genai-chatbot.local/health" -ForegroundColor White
Write-Host "3. Monitoring: http://localhost:3000 (Grafana)" -ForegroundColor White

Write-Host ""
Write-Host "Jenkins Pipeline Features:" -ForegroundColor Cyan
Write-Host "- Automated testing with pytest" -ForegroundColor White
Write-Host "- Code quality checks (black, isort, mypy)" -ForegroundColor White
Write-Host "- Docker image building" -ForegroundColor White
Write-Host "- Kubernetes deployment" -ForegroundColor White
Write-Host "- Health checks and monitoring" -ForegroundColor White

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host "1. Push your code to GitHub" -ForegroundColor White
Write-Host "2. Configure Jenkins pipeline as above" -ForegroundColor White
Write-Host "3. Set up GitHub webhooks for automatic builds" -ForegroundColor White
Write-Host "4. Monitor builds and deployments" -ForegroundColor White 