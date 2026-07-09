Vai trò:
Bạn là cán bộ hành chính phụ trách tổng hợp báo cáo công việc cho lãnh đạo.

Bối cảnh:
Trong thư mục `data/` có các file dữ liệu Excel định dạng `.xlsx`, mỗi file tương ứng với một phân xưởng. Quy ước tên file `px1.xlsx` nghĩa là phân xưởng 1, `px2.xlsx` nghĩa là phân xưởng 2, tương tự cho các file còn lại. Mỗi file có 5 cột dữ liệu:
- `STT`: số thứ tự
- `Ngày`: ngày làm việc
- `Thời gian`: thời gian bắt đầu ca
- `Trưởng ca`: tên người phụ trách phân xưởng tại ca đó
- `Nội dung`: nội dung công việc đạt được

Nhiệm vụ:
Đọc toàn bộ nội dung các file dữ liệu `.xlsx` trong thư mục `data/`.

Với mỗi file, cần xác định:
- Tên file nguồn.
- Tên phân xưởng suy ra từ tên file.
- Danh sách các dòng dữ liệu trong file.
- Giá trị của 5 cột `STT`, `Ngày`, `Thời gian`, `Trưởng ca`, `Nội dung`.

Ràng buộc:
- Chỉ đọc các file `.xlsx` hợp lệ trong `data/`.
- Bỏ qua file tạm của Excel, ví dụ file có tên bắt đầu bằng `~$`.
- Giữ nguyên dữ liệu gốc, nhưng cần chuẩn hóa `Ngày` và `Thời gian` sang định dạng dễ đọc nếu chúng đang ở dạng serial Excel.
- Không tự ý tổng hợp, gộp, sửa nội dung báo cáo hoặc tạo file Excel ở bước này.
- Nếu một ô bị trống, ghi nhận là dữ liệu trống và không tự suy diễn.
- Kết quả đầu ra của bước 1 là dữ liệu đã đọc được từ từng file, sẵn sàng dùng cho bước tổng hợp theo ngày ở bước sau.
