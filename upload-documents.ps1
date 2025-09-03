# Upload Documents Script for GenAI Chatbot
# Uploads available documents to enable RAG functionality
# =====================================================================

Write-Host "Uploading Documents to Knowledge Base for RAG Testing..." -ForegroundColor Green

# Configuration
$baseUrl = "http://localhost:8080"
$headers = @{"Content-Type" = "application/json"}

Write-Host "`n=== 1. Check Available Documents ===" -ForegroundColor Yellow

# Check what documents are available
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/documents/available" -Method GET -Headers $headers -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        $docs = $response.Content | ConvertFrom-Json
        Write-Host "✅ Available Documents:" -ForegroundColor Green
        Write-Host "   Total Count: $($docs.total_count)" -ForegroundColor White
        
        if ($docs.documents.Count -gt 0) {
            Write-Host "   Document Names:" -ForegroundColor White
            foreach ($doc in $docs.documents) {
                Write-Host "     - $($doc.name)" -ForegroundColor Gray
            }
        } else {
            Write-Host "   No documents found in data directory" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "❌ Could not check available documents: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== 2. Upload Sample Knowledge Document ===" -ForegroundColor Yellow

# Upload the sample knowledge document
try {
    $uploadBody = @{
        initialize_kb = $true
    }
    
    $response = Invoke-WebRequest -Uri "$baseUrl/knowledge-base/initialize" -Method POST -Headers $headers -Body ($uploadBody | ConvertTo-Json) -TimeoutSec 30
    
    if ($response.StatusCode -eq 200) {
        $result = $response.Content | ConvertFrom-Json
        Write-Host "✅ Knowledge Base Initialization Result:" -ForegroundColor Green
        Write-Host "   Success: $($result.success)" -ForegroundColor White
        Write-Host "   Message: $($result.message)" -ForegroundColor White
        Write-Host "   Documents Added: $($result.documents_added)" -ForegroundColor White
        
        if ($result.error) {
            Write-Host "   Error: $($result.error)" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "❌ Could not initialize knowledge base: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== 3. Check Knowledge Base Stats ===" -ForegroundColor Yellow

# Check knowledge base stats after upload
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/knowledge-base/stats" -Method GET -Headers $headers -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        $stats = $response.Content | ConvertFrom-Json
        Write-Host "✅ Knowledge Base Stats:" -ForegroundColor Green
        Write-Host "   Total Documents: $($stats.total_documents)" -ForegroundColor White
        Write-Host "   Persist Directory: $($stats.persist_directory)" -ForegroundColor White
        Write-Host "   Collection Name: $($stats.collection_name)" -ForegroundColor White
        
        if ($stats.total_documents -gt 0) {
            Write-Host "   Status: Knowledge base is ready for RAG testing!" -ForegroundColor Green
        } else {
            Write-Host "   Status: Knowledge base is empty" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "❌ Could not check knowledge base stats: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== 4. Test RAG Functionality ===" -ForegroundColor Yellow

# Test RAG functionality with a knowledge base query
try {
    $testBody = @{
        message = "What is the GenAI Chatbot project about?"
        user_id = "rag_test_user"
        use_rag = $true
    }
    
    $response = Invoke-WebRequest -Uri "$baseUrl/chat" -Method POST -Headers $headers -Body ($testBody | ConvertTo-Json) -TimeoutSec 30
    
    if ($response.StatusCode -eq 200) {
        $result = $response.Content | ConvertFrom-Json
        Write-Host "✅ RAG Test Result:" -ForegroundColor Green
        Write-Host "   Response Type: $($result.response_type)" -ForegroundColor White
        Write-Host "   Intent: $($result.intent)" -ForegroundColor White
        Write-Host "   Tokens Used: $($result.tokens_used)" -ForegroundColor White
        Write-Host "   Cost: $($result.cost)" -ForegroundColor White
        Write-Host "   Sources Used: $($result.sources_used)" -ForegroundColor White
        
        if ($result.response_type -eq "rag") {
            Write-Host "   Status: RAG is working correctly!" -ForegroundColor Green
        } else {
            Write-Host "   Status: RAG is not being used (falling back to direct)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "❌ Could not test RAG functionality: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== 5. Summary ===" -ForegroundColor Magenta

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "• If knowledge base is empty, add documents to the data/ directory" -ForegroundColor White
Write-Host "• Run the comprehensive test again to see RAG vs Direct usage" -ForegroundColor White
Write-Host "• Check the dashboard for RAG vs Direct differentiation" -ForegroundColor White

Write-Host "`nCheck your dashboard at:" -ForegroundColor Cyan
Write-Host "• Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "• Prometheus: http://localhost:9090" -ForegroundColor White
