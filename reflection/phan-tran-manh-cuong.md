# Reflection — Phan Trần Mạnh Cường

1. **Vai trò và phần mình làm**

   Mình phụ trách BA cho bài D2, từ việc xác định vấn đề của người đặt đồ ăn hộ đến viết tình huống và tiêu chí đánh giá.

   Mình tổng hợp 23 phản hồi khảo sát. Có 20 người ngoài nhóm qua sàng lọc, trong đó 13 người phải sửa món, đổi quán hoặc không đặt được ở lần gần nhất.

   Mình dùng phản hồi để bổ sung các ca CP3 và cập nhật phần bằng chứng, impact và rủi ro trong spec. Xem [bằng chứng](../evidence/summary.md), [benchmark](../eval/benchmark.csv) và [spec](../spec.md).

2. **AI hỗ trợ mình thế nào**

   Mình dùng Codex để soạn câu hỏi, trích dữ liệu từ Excel, tính số liệu và chuyển các tình huống trong khảo sát thành ca thử.

   Bản tổng hợp ban đầu chỉ có 17 người qua sàng lọc. Sau khi bổ sung 3 phản hồi, mình xác nhận 20 người đủ điều kiện đều ở ngoài nhóm để AI cập nhật kết luận và ghi rõ nguồn xác nhận trong CSV.

   Mình cũng phân biệt thời gian gom đến chốt quan sát được với thời gian công cụ có thể tiết kiệm. Khảo sát chỉ đo được con số đầu tiên. Xem [khai báo dùng AI](../docs/ai-usage.md).

3. **Một câu thử trượt và điều mình học được**

   Ở lượt 3, ca B04 trượt vì hệ thống hỏi An muốn đổi sang món gì dù hồ sơ đã xác nhận An đồng ý đổi món.

   Hệ thống không tạo giỏ vi phạm, nhưng câu hỏi thừa khiến người đặt không nhận được giỏ dù đã cung cấp đủ thông tin.

   Mình học được rằng tiêu chí cần kiểm cả bước tiếp theo sau khi hồ sơ đã được xác nhận. Với ca này, hệ thống cần giữ ràng buộc dị ứng và tiếp tục lập giỏ trong phạm vi món phù hợp. Xem [báo cáo đánh giá](../eval/report.md).
