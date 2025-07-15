variable "credentials" {
  description = "Path to the GCP service account key file"
  type        = string
  sensitive   = true
  default     = "../secrets/aic-hcmus-2025-c3dca18c8b8a.json"
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "aic-hcmus-2025"
}

variable "region" {
  description = "GCP Region for resources"
  type        = string
  default     = "asia-southeast1-a"
}

variable "GKE_enable_autopilot" {
  description = "GCP Autopilot mode"
  type        = bool
  default     = false
}

variable "GKE_initial_node_count" {
  description = "GCP Initial node count"
  type        = number
  default     = 3
}

variable "network_name" {
  description = "Name of the network to use"
  type        = string
  default     = "aic-hcmus-2025"
}
