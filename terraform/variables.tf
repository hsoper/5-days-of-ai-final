variable "project_id" {
  type        = string
  description = "The Google Cloud Project ID to deploy resources into."
  default     = "onboarding-project-fde"
}

variable "region" {
  type        = string
  description = "The GCP region for Cloud Run and Vertex AI services."
  default     = "us-central1"
}

variable "app_name" {
  type        = string
  description = "Name of the agent application service."
  default     = "socrates-ai-agent"
}

variable "container_image" {
  type        = string
  description = "Container image URI deployed to Cloud Run."
  default     = "gcr.io/onboarding-project-fde/socrates-ai-agent:latest"
}

variable "allow_unauthenticated" {
  type        = bool
  description = "Allow unauthenticated HTTP requests to Cloud Run."
  default     = true
}
