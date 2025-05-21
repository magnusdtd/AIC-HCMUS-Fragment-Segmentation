# API Documentation

This document describes the REST API endpoints for the AIC-HCMUS Fragment Segmentation backend (FastAPI).

### Authentication APIs

- **`GET /current-user`**
  - **Description**: Retrieves the current authenticated user.
  - **Dependencies**: Requires a valid token in the header field.
  - **Response**:
    - On success:
      ```json
      {
        "id": "<user_id>",
        "username": "<username>",
        "email": "<email>",
        "full_name": "<full_name>",
        "profile_picture": "<profile_picture_url>"
      }
      ```
    - On error:
      ```json
      {
        "detail": "Invalid or expired token. Please log in again."
      }
      ```

- **`POST /register`**
  - **Description**: Registers a new user.
  - **Request Body**:
    ```json
    {
      "username": "<username>",
      "password": "<password>",
      "email": "<email>",
      "full_name": "<full_name>"
    }
    ```
  - **Response**:
    - On success:
      ```json
      {
        "message": "User registered successfully."
      }
      ```
    - On error:
      ```json
      {
        "detail": "Username already exists"
      }
      ```

- **`POST /login`**
  - **Description**: Authenticates a user and provides an access token.
  - **Request Body**:
    ```json
    {
      "username": "<username>",
      "password": "<password>"
    }
    ```
  - **Response**:
    - On success:
      ```json
      {
        "access_token": "<token>",
        "token_type": "bearer"
      }
      ```
    - On error:
      ```json
      {
        "detail": "Invalid username or password"
      }
      ```

---

### Google Authentication APIs

- **`GET /google-login`**
  - **Description**: Initiates Google OAuth2 login.
  - **Response**: Redirects to Google's authorization page.

- **`GET /google-callback`**
  - **Description**: Handles the callback from Google after user authorization.
  - **Dependencies**: Requires a valid session.
  - **Response**:
    - On success:
      Redirects to the frontend with the access token as a query parameter.
    - On error:
      ```json
      {
        "detail": "Google OAuth error: <error_message>"
      }
      ```

---

### Image APIs

- **`GET /display_images`**
  - **Description**: Retrieves a list of images uploaded by the current user.
  - **Dependencies**: Requires authentication.
  - **Response**:
    - On success:
      ```json
      {
        "images": [
          {
            "id": "<image_id>",
            "filename": "<image_filename>",
            "size": "<image_size>",
            "upload_time": "<image_upload_time>"
          }
        ]
      }
      ```
    - On error:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /fetch_image/{filename}`**
  - **Description**: Fetches an image by its filename.
  - **Path Parameter**: `filename` - Name of the image file.
  - **Response**:
    - On success:
      Returns the image content with the appropriate MIME type.
    - If the image is not found:
      ```json
      {
        "detail": "Image not found"
      }
      ```
    - On error:
      ```json
      {
        "detail": "Error fetching image: <error_message>"
      }
      ```

- **`GET /check_image_exists`**
  - **Description**: Checks if an image exists on the server.
  - **Query Parameter**: `img_name` - Name of the image to check.
  - **Response**:
    - If the image exists:
      ```json
      {
        "exists": true,
        "message": "Image already exists on the server.",
        "metadata": {
          "id": "<image_id>",
          "filename": "<image_filename>",
          "size": "<image_size>",
          "upload_time": "<image_upload_time>"
        }
      }
      ```
    - If the image does not exist:
      ```json
      {
        "exists": false,
        "message": "Image does not exist on the server."
      }
      ```
    - On error:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

---

### Prediction APIs

- **`POST /upload`**
  - **Description**: Uploads an image for processing.
  - **Request Body**: Image file.
  - **Response**:
    - On success:
      ```json
      {
        "message": "File uploaded successfully",
        "metadata": {
          "id": "<image_id>",
          "filename": "<image_filename>",
          "size": "<image_size>",
          "upload_time": "<image_upload_time>"
        }
      }
      ```
    - On error:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`POST /upload_predict/{real_radius}&{unit}&{conf}&{iou}`**
  - **Description**: Uploads an image and initiates prediction.
  - **Path Parameters**:
    - `real_radius`: Real radius of the object.
    - `unit`: Unit of measurement.
    - `conf`: Confidence threshold.
    - `iou`: Intersection over Union threshold.
  - **Request Body**: Image file.
  - **Response**:
    - On success:
      ```json
      {
        "task_id": "<task_id>"
      }
      ```
    - On error:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /task_status/{task_id}`**
  - **Description**: Retrieves the status of a prediction task.
  - **Path Parameter**: `task_id` - ID of the task.
  - **Response**:
    - On success:
      ```json
      {
        "status": "<task_status>"
      }
      ```
    - On error:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /fetch_prediction/{task_id}`**
  - **Description**: Fetches prediction results for a task.
  - **Path Parameter**: `task_id` - ID of the task.
  - **Response**:
    - On success:
      Returns prediction data.
    - On error:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /get_user_tasks`**
  - **Description**: Retrieves all tasks associated with the current user.
  - **Response**:
    - On success:
      ```json
      {
        "tasks": [
          {
            "task_id": "<task_id>",
            "created_at": "<timestamp>"
          }
        ]
      }
      ```
    - On error:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /re_predict/{real_radius}&{img_name}&{unit}&{conf}&{iou}`**
  - **Description**: Re-runs prediction on an image with new parameters.
  - **Path Parameters**: Similar to `/upload_predict`.
  - **Response**:
    - On success:
      ```json
      {
        "task_id": "<task_id>"
      }
      ```
    - On error:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /get_prediction/{task_id}`**
  - **Description**: Retrieves prediction details for a specific task.
  - **Path Parameter**: `task_id` - ID of the task.
  - **Response**:
    - On success:
      Returns prediction details.
    - On error:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /download_results/{task_id}`**
  - **Description**: Downloads the results of a prediction task.
  - **Path Parameter**: `task_id` - ID of the task.
  - **Response**:
    - On success:
      Returns a ZIP file containing the results.
    - On error:
      ```json
      {
        "detail": "<error_message>"
      }
      ```
---

## Error Responses
- `401 Unauthorized`: Invalid or missing authentication.
- `404 Not Found`: Resource not found.
- `422 Unprocessable Entity`: Invalid input data.

---

**Note**:  
All endpoints (except `/login/` and `/register`) require token-based authentication.