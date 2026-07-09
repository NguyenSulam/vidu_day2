- Tên file px1.xlsx nghĩa là phân xưởng 1.
- Trưởng ca: người phụ trách phân xưởng tại ca đó
- 1 ca kéo dài 8 tiếng

## Tính năng Logging

Từ phiên bản cập nhật này, chương trình có tính năng ghi log:

- **Log File**: Tất cả hoạt động được ghi vào file trong thư mục `logs/`
- **Log Format**: `Baocao_TH_YYYYMMDD_HHMMSS.log` (theo thời gian chạy chương trình)
- **Chi tiết Log**:
  - Bắt đầu/kết thúc chương trình
  - Số lượng file đọc và dòng xử lý
  - Tổng hợp báo cáo
  - Ghi file Excel
  - Chi tiết lỗi (nếu có)
- **Mức Log**: DEBUG (ghi vào file) và INFO (hiển thị console)