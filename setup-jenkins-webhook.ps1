# Setup Jenkins Webhook with ngrok
Write-Host "Setting up Jenkins webhook with ngrok..." -ForegroundColor Green

Write-Host ""
Write-Host "Step 1: Install ngrok (if not already installed)" -ForegroundColor Yellow
Write-Host "Download from: https://ngrok.com/download" -ForegroundColor White
Write-Host "Or use: winget install ngrok" -ForegroundColor White

Write-Host ""
Write-Host "Step 2: Expose Jenkins with ngrok" -ForegroundColor Yellow
Write-Host "Run this command in a new terminal:" -ForegroundColor White
Write-Host "ngrok http 8080" -ForegroundColor Cyan

Write-Host ""
Write-Host "Step 3: Get the ngrok URL" -ForegroundColor Yellow
Write-Host "1. Go to: http://localhost:4040" -ForegroundColor White
Write-Host "2. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)" -ForegroundColor White

Write-Host ""
Write-Host "Step 4: Update GitHub Webhook" -ForegroundColor Yellow
Write-Host "1. Go to: https://github.com/Krish3na/genai-chatbot/settings/hooks" -ForegroundColor White
Write-Host "2. Click 'Edit' on the existing webhook" -ForegroundColor White
Write-Host "3. Update Payload URL to: https://YOUR_NGROK_URL/jenkins/github-webhook/" -ForegroundColor White
Write-Host "4. Click 'Update webhook'" -ForegroundColor White

Write-Host ""
Write-Host "Step 5: Test the webhook" -ForegroundColor Yellow
Write-Host "1. Make a small change to any file" -ForegroundColor White
Write-Host "2. Commit and push to GitHub" -ForegroundColor White
Write-Host "3. Check Jenkins to see if build starts automatically" -ForegroundColor White

Write-Host ""
Write-Host "Alternative: Use GitHub Actions for cloud-based CI/CD" -ForegroundColor Yellow
Write-Host "This is actually recommended for production!" -ForegroundColor Cyan 