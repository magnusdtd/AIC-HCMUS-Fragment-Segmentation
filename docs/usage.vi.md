# Hướng Dẫn Sử Dụng

Hướng dẫn này giải thích cách sử dụng ứng dụng Phân Đoạn Mảnh Vỡ AIC-HCMUS, từ cài đặt đến dự đoán.

---

## 1. Yêu Cầu Trước

- Đã cài đặt Docker và Docker Compose
- Trình duyệt web hiện đại (cho giao diện frontend)
- (Tùy chọn) Python 3.10+ và Node.js (nếu cài đặt thủ công)

---

## 2. Khởi Động Ứng Dụng

### Sử Dụng Docker Compose

1. Tạo bản sao mã nguồn:
   ```sh
   git clone https://github.com/magnusdtd/AIC-HCMUS-Fragment-Segmentation.git
   cd AIC-HCMUS-Fragment-Segmentation
   ```

2. Khởi động tất cả dịch vụ:
   ```sh
   docker-compose up --build
   ```

3. Truy cập website tại [http://localhost](http://localhost)  

---

## 3. Cài Đặt Thủ Công (Phát Triển)

### Backend

1. Cài đặt các thư viện phụ thuộc:
   ```
   cd backend
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
   pip install ultralytics --no-deps && \
   pip install -r requirements.txt
   ```

2. Khởi động máy chủ FastAPI:
   ```
   uvicorn app.main:app --reload
   ```

### Frontend

1. Cài đặt các thư viện phụ thuộc:
   ```
   cd frontend
   npm install
   ```

2. Khởi động máy chủ phát triển:
   ```
   npm run dev
   ```

---

## 4. Quy Trình Sử Dụng

### 1. Đăng Ký và Đăng Nhập

- Mở ứng dụng web.
- Đăng ký tài khoản mới hoặc đăng nhập bằng tài khoản đã có.

### 2. Tải Ảnh Lên

- Chuyển đến trang dự đoán.
- Tải lên một tệp ảnh (ví dụ: ảnh mảnh vỡ).
- Gửi để nhận kết quả phân đoạn.

### 3. Xem Kết Quả

- Kết quả phân đoạn sẽ hiển thị trên trang.
- Bạn có thể xem lại ảnh đã tải lên và kết quả trong trang cá nhân.

---

## 5. Sử Dụng API

- Xem [Tài liệu API](api.md) để biết chi tiết về các endpoint và định dạng yêu cầu.

---

## 6. Khắc Phục Sự Cố

- Đảm bảo các container Docker đang chạy (`docker ps`).
- Kiểm tra log để tìm lỗi (`docker-compose logs`).
- Nếu cài đặt thủ công, kiểm tra đã cài đủ các thư viện phụ thuộc.

---

Để được hỗ trợ thêm, xem trang [Giới Thiệu](about.md) hoặc tạo issue trên GitHub.