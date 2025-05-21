# 🚀 Phân Mảnh AIC-HCMUS

Chào mừng đến với **Phân Mảnh AIC-HCMUS**—giải pháp tất cả trong một để phân tích và tái tạo các mảnh đá vỡ. Được hỗ trợ bởi thị giác máy tính và học sâu, nền tảng của chúng tôi mang lại kết quả phân mảnh và ước tính thể tích chính xác, đáng tin cậy.

---

## ✨ Tính Năng Nổi Bật

### 🖥️ Giao Diện Người Dùng
- Giao diện hiện đại xây dựng bằng **React** & **TypeScript**
- Bố cục đẹp mắt với **TailwindCSS**
- Điều hướng mượt mà qua **React Router**
- Xác thực người dùng an toàn (đăng nhập/đăng ký)
- Tải ảnh lên, dự đoán và hiển thị kết quả dễ dàng (mặt nạ chồng lên ảnh, dữ liệu thể tích)
- Các thành phần mô-đun: Dự đoán, Ảnh Người Dùng, Tabs, và nhiều hơn nữa

### ⚡ Backend
- API nhanh, mở rộng với **FastAPI**
- Xác thực dựa trên JWT
- Các endpoint để tải ảnh, chạy dự đoán và lấy kết quả
- Tích hợp **YOLOv11m** cho phân mảnh & tính toán thể tích
- Dữ liệu lưu trữ trong **PostgreSQL**; ảnh & mặt nạ trong **MinIO**

### 🤖 Máy Học
- Mô hình phân mảnh **YOLOv11m** tiên tiến (từ Hugging Face)
- Tự động phát hiện vật thể hiệu chuẩn (ví dụ: bóng đỏ) để ước tính thể tích chính xác
- Tạo mặt nạ chồng lên ảnh và tính toán thể tích vật thể

### ☁️ Hạ Tầng
- **Docker Compose** để thiết lập cục bộ dễ dàng
- Tập lệnh **Kubernetes** cho triển khai mở rộng (PostgreSQL, MinIO, ứng dụng, NGINX)
- CI/CD tự động với **GitHub Actions**—triển khai trực tiếp lên Google Kubernetes Engine (GKE)

## 🗺️ Kiến Trúc Hệ Thống

![Sơ đồ Kiến trúc Hệ thống](assets/app-architecture.jpg)
