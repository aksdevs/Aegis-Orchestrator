variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "aiplatform.googleapis.com",
    "compute.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com"
  ])
  
  service = each.key
  project = var.project_id

  disable_dependent_services = true
  disable_on_destroy        = false
}

# Service account for the application
resource "google_service_account" "app_sa" {
  account_id   = "aegis-orchestrator-sa"
  display_name = "Aegis Orchestrator Service Account"
  project      = var.project_id
}

# IAM roles for the service account
resource "google_project_iam_member" "sa_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/storage.admin"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# Cloud Storage bucket for artifacts
resource "google_storage_bucket" "artifacts" {
  name     = "${var.project_id}-aegis-artifacts"
  location = var.region
  project  = var.project_id

  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
}

# Vertex AI Model Registry
resource "google_artifact_registry_repository" "model_registry" {
  provider = google-beta

  location      = var.region
  repository_id = "aegis-models"
  description   = "Repository for Aegis Orchestrator ML models"
  format        = "DOCKER"
  project       = var.project_id
}

# Cloud Run service for the application
resource "google_cloud_run_service" "app" {
  name     = "aegis-orchestrator"
  location = var.region
  project  = var.project_id

  template {
    spec {
      service_account_name = google_service_account.app_sa.email
      containers {
        image = "gcr.io/${var.project_id}/aegis-orchestrator:latest"
        
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "REGION"
          value = var.region
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "2Gi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access to the Cloud Run service
resource "google_cloud_run_service_iam_member" "public" {
  location = google_cloud_run_service.app.location
  project  = google_cloud_run_service.app.project
  service  = google_cloud_run_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "service_url" {
  value = google_cloud_run_service.app.status[0].url
}

output "service_account_email" {
  value = google_service_account.app_sa.email
}

output "artifact_bucket" {
  value = google_storage_bucket.artifacts.name
}

output "model_registry" {
  value = google_artifact_registry_repository.model_registry.name
}
