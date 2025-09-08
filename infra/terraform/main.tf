terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "trustnet-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "asia-south1"
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "dev"
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "pubsub.googleapis.com",
    "firestore.googleapis.com",
    "aiplatform.googleapis.com",
    "dlp.googleapis.com",
    "webrisk.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com"
  ])

  service                    = each.value
  disable_on_destroy        = false
  disable_dependent_services = false
}

# Firestore Database
resource "google_firestore_database" "main" {
  project                     = var.project_id
  name                       = "trustnet-${var.environment}"
  location_id               = var.region
  type                      = "FIRESTORE_NATIVE"
  concurrency_mode          = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"

  depends_on = [google_project_service.apis]
}

# Pub/Sub Topics
resource "google_pubsub_topic" "content_analysis" {
  name = "content-analysis"
  
  message_retention_duration = "604800s" # 7 days
}

resource "google_pubsub_topic" "evidence_retrieval" {
  name = "evidence-retrieval"
  
  message_retention_duration = "604800s"
}

resource "google_pubsub_topic" "fact_check_lookup" {
  name = "fact-check-lookup"
  
  message_retention_duration = "604800s"
}

resource "google_pubsub_topic" "verdict_updates" {
  name = "verdict-updates"
  
  message_retention_duration = "86400s" # 1 day
}

# Pub/Sub Subscriptions
resource "google_pubsub_subscription" "content_analysis_sub" {
  name  = "content-analysis-sub"
  topic = google_pubsub_topic.content_analysis.name

  message_retention_duration = "604800s"
  ack_deadline_seconds       = 600

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "300s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 7
  }
}

resource "google_pubsub_topic" "dead_letter" {
  name = "dead-letter-queue"
}

resource "google_pubsub_subscription" "dead_letter_sub" {
  name  = "dead-letter-sub"
  topic = google_pubsub_topic.dead_letter.name
}

# Cloud Storage for evidence corpus
resource "google_storage_bucket" "evidence_corpus" {
  name     = "trustnet-evidence-corpus-${var.environment}"
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

# Service Accounts
resource "google_service_account" "api_service" {
  account_id   = "trustnet-api"
  display_name = "TrustNet API Service"
  description  = "Service account for TrustNet API"
}

resource "google_service_account" "worker_service" {
  account_id   = "trustnet-worker"
  display_name = "TrustNet Worker Service"
  description  = "Service account for TrustNet background workers"
}

# IAM bindings
resource "google_project_iam_member" "api_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.api_service.email}"
}

resource "google_project_iam_member" "api_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.api_service.email}"
}

resource "google_project_iam_member" "worker_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.worker_service.email}"
}

resource "google_project_iam_member" "worker_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.worker_service.email}"
}

resource "google_project_iam_member" "worker_vertex" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.worker_service.email}"
}

resource "google_project_iam_member" "worker_dlp" {
  project = var.project_id
  role    = "roles/dlp.user"
  member  = "serviceAccount:${google_service_account.worker_service.email}"
}

resource "google_project_iam_member" "worker_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.worker_service.email}"
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "main" {
  location      = var.region
  repository_id = "trustnet"
  description   = "TrustNet container images"
  format        = "DOCKER"
}

# Secret Manager secrets
resource "google_secret_manager_secret" "fact_check_api_key" {
  secret_id = "fact-check-api-key"
  
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "perspective_api_key" {
  secret_id = "perspective-api-key"
  
  replication {
    automatic = true
  }
}

# Cloud Run services will be deployed via Cloud Build
# Outputs for other modules
output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "api_service_account_email" {
  value = google_service_account.api_service.email
}

output "worker_service_account_email" {
  value = google_service_account.worker_service.email
}

output "artifact_registry_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}"
}
