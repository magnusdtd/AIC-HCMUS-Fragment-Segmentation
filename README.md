# AIC-HCMUS-Fragment-Segmentation

## Root Level
- **`docker-compose.yml`**: Configures local development services (React, FastAPI, PostgreSQL, MinIO) with environment variables and volumes.
- **`.github/workflows/deploy.yml`**: Defines the CI/CD pipeline using GitHub Actions to build, push, and deploy Docker images to GCP Cloud Run.
- **`README.md`**: Contains comprehensive project documentation, including setup instructions and deployment details, contributed to by all members.

## Frontend (`frontend/`)
- **`src/`**: Core React source code.
  - **`components/`**: Reusable UI components like `Login.tsx`, `Register.tsx`, `ImageUpload.tsx`, and `Predictions.tsx`.
  - **`pages/`**: Page-level components for routing (if separated from components).
  - **`styles/`**: Custom CSS files with Tailwind directives.
  - **`utils/`**: Utility functions (e.g., API helpers).
- **`public/`**: Static assets (e.g., favicon, default images).
- **`tests/`**: Unit tests for components using Jest and React Testing Library.
- **`Dockerfile`**: Docker configuration for building and serving the React app.
- **`package.json`**: Node.js dependencies and scripts.
- **`tsconfig.json`**: TypeScript configuration.
- **`tailwind.config.js`**: Tailwind CSS configuration.

## Backend (`backend/`)
- **`app/`**: FastAPI application structure.
  - **`main.py`**: Entry point for the FastAPI app.
  - **`routers/`**: API endpoint routers.
    - **`auth.py`**: Handles `/login` and `/register` endpoints.
    - **`upload.py`**: Handles `/upload` endpoint for image uploads.
    - **`predict.py`**: Handles `/predict` endpoint for YOLOv11seg-m inference.
  - **`models/`**: SQLModel definitions and queries.
    - **`database.py`**: Defines `users` and `images` table schemas.
    - **`queries.py`**: Database operation functions (e.g., insert, retrieve).
  - **`utils/`**: Helper functions.
    - **`model.py`**: Loads and runs the YOLOv11seg-m model.
    - **`security.py`**: Handles password hashing and JWT utilities.
    - **`minio.py`**: Manages MinIO uploads and URL generation.
  - **`scripts/`**: Database and storage scripts.
    - **`init_db.py`**: Initializes the database schema.
    - **`backup_db.py`**: Backs up PostgreSQL data.
    - **`backup_minio.py`**: Backs up MinIO storage.
- **`migrations/`**: Alembic migration scripts for database schema management.
- **`tests/`**: Unit tests for FastAPI endpoints using pytest.
- **`Dockerfile`**: Docker configuration for the FastAPI app.
- **`requirements.txt`**: Python dependencies.
- **`.env.example`**: Template for environment variables (e.g., database URL, MinIO credentials).

## Notes
- **Dockerfiles**: Located in `frontend/` and `backend/`. PostgreSQL and MinIO use official images configured in `docker-compose.yml`, not custom Dockerfiles.
- **Model**: Not stored in the repository; downloaded dynamically from [Hugging Face](https://huggingface.co/) during the Docker build or runtime.
