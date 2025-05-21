# Mô Hình Phân Đoạn Mảnh Đá

## Tổng Quan

Mô hình Phân Đoạn Mảnh Đá AIC-HCMUS được thiết kế để nhận dạng và phân đoạn các mảnh đá trong hình ảnh. Mô hình sử dụng kiến trúc dựa trên YOLOv11 để phát hiện từng mảnh đá riêng biệt, tạo mask phân đoạn chính xác và ước tính đường kính tương đương của mảnh đá.

## Kiến Trúc Mô Hình

- **Mô Hình Cơ Sở**: YOLOv11m với khả năng phân đoạn
- **Nguồn**: Được lưu trữ trên Hugging Face Hub (`magnusdtd/aic-hcmus-2025-yolo11m-seg`)
- **Tệp**: `yolov11m_finetuned.pt`

## Tính Năng Chính

- **Phát Hiện Mảnh Đá**: Nhận diện chính xác từng mảnh đá riêng biệt trong hình ảnh
- **Phân Đoạn Đối Tượng**: Tạo mask pixel chính xác cho mỗi mảnh đá được phát hiện
- **Ước Tính Đường Kính Tương Đương**: Tính toán đường kính tương đương dựa trên hình dạng mảnh đá
- **Hiển Thị**: Tạo hình ảnh với lớp phủ màu để kiểm tra trực quan

## Hướng tiếp cận

### Phân Tích Hình Dạng
Đối với mỗi mảnh đá được phát hiện, mô hình tính toán một số thuộc tính hình học:

- **Độ Tròn**: $C = \frac{4\pi A}{P^2}$
    - Trong đó $A$ là diện tích đường viền và $P$ là chu vi
    - Hình tròn hoàn hảo có $C = 1$
    - Các hình dạng phức tạp, không đều có $C \ll 1$

- **Đường Kính Tương Đương**: $D_{eq} = \sqrt{\frac{4A}{\pi}}$
    - Đường kính của một hình tròn có cùng diện tích với mảnh đá

### Ước Tính Đường Kính Tương Đương
Đường kính tương đương ($D_{eq}$) được sử dụng để mô tả kích thước của mảnh đá, giúp so sánh các mảnh đá có hình dạng khác nhau một cách nhất quán. Đường kính này được tính theo công thức:

$$D_{eq} = \sqrt{\frac{4A}{\pi}}$$

Trong đó $A$ là diện tích của mảnh đá. Đường kính tương đương là đường kính của hình tròn có diện tích bằng với diện tích của mảnh đá thực tế.

Phương pháp này cung cấp một chỉ số kích thước đơn giản, dễ so sánh giữa các mảnh đá khác nhau, bất kể hình dạng thực tế của chúng.

### Phát Hiện Hiệu Chuẩn
Đối với các đối tượng hiệu chuẩn (thường là các hình cầu màu đỏ), mô hình phân tích đường viền bằng:

$$C = \frac{4\pi A}{P^2} > 0.7$$

Trong đó các đối tượng hiệu chuẩn phải có độ tròn cao để được coi là đối tượng tham chiếu hợp lệ.

## Ghi Chú Hiệu Suất
- Thực thi mặc định trên CPU
- Thời gian xử lý phụ thuộc vào độ phân giải hình ảnh và số lượng mảnh đá
- Kết quả tối ưu với các mảnh đá rõ ràng, được tách biệt
- Độ phân giải hình ảnh khuyến nghị: 640×640 pixels

## Hạn Chế
- Đường kính tương đương là xấp xỉ dựa trên phép chiếu 2D
- Hiệu suất có thể giảm với các mảnh đá đông đúc hoặc chồng lấp
- Kết quả tốt nhất đạt được với ánh sáng và độ tương phản tốt
