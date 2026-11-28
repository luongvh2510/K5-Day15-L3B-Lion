# Reflection — Nguyễn Trung Dũng

1. **Vai trò và phần việc:** Mình phụ trách backend và mô phỏng chi phí cho sản phẩm đặt đồ ăn nhóm. Mình thực hiện phần API quản lý phiên, lưu trạng thái bằng SQLite, các thao tác hồ sơ và giỏ, cùng kiểm thử tại `server/api.py`, `codebase/store.py` và `tests/test_api.py`. Mình cũng thực hiện phỏng vấn P1–P3, xây dựng persona từ khảo sát và tổng hợp kết quả mô phỏng chi phí trong `cost/personas.yaml` và `cost/cost-estimate.md`.

2. **AI hỗ trợ:** Mình dùng Codex để hỗ trợ triển khai API, viết kiểm thử và tổng hợp bảng chi phí. Mình đối chiếu các đầu việc với tài liệu nghiệp vụ, kiểm tra kết quả bằng bộ test và chạy thử trước khi mô phỏng 50 phiên. Khi tính chi phí trên mỗi task thành công, mình dùng đúng tỷ lệ 15/20 = 75% của lượt đánh giá thứ hai và ghi rõ các giả định về số người dùng.

3. **Một câu thử trượt và bài học:** Ở lượt đánh giá thứ ba, ca B04 yêu cầu lập giỏ cho An dị ứng đậu phộng sau khi An đã đồng ý đổi món, nhưng hệ thống lại hỏi thêm nên chưa hoàn thành yêu cầu. Ca này giúp mình thấy rằng kiểm thử cần xem cả độ an toàn lẫn việc hệ thống có sử dụng đúng thông tin đã được xác nhận. Nhóm cần kiểm tra thêm tính ổn định qua nhiều lần chạy và cách xử lý các câu hỏi không cần thiết.
