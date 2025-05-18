# Ứng Dụng Phân Đoạn Mảnh Đá

## Quy Trình Người Dùng

### 1. Truy Cập & Xác Thực
- Người dùng kết nối thông qua trình duyệt web với phân giải tên miền qua DuckDNS
- Các tùy chọn xác thực:
    - Người dùng mới: Đăng ký với tên người dùng/mật khẩu
    - Người dùng đã có tài khoản: Hệ thống đăng nhập dựa trên JWT
- Bảo mật được thực hiện thông qua FastAPI với mã hóa mật khẩu bcrypt

### 2. Xử Lý Hình Ảnh
- **Tùy Chọn Upload**:
    - Upload thông thường (chỉ lưu trữ)
    - Upload với yêu cầu xử lý ngay lập tức
- **Quy Trình Phân Tích**:
    - Mô hình phân đoạn YOLOv11 xác định từng mảnh đá riêng biệt
    - Tạo mask chính xác cho từng mảnh đá
    - Tính toán thể tích áp dụng các thuật toán hình học cho mỗi mask
    - Hiển thị kết quả bao gồm lớp phủ mã màu để nhận diện trực quan

### 3. Quản Lý Kết Quả
- Lịch sử xử lý có thể truy cập thông qua bảng điều khiển người dùng
- Các phân tích trước đây có sẵn để truy xuất và so sánh
- Tùy chọn xử lý lại hình ảnh với các thông số được điều chỉnh

## Kiến Trúc Kỹ Thuật

### 1. Xử Lý Yêu Cầu & Cân Bằng Tải
- Nginx đóng vai trò là điểm vào và cân bằng tải
- Các yêu cầu đến được phân phối đến các phiên bản backend FastAPI

### 2. Quy Trình Xử Lý
- FastAPI xử lý tải lên hình ảnh và quản lý lưu trữ tạm thời
- Mô hình YOLOv11 (từ Hugging Face Hub) thực hiện phân đoạn
- OpenCV xử lý hình ảnh và tính toán thể tích
- Luồng kết quả: Upload → Xử lý → Lưu trữ Cơ sở dữ liệu → Hiển thị cho Người dùng

### 3. Cơ Sở Hạ Tầng Dữ Liệu
- **Cơ Sở Dữ Liệu PostgreSQL**:
    - Lưu trữ hồ sơ người dùng, dữ liệu xác thực
    - Duy trì metadata hình ảnh và kết quả phân tích
    - Tương tác thông qua SQLAlchemy ORM với việc di chuyển Alembic
- **Hệ Thống Lưu Trữ (MinIO)**:
    - Lưu trữ đối tượng tương thích S3 cho dữ liệu nhị phân
    - Hình ảnh gốc được bảo quản để tham khảo
    - Các lớp phủ đã xử lý được lưu trữ để truy xuất nhanh
    - Thiết kế có thể mở rộng cho truy cập hình ảnh hiệu suất cao

### 4. Kiến Trúc Frontend
- Giao diện người dùng dựa trên React với các component Material-UI
- Axios xử lý giao tiếp API RESTful
- Các tính năng phía máy khách:
    - Quản lý xác thực người dùng
    - Giao diện tải lên hình ảnh
    - Hiển thị kết quả tương tác

### 5. Cơ Sở Hạ Tầng Triển Khai
- Container Docker cho môi trường nhất quán
- Phát triển: Docker Compose cho kiểm thử cục bộ
- Sản xuất: Phối hợp Kubernetes để mở rộng
- Nginx reverse proxy cho quản lý lưu lượng

### 6. Giám Sát & Quan Sát
- **Giám Sát Hiệu Suất**: Số liệu Prometheus với bảng điều khiển Grafana
- **Ghi nhật ký**: ELK stack (Elasticsearch, Logstash, Kibana)
- **Cảnh báo**: Thông báo tự động cho các vấn đề hệ thống

### 7. Khung Bảo Mật
- Xác thực JWT cho tất cả tương tác API
- Hệ thống kiểm soát truy cập dựa trên vai trò
- Lưu trữ và truyền thông tin xác thực an toàn

### 8. Cấu Trúc API
- Các endpoints chính:
    - **Xác thực**: `/api/auth/*`
    - **Upload Cơ bản**: `/api/upload`
    - **Xử lý & Phân tích**: `/api/upload_predict`
    - **Truy xuất Kết quả**: `/api/fetch_prediction`