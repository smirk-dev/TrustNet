# TrustNet Python Backend Setup Script for Windows
# PowerShell script to set up the development environment

Write-Host "🚀 TrustNet Python Backend Setup for Windows" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

# Check if we're in the correct directory
$currentPath = Get-Location
$expectedPath = Join-Path $currentPath "services\api-python"

if (-not (Test-Path $expectedPath)) {
    Write-Host "❌ Please run this script from the TrustNet root directory" -ForegroundColor Red
    exit 1
}

# Change to api-python directory
Set-Location $expectedPath
Write-Host "📂 Changed to directory: $expectedPath" -ForegroundColor Cyan

# Check Python installation
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Install dependencies
Write-Host "`n🔧 Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Yellow

try {
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies. Please check your internet connection." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
$envFile = ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "`n📝 Creating .env configuration file..." -ForegroundColor Yellow
    
    $envContent = @"
# TrustNet Environment Configuration
# Google Cloud Platform
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Database Configuration
FIRESTORE_COLLECTION_PREFIX=trustnet
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# API Configuration
API_HOST=localhost
API_PORT=8000
API_RELOAD=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Development flags
DEVELOPMENT_MODE=true
USE_MOCK_SERVICES=true
"@
    
    $envContent | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host "✅ Created .env file with default configuration" -ForegroundColor Green
} else {
    Write-Host "ℹ️  .env file already exists" -ForegroundColor Blue
}

# Create logs directory
$logsDir = "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
    Write-Host "✅ Created logs directory" -ForegroundColor Green
}

# Final instructions
Write-Host "`n" + ("=" * 60) -ForegroundColor Green
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Update the .env file with your configuration" -ForegroundColor White
Write-Host "2. Set up Google Cloud credentials (if using real GCP services)" -ForegroundColor White
Write-Host "3. Start the development server:" -ForegroundColor White
Write-Host "   cd services\api-python" -ForegroundColor Cyan
Write-Host "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Cyan

Write-Host "`n4. API Documentation will be available at:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs (Swagger UI)" -ForegroundColor Cyan
Write-Host "   http://localhost:8000/redoc (ReDoc)" -ForegroundColor Cyan

Write-Host "`n5. Health check:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/health" -ForegroundColor Cyan

Write-Host "`n📚 For more information, see:" -ForegroundColor Yellow
Write-Host "   - docs/guides/development.md" -ForegroundColor Cyan
Write-Host "   - README.md" -ForegroundColor Cyan

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null