# Test TrustNet API
Write-Host "🧪 Testing TrustNet API..." -ForegroundColor Green

# Test 1: Health Check
Write-Host "`n1. Testing Health Check..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:3000/health" -Method Get -TimeoutSec 5
    Write-Host "✅ Health Check SUCCESS" -ForegroundColor Green
    Write-Host "Status: $($healthResponse.status)" -ForegroundColor Cyan
    Write-Host "Version: $($healthResponse.version)" -ForegroundColor Cyan
    $healthResponse | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Health Check FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: API Info
Write-Host "`n2. Testing API Info..." -ForegroundColor Yellow
try {
    $infoResponse = Invoke-RestMethod -Uri "http://localhost:3000/" -Method Get -TimeoutSec 5
    Write-Host "✅ API Info SUCCESS" -ForegroundColor Green
    Write-Host "Name: $($infoResponse.name)" -ForegroundColor Cyan
    $infoResponse | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ API Info FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Verification Request
Write-Host "`n3. Testing Verification Request..." -ForegroundColor Yellow
try {
    $verifyPayload = @{
        text = "This is a test claim about health misinformation"
        language = "en"
        urls = @("https://example.com")
    } | ConvertTo-Json

    $verifyResponse = Invoke-RestMethod -Uri "http://localhost:3000/v1/verify" -Method Post -Body $verifyPayload -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ Verification Request SUCCESS" -ForegroundColor Green
    Write-Host "Verification ID: $($verifyResponse.verification_id)" -ForegroundColor Cyan
    Write-Host "Status: $($verifyResponse.status)" -ForegroundColor Cyan
    $verifyResponse | ConvertTo-Json -Depth 3

    # Test 4: Get Verification Results
    Write-Host "`n4. Testing Verification Results..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2  # Wait a moment
    $resultsResponse = Invoke-RestMethod -Uri "http://localhost:3000/v1/verify/$($verifyResponse.verification_id)" -Method Get -TimeoutSec 5
    Write-Host "✅ Verification Results SUCCESS" -ForegroundColor Green
    Write-Host "Rating: $($resultsResponse.analysis_result.rating)" -ForegroundColor Cyan
    Write-Host "Credibility Score: $($resultsResponse.analysis_result.credibility_score)" -ForegroundColor Cyan
    $resultsResponse | ConvertTo-Json -Depth 4

} catch {
    Write-Host "❌ Verification FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Feedback Submission
Write-Host "`n5. Testing Feedback Submission..." -ForegroundColor Yellow
try {
    $feedbackPayload = @{
        verdict_id = "test-verdict-123"
        rating = 4
        comments = "This is a test feedback"
    } | ConvertTo-Json

    $feedbackResponse = Invoke-RestMethod -Uri "http://localhost:3000/v1/feedback" -Method Post -Body $feedbackPayload -ContentType "application/json" -TimeoutSec 5
    Write-Host "✅ Feedback Submission SUCCESS" -ForegroundColor Green
    Write-Host "Feedback ID: $($feedbackResponse.feedback_id)" -ForegroundColor Cyan
    $feedbackResponse | ConvertTo-Json -Depth 3

} catch {
    Write-Host "❌ Feedback Submission FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🏁 API Testing Complete!" -ForegroundColor Green
