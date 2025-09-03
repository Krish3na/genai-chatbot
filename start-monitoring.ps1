# Start monitoring services port forwarding
Write-Host "Starting port forwarding for monitoring services..." -ForegroundColor Green

# Stop any existing port forwarding
Get-Process | Where-Object { $_.ProcessName -eq "kubectl" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Start port forwarding for all services
Write-Host "Starting port forwarding..." -ForegroundColor Yellow

# Chatbot API
Start-Process kubectl -ArgumentList "port-forward", "-n", "genai-chatbot", "svc/genai-chatbot-service", "8080:80" -WindowStyle Hidden

# Prometheus
Start-Process kubectl -ArgumentList "port-forward", "-n", "genai-chatbot", "svc/prometheus-service", "9090:9090" -WindowStyle Hidden

# Grafana
Start-Process kubectl -ArgumentList "port-forward", "-n", "genai-chatbot", "svc/grafana-service", "3000:3000" -WindowStyle Hidden

Start-Sleep -Seconds 3

Write-Host "Port forwarding started!" -ForegroundColor Green
Write-Host "`nAccess URLs:" -ForegroundColor Cyan
Write-Host "Chatbot API: http://localhost:8080" -ForegroundColor White
Write-Host "Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "`nTo stop port forwarding, run: Get-Process kubectl | Stop-Process -Force" -ForegroundColor Yellow
