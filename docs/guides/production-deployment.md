# TrustNet Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying TrustNet to Google Cloud Platform with production-ready configurations, monitoring, and scaling capabilities.

## 1. Prerequisites & Environment Setup

### Required Google Cloud APIs

Enable the following APIs in your Google Cloud Console:

```bash
# Enable required Google Cloud APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com  
gcloud services enable pubsub.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable dlp.googleapis.com
gcloud services enable webrisk.googleapis.com
gcloud services enable commentanalyzer.googleapis.com
gcloud services enable factchecktools.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable redis.googleapis.com
```

### Environment Variables Configuration

Create a comprehensive environment configuration:

```bash
# Create production environment file
cat > .env.production << EOF
# Project Configuration
PROJECT_ID=trustnet-production
REGION=asia-south1
ZONE=asia-south1-a

# Service Configuration  
API_SERVICE_NAME=trustnet-api
WORKER_SERVICE_NAME=trustnet-analysis-worker
FRONTEND_SERVICE_NAME=trustnet-frontend

# Database Configuration
FIRESTORE_DATABASE_ID=(default)
REDIS_INSTANCE_ID=trustnet-cache

# AI/ML Configuration
VERTEX_AI_LOCATION=asia-south1
VERTEX_AI_MODEL_NAME=trustnet-verification-model

# External APIs
PERSPECTIVE_API_KEY=\${PERSPECTIVE_API_KEY}
FACTCHECK_TOOLS_API_KEY=\${FACTCHECK_TOOLS_API_KEY}

# Security & Monitoring
LOG_LEVEL=info
ENABLE_REQUEST_LOGGING=true
ENABLE_PERFORMANCE_MONITORING=true
API_RATE_LIMIT=100
EOF
```

### Service Account Setup

Create and configure service accounts with appropriate permissions:

```bash
#!/bin/bash
# setup-service-accounts.sh

PROJECT_ID="trustnet-production"

# Create service accounts
gcloud iam service-accounts create trustnet-api-service \
    --display-name="TrustNet API Service Account" \
    --project=$PROJECT_ID

gcloud iam service-accounts create trustnet-worker-service \
    --display-name="TrustNet Worker Service Account" \
    --project=$PROJECT_ID

# Grant necessary roles
ROLES=(
    "roles/firestore.user"
    "roles/pubsub.editor"
    "roles/aiplatform.user"
    "roles/dlp.user" 
    "roles/webrisk.user"
    "roles/logging.writer"
    "roles/monitoring.metricWriter"
    "roles/secretmanager.secretAccessor"
    "roles/redis.editor"
)

for role in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:trustnet-api-service@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="$role"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:trustnet-worker-service@$PROJECT_ID.iam.gserviceaccount.com" \
        --role="$role"
done
```

## 2. Infrastructure Deployment

### Terraform Infrastructure Setup

Enhanced Terraform configuration for production:

```hcl
# infra/terraform/production.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.84"
    }
  }
  
  backend "gcs" {
    bucket = "trustnet-terraform-state"
    prefix = "production/terraform.tfstate"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "asia-south1"
}

# Firestore Database
resource "google_firestore_database" "trustnet_db" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
  
  depends_on = [
    google_project_service.firestore_api
  ]
}

# Pub/Sub Topics and Subscriptions
resource "google_pubsub_topic" "verification_requests" {
  name = "verification-requests"
  
  message_retention_duration = "604800s" # 7 days
}

resource "google_pubsub_subscription" "verification_processing" {
  name  = "verification-processing"
  topic = google_pubsub_topic.verification_requests.name
  
  ack_deadline_seconds = 600 # 10 minutes for processing
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter_queue.id
    max_delivery_attempts = 5
  }
}

resource "google_pubsub_topic" "dead_letter_queue" {
  name = "verification-dead-letter"
}

# Redis Instance for Caching
resource "google_redis_instance" "trustnet_cache" {
  name           = "trustnet-cache"
  memory_size_gb = 5
  region         = var.region
  tier           = "STANDARD_HA"
  
  redis_version     = "REDIS_6_X"
  display_name      = "TrustNet Cache"
  
  auth_enabled = true
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 2
        minutes = 0
        seconds = 0
        nanos   = 0
      }
    }
  }
}

# Cloud Storage Buckets
resource "google_storage_bucket" "model_artifacts" {
  name     = "${var.project_id}-model-artifacts"
  location = var.region
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "processed_content" {
  name     = "${var.project_id}-processed-content"
  location = var.region
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Secret Manager for API Keys
resource "google_secret_manager_secret" "api_keys" {
  for_each = toset([
    "perspective-api-key",
    "factcheck-tools-api-key",
    "redis-auth-string"
  ])
  
  secret_id = each.value
  
  replication {
    automatic = true
  }
}

# Cloud Run Services
resource "google_cloud_run_service" "trustnet_api" {
  name     = "trustnet-api"
  location = var.region
  
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/trustnet-api:latest"
        
        ports {
          container_port = 8080
        }
        
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "REDIS_HOST"
          value = google_redis_instance.trustnet_cache.host
        }
        
        env {
          name = "REDIS_AUTH"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.api_keys["redis-auth-string"].secret_id
              key  = "latest"
            }
          }
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "4Gi"
          }
          requests = {
            cpu    = "1"
            memory = "2Gi"
          }
        }
      }
      
      service_account_name = "trustnet-api-service@${var.project_id}.iam.gserviceaccount.com"
      
      container_concurrency = 100
      timeout_seconds      = 300
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "2"
        "autoscaling.knative.dev/maxScale" = "100"
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  autogenerate_revision_name = true
}

# IAM for Cloud Run
resource "google_cloud_run_service_iam_policy" "api_policy" {
  location = google_cloud_run_service.trustnet_api.location
  project  = google_cloud_run_service.trustnet_api.project
  service  = google_cloud_run_service.trustnet_api.name
  
  policy_data = data.google_iam_policy.invoker.policy_data
}

data "google_iam_policy" "invoker" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

# Monitoring and Alerting
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "TrustNet High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate above 5%"
    
    condition_threshold {
      filter         = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"trustnet-api\""
      duration       = "300s"
      comparison     = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.name]
  
  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_notification_channel" "email" {
  display_name = "TrustNet Email Notifications"
  type         = "email"
  
  labels = {
    email_address = "alerts@trustnet.com"
  }
}

# Output important values
output "api_url" {
  value = google_cloud_run_service.trustnet_api.status[0].url
}

output "redis_host" {
  value = google_redis_instance.trustnet_cache.host
}
```

### Deploy Infrastructure

```bash
#!/bin/bash
# deploy-infrastructure.sh

set -e

PROJECT_ID="trustnet-production"
REGION="asia-south1"

echo "Deploying TrustNet infrastructure..."

# Initialize Terraform
cd infra/terraform
terraform init

# Plan deployment
terraform plan \
    -var="project_id=$PROJECT_ID" \
    -var="region=$REGION" \
    -out=production.plan

# Apply infrastructure changes
terraform apply production.plan

echo "Infrastructure deployment complete!"
```

## 3. Application Deployment Pipeline

### Docker Containerization

**API Service Dockerfile:**

```dockerfile
# services/api/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:18-alpine AS runtime

# Install production dependencies
RUN apk add --no-cache dumb-init

# Create app user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

WORKDIR /app

# Copy application files
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs . .

# Security: remove package files
RUN rm -f package*.json

# Switch to non-root user
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node healthcheck.js

EXPOSE 8080

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "src/index.js"]
```

**Cloud Build Configuration:**

```yaml
# cloudbuild.yaml
steps:
  # Build API service
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build', 
      '-t', 'gcr.io/$PROJECT_ID/trustnet-api:$COMMIT_SHA',
      '-t', 'gcr.io/$PROJECT_ID/trustnet-api:latest',
      './services/api'
    ]
  
  # Build worker service  
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', 'gcr.io/$PROJECT_ID/trustnet-worker:$COMMIT_SHA',
      '-t', 'gcr.io/$PROJECT_ID/trustnet-worker:latest', 
      './services/workers'
    ]
  
  # Push images
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '--all-tags', 'gcr.io/$PROJECT_ID/trustnet-api']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '--all-tags', 'gcr.io/$PROJECT_ID/trustnet-worker']
  
  # Deploy API to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args: [
      'run', 'deploy', 'trustnet-api',
      '--image', 'gcr.io/$PROJECT_ID/trustnet-api:$COMMIT_SHA',
      '--region', 'asia-south1',
      '--platform', 'managed',
      '--allow-unauthenticated',
      '--max-instances', '100',
      '--memory', '4Gi',
      '--cpu', '2',
      '--timeout', '300',
      '--set-env-vars', 'PROJECT_ID=$PROJECT_ID',
      '--service-account', 'trustnet-api-service@$PROJECT_ID.iam.gserviceaccount.com'
    ]
  
  # Deploy worker to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args: [
      'run', 'deploy', 'trustnet-worker',
      '--image', 'gcr.io/$PROJECT_ID/trustnet-worker:$COMMIT_SHA',
      '--region', 'asia-south1', 
      '--platform', 'managed',
      '--no-allow-unauthenticated',
      '--max-instances', '50',
      '--memory', '8Gi',
      '--cpu', '4',
      '--timeout', '900',
      '--set-env-vars', 'PROJECT_ID=$PROJECT_ID',
      '--service-account', 'trustnet-worker-service@$PROJECT_ID.iam.gserviceaccount.com'
    ]

# Build timeout
timeout: '1200s'

# Build options
options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY

# Substitutions
substitutions:
  _DEPLOY_REGION: asia-south1
```

## 4. Monitoring & Observability

### Comprehensive Logging Setup

```javascript
// services/api/src/utils/logger.js - Enhanced Production Logger
const winston = require('winston');
const { LoggingWinston } = require('@google-cloud/logging-winston');

// Create Cloud Logging transport
const loggingWinston = new LoggingWinston({
  projectId: process.env.PROJECT_ID,
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS,
  logName: 'trustnet-api',
  resource: {
    type: 'cloud_run_revision',
    labels: {
      service_name: process.env.K_SERVICE || 'trustnet-api',
      revision_name: process.env.K_REVISION || 'unknown',
      location: process.env.FUNCTION_REGION || 'asia-south1'
    }
  }
});

// Configure logger with multiple transports
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json(),
    winston.format.printf((info) => {
      return JSON.stringify({
        timestamp: info.timestamp,
        level: info.level,
        message: info.message,
        service: 'trustnet-api',
        version: process.env.SERVICE_VERSION || '1.0.0',
        traceId: info.traceId,
        spanId: info.spanId,
        userId: info.userId,
        requestId: info.requestId,
        ...info.metadata
      });
    })
  ),
  transports: [
    // Console transport for local development
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    // Cloud Logging transport for production
    loggingWinston
  ]
});

// Enhanced request logging middleware
const requestLogger = (req, res, next) => {
  const startTime = Date.now();
  const requestId = req.headers['x-request-id'] || generateRequestId();
  
  req.logger = logger.child({
    requestId,
    traceId: req.headers['x-cloud-trace-context']?.split('/')[0],
    userId: req.user?.id,
    userAgent: req.headers['user-agent'],
    ip: req.ip,
    method: req.method,
    url: req.originalUrl
  });
  
  req.logger.info('Request started', {
    method: req.method,
    url: req.originalUrl,
    userAgent: req.headers['user-agent'],
    contentLength: req.headers['content-length']
  });
  
  // Log response completion
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const logLevel = res.statusCode >= 400 ? 'error' : 'info';
    
    req.logger.log(logLevel, 'Request completed', {
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      contentLength: res.get('content-length')
    });
  });
  
  next();
};

module.exports = { logger, requestLogger };
```

### Performance Monitoring Dashboard

```javascript
// monitoring/performance-metrics.js
const { Monitoring } = require('@google-cloud/monitoring');

class PerformanceMonitor {
  constructor() {
    this.monitoring = new Monitoring.MetricServiceClient();
    this.projectPath = this.monitoring.projectPath(process.env.PROJECT_ID);
  }
  
  async recordCustomMetric(metricType, value, labels = {}) {
    const dataPoint = {
      interval: {
        endTime: {
          seconds: Date.now() / 1000
        }
      },
      value: {
        doubleValue: value
      }
    };
    
    const timeSeriesData = {
      metric: {
        type: `custom.googleapis.com/${metricType}`,
        labels: labels
      },
      resource: {
        type: 'cloud_run_revision',
        labels: {
          project_id: process.env.PROJECT_ID,
          service_name: process.env.K_SERVICE,
          revision_name: process.env.K_REVISION,
          location: process.env.FUNCTION_REGION
        }
      },
      points: [dataPoint]
    };
    
    const request = {
      name: this.projectPath,
      timeSeries: [timeSeriesData]
    };
    
    await this.monitoring.createTimeSeries(request);
  }
  
  // Verification accuracy metric
  async recordVerificationAccuracy(accuracy, confidence, category) {
    await this.recordCustomMetric('verification/accuracy', accuracy, {
      confidence_level: this.getConfidenceBucket(confidence),
      content_category: category
    });
  }
  
  // Response time percentiles
  async recordResponseTime(duration, endpoint) {
    await this.recordCustomMetric('api/response_time', duration, {
      endpoint: endpoint,
      percentile: this.getPercentileBucket(duration)
    });
  }
  
  // User satisfaction metric
  async recordUserFeedback(rating, feature) {
    await this.recordCustomMetric('user/satisfaction', rating, {
      feature: feature,
      rating_category: this.getRatingCategory(rating)
    });
  }
  
  getConfidenceBucket(confidence) {
    if (confidence < 0.3) return 'very_low';
    if (confidence < 0.5) return 'low'; 
    if (confidence < 0.7) return 'medium';
    if (confidence < 0.85) return 'high';
    return 'very_high';
  }
  
  getPercentileBucket(duration) {
    if (duration < 500) return 'p50';
    if (duration < 1000) return 'p75';
    if (duration < 2000) return 'p90';
    if (duration < 5000) return 'p95';
    return 'p99';
  }
  
  getRatingCategory(rating) {
    if (rating <= 2) return 'poor';
    if (rating <= 3) return 'fair';
    if (rating <= 4) return 'good';
    return 'excellent';
  }
}

module.exports = PerformanceMonitor;
```

## 5. Production Rollout Strategy

### Blue-Green Deployment Process

```bash
#!/bin/bash
# deploy-blue-green.sh

set -e

PROJECT_ID="trustnet-production"
SERVICE_NAME="trustnet-api"
REGION="asia-south1"
NEW_IMAGE="gcr.io/$PROJECT_ID/trustnet-api:$COMMIT_SHA"

echo "Starting blue-green deployment..."

# Deploy to new revision (green)
echo "Deploying new revision..."
gcloud run deploy $SERVICE_NAME \
    --image $NEW_IMAGE \
    --region $REGION \
    --no-traffic \
    --tag green

# Get the new revision URL
GREEN_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format 'value(status.traffic[?tag=="green"].url)')

echo "Green deployment URL: $GREEN_URL"

# Run smoke tests against green deployment
echo "Running smoke tests..."
./scripts/smoke-tests.sh $GREEN_URL

if [ $? -eq 0 ]; then
    echo "Smoke tests passed. Shifting traffic..."
    
    # Gradual traffic shift
    echo "Shifting 10% traffic to green..."
    gcloud run services update-traffic $SERVICE_NAME \
        --to-tags green=10 \
        --region $REGION
    
    sleep 300 # Wait 5 minutes
    
    echo "Shifting 50% traffic to green..."
    gcloud run services update-traffic $SERVICE_NAME \
        --to-tags green=50 \
        --region $REGION
        
    sleep 300 # Wait 5 minutes
    
    echo "Shifting 100% traffic to green..."
    gcloud run services update-traffic $SERVICE_NAME \
        --to-tags green=100 \
        --region $REGION
    
    # Clean up old revision
    echo "Cleaning up old revision..."
    gcloud run revisions delete $(gcloud run revisions list \
        --service $SERVICE_NAME \
        --region $REGION \
        --filter "NOT metadata.labels.serving.knative.dev/route:*" \
        --format "value(metadata.name)" \
        --limit 1) \
        --region $REGION --quiet
        
    echo "Blue-green deployment completed successfully!"
    
else
    echo "Smoke tests failed. Rolling back..."
    gcloud run services update-traffic $SERVICE_NAME \
        --to-revisions LATEST=100 \
        --region $REGION
    exit 1
fi
```

This comprehensive deployment guide ensures TrustNet can be deployed to production with enterprise-grade reliability, monitoring, and operational excellence.
