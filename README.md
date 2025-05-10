# AIC-HCMUS Fragment Segmentation Application Summary

## Overview
This application is a full-stack solution for fragment segmentation, built for the HCMUS AI Challenge. It includes a **React frontend**, a **FastAPI backend**, and supporting services like **PostgreSQL**, **MinIO**, and **NGINX**. The application is containerized using **Docker** and orchestrated with **Kubernetes** for deployment.

---

## Key Features
1. **Frontend**:
   - Built with **React** and **TypeScript**.
   - Uses **TailwindCSS** for styling.
   - Implements **React Router** for navigation.
   - Provides user authentication (login/register).
   - Allows users to upload images, view predictions, and visualize results (e.g., overlaid masks, volume data).
   - Includes reusable UI components like `Predict`, `UserImages`, and `Tabs`.

2. **Backend**:
   - Built with **FastAPI**.
   - Handles user authentication with JWT tokens.
   - Provides endpoints for image upload, prediction, and fetching results.
   - Integrates with **YOLOv11m** for segmentation and volume calculation.
   - Stores metadata and predictions in **PostgreSQL**.
   - Uses **MinIO** for object storage (e.g., images, binary masks).
   - Uses **Celery** for asynchronous task processing (e.g., running predictions in the background).

3. **Machine Learning**:
   - Utilizes a YOLOv11m segmentation model downloaded from **Hugging Face**.
   - Detects calibration objects (e.g., red balls) for volume estimation.
   - Generates overlaid masks and calculates object volumes.

4. **Infrastructure**:
   - **Docker Compose** for local development.
   - **Kubernetes** manifests for deployment (PostgreSQL, MinIO, app, NGINX).
   - CI/CD pipeline using **GitHub Actions** to build and deploy to **Google Kubernetes Engine (GKE)**.
   - Uses a Celery worker and **Redis** as the message broker for task queuing.

---

## Application Structure

### Root Level
- **`docker-compose.yml`**: Defines services for local development.
- **`Dockerfile`**: Multi-stage build for frontend and backend.
- **`.github/workflows/deploy.yml`**: CI/CD pipeline for GKE deployment.

### Frontend (`frontend/`)
- **Core Technologies**: React, TypeScript, TailwindCSS, Vite.
- **Key Files**:
  - `vite.config.ts`: Configures Vite for development and build.
  - `src/components/`: Contains reusable UI components (e.g., `Predict`, `UserImages`, `Login`, `Register`).
  - `src/services/api.ts`: Axios instance for API communication.
  - `src/context/UserContext.tsx`: Manages user authentication state.
  - `package.json`: Defines dependencies and scripts.

### Backend (`backend/`)
- **Core Technologies**: FastAPI, SQLModel, MinIO, YOLOv11m-seg, Celery.
- **Key Files**:
  - `app/main.py`: Entry point for the FastAPI app.
  - `app/routers/`: Contains API endpoint routers (e.g., `auth.py`, `predict.py`, `display_img.py`).
  - `app/models/`: Defines database models and queries.
  - `app/utils/`: Includes helper modules for security, MinIO, and YOLO model integration.
  - `app/predict/tasks.py`: Defines Celery tasks for background processing.
  - `celery_worker.py`: Entry point for running the Celery worker.
  - `requirements.txt`: Lists Python dependencies.

### Kubernetes (`k8s/`)
- **Manifests**:
  - `namespace.yaml`: Defines the `aic-hcmus` namespace.
  - `postgres.yaml`: Configures PostgreSQL deployment and service.
  - `minio.yaml`: Configures MinIO deployment and service.
  - `app.yaml`: Configures the FastAPI app deployment and service.
  - `nginx.yaml`: Configures NGINX as a reverse proxy.

---

## Deployment Workflow
1. **Local Development**:
   - Use `docker-compose.yml` to spin up services locally.
   - Frontend runs on `http://localhost:3000`, backend on `http://localhost:8080`.

2. **CI/CD Pipeline**:
   - Triggered on `deploy` branch push.
   - Builds Docker images and pushes them to **Google Container Registry (GCR)**.
   - Deploys to **Google Kubernetes Engine (GKE)** using Kubernetes manifests.

3. **Production Deployment**:
   - Services are deployed in the `aic-hcmus` namespace.
   - NGINX serves as a reverse proxy for the frontend and backend.
   - Celery worker and Redis are deployed as part of the Kubernetes manifests.

---

## Key Endpoints (Updated)
### Backend API
- **Authentication**:
  - `POST /api/auth/register`: Register a new user.
  - `POST /api/auth/login`: Login and retrieve JWT token.
  - `GET /api/auth/current-user`: Validate token and fetch user info.
- **Image Upload & Prediction**:
  - `POST /api/upload`: Upload an image.
  - `POST /api/upload_predict`: Upload an image and run prediction.
  - `GET /api/display_images`: Fetch metadata for user-uploaded images.
  - `GET /api/fetch_image/{filename}`: Fetch an image from MinIO.
  - **NEW**: Background tasks are now handled by Celery for long-running operations like predictions.

---

## Technologies Used (Updated)
- **Frontend**: React, TypeScript, TailwindCSS, Vite.
- **Backend**: FastAPI, SQLModel, MinIO, YOLOv11m, Celery.
- **Database**: PostgreSQL.
- **Storage**: MinIO.
- **Task Queue**: Celery with Redis as the message broker.
- **Containerization**: Docker.
- **Orchestration**: Kubernetes.
- **CI/CD**: GitHub Actions.
- **Cloud**: Google Kubernetes Engine (GKE).

---

## Notes
- The YOLOv11m model is dynamically downloaded from **Hugging Face** during runtime.
- The application uses **GNU GPL v3** as its license.