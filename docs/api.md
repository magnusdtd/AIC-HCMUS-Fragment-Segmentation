# API Documentation

This document describes the REST API endpoints for the AIC-HCMUS Fragment Segmentation backend (FastAPI).

## Authentication

### `POST /auth/register`
Register a new user.

- **Request Body:**  
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response:**  
  - `201 Created` on success

---

### `POST /auth/login`
Authenticate a user and obtain a JWT token.

- **Request Body:**  
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response:**  
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

---

## Image Prediction

### `POST /predict`
Upload an image and receive segmentation results.

- **Request:**  
  - Content-Type: `multipart/form-data`
  - Form field: `file` (image file)
- **Response:**  
  ```json
  {
    "result": "segmentation_result_url_or_data"
  }
  ```

---

## User Images

### `GET /images`
Get a list of user-uploaded images.

- **Headers:**  
  - `Authorization: Bearer <token>`
- **Response:**  
  ```json
  [
    {
      "id": 1,
      "filename": "image.jpg",
      "uploaded_at": "2024-01-01T12:00:00"
    }
  ]
  ```

---

### `GET /images/{image_id}`
Get a specific image or its segmentation result.

- **Headers:**  
  - `Authorization: Bearer <token>`
- **Response:**  
  - Image file or segmentation data

---

## Health Check

### `GET /health`
Check if the API is running.

- **Response:**  
  ```json
  {
    "status": "ok"
  }
  ```

---

## Error Responses

- `401 Unauthorized`: Invalid or missing authentication.
- `404 Not Found`: Resource does not exist.
- `422 Unprocessable Entity`: Invalid input.

---

**Note:**  
All endpoints (except `/auth/*` and `/health`) require authentication via Bearer token.
