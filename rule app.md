# Project: FPT Telecom Sales Reporting Dashboard (FSRD)

## 1. Tổng quan dự án
Xây dựng ứng dụng dashboard bằng Python để phân tích dữ liệu bán hàng từ file Excel (.xlsx) của FPT Telecom. Ứng dụng giúp theo dõi các chỉ số phát triển thuê bao (PTTB), chất lượng triển khai, hiệu suất nhân viên và chất lượng thanh toán.

## 2. Cấu trúc dữ liệu (Data Schema)
Dựa trên định dạng file xuất từ hệ thống:

### Sheet "Internet"
- **Cột J (Hợp đồng):** Mã định danh duy nhất của hợp đồng.
- **Cột O (Ngày tạo HĐ):** Ngày khách hàng ký kết.
- **Cột P (Ngày Online):** Ngày nghiệm thu kỹ thuật thành công.
- **Cột Q (Ngày hủy dịch vụ):** Ngày hợp đồng bị hủy trước khi online (Hủy TSD).
- **Cột R (Acc nhân viên bán):** Mã/Tên nhân viên kinh doanh.
- **Cột T (Xã/Phường):** Thông tin địa giới hành chính chính xác (Bỏ qua cột U).
- **Cột Y (Số tháng trả trước):** Phân loại 0 (trả sau), 6 (trả 6 tháng), 13 (trả 1 năm).
- **Cột AA (Hình thức thanh toán):** Tiền mặt, Chuyển khoản ngân hàng, v.v.

### Sheet "Pay"
- **Cột L (Hợp đồng):** Dùng để đối chiếu với Sheet Internet (Xác định Combo).
- **Cột H (Phân loại):** Gói dịch vụ FPT Play (Vip, V.Vip).

## 3. Logic xử lý & Chỉ số KPI (Metrics)

### 3.1. Chỉ số PTTB & Chất lượng
1. **Tổng PTTB:** Tổng số lượng hợp đồng trong Sheet Internet.
2. **PTTB Combo:** Số lượng hợp đồng trùng nhau giữa Sheet Internet và Sheet Pay.
3. **PTTB V.Vip/Vip:** Đếm tại cột H sheet Pay (Lọc các giá trị "V.Vip" hoặc "VIP").
4. **Tỷ lệ Online:** Số lượng hợp đồng có Ngày Online (Cột P) / Tổng PTTB.
5. **Tỷ lệ Hủy TSD:** Số lượng hợp đồng có Ngày hủy (Cột Q) / Tổng PTTB.
   - *Ngưỡng cảnh báo:* Nếu tỷ lệ > 15% -> Hiển thị cảnh báo đỏ (Critical).
6. **Thời gian triển khai trung bình:** Khoảng cách ngày trung bình giữa `Ngày Online (P)` và `Ngày tạo HĐ (O)`.

### 3.2. Xử lý Địa giới & Nhân sự
- **Địa giới (Cột T):** - Nếu dữ liệu trống hoặc "Không xác định" -> Quy về nhóm **"Khác"**.
  - Thống kê sản lượng PTTB, tỷ lệ trả trước theo từng Xã/Phường.
- **Nhân sự (Cột R):**
  - Sale có PTTB cao nhất/thấp nhất.
  - Sale có tỷ lệ Online cao nhất.
  - Sale có tỷ lệ Hủy TSD cao nhất.

### 3.3. Chất lượng thanh toán
- Phân nhóm theo số tháng trả trước (Cột Y): 0, 6, 13.
- Thống kê tỷ lệ Hình thức thanh toán (Cột AA).

## 4. Quy trình hoạt động (Application Phases)

### Phase 1: Input & Tiền xử lý
- Người dùng upload file `.xlsx`.
- Hệ thống tự động quét Cột O để xác định khoảng thời gian báo cáo. 
- *Ví dụ:* "Báo cáo bán hàng từ ngày 01/04/2026 đến 22/04/2026".

### Phase 2: Dashboard trực quan (UI)
- **Khu vực Metrics:** Hiển thị dạng Card các số liệu: Tổng PTTB, Combo, V.Vip, % Online, % Hủy TSD, Số ngày triển khai TB.
- **Khu vực Biểu đồ:**
  - Biểu đồ tròn: Cơ cấu trạng thái (Online / Hủy / Đang chờ).
  - Biểu đồ cột ngang: Top Xã/Phường có sản lượng cao nhất.
  - Biểu đồ thanh: Hiệu suất triển khai trung bình theo Xã/Phường.
  - Biểu đồ cột chồng: Tỷ lệ trả trước (0, 6, 13) theo khu vực.

### Phase 3: Kết xuất báo cáo (Export)
- Cho phép tải xuống báo cáo tổng hợp dưới định dạng:
  - **Microsoft Word (.docx):** Văn bản tóm tắt số liệu.
  - **PDF:** Báo cáo cố định để gửi lãnh đạo.
  - **PowerPoint (.pptx):** Mỗi slide chứa một biểu đồ và nhận xét tương ứng.

## 5. Yêu cầu kỹ thuật
- **Ngôn ngữ:** Python 3.10+
- **Thư viện chính:** - `Streamlit` (Giao diện web Dashboard).
  - `Pandas`, `Openpyxl` (Xử lý dữ liệu).
  - `Plotly` (Biểu đồ tương tác).
  - `python-docx`, `FPDF`, `python-pptx` (Kết xuất file). 
  - Đề xuất cho tôi những thư viện cần thiết để build app

## 6. Lưu ý UI/UX
- Giao diện chuyên nghiệp, tập trung vào các con số biết nói.
- Cần có bộ lọc (Filter) theo thời gian và theo Sale trên Dashboard.