# Khai báo dùng AI

Tóm tắt tại [README](../README.md#dùng-ai-vào-việc-gì) và [spec.md §10](../spec.md).

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử CP2 | Codex | Viết khung đọc chat mô phỏng, đọc menu và kiểm giỏ bằng Python. | Kiểm bằng CLI trên 10 ca mô phỏng. Phân công và thiết kế bản hiện tại ghi trong spec §4, §10. | Cường phối hợp AI/BE |
| Tổng hợp khảo sát | Codex | Trích 23 phản hồi, bỏ cột hồ sơ đáp viên, đếm 20 phản hồi qua Q1 và tính số liệu từ Q2–Q7. | Cường xác nhận điều kiện ngoài nhóm cho 20 mã qua Q1. Log và trích dẫn tra lại qua mã PH trong `evidence/survey/results.csv`. | Cường |
| Rà câu hỏi khảo sát | Codex | Gợi ý câu sàng lọc và câu hỏi về lần đặt hộ đã xảy ra. | Câu hỏi lưu theo workbook đã thu trong `evidence/survey/questions.md`. | Cường |
| Viết ca benchmark | Codex | Soạn tình huống mô phỏng và chuyển một số phản hồi khảo sát thành ca CP3. | Cột `source` dẫn tới quy tắc, menu hoặc mã phản hồi có thể đối chiếu. Chuẩn đạt CP2 giữ nguyên. | Cường |
| Chấm thử 5 output mô phỏng CP2 | Hai agent Codex | Chấm độc lập B02, B04, B05, B07 và B09. Đồng thuận 5/5. | Đây là chấm thử. Chưa có kết quả chấm tay độc lập cho 5 output này. Ba lượt model thật dùng điểm do người chấm ghi, xem `eval/report.md`. | Cường |
| Văn bản CP3–CP4 | Codex | Soạn tóm tắt bằng chứng, bảng impact, mục chi phí và rủi ro trong spec. | Đối chiếu với workbook khảo sát, số mô phỏng của Dũng và CSV từng lượt eval. | Cường |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
