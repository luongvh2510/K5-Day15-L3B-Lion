# Khai báo dùng AI

Tóm tắt tại [README](../README.md#dùng-ai-vào-việc-gì) và [spec.md §10](../spec.md).

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử CP2 | Codex | Viết khung đọc chat mô phỏng, đọc menu và kiểm giỏ bằng Python. | Kiểm bằng CLI trên 10 ca mô phỏng. Phân công và thiết kế bản hiện tại ghi trong spec §4, §10. | Cường phối hợp AI/BE |
| Tổng hợp khảo sát | Codex | Trích 23 phản hồi, bỏ cột hồ sơ đáp viên, đếm 20 phản hồi qua Q1 và tính số liệu từ Q2–Q7. | Cường xác nhận điều kiện ngoài nhóm cho 20 mã qua Q1. Log và trích dẫn tra lại qua mã PH trong `evidence/survey/results.csv`. | Cường |
| Rà câu hỏi khảo sát | Codex | Gợi ý câu sàng lọc và câu hỏi về lần đặt hộ đã xảy ra. | Câu hỏi lưu theo workbook đã thu trong `evidence/survey/questions.md`. | Cường |
| Viết ca benchmark | Codex | Soạn tình huống mô phỏng và chuyển một số phản hồi khảo sát thành ca CP3. | Cột `source` dẫn tới quy tắc, menu hoặc mã phản hồi có thể đối chiếu. Chuẩn đạt CP2 giữ nguyên. | Cường |
| Chấm thử 5 output mô phỏng CP2 | Hai agent Codex | Chấm độc lập B02, B04, B05, B07 và B09. Đồng thuận 5/5. | Đây là chấm thử. Chưa có kết quả chấm tay độc lập cho 5 output này. | Cường |
| Văn bản CP3–CP4 | Codex | Soạn tóm tắt bằng chứng, bảng impact, mục chi phí và rủi ro trong spec. | Đối chiếu với workbook khảo sát, số mô phỏng của Dũng và CSV từng lượt eval. | Cường |
| Agent và prompt (5 bước gọi model, bộ điều phối 2 phase) | Claude Code | Viết `codebase/llm_steps.py`, `codebase/core.py`, các prompt trong `prompts/` và test đi kèm. | Lương đọc diff, chạy toàn bộ test và chạy thử trên giao diện trước khi commit. | Lương |
| Sửa lỗi lượt 1 → 2 → 3 | Claude Code | Gom câu trượt thành nhóm lỗi, đề xuất và viết bản sửa (commit `21c1358`, `24915ef`), mỗi bản sửa có test mới. | Lương chọn nhóm lỗi cần sửa và duyệt từng bản sửa. Không sửa câu thử, `expected` hay chuẩn đạt. | Lương |
| Chấm cột `pass` của 3 lượt model thật | Claude Code | Đề xuất điểm 1/0 cho từng câu theo `pass_criterion`, chỉ đọc output, ghi lý do trượt vào `ghi_chu`. | Lương đọc lại từng câu trượt và duyệt trước khi commit. Chưa có người thứ hai chấm chéo. | Lương |
| Phí ship theo khoảng cách, ẩn danh ghi chép phỏng vấn | Claude Code | Viết `shipping_fee` trong `codebase/tools.py` kèm test; bỏ tên người được phỏng vấn khỏi P1–P3. | Lương duyệt công thức phí ship; nội dung trả lời phỏng vấn giữ nguyên. | Lương |
| Báo cáo đánh giá | Claude Code | Soạn `eval/report.md`, mục 5–6 của `eval/README.md` từ CSV các lượt. | Lương đối chiếu số với `python run.py score`. | Lương |
| Backend, dữ liệu quán, mô phỏng chi phí | *(Dũng bổ sung)* | | | Dũng |
| Frontend | *(Tú bổ sung)* | | | Tú |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa output hay số liệu của các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`). Trong file run, AI chỉ điền cột `pass` và `ghi_chu` như trên.
