# Tài liệu API

Tài liệu này mô tả các endpoint REST API cho backend Phân đoạn Mảnh vỡ AIC-HCMUS (FastAPI).

## Xác thực

### `POST /auth/register`
Đăng ký người dùng mới.

- **Request Body:**  
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Phản hồi:**  
  - `201 Created` nếu thành công

---

### `POST /auth/login`
Xác thực người dùng và nhận token JWT.

- **Request Body:**  
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Phản hồi:**  
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

---

## Dự đoán Ảnh

### `POST /predict`
Tải lên một ảnh và nhận kết quả phân đoạn.

- **Yêu cầu:**  
  - Content-Type: `multipart/form-data`
  - Trường form: `file` (tệp ảnh)
- **Phản hồi:**  
  ```json
  {
    "result": "segmentation_result_url_or_data"
  }
  ```

---

## Ảnh Người Dùng

### `GET /images`
Lấy danh sách các ảnh đã tải lên của người dùng.

- **Headers:**  
  - `Authorization: Bearer <token>`
- **Phản hồi:**  
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
Lấy một ảnh cụ thể hoặc kết quả phân đoạn của nó.

- **Headers:**  
  - `Authorization: Bearer <token>`
- **Phản hồi:**  
  - Tệp ảnh hoặc dữ liệu phân đoạn

---

## Kiểm tra Lỗi API

### `GET /health`
Kiểm tra API có đang hoạt động không.

- **Phản hồi:**  
  ```json
  {
    "status": "ok"
  }
  ```

---

## Phản hồi Lỗi

- `401 Unauthorized`: Xác thực không hợp lệ hoặc thiếu.
- `404 Not Found`: Không tìm thấy tài nguyên.
- `422 Unprocessable Entity`: Dữ liệu đầu vào không hợp lệ.

---

**Lưu ý:**  
Tất cả các endpoint (trừ `/auth/*` và `/health`) đều yêu cầu xác thực qua Bearer token.
