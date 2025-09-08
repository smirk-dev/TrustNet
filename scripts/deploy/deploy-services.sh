#!/bin/bash

# TrustNet Deployment Script
# Usage: ./deploy-services.sh [environment] [region]

set -e

ENVIRONMENT=${1:-dev}
REGION=${2:-asia-south1}
PROJECT_ID=$(gcloud config get-value project)

echo "Deploying TrustNet to ${ENVIRONMENT} environment in ${REGION}"

# Ensure required APIs are enabled
echo "Enabling required APIs..."
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

# Deploy infrastructure
echo "Deploying infrastructure with Terraform..."
cd infra/terraform
terraform init
terraform plan -var="project_id=${PROJECT_ID}" -var="region=${REGION}" -var="environment=${ENVIRONMENT}"
terraform apply -auto-approve -var="project_id=${PROJECT_ID}" -var="region=${REGION}" -var="environment=${ENVIRONMENT}"
cd ../..

# Build and deploy services
echo "Building and deploying services..."
gcloud builds submit \
  --config=infra/ci/cloudbuild.yaml \
  --substitutions=_REGION=${REGION},_ENVIRONMENT=${ENVIRONMENT} \
  .

# Configure Vertex AI Search
echo "Setting up Vertex AI Search index..."
# This would typically involve uploading initial corpus and creating search index
# Implementation would depend on specific corpus structure

# Set up monitoring
echo "Configuring monitoring and alerting..."
# Create monitoring dashboards and alert policies
# Implementation would use Cloud Monitoring APIs

echo "Deployment complete!"
echo "API URL: https://trustnet-api-$(gcloud run services describe trustnet-api --region=${REGION} --format='value(status.url)' | cut -d'/' -f3)"
