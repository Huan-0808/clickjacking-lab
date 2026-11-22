# Labtainer: Clickjacking (UI Redressing) Attack & Defense

Bài lab thực hành tấn công và phòng thủ Clickjacking trên nền tảng **Labtainers**, mô phỏng môi trường ví điện tử NovaPay hiện đại.

## 📌 Tổng quan kịch bản
- **Nạn nhân (victim - `172.25.0.2:5000`)**: Chạy ứng dụng ví điện tử NovaPay (giao diện gradient tím-xanh, thẻ bo góc, bảng giao dịch phân biệt màu, nút chuyển tiền). Ứng dụng ban đầu thiếu các header bảo mật chống nhúng khung (`X-Frame-Options` và `Content-Security-Policy: frame-ancestors`).
- **Kẻ tấn công (attacker - `172.25.0.3:8000`)**: Chạy trang web khuyến mãi mồi nhử "Nhận quà tặng 500.000đ" có đồng hồ đếm ngược và nút nhận quà. Sinh viên hoàn thiện việc nhúng iframe NovaPay đè lên nút nhận quà với độ trong suốt và căn chỉnh tọa độ chính xác.

## 🎯 6 Nhiệm vụ (Tasks)
1. **Task 1**: Khởi động lab, đăng nhập NovaPay bằng tài khoản mẫu `nan_nhan` / `123456`, xác định endpoint nhạy cảm `/transfer`.
2. **Task 2**: Sử dụng `curl -I http://victim:5000/transfer` trên container attacker để kiểm tra các header phản hồi và phát hiện thiếu header chống nhúng khung.
3. **Task 3**: Tạo file `~/www/test.html` trên container attacker nhúng iframe để chứng minh lỗ hổng nhúng khung (Proof-of-Concept).
4. **Task 4**: Hoàn thiện trang mồi `~/www/index.html` (thêm thuộc tính làm trong suốt `opacity: 0`, căn chỉnh `position: absolute` và `z-index` để nút "Xác nhận chuyển tiền" nằm khớp dưới nút "Nhận quà ngay").
5. **Task 5**: Thực hiện cuộc tấn công clickjacking khi nạn nhân đăng nhập, kích hoạt chuyển tiền trái phép đến ví của kẻ tấn công.
6. **Task 6**: Vá lỗ hổng trên `app.py` bằng cách bật các header phòng vệ `X-Frame-Options: DENY` và `Content-Security-Policy: frame-ancestors 'none'`, sau đó kiểm chứng iframe bị trình duyệt chặn hoàn toàn.

## 📦 Cài đặt qua Labtainer IModule
Để tích hợp bài lab này vào hệ thống Labtainers:
```bash
imodule https://github.com/Huan-0808/clickjacking-lab/raw/master/imodule_clickjacking.tar
```
Hoặc tải trực tiếp file `imodule_clickjacking.tar` và chạy:
```bash
imodule file:///đường/dẫn/đến/imodule_clickjacking.tar
labtainer clickjacking
```

## 📁 Cấu trúc thư mục
- `imodule_clickjacking.tar`: Gói phân phối sẵn cho Labtainers
- `config/`: Cấu hình mạng, IP, X11 và tham số khởi động (`start.config`, `parameter.config`)
- `instr_config/`: Cấu hình chấm điểm tự động (`results.config`, `goals.config`)
- `dockerfiles/`: Dockerfile cho 2 container `victim` và `attacker`
- `docs/`: Tài liệu hướng dẫn thực hành (`read_first.txt`, `clickjacking.tex`)
- `victim/`: Mã nguồn ứng dụng NovaPay (`app.py`, cấu hình Firefox)
- `attacker/`: Trang web mồi khuyến mãi (`index.html`, cấu hình máy chủ web)
