terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
  }
  required_version = "1.12.1"
}

provider "google" {
  credentials = var.credentials
  project     = var.project_id
  region      = var.region
}

// Create VPC network
resource "google_compute_network" "vpc_network" {
  name                    = var.network_name
  auto_create_subnetworks = "true"
}

// Google Kubernetes Engine
resource "google_container_cluster" "primary" {
  name                = "${var.project_id}-gke"
  location            = var.region
  enable_autopilot    = var.GKE_enable_autopilot
  initial_node_count  = var.GKE_initial_node_count
  deletion_protection = false

  node_config {
    machine_type = "e2-standard-2"
    disk_size_gb = 50
  }
}

