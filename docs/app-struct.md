# Application Structure

This document outlines the structure of the AIC-HCMUS Fragment Segmentation application, describing key components and their relationships.

## Root Level

- **docker-compose.yml**: Defines services for local development.
- **Dockerfile**: Multi-stage build for frontend and backend.
- **.github/workflows/deploy.yml**: CI/CD pipeline for GKE deployment.

## Frontend (frontend/)

### Core Technologies
- React
- TypeScript
- TailwindCSS
- Vite

### Key Files
- **vite.config.ts**: Configures Vite for development and build.
- **src/components/**: Contains reusable UI components (e.g., Predict, UserImages, Login, Register).
- **src/services/api.ts**: Axios instance for API communication.
- **src/context/UserContext.tsx**: Manages user authentication state.
- **package.json**: Defines dependencies and scripts.

## Backend (backend/)

### Core Technologies
- FastAPI
- SQLModel
- MinIO
- YOLOv11m

### Key Files
- **app/main.py**: Entry point for the FastAPI app.
- **app/routers/**: Contains API endpoint routers (e.g., auth.py, predict.py, display_img.py).
- **app/models/**: Defines database models and queries.
- **app/utils/**: Includes helper modules for security, MinIO, and YOLO model integration.
- **requirements.txt**: Lists Python dependencies.

## Kubernetes (k8s/)

### Manifests
- **namespace.yaml**: Defines the aic-hcmus namespace.
- **postgres.yaml**: Configures PostgreSQL deployment and service.
- **minio.yaml**: Configures MinIO deployment and service.
- **app.yaml**: Configures the FastAPI app deployment and service.
- **nginx.yaml**: Configures NGINX as a reverse proxy.
