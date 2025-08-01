# Setup Automatic Builds on GitHub Changes
Write-Host "Setting up automatic builds on GitHub changes..." -ForegroundColor Green

Write-Host ""
Write-Host "Step 1: Apply Jenkins Webhook Configuration" -ForegroundColor Yellow
kubectl apply -f k8s/jenkins-webhook-configmap.yaml
kubectl apply -f k8s/jenkins-deployment.yaml

Write-Host ""
Write-Host "Step 2: Wait for Jenkins to restart..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "Step 3: Configure Jenkins Pipeline for Automatic Builds" -ForegroundColor Yellow
Write-Host "1. Go to Jenkins: http://localhost:8080/jenkins" -ForegroundColor White
Write-Host "2. Login with: admin / admin123" -ForegroundColor White
Write-Host "3. Click on 'genai-chatbot-pipeline'" -ForegroundColor White
Write-Host "4. Click 'Configure'" -ForegroundColor White
Write-Host "5. Scroll to 'Build Triggers' section" -ForegroundColor White
Write-Host "6. Check 'GitHub hook trigger for GITScm polling'" -ForegroundColor White
Write-Host "7. Click 'Save'" -ForegroundColor White

Write-Host ""
Write-Host "Step 4: Set up GitHub Webhook" -ForegroundColor Yellow
Write-Host "1. Go to your GitHub repository: https://github.com/Krish3na/genai-chatbot" -ForegroundColor White
Write-Host "2. Go to Settings > Webhooks" -ForegroundColor White
Write-Host "3. Click 'Add webhook'" -ForegroundColor White
Write-Host "4. Payload URL: http://jenkins.genai-chatbot.local/jenkins/github-webhook/" -ForegroundColor White
Write-Host "5. Content type: application/json" -ForegroundColor White
Write-Host "6. Events: Just the push event" -ForegroundColor White
Write-Host "7. Click 'Add webhook'" -ForegroundColor White

Write-Host ""
Write-Host "Step 5: Test Automatic Build" -ForegroundColor Yellow
Write-Host "1. Make a small change to any file in your repository" -ForegroundColor White
Write-Host "2. Commit and push to GitHub" -ForegroundColor White
Write-Host "3. Check Jenkins to see if build starts automatically" -ForegroundColor White

Write-Host ""
Write-Host "Automatic build setup completed!" -ForegroundColor Green
Write-Host "Now every push to GitHub will automatically trigger a Jenkins build!" -ForegroundColor Cyan 