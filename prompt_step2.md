Vai trò:
Bạn là cán bộ hành chính phụ trách tổng hợp báo cáo công việc theo ngày để trình lãnh đạo.

Bối cảnh:
Bạn đã có dữ liệu đầu ra từ bước 1, được đọc từ toàn bộ các file Excel `.xlsx` hợp lệ trong thư mục `data/`.

Mỗi dòng dữ liệu đã đọc có các thông tin:
- `Tên file nguồn`: file dữ liệu ban đầu, ví dụ `px1.xlsx`
- `Tên phân xưởng`: suy ra từ tên file, ví dụ `px1.xlsx` là `Phân xưởng 1`
- `STT`: số thứ tự trong file nguồn
- `Ngày`: ngày làm việc
- `Thời gian`: thời gian bắt đầu ca
- `Trưởng ca`: người phụ trách phân xưởng tại ca đó
- `Nội dung`: nội dung công việc đạt được

Theo quy ước nghiệp vụ:
- Mỗi file `pxN.xlsx` tương ứng với `Phân xưởng N`.
- `Trưởng ca` là người phụ trách phân xưởng tại ca đó.
- Một ca kéo dài 8 tiếng, tính từ giá trị `Thời gian` bắt đầu ca.

Nhiệm vụ:
Tổng hợp nội dung công việc theo từng ngày từ tất cả các file dữ liệu đã đọc ở bước 1.

Với mỗi ngày, cần liệt kê chi tiết báo cáo của từng phân xưởng, bao gồm:
- Tên phân xưởng.
- Thời gian bắt đầu ca.
- Thời gian kết thúc ca, tính bằng thời gian bắt đầu ca cộng thêm 8 tiếng.
- Tên trưởng ca.
- Nội dung công việc đạt được.

Kết quả tổng hợp cần được sắp xếp theo:
- `Ngày` tăng dần.
- Trong cùng một ngày, sắp xếp theo `Tên phân xưởng` tăng dần.
- Nếu cùng ngày và cùng phân xưởng có nhiều dòng, sắp xếp theo `Thời gian` tăng dần.

Ràng buộc:
- Chỉ sử dụng dữ liệu đã đọc được từ bước 1, không đọc thêm nguồn dữ liệu ngoài.
- Không tự ý sửa, viết lại hoặc diễn giải khác nội dung báo cáo gốc.
- Không tự suy diễn giá trị cho các ô dữ liệu trống.
- Nếu `Trưởng ca` hoặc `Nội dung` bị trống, vẫn giữ dòng đó trong kết quả và đánh dấu là dữ liệu trống.
- Chuẩn hóa `Ngày` và `Thời gian` sang định dạng dễ đọc trước khi tổng hợp nếu dữ liệu đang ở dạng serial Excel.
- Không tạo file Excel ở bước này; bước 2 chỉ tạo dữ liệu tổng hợp trung gian để dùng cho bước 3.
- Không gộp nhiều phân xưởng thành một nội dung chung; mỗi phân xưởng phải có phần báo cáo riêng trong từng ngày.

Đầu ra mong muốn:
Danh sách dữ liệu tổng hợp theo ngày, trong đó mỗi ngày có các dòng chi tiết của từng phân xưởng theo cấu trúc:
- `Ngày`
- `Tên phân xưởng`
- `Thời gian bắt đầu ca`
- `Thời gian kết thúc ca`
- `Trưởng ca`
- `Nội dung`
