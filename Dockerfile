# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

COPY ./frontend/package*.json ./
RUN npm ci

COPY ./frontend ./
RUN npm run build

# Stage 2: Build Backend
FROM python:3.10-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./backend/requirements.txt .

RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install ultralytics --no-deps && \
    pip install -r requirements.txt

COPY ./backend/app ./app

COPY --from=frontend-builder /frontend/dist ./app/build

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]