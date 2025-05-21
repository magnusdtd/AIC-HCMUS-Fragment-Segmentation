# Tài liệu API

Tài liệu này mô tả các endpoint REST API cho backend Phân đoạn Mảnh vỡ AIC-HCMUS (FastAPI).

### API Xác thực

- **`GET /current-user`**
  - **Mô tả**: Lấy thông tin người dùng hiện tại đã xác thực.
  - **Yêu cầu**: Cần token hợp lệ trong header.
  - **Phản hồi**:
    - Thành công:
      ```json
      {
        "id": "<user_id>",
        "username": "<username>",
        "email": "<email>",
        "full_name": "<full_name>",
        "profile_picture": "<profile_picture_url>"
      }
      ```
    - Lỗi:
      ```json
      {
        "detail": "Token không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại."
      }
      ```

- **`POST /register`**
  - **Mô tả**: Đăng ký người dùng mới.
  - **Request Body**:
    ```json
    {
      "username": "<username>",
      "password": "<password>",
      "email": "<email>",
      "full_name": "<full_name>"
    }
    ```
  - **Phản hồi**:
    - Thành công:
      ```json
      {
        "message": "Đăng ký người dùng thành công."
      }
      ```
    - Lỗi:
      ```json
      {
        "detail": "Tên người dùng đã tồn tại."
      }
      ```

- **`POST /login`**
  - **Mô tả**: Xác thực người dùng và cung cấp token truy cập.
  - **Request Body**:
    ```json
    {
      "username": "<username>",
      "password": "<password>"
    }
    ```
  - **Phản hồi**:
    - Thành công:
      ```json
      {
        "access_token": "<token>",
        "token_type": "bearer"
      }
      ```
    - Lỗi:
      ```json
      {
        "detail": "Tên người dùng hoặc mật khẩu không hợp lệ."
      }
      ```

---

### API Xác thực Google

- **`GET /google-login`**
  - **Mô tả**: Khởi tạo đăng nhập Google OAuth2.
  - **Phản hồi**: Chuyển hướng đến trang ủy quyền của Google.

- **`GET /google-callback`**
  - **Mô tả**: Xử lý callback từ Google sau khi người dùng ủy quyền.
  - **Yêu cầu**: Cần phiên làm việc hợp lệ.
  - **Phản hồi**:
    - Thành công: Chuyển hướng đến frontend với token truy cập dưới dạng tham số query.
    - Lỗi:
      ```json
      {
        "detail": "Lỗi Google OAuth: <error_message>"
      }
      ```

---

### API Ảnh

- **`GET /display_images`**
  - **Mô tả**: Lấy danh sách các ảnh đã tải lên bởi người dùng hiện tại.
  - **Yêu cầu**: Cần xác thực.
  - **Phản hồi**:
    - Thành công:
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
    - Lỗi:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /fetch_image/{filename}`**
  - **Mô tả**: Lấy một ảnh theo tên tệp.
  - **Tham số đường dẫn**: `filename` - Tên của tệp ảnh.
  - **Phản hồi**:
    - Thành công: Trả về nội dung ảnh với MIME type phù hợp.
    - Nếu không tìm thấy ảnh:
      ```json
      {
        "detail": "Không tìm thấy ảnh."
      }
      ```
    - Lỗi:
      ```json
      {
        "detail": "Lỗi khi lấy ảnh: <error_message>"
      }
      ```

- **`GET /check_image_exists`**
  - **Mô tả**: Kiểm tra xem một ảnh có tồn tại trên máy chủ hay không.
  - **Tham số query**: `img_name` - Tên của ảnh cần kiểm tra.
  - **Phản hồi**:
    - Nếu ảnh tồn tại:
      ```json
      {
        "exists": true,
        "message": "Ảnh đã tồn tại trên máy chủ.",
        "metadata": {
          "id": "<image_id>",
          "filename": "<image_filename>",
          "size": "<image_size>",
          "upload_time": "<image_upload_time>"
        }
      }
      ```
    - Nếu ảnh không tồn tại:
      ```json
      {
        "exists": false,
        "message": "Ảnh không tồn tại trên máy chủ."
      }
      ```
    - Lỗi:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

---

### API Dự đoán

- **`POST /upload`**
  - **Mô tả**: Tải lên một ảnh để xử lý.
  - **Request Body**: Tệp ảnh.
  - **Phản hồi**:
    - Thành công:
      ```json
      {
        "message": "Tệp đã được tải lên thành công.",
        "metadata": {
          "id": "<image_id>",
          "filename": "<image_filename>",
          "size": "<image_size>",
          "upload_time": "<image_upload_time>"
        }
      }
      ```
    - Lỗi:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`POST /upload_predict/{real_radius}&{unit}&{conf}&{iou}`**
  - **Mô tả**: Tải lên một ảnh và bắt đầu dự đoán.
  - **Tham số đường dẫn**:
    - `real_radius`: Bán kính thực của đối tượng.
    - `unit`: Đơn vị đo lường.
    - `conf`: Ngưỡng độ tin cậy.
    - `iou`: Ngưỡng Intersection over Union.
  - **Request Body**: Tệp ảnh.
  - **Phản hồi**:
    - Thành công:
      ```json
      {
        "task_id": "<task_id>"
      }
      ```
    - Lỗi:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /task_status/{task_id}`**
  - **Mô tả**: Lấy trạng thái của một tác vụ dự đoán.
  - **Tham số đường dẫn**: `task_id` - ID của tác vụ.
  - **Phản hồi**:
    - Thành công:
      ```json
      {
        "status": "<task_status>"
      }
      ```
    - Lỗi:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /fetch_prediction/{task_id}`**
  - **Mô tả**: Lấy kết quả dự đoán cho một tác vụ.
  - **Tham số đường dẫn**: `task_id` - ID của tác vụ.
  - **Phản hồi**:
    - Thành công: Trả về dữ liệu dự đoán.
    - Lỗi:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /get_user_tasks`**
  - **Mô tả**: Lấy tất cả các tác vụ liên quan đến người dùng hiện tại.
  - **Phản hồi**:
    - Thành công:
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
    - Lỗi:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /re_predict/{real_radius}&{img_name}&{unit}&{conf}&{iou}`**
  - **Mô tả**: Chạy lại dự đoán trên một ảnh với các tham số mới.
  - **Tham số đường dẫn**: Tương tự như `/upload_predict`.
  - **Phản hồi**:
    - Thành công:
      ```json
      {
        "task_id": "<task_id>"
      }
      ```
    - Lỗi:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /get_prediction/{task_id}`**
  - **Mô tả**: Lấy chi tiết dự đoán cho một tác vụ cụ thể.
  - **Tham số đường dẫn**: `task_id` - ID của tác vụ.
  - **Phản hồi**:
    - Thành công: Trả về chi tiết dự đoán.
    - Lỗi:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

- **`GET /download_results/{task_id}`**
  - **Mô tả**: Tải xuống kết quả của một tác vụ dự đoán.
  - **Tham số đường dẫn**: `task_id` - ID của tác vụ.
  - **Phản hồi**:
    - Thành công: Trả về tệp ZIP chứa kết quả.
    - Lỗi:
      ```json
      {
        "detail": "<error_message>"
      }
      ```

---

## Phản hồi Lỗi

- `401 Unauthorized`: Xác thực không hợp lệ hoặc thiếu.
- `404 Not Found`: Không tìm thấy tài nguyên.
- `422 Unprocessable Entity`: Dữ liệu đầu vào không hợp lệ.

---

**Lưu ý**:
Tất cả các endpoint (trừ `/login/` và `/register`) đều yêu cầu xác thực qua token.
