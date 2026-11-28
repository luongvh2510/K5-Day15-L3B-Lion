# Khảo sát · Lần gần nhất bạn đặt đồ ăn hộ cả nhóm

Nguồn: tab **Dữ liệu khảo sát**, vùng **A4:J27** trong workbook `Khao_sat_dat_do_an_nhom_23_dap_vien.xlsx` do nhóm cung cấp. Workbook chưa ghi kênh gửi, thời điểm mở/chốt hoặc danh sách xác nhận người ngoài nhóm. Bản dùng trong repo là [Excel đã ẩn danh](Khao_sat_dat_do_an_nhom_23_dap_vien_an_danh.xlsx).

| Mã | Câu hỏi theo tiêu đề cột trong workbook |
|---|---|
| Q1 | Đặt hộ nhóm 4–6 người trong 30 ngày qua? |
| Q2 | Số lần đặt hộ trong 30 ngày qua |
| Q3 | Kênh nhóm gửi lựa chọn món |
| Q4 | Cách thức gom yêu cầu và chọn món |
| Q5 | Thời gian gom đến lúc chốt (phút) |
| Q6 | Chuyện phát sinh (Chọn nhiều) |
| Q7 | Kết quả cuối cùng |
| Q8 | Chi tiết tình huống xử lý hoặc yếu tố giúp chốt đơn suôn sẻ (Nguyên văn) |

- Nếu Q1 = “Không”, kết thúc khảo sát. Giữ dòng Q1 trong log để kiểm mẫu số sàng lọc.
- [results.csv](results.csv) giữ mã PH và các cột Q1–Q8. Bỏ cột hồ sơ đáp viên chứa vai trò, giới tính và tuổi. Ô gạch ngang được xuất thành ô trống. PH15 trả lời “Không nhớ” ở Q5 và được loại riêng khỏi phép tính thời gian.
- Dùng Q6 để đếm từng nhãn tự báo cáo, một người có thể đánh dấu nhiều nhãn. Dùng Q7 để đếm kết quả cuối của từng người. Q8 dùng để kiểm ngữ cảnh và trích nguyên văn.
