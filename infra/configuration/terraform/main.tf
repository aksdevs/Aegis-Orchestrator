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
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "iam.googleapis.com",
    "run.googleapis.com",
    "storage.googleapis.com"
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
    "roles/artifactregistry.reader", 
    "roles/cloudsql.client",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/storage.admin"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.app_sa.email}"

  depends_on = [google_service_account.app_sa]
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

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "aegis-repo"
  description   = "Repository for Aegis Orchestrator Docker images"
  format        = "DOCKER"
  project       = var.project_id

  depends_on = [google_project_service.services]
}

# Vertex AI Model Registry  
resource "google_artifact_registry_repository" "model_registry" {
  location      = var.region
  repository_id = "aegis-models"
  description   = "Repository for Aegis Orchestrator ML models"
  format        = "PYTHON"
  project       = var.project_id

  depends_on = [google_project_service.services]
}

# Cloud Run service for the application
resource "google_cloud_run_service" "app" {
  name     = "aegis-orchestrator"
  location = var.region
  project  = var.project_id

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "autoscaling.knative.dev/minScale" = "0"
        "run.googleapis.com/execution-environment" = "gen2"
      }
    }
    
    spec {
      service_account_name = google_service_account.app_sa.email
      timeout_seconds      = 3600
      
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/aegis-repo/aegis-orchestrator:latest"
        
        ports {
          container_port = 8080
        }
        
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "REGION"
          value = var.region
        }
        
        env {
          name  = "WORKSPACE_DIR"
          value = "/workspace"
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "2Gi"
          }
          requests = {
            cpu    = "500m"
            memory = "1Gi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_artifact_registry_repository.docker_repo,
    google_service_account.app_sa,
    google_project_service.services
  ]
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
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_service.app.status[0].url
}

output "service_account_email" {
  description = "Email of the service account"
  value       = google_service_account.app_sa.email
}

output "artifact_bucket" {
  description = "Name of the GCS bucket for artifacts"
  value       = google_storage_bucket.artifacts.name
}

output "docker_registry" {
  description = "Docker registry URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/aegis-repo"
}

output "model_registry" {
  description = "ML model registry name"
  value       = google_artifact_registry_repository.model_registry.name
}
