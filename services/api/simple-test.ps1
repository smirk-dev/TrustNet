# Simple API Test
$testUrl = "http://localhost:8080/test"
Write-Host "`n🧪 Testing simple server..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri $testUrl -Method GET
    Write-Host "✅ Test successful!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
}
