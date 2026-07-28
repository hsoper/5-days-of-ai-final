# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
