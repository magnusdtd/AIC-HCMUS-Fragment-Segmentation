# Stage 1: Build Frontend
FROM node:18 AS frontend-builder

WORKDIR /frontend

# Copy frontend source code
COPY ./frontend/package.json ./frontend/package-lock.json ./
RUN npm install

COPY ./frontend ./
RUN npm run build

# Stage 2: Build Backend
FROM python:3.10-slim AS backend

WORKDIR /app

# Install backend dependencies
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY ./backend/app ./app

# Copy frontend build files from the frontend-builder stage
COPY --from=frontend-builder /frontend/dist ./app/build

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Expose port
EXPOSE 8080

# Run the backend application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]