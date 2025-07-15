# AIC-HCMUS Fragment Segmentation Helm Chart

Deploy the complete AI-powered fragment segmentation system on Kubernetes using this Helm chart.

---

## Table of Contents

1. [Overview](#overview)
2. [Components](#components)
3. [Prerequisites](#prerequisites)
4. [Directory Structure](#directory-structure)
5. [Configuration](#configuration)
6. [Secrets Management](#secrets-management)
7. [SSL/TLS Setup](#ssltls-setup)
8. [Installation](#installation)
9. [Upgrading](#upgrading)
10. [Uninstalling](#uninstalling)
11. [Monitoring & Access](#monitoring--access)
12. [Scaling](#scaling)
13. [Troubleshooting](#troubleshooting)
14. [Contributing](#contributing)
15. [License](#license)

---

## Overview

This Helm chart deploys the AIC-HCMUS Fragment Segmentation application, including backend, frontend, Celery workers, database, object storage, reverse proxy, and monitoring stack.

---

## Components

- **Backend**: FastAPI for AI inference and API endpoints
- **Frontend**: React user interface
- **Celery**: Background task workers
- **PostgreSQL**: Application database
- **MinIO**: Object storage for images and models
- **Redis**: Cache and Celery broker
- **Nginx**: SSL-terminating reverse proxy
- **Monitoring**: Prometheus, Grafana, and exporters

---

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- kubectl configured for your cluster

---

## Directory Structure

```text
k8s/helm/
├── Chart.yaml
├── values.yaml
├── README.md
├── validate.sh
└── templates/
    ├── _helpers.tpl
    ├── namespace.yaml
    ├── secret.yaml
    ├── configmap.yaml
    ├── backend/
    ├── frontend/
    ├── celery/
    ├── database/
    ├── minio/
    ├── redis/
    ├── nginx/
    └── monitoring/
```

---

## Configuration

All configuration is managed via `values.yaml`. You can override any value using `--set` or by providing your own values file.

**Example: Minimal values.yaml**
```yaml
secrets:
  googleClientId: "your-client-id"
  googleClientSecret: "your-client-secret"
  secretKey: "your-secret-key"
  dbPassword: "your-db-password"
  minioPassword: "your-minio-password"

backend:
  replicaCount: 2

frontend:
  replicaCount: 1
```

For all available options, see the comments in `values.yaml`.

---

## Secrets Management

Sensitive data is managed via Kubernetes secrets:

- Google OAuth credentials
- Database credentials
- MinIO credentials
- Application secret key

**Set secrets at install/upgrade:**
```bash
helm install aic-hcmus-fragment-segmentation ./k8s/helm \
  --set secrets.googleClientId="your-client-id" \
  --set secrets.googleClientSecret="your-client-secret" \
  --set secrets.secretKey="your-secret-key" \
  --set secrets.dbPassword="your-db-password" \
  --set secrets.minioPassword="your-minio-password"
```

---

## SSL/TLS Setup

Create a Kubernetes TLS secret for Nginx:

```bash
kubectl create secret tls nginx-ssl \
  --cert=path/to/certificate.crt \
  --key=path/to/private.key \
  -n aic-hcmus-app
```

---

## Installation

1. **Create namespaces (if not present):**
   ```bash
   kubectl create namespace aic-hcmus-app
   kubectl create namespace aic-hcmus-monitor
   ```

3. **Install the chart:**
   ```bash
   helm install aic-hcmus-prod ./k8s/helm -n aic-hcmus-app \
     --values ./k8s/helm/values.yaml \
     # or override secrets inline as above
   ```

4. **Verify:**
   ```bash
   kubectl get pods -n aic-hcmus-app
   kubectl get services -n aic-hcmus-app
   ```

---

## Upgrading

```bash
helm upgrade aic-hcmus-prod ./k8s/helm -n aic-hcmus-app
```

---

## Uninstalling

```bash
helm uninstall aic-hcmus-prod -n aic-hcmus-app
```

**To fully clean up:**
```bash
kubectl delete pvc --all -n aic-hcmus-app
kubectl delete namespace aic-hcmus-app
kubectl delete namespace aic-hcmus-monitor
```

---

## Monitoring & Access

- **Grafana:**  
  ```bash
  kubectl port-forward svc/aic-hcmus-fragment-segmentation-grafana 3000:3000 -n aic-hcmus-monitor
  # Visit http://localhost:3000 (default: admin/admin)
  ```
---

## Scaling

- **Horizontal Pod Autoscaling:**  
  Configurable in `values.yaml`:
  ```yaml
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 50
  ```

- **Manual scaling:**
  ```bash
  kubectl scale deployment aic-hcmus-fragment-segmentation-backend --replicas=5 -n aic-hcmus-app
  ```

---

## Troubleshooting

- **Check logs:**
  ```bash
  kubectl logs -f deployment/aic-hcmus-fragment-segmentation-backend -n aic-hcmus-app
  kubectl logs -f deployment/aic-hcmus-fragment-segmentation-frontend -n aic-hcmus-app
  kubectl logs -f deployment/aic-hcmus-fragment-segmentation-celery -n aic-hcmus-app
  ```

- **Check status:**
  ```bash
  kubectl get all -n aic-hcmus-app
  kubectl describe pods -n aic-hcmus-app
  ```

- **Common Issues:**
  1. **Images not found:** Ensure images are pushed to the correct registry.
  2. **Storage issues:** Verify your storage class exists and is available.
  3. **SSL certificate issues:** Check that the nginx-ssl secret exists and is valid.
  4. **Database connection issues:** Verify credentials and network connectivity.

---

## Contributing

- Follow structure and naming conventions.
- Update `Chart.yaml` version for changes.
- Test with both dev and prod values.
- Update this README for new options.

---

## License

MIT License. See [LICENSE](../../LICENSE) for details. 