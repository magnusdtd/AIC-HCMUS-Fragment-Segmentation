// Variables to use across the project

variable "project_id" {
  description = "The project ID to host the cluster in"
  default     = "aic-hcmus"
}

variable "region" {
  description = "The region where the cluster will be deployed"
  default     = "us-central1"
}

variable "cluster_name" {
  description = "The name of the GKE cluster"
  default     = "my-gke-cluster"
}

variable "node_count" {
  description = "The number of nodes in the cluster"
  default     = 3
}

variable "machine_type" {
  description = "The machine type to use for cluster nodes"
  default     = "n2-standard-2"  # 2 CPU and 8 GB RAM
}
