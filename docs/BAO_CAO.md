# BÁO CÁO THỰC HÀNH VÀ PHÁT TRIỂN LAB LABTAINERS
# ĐỀ TÀI: TẤN CÔNG VÀ PHÒNG THỦ CLICKJACKING TRÊN NỀN TẢNG VÍ ĐIỆN TỬ NOVAPAY

---

## 1. GIỚI THIỆU

### 1.1. Bối cảnh và Khái niệm Clickjacking
**Clickjacking** (còn gọi là *UI Redressing Attack* - Tấn công ngụy trang giao diện) là kỹ thuật tấn công nguy hiểm trong an toàn ứng dụng web, trong đó kẻ tấn công lừa người dùng nhấp chuột vào một phần tử giao diện của trang web hợp lệ mà họ không hề hay biết. 

Bằng cách nhúng trang web mục tiêu (victim) vào một khung nội tuyến (`<iframe>`) trong suốt hoặc ngụy trang, sau đó đặt nó đè chính xác lên một phần tử hấp dẫn trên trang web của kẻ tấn công (ví dụ: nút "Nhận thưởng", video kích thích tò mò), nạn nhân tưởng rằng mình đang tương tác với trang mồi nhưng thực tế mọi thao tác nhấp chuột đều được chuyển tiếp đến trang web nạn nhân đang đăng nhập.

Hậu quả của Clickjacking rất đa dạng và nghiêm trọng:
- Thực hiện giao dịch tài chính trái phép (chuyển tiền, thanh toán hóa đơn).
- Thao túng quyền tài khoản (thay đổi mật khẩu, cấp quyền OAuth, cập nhật email khôi phục).
- Tương tác mạng xã hội giả mạo (Like, Share, Follow ngoài ý muốn).

### 1.2. Kịch bản mô phỏng trong bài Lab
Bài lab được xây dựng trên nền tảng ảo hóa giáo dục **Labtainers**, mô phỏng môi trường thực tế gồm hai thực thể độc lập:
1. **NovaPay E-Wallet (Container `victim`)**: Hệ thống ví điện tử mô phỏng chạy tại địa chỉ `http://victim:5000`. Ứng dụng cung cấp đầy đủ chức năng đăng nhập, theo dõi số dư, xem lịch sử giao dịch và tính năng chuyển tiền nhanh tại endpoint `/transfer`. Ứng dụng ban đầu tồn tại lỗ hổng nghiêm trọng do không cấu hình các HTTP response header chống nhúng khung.
2. **NovaPay Rewards Club (Container `attacker`)**: Trang web mồi nhử của kẻ tấn công chạy tại `http://attacker:8000`, ngụy trang thành chương trình tri ân "Tặng quà 500.000đ" có đồng hồ đếm ngược và nút nhận thưởng bắt mắt. Sinh viên sẽ đóng vai kẻ tấn công, sử dụng kỹ thuật CSS để làm tàng hình trang NovaPay `/transfer` và đặt nút "Xác nhận chuyển tiền" trùng khít lên nút "Nhận quà ngay".

### 1.3. Mục tiêu đào tạo
- Giúp sinh viên hiểu rõ bản chất kỹ thuật, điều kiện phát sinh và tác hại thực tế của lỗ hổng Clickjacking.
- Rèn luyện kỹ năng kiểm tra header bảo mật qua CLI (`curl -I`).
- Nắm vững kỹ thuật khai thác Client-side UI Redressing thông qua việc phối hợp các thuộc tính CSS nâng cao (`opacity`, `position`, `z-index`, `transform`).
- Thực hành triển khai giải pháp phòng thủ theo chiều sâu: Header `X-Frame-Options` và cơ chế hiện đại `Content-Security-Policy: frame-ancestors`.

---

## 2. NỘI DUNG VÀ HƯỚNG DẪN 6 NHIỆM VỤ (TASKS)

Bài lab được thiết kế theo lộ trình thực hành 6 bước liền mạch từ trinh sát, khai thác đến phòng thủ:

```
[Task 1: Khám phá NovaPay] ──> [Task 2: Trinh sát Header] ──> [Task 3: Thử nghiệm PoC Iframe]
                                                                        │
[Task 6: Vá lỗ hổng & Kiểm chứng] <── [Task 5: Thực thi Tấn công] <── [Task 4: Hoàn thiện Trang mồi]
```

### Task 1: Khám phá ứng dụng ví điện tử NovaPay
- **Mục tiêu**: Làm quen với quy trình nghiệp vụ và xác định chức năng nhạy cảm có thể bị lợi dụng.
- **Thao tác**:
  1. Mở trình duyệt Firefox trên container `victim`:
     ```bash
     firefox http://victim:5000
     ```
  2. Đăng nhập bằng tài khoản nạn nhân mẫu:
     - Tên đăng nhập: `nan_nhan`
     - Mật khẩu: (mật khẩu mặc định được định sẵn trong hệ thống)
  3. Khám phá Dashboard: quan sát số dư khả dụng ban đầu (50.000.000 đ) và lịch sử biến động số dư.
  4. Truy cập vào mục **Chuyển tiền** (`/transfer`), nhận diện nút bấm `"Xác nhận chuyển tiền"` chính là hành động quan trọng cần lừa nạn nhân bấm vào.

### Task 2: Kiểm tra các Header bảo mật chống nhúng khung
- **Mục tiêu**: Sử dụng công cụ dòng lệnh để xác định sự vắng mặt của các rào chắn phòng vệ.
- **Thao tác**:
  1. Mở terminal trên container `attacker`.
  2. Thực hiện truy vấn kiểm tra HTTP Response Header:
     ```bash
     curl -I http://victim:5000/transfer
     ```
  3. Phân tích kết quả trả về: Ứng dụng phản hồi mã `200 OK` nhưng hoàn toàn **thiếu** header `X-Frame-Options` cũng như `Content-Security-Policy: frame-ancestors`.

### Task 3: Kiểm chứng khả năng nhúng iframe (Proof-of-Concept)
- **Mục tiêu**: Chứng minh trang chuyển tiền có thể bị nạp trong ngữ cảnh iframe của tên miền độc hại.
- **Thao tác**:
  1. Trên container `attacker`, tạo file `test.html` trong thư mục web:
     ```bash
     echo '<iframe src="http://victim:5000/transfer" width="800" height="600"></iframe>' > ~/www/test.html
     ```
  2. Mở trình duyệt truy cập `http://attacker:8000/test.html`.
  3. Xác nhận giao diện ví NovaPay hiển thị nguyên vẹn bên trong website của kẻ tấn công mà không bị trình duyệt chặn.

### Task 4: Hoàn thiện trang web mồi Clickjacking
- **Mục tiêu**: Thiết kế lớp phủ giao diện chính xác để đánh lừa thị giác người dùng.
- **Thao tác**:
  1. Mở file `~/www/index.html` trên container `attacker`.
  2. Tìm đến bộ chọn CSS `#victim-iframe` (nơi có chú thích `TODO`):
     - Thiết lập độ trong suốt tuyệt đối: `opacity: 0;`
     - Thiết lập định vị tuyệt đối để tách khỏi luồng văn bản: `position: absolute;`
     - Đặt lớp hiển thị nổi lên phía trên nút mồi: `z-index: 999;`
     - Căn chỉnh tọa độ `top` và `left` sao cho nút "Xác nhận chuyển tiền" trong iframe nằm chính xác dưới nút "🎁 NHẬN QUÀ NGAY".
  3. Lưu file và kiểm tra lại trực quan.

### Task 5: Thực hiện cuộc tấn công Clickjacking
- **Mục tiêu**: Đóng vai nạn nhân để kích hoạt giao dịch ngoài ý muốn.
- **Thao tác**:
  1. Đảm bảo tài khoản `nan_nhan` đang ở trạng thái đăng nhập trên Firefox.
  2. Mở tab mới truy cập trang web mồi: `http://attacker:8000/`.
  3. Bấm vào nút "🎁 NHẬN QUÀ NGAY".
  4. Quay trở lại tab ví điện tử NovaPay (`http://victim:5000/dashboard`), nhấn F5 tải lại trang:
     - Số dư bị trừ đúng 5.000.000 đ.
     - Xuất hiện giao dịch chuyển tiền đến tài khoản `attacker_wallet`.

### Task 6: Phòng thủ và vá lỗ hổng
- **Mục tiêu**: Cấu hình các header bảo vệ chuẩn công nghiệp và kiểm chứng hiệu quả.
- **Thao tác**:
  1. Trên container `victim`, mở file mã nguồn `~/novapay/app.py`.
  2. Tìm khối chú thích `[TASK 6: VÁ LỖ HỔNG CLICKJACKING]` trong hàm `send_standard_headers`:
     ```python
     self.send_header('X-Frame-Options', 'DENY')
     self.send_header('Content-Security-Policy', "frame-ancestors 'none'")
     ```
  3. Bỏ comment hai dòng trên và lưu file.
  4. Khởi động lại dịch vụ NovaPay:
     ```bash
     ~/restart_novapay.sh
     ```
  5. Trên `attacker`, chạy lại `curl -I http://victim:5000/transfer` để xác nhận header `X-Frame-Options: DENY` đã xuất hiện.
  6. Tải lại trang mồi `http://attacker:8000/`: Xác nhận iframe bị trình duyệt từ chối hiển thị hoàn toàn.

---

## 3. PHÂN TÍCH YÊU CẦU

### 3.1. Yêu cầu Chức năng
1. **Ví điện tử NovaPay (`victim`)**:
   - Quản lý phiên đăng nhập (Session cookie) độc lập, hoạt động ổn định trong ngữ cảnh nhúng iframe cross-origin (`SameSite=None`).
   - Xử lý chuyển tiền tự động, cập nhật biến động số dư và bảng lịch sử giao dịch.
   - Cơ chế ghi log sự kiện tức thời (unbuffered flush) vào file `/home/ubuntu/novapay.log`.
   - Cơ chế phát hiện và ghi nhận thông tin nguồn gốc request (`Referer` tracking), đảm bảo phân biệt chính xác giữa việc bấm chuyển tiền từ iframe trang mồi (`dest=iframe`) và việc gõ URL trực tiếp trên trình duyệt (`dest=direct`).
2. **Trang web mồi (`attacker`)**:
   - Máy chủ HTTP tĩnh phục vụ mã nguồn HTML/CSS/JS tại cổng 8000.
   - Giao diện khuyến mãi bắt mắt, có đồng hồ đếm ngược và hiệu ứng thị giác thu hút.

### 3.2. Yêu cầu Giao diện (UI/UX) - Tiêu chí đặc thù
Theo yêu cầu bắt buộc của bài lab, giao diện của cả hai ứng dụng phải đạt tiêu chuẩn thẩm mỹ hiện đại:
- **Phong cách thiết kế**: Nền gradient tối tím-xanh (`linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%)`).
- **Thẻ nội dung (Cards)**: Bo góc lớn (`border-radius: 20px`), hiệu ứng chiều sâu với đổ bóng mờ (`box-shadow: 0 20px 40px -15px rgba(0,0,0,0.5)`).
- **Nút bấm (Buttons)**: Bo tròn hoàn toàn (`pill button`), có gradient màu và chuyển động khi hover/active.
- **Biểu diễn dữ liệu**: Bảng lịch sử giao dịch rõ ràng, phân biệt màu sắc giữa dòng tiền vào (xanh lá nhạt) và tiền ra (đỏ nhạt).
- **Quy tắc cô lập môi trường**: Hoàn toàn không sử dụng thư viện ngoài, không CDN, không tải ảnh hay font từ internet để đảm bảo lab chạy mượt mà ngay cả khi ngắt kết nối mạng ngoài. Tất cả biểu tượng dùng SVG inline nhúng trực tiếp.

### 3.3. Yêu cầu Phi chức năng & Tính tương thích
- **Khả năng tương thích**: Ứng dụng backend NovaPay được lập trình hoàn toàn bằng thư viện chuẩn `http.server` của Python 3, tương thích tuyệt đối với Python 3.5.2 trên nền Ubuntu 16.04 của Labtainers (không dùng f-strings, không phụ thuộc Flask/pip).
- **Bảo mật thông tin**: Tuân thủ tuyệt đối quy tắc không lưu trữ mật khẩu hay access token bí mật dạng bản rõ trong mã nguồn hoặc tệp cấu hình chia sẻ.

---

## 4. THIẾT KẾ HỆ THỐNG VÀ ĐÁNH GIÁ TỰ ĐỘNG

### 4.1. Kiến trúc Mạng Labtainer
Hệ thống gồm 2 container hoạt động trên cùng dải mạng ảo riêng biệt `CLICK_NET` (`172.25.0.0/24`):
- `victim`: 172.25.0.2 (Port 5000)
- `attacker`: 172.25.0.3 (Port 8000)

### 4.2. Bảng thiết kế Đánh giá tự động (Results & Goals)
Labtainers sử dụng cơ chế giám sát hành vi tự động thông qua hai tệp `results.config` và `goals.config`:

| STT | Nhiệm vụ (Task) | Result Name | Container | Target File / Command | Loại kiểm tra (Type) | Tiêu chí đánh giá hợp lệ | Goal Name |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Task 1: Đăng nhập NovaPay | `r_login` | `victim` | `novapay.log` | `CONTAINS` | Chứa chuỗi `POST /login` | `g_login` |
| **2** | Task 2: Kiểm tra Header | `r_curl_check` | `attacker` | `.bash_history` | `CONTAINS` | Chứa lệnh `curl -I` | `g_curl_check` |
| **3** | Task 3: Thử nghiệm PoC | `r_test_iframe` | `attacker` | `www/test.html` | `CONTAINS` | Chứa thẻ `iframe` | `g_test_iframe` |
| **4** | Task 4: Làm tàng hình iframe | `r_index_opacity` | `attacker` | `www/index.html` | `CONTAINS` | Chứa thuộc tính CSS `opacity: 0` | `g_index_opacity` |
| **5** | Task 5: Tấn công Clickjacking | `r_transfer` | `victim` | `novapay.log` | `CONTAINS` | Chứa log `POST /transfer dest=iframe` | `g_transfer` |
| **6** | Task 6: Vá lỗ hổng | `r_header_deny` | `attacker` | `curl.stdout` | `CONTAINS` | Phản hồi chứa `X-Frame-Options` | `g_header_deny` |

---

## 5. CÀI ĐẶT VÀ CẤU HÌNH CHI TIẾT

### 5.1. Cấu trúc thư mục Labtainer chuẩn
Toàn bộ mã nguồn và cấu hình bài lab được tổ chức đúng cấu trúc chuẩn của Labtainers:
- `config/start.config`, `parameter.config`, `about.txt`, `keywords.txt`
- `instr_config/results.config`, `goals.config`
- `dockerfiles/Dockerfile.clickjacking.victim.student`, `Dockerfile.clickjacking.attacker.student`
- `victim/` (`app.py`, `restart_novapay.sh`, `_bin/fixlocal.sh`, `_system/etc/firefox/syspref.js`)
- `attacker/` (`www/index.html`, `_bin/treataslocal`, `_bin/fixlocal.sh`, `_system/etc/firefox/syspref.js`)
- `docs/` (`read_first.txt`, `clickjacking.tex`, `Makefile`)
- `imodule_clickjacking.tar` (Gói cài đặt độc lập)

---

## 6. TÍCH HỢP VÀ TRIỂN KHAI (DOCKER & GITHUB)

### 6.1. Đóng gói IModule (Labtainers Instructor Module)
Toàn bộ bài lab được đóng gói thành file phân phối `imodule_clickjacking.tar` (kích thước ~130 KB). Gói này giữ nguyên cấu trúc phân cấp thư mục `clickjacking/`, cho phép bất kỳ giảng viên hoặc sinh viên nào tích hợp bài lab vào hệ thống chỉ bằng một lệnh duy nhất:
```bash
imodule https://github.com/Huan-0808/clickjacking-lab/raw/master/imodule_clickjacking.tar
```

### 6.2. Triển khai Repository trên GitHub
Mã nguồn bài lab được quản trị và phát hành công khai tại GitHub:
- **Tên Repository**: `clickjacking-lab`
- **Địa chỉ kho lưu trữ**: [https://github.com/Huan-0808/clickjacking-lab](https://github.com/Huan-0808/clickjacking-lab)
- **Link tải trực tiếp file `imodule_clickjacking.tar`**: [https://github.com/Huan-0808/clickjacking-lab/raw/master/imodule_clickjacking.tar](https://github.com/Huan-0808/clickjacking-lab/raw/master/imodule_clickjacking.tar)
- **Nhánh chính**: `master`

---

## 7. THỬ NGHIỆM VÀ ĐÁNH GIÁ

### 7.1. Kết quả kiểm thử Đăng nhập (Task 1)
```text
2026-11-21 04:38:45 - POST /login - Attempted login for user: nan_nhan
172.25.0.2 - - [21/Nov/2026 04:38:45] "POST /login HTTP/1.1" 303 -
```
$\rightarrow$ Khớp Goal `g_login`.

### 7.2. Kết quả kiểm thử Trinh sát Header (Task 2)
```http
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.5.2
Date: Sat, 21 Nov 2026 04:09:38 GMT
Content-Type: text/html; charset=utf-8
```
$\rightarrow$ Khớp Goal `g_curl_check`.

### 7.3. Kết quả kiểm chứng chống gian lận & Tấn công thực tế (Task 5)
1. **Trường hợp gian lận mở trực tiếp `/transfer?dest=iframe` trên tab thường**:
   ```text
   2026-11-21 04:38:45 - POST /transfer dest=direct - Transaction processed
   ```
   $\rightarrow$ Không tính điểm.
2. **Trường hợp tấn công Clickjacking thật qua trang mồi**:
   ```text
   2026-11-21 04:38:46 - POST /transfer dest=iframe - Transaction processed
   ```
   $\rightarrow$ Đạt yêu cầu và ghi nhận Goal `g_transfer`.

### 7.4. Kết quả kiểm thử Phòng thủ (Task 6)
```http
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.5.2
Date: Sat, 21 Nov 2026 04:12:05 GMT
Content-Type: text/html; charset=utf-8
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none'
```
$\rightarrow$ Khớp Goal `g_header_deny`.
