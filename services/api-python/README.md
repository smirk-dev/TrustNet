# TrustNet Python Backend

🚀 **AI-powered misinformation detection service** built with FastAPI, designed for seamless frontend integration and production deployment.

## 🌟 Features

### 🔍 Core Capabilities
- **Instant Content Verification** - Submit text/URL for AI-powered fact-checking
- **Quarantine Room** - Human-AI collaboration for uncertain content
- **Educational Feed** - Proactive learning with real-world examples
- **Manipulation Detection** - Identify emotional manipulation and logical fallacies
- **Community Feedback** - Continuous improvement through user input

### 🛠 Technical Stack
- **FastAPI** - Modern, fast web framework with automatic OpenAPI documentation
- **Pydantic** - Data validation using Python type annotations
- **Google Cloud Platform** - Vertex AI, Firestore, Pub/Sub, DLP, Web Risk
- **Redis** - High-performance caching layer
- **Uvicorn** - Lightning-fast ASGI server

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### 1. Automated Setup (Recommended)

**Windows (PowerShell):**
```powershell
cd services\api-python
.\setup.ps1
```

**Linux/Mac:**
```bash
cd services/api-python
python setup.py
```

### 2. Manual Setup

```bash
# Navigate to Python backend directory
cd services/api-python

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit configuration (optional for development)
nano .env
```

### 3. Start Development Server

```bash
# Start with hot reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main module
python main.py
```

### 4. Verify Installation

Open your browser:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Info**: http://localhost:8000/

## 📚 API Documentation

### 🔗 Core Endpoints

#### Content Verification
```http
POST /v1/verify
Content-Type: application/json

{
  "content": "Your content to verify",
  "content_type": "text",
  "priority": "normal"
}
```

#### Get Verification Results
```http
GET /v1/verify/{verification_id}
```

#### Educational Feed
```http
GET /v1/feed?language=en&limit=10&category=health
```

#### Content Analysis
```http
POST /v1/analysis/analyze
Content-Type: application/json

{
  "content": "Content to analyze",
  "analysis_type": "comprehensive"
}
```

#### Submit Feedback
```http
POST /v1/feedback/submit
Content-Type: application/json

{
  "feedback_type": "verification_accuracy",
  "content": "Your feedback here",
  "rating": 4
}
```

### 📖 Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🏗 Architecture

### 📁 Project Structure
```
services/api-python/
├── app/
│   ├── api/v1/                 # API routes
│   │   └── endpoints/          # Individual endpoint modules
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Firestore operations
│   │   ├── cache.py           # Redis caching
│   │   ├── gcp.py             # Google Cloud integration
│   │   └── logging.py         # Structured logging
│   ├── models/                 # Data models
│   │   └── schemas.py         # Pydantic schemas
│   └── services/              # Business logic
│       ├── educational.py     # Educational content
│       ├── analysis.py        # Content analysis
│       ├── feedback.py        # Community feedback
│       └── community.py       # User engagement
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── setup.py                   # Setup script
└── setup.ps1                 # Windows setup script
```

### 🔄 Request Flow
1. **Client Request** → FastAPI Router
2. **Validation** → Pydantic Models
3. **Business Logic** → Service Layer
4. **Data Access** → Database/Cache
5. **External APIs** → Google Cloud Services
6. **Response** → JSON with proper status codes

## ⚙️ Configuration

### 🌍 Environment Variables

Create `.env` file:
```env
# Development
DEVELOPMENT_MODE=true
USE_MOCK_SERVICES=true
LOG_LEVEL=INFO

# API Configuration
API_HOST=localhost
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000"]

# Google Cloud (for production)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Database
FIRESTORE_COLLECTION_PREFIX=trustnet
REDIS_URL=redis://localhost:6379
```

### 🔧 Development vs Production

**Development Mode:**
- Mock Google Cloud services (no GCP account needed)
- Detailed logging and error messages
- Hot reload enabled
- API documentation available

**Production Mode:**
- Real Google Cloud services
- Optimized logging
- Security headers
- Rate limiting enabled

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest app/tests/unit/

# Integration tests  
pytest app/tests/integration/

# All tests with coverage
pytest --cov=app --cov-report=html
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Verify content
curl -X POST "http://localhost:8000/v1/verify" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test content", "content_type": "text"}'
```

## 🚀 Deployment

### 🐳 Docker (Recommended)
```bash
# Build image
docker build -t trustnet-api .

# Run container
docker run -p 8000:8000 trustnet-api
```

### ☁️ Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy trustnet-api \
  --image gcr.io/your-project/trustnet-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 🖥 Traditional Server
```bash
# Production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🔧 Development

### 🚀 Adding New Features

1. **Create endpoint**: Add new route in `app/api/v1/endpoints/`
2. **Add business logic**: Implement in `app/services/`
3. **Update models**: Add Pydantic schemas in `app/models/schemas.py`
4. **Include router**: Update `app/api/v1/__init__.py`

### 🎯 Best Practices

- **Async/await** for all I/O operations
- **Pydantic models** for request/response validation
- **Structured logging** with context information
- **Error handling** with proper HTTP status codes
- **Caching** for frequently accessed data

## 🤝 Frontend Integration

### 🔗 CORS Configuration
Frontend origins configured in `CORS_ORIGINS` environment variable.

### 📡 API Response Format
```json
{
  "status": "success",
  "data": { ... },
  "message": "Human-readable message",
  "request_id": "unique-identifier"
}
```

### 🚨 Error Response Format
```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 📊 Monitoring & Logging

### 📝 Structured Logging
- JSON format for production
- Contextual information (request_id, user_id)
- Different log levels (DEBUG, INFO, WARNING, ERROR)

### 📈 Health Monitoring
- `/health` endpoint for load balancer checks
- Metrics collection for performance monitoring
- Error rate tracking

## 🛡 Security

### 🔒 Security Features
- CORS protection for frontend integration
- Input validation with Pydantic
- SQL injection prevention (NoSQL database)
- Rate limiting (configurable)
- Security headers middleware

### 🔑 Authentication (Future)
Ready for integration with:
- OAuth 2.0 / OpenID Connect
- JWT tokens
- API key authentication

## 🆘 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure you're in the correct directory
cd services/api-python
# Reinstall dependencies
pip install -r requirements.txt
```

**Port Already in Use:**
```bash
# Change port in .env file
API_PORT=8001
# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

**Google Cloud Errors:**
```bash
# Use mock services for development
USE_MOCK_SERVICES=true
```

### 📞 Support

- Check logs in `logs/` directory
- Review API documentation at `/docs`
- Verify configuration in `.env` file

## 🎯 Roadmap

### ✅ Completed
- ✅ FastAPI backend architecture
- ✅ All 5 MVP endpoints implemented
- ✅ Google Cloud Platform integration
- ✅ Comprehensive data models
- ✅ Service layer architecture
- ✅ Development environment setup

### 🔄 In Progress
- 🔄 ML pipeline integration
- 🔄 Comprehensive testing suite
- 🔄 Docker deployment configuration

### 📋 Planned
- 📋 Authentication system
- 📋 Advanced analytics
- 📋 Real-time notifications
- 📋 Performance optimization

---

## 📄 License

See main project LICENSE file.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Built with ❤️ for combating misinformation in India** 🇮🇳