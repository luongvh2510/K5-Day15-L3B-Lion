# Lion — Từ chat nhóm đến giỏ đồ ăn an toàn

**Thành viên, lớp, track:** xem [TEAMS.md](TEAMS.md) · **Canvas:** [canvas.md](canvas.md)

**Track D (Thương mại điện tử), hướng D2.**

**Bài toán:** Một người cầm quỹ chung 250k–300k đặt đồ ăn hộ cả nhóm 5 người, trong khi mọi người chỉ nhắn rải rác vào nhóm chat (có người ăn chay, có người dị ứng đậu phộng, có người giục đặt nhanh). Người đặt phải tự đọc hết tin nhắn, dò từng món trong menu rồi cộng cả phí ship, nên dễ sót dặn dò, vượt quỹ và phải làm lại.

**Lát cắt:** Một người đặt hộ cho nhóm 5 người dán đoạn chat và quỹ chung. Sau khi họ xác nhận hồ sơ, hệ thống tự chọn quán và trả giỏ đã kiểm theo menu hoặc giải thích vì sao chưa thể lập giỏ.

## Chạy CLI hoặc API

Cần Python 3.10 trở lên; không cần cài thư viện ngoài. Chạy `python run.py` (hoặc `python3 run.py` nếu máy không có lệnh `python`), rồi chọn `1` cho CLI hoặc `2` cho API. API mở tại `http://127.0.0.1:8000/api`. Có thể mở thẳng API bằng `LION_MODE=web python3 run.py`; dừng bằng Ctrl+C. Nếu frontend chạy ở cổng khác trên cùng máy, API cho phép truy cập CORS.

API gồm `POST /sessions` (`{"chat_text":"..."}`), `GET /sessions/{id}`, `POST /sessions/{id}/messages` (`{"text":"..."}`), `POST /sessions/{id}/confirm`, `POST /sessions/{id}/finalize`, `GET /restaurants`, `GET /restaurants/{id}/menu` và `POST /debug/validate-cart`. Dữ liệu phiên lưu trong `sessions.sqlite3`, đã được bỏ qua bởi Git; có thể đặt đường dẫn khác bằng biến `LION_DB_PATH`. Server mặc định chỉ lắng nghe trên máy hiện tại; khóa phiên chỉ phối hợp các luồng trong một tiến trình server.

Hợp đồng API đầy đủ: [docs/ba/04-hop-dong-du-lieu-API.md](docs/ba/04-hop-dong-du-lieu-API.md). Hướng dẫn nối frontend: [docs/frontend-tu.md](docs/frontend-tu.md). Mock JSON sinh từ API thật: [docs/ba/mocks/](docs/ba/mocks/).

Cấu hình model thật trong `.env`: `MODEL_PROVIDER=openrouter` (nhóm đang dùng), `openai`, `anthropic` hoặc `ollama`, cùng `MODEL_NAME` và `API_KEY` (Ollama không cần khóa). Xem [hướng dẫn nối model](docs/connect-model.md); không đưa khóa vào Git. Chế độ `fake` không tạo được hồ sơ AI hợp lệ. API hỗ trợ mở lại hồ sơ, sửa thành viên và các hành động đổi quỹ hoặc đổi quán. Các nhãn dị ứng CRUSTACEAN/MOLLUSC và nguồn trích chi tiết cũng cần nhóm thống nhất thêm với BA và AI trước khi frontend phụ thuộc vào chúng.

Kiểm thử: `python3 -m unittest discover -s tests -v`.

