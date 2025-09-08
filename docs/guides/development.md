# TrustNet Development Guide

## Local Development Setup

### Prerequisites

- Node.js 18+ 
- Docker and Docker Compose
- Google Cloud SDK (`gcloud`)
- Terraform 1.0+

### Quick Start

1. **Clone and configure:**
   ```bash
   git clone https://github.com/smirk-dev/TrustNet.git
   cd TrustNet
   cp .env.example .env.local
   ```

2. **Set up Google Cloud:**
   ```bash
   gcloud auth application-default login
   gcloud config set project your-project-id
   ```

3. **Install dependencies:**
   ```bash
   cd services/api
   npm install
   cd ../workers  
   npm install
   ```

4. **Start local services:**
   ```bash
   docker-compose up -d  # Starts local Firestore emulator
   npm run dev           # Starts API server
   ```

### Environment Variables

Create `.env.local` with:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# API Keys (get from Google Cloud Console)
FACT_CHECK_API_KEY=your-fact-check-api-key
PERSPECTIVE_API_KEY=your-perspective-api-key

# Local development
NODE_ENV=development
LOG_LEVEL=debug
PORT=8080

# Firestore Emulator (for local development)
FIRESTORE_EMULATOR_HOST=localhost:8080
```

## Testing

```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# Load testing
npm run test:load

# Test specific language
npm run test:lang -- hindi
```

## Code Structure

```
services/api/src/
├── index.js           # Express app entry point
├── middleware/        # Request validation, auth, rate limiting
├── routes/           # API route handlers  
├── services/         # Business logic
└── utils/            # Shared utilities

services/workers/
├── analysis-worker.js # Main analysis pipeline
├── evidence-worker.js # Evidence retrieval
└── utils/            # Shared worker utilities

integrations/
├── factcheck/        # Fact Check Tools API client
├── webrisk/         # Web Risk API client
├── perspective/     # Perspective API client
└── dlp/             # DLP API client
```

## API Usage Examples

### Analyze Content

```bash
curl -X POST http://localhost:8080/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "वैक्सीन में माइक्रोचिप्स होती हैं",
    "language": "hi",
    "priority": "high"
  }'
```

### Check Results

```bash
curl http://localhost:8080/v1/claims/550e8400-e29b-41d4-a716-446655440000
```

### Submit Feedback

```bash
curl -X POST http://localhost:8080/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "verdict_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_rating": "accurate", 
    "feedback_type": "rating_disagreement",
    "comments": "The explanation was clear and well-sourced"
  }'
```

## Deployment

### Development Environment

```bash
./scripts/deploy/deploy-services.sh dev asia-south1
```

### Production Deployment

```bash
# Deploy infrastructure
cd infra/terraform
terraform workspace select prod
terraform apply

# Deploy application
gcloud builds submit --config=infra/ci/cloudbuild.yaml
```

## Monitoring and Debugging

### View Logs

```bash
# API service logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=trustnet-api"

# Worker logs  
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=trustnet-worker"

# Pub/Sub metrics
gcloud logging read "resource.type=pubsub_topic"
```

### Health Checks

```bash
# API health
curl https://trustnet-api-xyz.a.run.app/health

# Check Firestore connection
gcloud firestore collections list --database=trustnet-dev

# Check Pub/Sub topics
gcloud pubsub topics list
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required APIs are enabled in Google Cloud Console
2. **Permission Denied**: Check service account IAM roles
3. **Quota Exceeded**: Monitor API quotas in Cloud Console
4. **High Latency**: Check Vertex AI region and model deployment

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug

# Run with debugging
node --inspect src/index.js

# Profile performance  
node --prof src/index.js
```

## Contributing

1. Create feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass: `npm test`
4. Run linter: `npm run lint`
5. Submit pull request with description

### Code Standards

- ESLint configuration in `.eslintrc.js`
- Prettier for code formatting
- JSDoc comments for public functions
- Error handling with proper logging
- Input validation using Joi schemas

## Security

### API Security

- Rate limiting: 100 requests/15 minutes per IP
- Input sanitization and validation
- CORS configuration for allowed origins
- Helmet.js for security headers

### Data Protection

- PII redaction using DLP API
- Secure credential storage in Secret Manager
- Encrypted data at rest in Firestore
- Audit logging for sensitive operations

## Performance Optimization

### Caching Strategy

- Redis for frequent evidence lookups
- CDN for static assets
- Firestore query optimization
- Response compression

### Cost Optimization

- Auto-scaling based on traffic
- Batch processing for lower priority requests
- Efficient Pub/Sub message handling
- Resource monitoring and alerting
