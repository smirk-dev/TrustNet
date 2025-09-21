"""
Python Backend Installation and Setup Script
Run this to install dependencies and configure the development environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main setup process."""
    print("🚀 TrustNet Python Backend Setup")
    print("=" * 60)
    
    # Check if we're in the correct directory
    current_dir = Path.cwd()
    if not (current_dir / "services" / "api-python").exists():
        print("❌ Please run this script from the TrustNet root directory")
        sys.exit(1)
    
    # Change to api-python directory
    api_python_dir = current_dir / "services" / "api-python"
    os.chdir(api_python_dir)
    print(f"📂 Changed to directory: {api_python_dir}")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major != 3 or python_version.minor < 8:
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your internet connection and try again.")
        return False
    
    # Set up environment variables (create .env file)
    env_content = """# TrustNet Environment Configuration
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
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file with default configuration")
        print("📝 Please update .env file with your actual configuration values")
    else:
        print("ℹ️  .env file already exists")
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print("✅ Created logs directory")
    
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update the .env file with your configuration")
    print("2. Set up Google Cloud credentials (if using real GCP services)")
    print("3. Start the development server:")
    print("   cd services/api-python")
    print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n4. API Documentation will be available at:")
    print("   http://localhost:8000/docs (Swagger UI)")
    print("   http://localhost:8000/redoc (ReDoc)")
    print("\n5. Health check:")
    print("   http://localhost:8000/health")

if __name__ == "__main__":
    main()