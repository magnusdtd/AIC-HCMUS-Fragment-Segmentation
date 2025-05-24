provider "google" {
  project     = var.project_id
  region      = var.region
  zone    = "${var.region}-a"
}

resource "google_container_cluster" "primary" {
  project  = var.project_id
  name     = var.cluster_name
  location = var.region
  initial_node_count = var.node_count

  node_config {
    machine_type = var.node_count
  }
}

resource "kubernetes_namespace" "app" {
  metadata {
    name = "aic-hcmus-app"
  }
}

resource "kubernetes_secret" "nginx_ssl" {
  metadata {
    name      = "nginx-ssl"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    tls.crt = filebase64("../nginx-ssl/tls.crt")
    tls.key = filebase64("../nginx-ssl/tls.key")
  }
}

resource "kubernetes_config_map" "grafana_dashboards" {
  metadata {
    name      = "grafana-dashboards"
    namespace = "aic-hcmus-monitor"
  }

  data = {
    "dashboard.json" = file("../grafana/dashboards/my_dashboard.json")
  }
}

resource "kubernetes_deployment" "app" {
  metadata {
    name      = "app"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "app"
      }
    }

    template {
      metadata {
        labels = {
          app = "app"
        }
      }

      spec {
        container {
          image = "gcr.io/${var.project_id}/app:latest"
          name  = "app"

          ports {
            container_port = 80
          }
        }
      }
    }
  }
}
