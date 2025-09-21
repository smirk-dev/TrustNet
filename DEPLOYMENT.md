# TrustNet Deployment Guide

This guide provides comprehensive instructions for deploying TrustNet, an AI-powered misinformation detection system, to Google Cloud Platform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Deployment](#quick-deployment)
- [Manual Deployment](#manual-deployment)
- [Environment Configuration](#environment-configuration)
- [Production Deployment](#production-deployment)
- [Local Development](#local-development)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [Rollback Procedures](#rollback-procedures)

## Prerequisites

### Required Tools

1. **Google Cloud SDK**

   ```bash
   # Install gcloud CLI
   # Download from: https://cloud.google.com/sdk/docs/install
   
   # Verify installation
   gcloud --version
   ```

2. **Terraform** (v1.0+)

   ```bash
   # Download from: https://terraform.io/downloads
   terraform --version
   ```

3. **Docker**

   ```bash
   # Download from: https://docker.com/get-started
   docker --version
   ```

4. **Node.js** (v18+)

   ```bash
   # Download from: https://nodejs.org
   node --version
   npm --version
   ```

### Google Cloud Setup

1. **Create or Select Project**

   ```bash
   # Create new project
   gcloud projects create trustnet-prod --name="TrustNet Production"
   
   # Or use existing project
   gcloud config set project your-project-id
   ```

2. **Enable Billing**

   ```bash
   # Link billing account (replace BILLING_ACCOUNT_ID)
   gcloud billing projects link trustnet-prod --billing-account=BILLING_ACCOUNT_ID
   ```

3. **Set Default Configuration**

   ```bash
   gcloud config set project trustnet-prod
   gcloud config set compute/region asia-south1
   gcloud auth application-default login
   ```

4. **Create Terraform State Bucket**

   ```bash
   gsutil mb gs://trustnet-terraform-state
   gsutil versioning set on gs://trustnet-terraform-state
   ```

## Quick Deployment

For rapid deployment using the automated script:

```bash
# Clone repository
git clone https://github.com/Your-Voldemort/TrustNet.git
cd TrustNet

# Make deployment script executable
chmod +x scripts/deploy/deploy-services.sh

# Deploy to development environment
./scripts/deploy/deploy-services.sh dev asia-south1

# Deploy to production environment
./scripts/deploy/deploy-services.sh prod asia-south1
```

The automated script will:

- ✅ Enable required Google Cloud APIs
- ✅ Deploy infrastructure with Terraform
- ✅ Build and deploy services via Cloud Build
- ✅ Configure monitoring and alerts

## Manual Deployment

### Step 1: Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  pubsub.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  dlp.googleapis.com \
  webrisk.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

### Step 2: Configure Secrets

```bash
# Store API keys in Secret Manager
echo "your-fact-check-api-key" | gcloud secrets create fact-check-api-key --data-file=-
echo "your-perspective-api-key" | gcloud secrets create perspective-api-key --data-file=-
```

### Step 3: Deploy Infrastructure

```bash
cd infra/terraform

# Initialize Terraform
terraform init

# Create workspace for environment
terraform workspace new production
terraform workspace select production

# Plan deployment
terraform plan \
  -var="project_id=trustnet-prod" \
  -var="region=asia-south1" \
  -var="environment=prod"

# Apply infrastructure
terraform apply \
  -var="project_id=trustnet-prod" \
  -var="region=asia-south1" \
  -var="environment=prod"
```

### Step 4: Build and Deploy Services

```bash
# Return to project root
cd ../..

# Submit build to Cloud Build
gcloud builds submit \
  --config=infra/ci/cloudbuild.yaml \
  --substitutions=_REGION=asia-south1,_ENVIRONMENT=prod \
  .
```

### Step 5: Verify Deployment

```bash
# Check API health
API_URL=$(gcloud run services describe trustnet-api --region=asia-south1 --format='value(status.url)')
curl ${API_URL}/health

# Check worker status
gcloud run services describe trustnet-worker --region=asia-south1
```

## Environment Configuration

### Development Environment

```bash
# .env.development
GOOGLE_CLOUD_PROJECT_ID=trustnet-dev
ENVIRONMENT=development
FIRESTORE_DATABASE=trustnet-dev
LOG_LEVEL=debug
MAX_INSTANCES=10
CPU=1
MEMORY=2Gi
```

### Staging Environment

```bash
# .env.staging
GOOGLE_CLOUD_PROJECT_ID=trustnet-staging
ENVIRONMENT=staging
FIRESTORE_DATABASE=trustnet-staging
LOG_LEVEL=info
MAX_INSTANCES=50
CPU=2
MEMORY=4Gi
```

### Production Environment

```bash
# .env.production
GOOGLE_CLOUD_PROJECT_ID=trustnet-prod
ENVIRONMENT=production
FIRESTORE_DATABASE=trustnet-prod
LOG_LEVEL=warn
MAX_INSTANCES=1000
CPU=4
MEMORY=8Gi
```

## Production Deployment

### Pre-deployment Checklist

- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Database migrations tested
- [ ] Monitoring dashboards configured
- [ ] Rollback plan documented
- [ ] Team notified of deployment window

### Production Deployment Steps

1. **Create Production Branch**
   ```bash
   git checkout -b release/v1.0.0
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Deploy Infrastructure**
   ```bash
   cd infra/terraform
   terraform workspace select production
   terraform apply -var-file="production.tfvars"
   ```

3. **Deploy Application**
   ```bash
   gcloud builds submit \
     --config=infra/ci/cloudbuild.yaml \
     --substitutions=_REGION=asia-south1,_ENVIRONMENT=prod \
     --tag=v1.0.0
   ```

4. **Post-deployment Verification**
   ```bash
   # Health check
   curl https://api.trustnet.com/health
   
   # Functional test
   curl -X POST https://api.trustnet.com/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"text": "Test content", "language": "en"}'
   
   # Performance test
   ab -n 100 -c 10 https://api.trustnet.com/health
   ```

## Local Development

### Setup Local Environment

```bash
# Clone repository
git clone https://github.com/Your-Voldemort/TrustNet.git
cd TrustNet

# Install dependencies
cd services/api
npm install

# Set up local environment
cp .env.example .env.local
```

### Configure Local Environment Variables

```bash
# .env.local
GOOGLE_CLOUD_PROJECT_ID=trustnet-dev
ENVIRONMENT=development
PORT=8080
FIRESTORE_EMULATOR_HOST=localhost:8080
PUBSUB_EMULATOR_HOST=localhost:8085
```

### Run with Emulators

```bash
# Start Google Cloud emulators
gcloud emulators firestore start --host-port=localhost:8080 &
gcloud emulators pubsub start --host-port=localhost:8085 &

# Start development server
npm run dev
```

### Development with Docker

```bash
# Build local image
docker build -t trustnet-api:local ./services/api

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## Monitoring & Troubleshooting

### Health Monitoring

```bash
# API health endpoint
curl https://api.trustnet.com/health

# Cloud Run service health
gcloud run services describe trustnet-api --region=asia-south1
```

### Logging

```bash
# View API logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=trustnet-api" --limit=50

# View worker logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=trustnet-worker" --limit=50

# Filter by severity
gcloud logs read "severity>=ERROR" --limit=20
```

### Performance Monitoring

```bash
# Check service metrics
gcloud monitoring metrics list --filter="resource.type=cloud_run_revision"

# View request latency
gcloud monitoring time-series list \
  --filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"'
```

### Common Issues

#### Issue: Service Not Starting

```bash
# Check build logs
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')

# Check service configuration
gcloud run services describe trustnet-api --region=asia-south1
```

#### Issue: High Memory Usage

```bash
# Update service memory
gcloud run services update trustnet-api \
  --region=asia-south1 \
  --memory=8Gi
```

#### Issue: API Key Errors

```bash
# Verify secrets
gcloud secrets versions access latest --secret="fact-check-api-key"

# Update secret
echo "new-api-key" | gcloud secrets versions add fact-check-api-key --data-file=-
```

## Rollback Procedures

### Application Rollback

```bash
# List recent revisions
gcloud run revisions list --service=trustnet-api --region=asia-south1

# Rollback to previous revision
gcloud run services update-traffic trustnet-api \
  --region=asia-south1 \
  --to-revisions=trustnet-api-00002-abc=100
```

### Infrastructure Rollback

```bash
cd infra/terraform

# View state history
terraform state list

# Rollback to previous state
terraform apply -target=resource_name -var-file="previous.tfvars"
```

### Database Rollback

```bash
# Firestore automatic backups are enabled
# Contact support for restore procedures if needed
```

## Cost Optimization

### Resource Sizing Guidelines

| Environment | API Instances | Worker Instances | CPU | Memory |
|-------------|---------------|------------------|-----|--------|
| Development | 1-5 | 1-2 | 1 | 2Gi |
| Staging | 2-10 | 2-5 | 2 | 4Gi |
| Production | 10-1000 | 5-100 | 4 | 8Gi |

### Cost Monitoring

```bash
# Set up billing alerts
gcloud alpha billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="TrustNet Budget" \
  --budget-amount=1000USD
```

## Security Considerations

### Network Security

- All services deployed with Cloud Run (fully managed, no VPC required)
- HTTPS enforced for all external traffic
- Internal service communication via private Google network

### IAM Security

- Principle of least privilege applied
- Service accounts with minimal required permissions
- Regular access reviews recommended

### Data Security

- Data encrypted at rest (Firestore native encryption)
- Data encrypted in transit (TLS 1.2+)
- API keys stored in Secret Manager
- No sensitive data in logs

## Support & Maintenance

### Regular Maintenance Tasks

- [ ] Weekly: Review logs and error rates
- [ ] Monthly: Update dependencies and security patches
- [ ] Quarterly: Performance optimization review
- [ ] Annually: Architecture and cost review

### Emergency Contacts

- **Development Team**: `dev-team@trustnet.com`
- **DevOps Team**: `devops@trustnet.com`
- **Google Cloud Support**: [Support Case](https://cloud.google.com/support)

---

For additional support, see [Architecture Documentation](ARCHITECTURE.md) or contact the development team.