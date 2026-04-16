provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_service" "api" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      containers {
        image = var.image

        resources {
          limits = {
            memory = "512Mi"
            cpu    = "1"
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

resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
