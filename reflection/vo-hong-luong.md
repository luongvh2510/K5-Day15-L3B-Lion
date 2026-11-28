# Reflection — Võ Hồng Lương

1. **Vai trò + phần mình làm:** Trưởng nhóm, phụ trách AI/agent và đánh giá.
   - Thiết kế luồng 2 giai đoạn và viết `codebase/core.py`, `codebase/llm_steps.py`, các prompt trong `prompts/` cùng test đi kèm (commit `f9b9e90`). Viết phí ship theo khoảng cách (`929e979`) và nối OpenRouter (`381aa39`).
   - Chạy 3 lượt eval (`e240a23`, `5173487`, `f4c8d6f`), sửa lỗi giữa các lượt (`21c1358`, `24915ef`) và viết `eval/report.md`.
   - Ẩn danh ghi chép phỏng vấn (`c8bdaac`), review và merge PR của Dũng, Tú, Cường vào `main`.

2. **AI hỗ trợ mình thế nào:**
   - Dùng Claude Code để viết code agent, prompt và test, gom câu trượt thành nhóm lỗi, đề xuất điểm cột `pass` và soạn báo cáo. Mình đọc diff, chạy toàn bộ test, chạy thử trên giao diện rồi mới commit. Mình cũng đọc lại từng câu trượt trước khi chốt điểm.
   - **Chỗ phải sửa lại output AI:** câu xác nhận khảo sát AI soạn ban đầu khẳng định như thể repo đã có danh sách đối chiếu. Thực tế repo không có tài liệu đó, nên mình sửa lại thành "dựa trên đối chiếu của Cường, repo chưa có tài liệu đối chiếu".
   - Ở mục chi phí, mình chọn tỉ lệ 75% của lượt 2 thay vì để tự lấy 90% của lượt 3, để số không lạc quan hơn thực tế.
   - Hình dạng hệ thống: AI gọi là "agent", nhưng thực chất là workflow, vì code giữ luồng và mọi bước kiểm. Mình phải tự đối chiếu với code mới nói đúng được.

3. **Một câu thử trượt và mình học được gì:**
   - **B14:** cả 5 người nhắn "món nào cũng được", nhưng hồ sơ ra rỗng và cả luồng dừng. Nguyên nhân là prompt ghi "'Gì cũng được' không tạo gì", và model hiểu thành không tạo luôn cả thành viên.
   - Bài học thứ nhất: một câu chữ mơ hồ trong prompt có thể làm hỏng cả luồng. Vì vậy bản sửa không chỉ sửa prompt mà thêm một lưới an toàn bằng code: model trả rỗng thì lấy người gửi tin làm thành viên.
   - Bài học thứ hai: B01 và B04 cho thấy temperature 0 vẫn dao động giữa các lần chạy. Một lần chạy đạt chưa chứng minh được gì, nên phải chạy nhiều lần và giữ phần kiểm an toàn bằng code chứ không giao cho model.
