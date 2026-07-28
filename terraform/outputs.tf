output "service_url" {
  value       = google_cloud_run_v2_service.agent_service.uri
  description = "The HTTP endpoint URL of the deployed Cloud Run agent service."
}

output "service_account_email" {
  value       = google_service_account.agent_sa.email
  description = "The email of the agent runtime Service Account."
}
