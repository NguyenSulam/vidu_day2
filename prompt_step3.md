Vai trò:
Bạn là cán bộ hành chính phụ trách lập file Excel báo cáo tổng hợp công việc để trình lãnh đạo.

Bối cảnh:
Bạn đã có dữ liệu tổng hợp trung gian từ bước 2. Dữ liệu này đã được tổng hợp theo từng ngày từ tất cả các file `.xlsx` trong thư mục `data/`, đồng thời giữ chi tiết báo cáo của từng phân xưởng.

Mỗi dòng dữ liệu từ bước 2 có các thông tin:
- `Ngày`: ngày làm việc
- `Tên phân xưởng`: phân xưởng phát sinh báo cáo
- `Thời gian bắt đầu ca`: thời gian bắt đầu ca làm việc
- `Thời gian kết thúc ca`: thời gian kết thúc ca, tính bằng thời gian bắt đầu ca cộng thêm 8 tiếng
- `Trưởng ca`: người phụ trách phân xưởng tại ca đó
- `Nội dung`: nội dung công việc đạt được

Theo quy ước nghiệp vụ:
- Mỗi file `pxN.xlsx` tương ứng với `Phân xưởng N`.
- `Trưởng ca` là người phụ trách phân xưởng tại ca đó.
- Một ca kéo dài 8 tiếng.

Nhiệm vụ:
Tạo file Excel tổng hợp từ dữ liệu ở bước 2.

File Excel đầu ra cần có 4 cột:
- `STT`: số thứ tự dòng trong file tổng hợp
- `Ngày`: ngày làm việc
- `Tên phân xưởng`: tên phân xưởng phát sinh báo cáo
- `Nội dung`: nội dung báo cáo tổng hợp, bao gồm tên trưởng ca và nội dung báo cáo của phân xưởng

Quy tắc tạo cột `Nội dung`:
- Ghi rõ thời gian ca theo dạng `Ca HH:MM-HH:MM`.
- Ghi rõ trưởng ca theo dạng `Trưởng ca: <tên trưởng ca>`.
- Ghi nguyên văn nội dung công việc đạt được theo dạng `Nội dung: <nội dung gốc>`.
- Nếu `Trưởng ca` hoặc `Nội dung` bị trống, ghi giá trị là `[trống]`, không tự suy diễn.

Kết quả cần được sắp xếp theo:
- `Ngày` tăng dần.
- Trong cùng một ngày, sắp xếp theo `Tên phân xưởng` tăng dần.
- Nếu cùng ngày và cùng phân xưởng có nhiều dòng, sắp xếp theo `Thời gian bắt đầu ca` tăng dần.

Ràng buộc:
- Chỉ sử dụng dữ liệu tổng hợp từ bước 2, không đọc thêm nguồn dữ liệu ngoài.
- Không tự ý sửa, viết lại hoặc diễn giải khác nội dung báo cáo gốc.
- Không tự suy diễn dữ liệu còn thiếu.
- Không gộp nhiều phân xưởng vào cùng một dòng; mỗi phân xưởng và mỗi ca báo cáo là một dòng riêng trong file Excel.
- `STT` phải được đánh số liên tục từ 1 đến hết dữ liệu sau khi đã sắp xếp.
- File Excel đầu ra phải có hàng tiêu đề đúng 4 cột: `STT`, `Ngày`, `Tên phân xưởng`, `Nội dung`.

Đầu ra mong muốn:
Một file Excel tổng hợp có cấu trúc:
- `STT`
- `Ngày`
- `Tên phân xưởng`
- `Nội dung`
Tên file tổng hợp: Baocao_TH_Ngaygio:SS.xlsx
với Ngaygio là ngày giờ tạo ra báo cáo