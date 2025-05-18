# Mô Hình Phân Đoạn Mảnh Đá

## Tổng Quan

Mô hình Phân Đoạn Mảnh Đá AIC-HCMUS được thiết kế để nhận dạng và phân đoạn các mảnh đá trong hình ảnh. Mô hình sử dụng kiến trúc dựa trên YOLOv11 để phát hiện từng mảnh đá riêng biệt, tạo mask phân đoạn chính xác và ước tính thể tích của mảnh đá.

## Kiến Trúc Mô Hình

- **Mô Hình Cơ Sở**: YOLOv11m với khả năng phân đoạn
- **Nguồn**: Được lưu trữ trên Hugging Face Hub (`magnusdtd/aic-hcmus-2025-yolo11m-seg`)
- **Tệp**: `yolov11m_finetuned.pt`

## Tính Năng Chính

- **Phát Hiện Mảnh Đá**: Nhận diện chính xác từng mảnh đá riêng biệt trong hình ảnh
- **Phân Đoạn Đối Tượng**: Tạo mask pixel chính xác cho mỗi mảnh đá được phát hiện
- **Ước Tính Thể Tích**: Tính toán thể tích xấp xỉ dựa trên hình dạng mảnh đá
- **Hiển Thị**: Tạo hình ảnh với lớp phủ màu để kiểm tra trực quan

## Hướng tiếp cận

### Phân Tích Hình Dạng
Đối với mỗi mảnh đá được phát hiện, mô hình tính toán một số thuộc tính hình học:

- **Độ Tròn**: $C = \frac{4\pi A}{P^2}$
    - Trong đó $A$ là diện tích đường viền và $P$ là chu vi
    - Hình tròn hoàn hảo có $C = 1$
    - Các hình dạng phức tạp, không đều có $C \ll 1$

- **Tỷ Lệ Khung**: $AR = \frac{a}{b}$
    - Trong đó $a$ và $b$ là trục chính và trục phụ của ellipse vừa khít

- **Đường Kính Tương Đương**: $D_{eq} = \sqrt{\frac{4A}{\pi}}$
    - Đường kính của một hình tròn có cùng diện tích với mảnh đá

### Ước Tính Thể Tích
Ước tính thể tích sử dụng kết hợp có trọng số của ba phương pháp:

- **Xấp Xỉ Hình Cầu**: $V_{sphere} = \frac{4}{3}\pi\left(\frac{D_{eq}}{2}\right)^3$

- **Xấp Xỉ Hình Ellipsoid**: $V_{ellipsoid} = \frac{4}{3}\pi\left(\frac{a}{2}\right)\left(\frac{b}{2}\right)^2$
    - Giả định rằng trục thứ ba bằng trục phụ

- **Công Thức Thực Nghiệm**: $V_{empirical} = A^{1.5} \times (0.8 + 0.4C)$
    - Được rút ra từ các tương quan thực nghiệm

Thể tích cuối cùng là trung bình có trọng số dựa trên độ tròn:

$$V_{final} = \begin{cases}
0.6V_{sphere} + 0.2V_{ellipsoid} + 0.2V_{empirical} & \text{if } C > 0.8 \\
0.3V_{sphere} + 0.4V_{ellipsoid} + 0.3V_{empirical} & \text{if } C > 0.5 \\
0.1V_{sphere} + 0.5V_{ellipsoid} + 0.4V_{empirical} & \text{otherwise}
\end{cases}$$

Phương pháp thích ứng này cung cấp ước tính chính xác hơn trên nhiều hình dạng mảnh đá khác nhau.

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
- Ước tính thể tích là xấp xỉ dựa trên phép chiếu 2D
- Hiệu suất có thể giảm với các mảnh đá đông đúc hoặc chồng lấp
- Kết quả tốt nhất đạt được với ánh sáng và độ tương phản tốt