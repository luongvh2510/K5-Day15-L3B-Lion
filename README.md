# Lion — Từ chat nhóm đến giỏ đồ ăn an toàn

**Thành viên, lớp, track:** xem [TEAMS.md](TEAMS.md). **Track D (Thương mại điện tử)** — hướng D2. **Canvas:** [canvas.md](canvas.md).

*Lát cắt:* Một người cầm quỹ chung đặt đồ ăn hộ nhóm 5 người · dán đoạn chat nhóm lộn xộn (quỹ 250k–300k, người ăn chay, người dị ứng, người "gì cũng được") · AI trích ràng buộc từng người, hỏi lại khi mơ hồ, tự chọn một quán và chọn món; code kiểm cứng dị ứng, ăn chay, menu và tổng tiền gồm phí ship · người đặt xác nhận hồ sơ rồi nhận giỏ đã kiểm, hoặc lời giải thích vì sao chưa lập được giỏ kèm đề xuất tăng quỹ / đổi quán. Chi tiết: [spec.md](spec.md) §4.

**Demo:** [video demo CP4](https://drive.google.com/file/d/1CMf3zfUAsNhWSvOaJuHrElhSdF42p5EU/view?usp=drive_link) · [slide (PDF)](demo-slides.pdf)

> Công cụ chỉ **đề xuất** giỏ, không tự đặt đơn, không thanh toán. AI không được bỏ ràng buộc dị ứng / ăn chay đã xác nhận, kể cả khi người dùng yêu cầu. Menu là dữ liệu mô phỏng, chưa xác minh nhiễm chéo trong bếp — người đặt vẫn cần báo quán.

---

## Nhóm làm gì, khung làm gì

| Nhóm quyết định và viết | Khung làm sẵn (không cần sửa) |
|---|---|
| Người dùng, pain, bằng chứng, impact (`evidence/`, `spec.md` §1–§2) | — |
| Hình dạng giải pháp, công cụ, prompt, luồng (`spec.md` §4, `codebase/agent.py`, `core.py`, `llm_steps.py`, `tools.py`, `ai.py`, `prompts/`) | Ghi mọi lần gọi model / công cụ vào trace, cộng token (`codebase/tracing.py`) |
| Bộ câu thử, metric, chuẩn "đạt" (`eval/benchmark.csv`, `eval/metric_spec.yaml`, `spec.md` §7) | Kiểm đủ cột, đủ câu `kho` / `tu_choi` (`run.py check`) |
| Chấm cột `pass` theo metric spec | Chạy cả bộ một lệnh, có run ID, model, token từng câu (`run.py eval`) · tính % đạt (`run.py score`) |
| Persona, số người dùng, giá model (`cost/personas.yaml`) | Sinh ≥50 phiên, chạy thật qua bản chạy thử, tính chi phí / phiên, / task thành công, / tháng 3 kịch bản (`run.py simulate`) |
| Backend API (`server/`) và giao diện web (`frontend/`, React + Vite) | — |

## Chạy trong 3 phút

Cần **Python 3.10 trở lên**, **không cần `pip install`**. Giao diện web cần thêm Node.js.

**Bước 1 — Mở cửa sổ lệnh ngay trong thư mục repo**

| Windows (PowerShell) | macOS |
|---|---|
| Mở thư mục repo bằng File Explorer → bấm vào thanh địa chỉ → gõ `powershell` → Enter | Mở **Terminal** → gõ `cd ` (có dấu cách) → kéo thả thư mục repo vào → Enter |

**Bước 2 — Kiểm Python, nối model, chạy thử**

| Việc | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Kiểm Python | `python --version` (không được thì `py --version`) | `python3 --version` |
| Tạo file `.env` để nối model | `copy .env.example .env` | `cp .env.example .env` |
| Chạy bản chạy thử (chọn `1` = CLI, `2` = API) | `python run.py` | `python3 run.py` |
| Kiểm bộ câu thử | `python run.py check` | `python3 run.py check` |

- Điền `.env`: `MODEL_PROVIDER=openrouter`, `MODEL_NAME=deepseek/deepseek-v4.1-flash`, `API_KEY=…` (nhóm đang dùng). Hỗ trợ thêm `openai`, `anthropic`, `ollama`. Xem [docs/connect-model.md](docs/connect-model.md). **Không** đưa khóa vào Git. Chế độ `fake` không tạo được hồ sơ AI hợp lệ.
- Thử CLI: dán ô `input` của câu B01 trong `eval/benchmark.csv` → thường ra giỏ ở `store_01`, 5 suất phở gà, tổng 285.000đ gồm ship, còn 15.000đ. Mỗi bước gọi model mất khoảng 10–40 giây.

**Bước 3 — Chạy giao diện web (tùy chọn)**

| Việc | Lệnh (PowerShell) |
|---|---|
| Chạy API (cửa sổ 1, ở thư mục repo) | `$env:LION_MODE="web"; python run.py` → `http://127.0.0.1:8000/api` |
| Cài và chạy frontend (cửa sổ 2) | `cd frontend; npm.cmd install; $env:VITE_USE_MOCK="false"; npm.cmd run dev` → mở `http://localhost:5173` |

macOS / Linux: `LION_MODE=web python3 run.py` và `cd frontend && npm install && VITE_USE_MOCK=false npm run dev`.

## Lệnh

| Lệnh | Làm gì |
|---|---|
| `python run.py` | Chạy bản chạy thử (CLI hoặc API) |
| `python run.py check` | Kiểm `eval/benchmark.csv` và `eval/metric_spec.yaml`. Chỉ cảnh báo, không sửa file |
| `python run.py eval --try` | Thử nối model: chạy 3 câu đầu → `eval/run-try.csv`. Không tính là một lượt |
| `python run.py eval` | Chạy cả bộ 20 câu qua `codebase/agent.py` → `eval/run-N.csv` + `traces/run-N.jsonl` |
| `python run.py score eval/run-N.csv` | Sau khi điền cột `pass` (1 / 0): in % đạt tổng và theo `type` |
| `python run.py simulate --try` | Thử mô phỏng chi phí 10 phiên → `cost/simulate-try.csv` |
| `python run.py simulate --rate-from eval/run-2.csv` | Mô phỏng chi phí theo `cost/personas.yaml` (50 phiên), lấy tỉ lệ đạt của lượt 2 → `cost/simulate-N.csv` + `cost/simulate-N-summary.md` |
| `python -X utf8 -m unittest discover -s tests` | Chạy bộ test của nhóm (`tests/`) |

**API** (chế độ web): `POST /sessions` (`{"chat_text":"..."}`), `GET /sessions/{id}`, `POST /sessions/{id}/messages` (`{"text":"..."}`), `POST /sessions/{id}/confirm`, `POST /sessions/{id}/finalize`, `GET /restaurants`, `GET /restaurants/{id}/menu`, `POST /debug/validate-cart`. Phiên lưu trong `sessions.sqlite3` (đã bỏ qua bởi Git; đổi đường dẫn bằng `LION_DB_PATH`). Hợp đồng đầy đủ: [docs/ba/04-hop-dong-du-lieu-API.md](docs/ba/04-hop-dong-du-lieu-API.md) · nối frontend: [docs/frontend-tu.md](docs/frontend-tu.md) · mock JSON: [docs/ba/mocks/](docs/ba/mocks/).

**Lượt có lỗi kỹ thuật:** không sửa tay file đó, chạy lại thành lượt mới và ghi vào bảng các lượt ở `eval/README.md`. Không xoá file lượt nào.

## Bản chạy thử — viết ở đâu

| File | Viết gì |
|---|---|
| `codebase/agent.py` | `answer(text)` — đọc đầu vào câu thử (quán ứng viên, quỹ, phí ship, chat, xác nhận) và chạy luồng chính |
| `codebase/core.py` | Bộ điều phối 2 phase: PROFILE_DRAFT → CART_VALID / CART_INFEASIBLE → FINALIZED; chọn quán, lập giỏ, đổi món / quỹ / quán qua chat |
| `codebase/llm_steps.py` + `prompts/` | 5 bước gọi model: trích hồ sơ, áp câu trả lời, chọn quán, chọn món, phân loại tin nhắn tiếp theo |
| `codebase/tools.py` | Công cụ tất định có `@tool`: `list_restaurants`, `load_menu`, `safe_mains`, `feasibility`, `validate_cart`, `shipping_fee`, `store_summary` |
| `codebase/ai.py` | `call_model(system, user)` — chỗ duy nhất gọi model |

## Phần nào thật, phần nào giả

| Thành phần | Thật / Giả | Ghi chú |
|---|---|---|
| Lời gọi AI ở quyết định trung tâm (`codebase/llm_steps.py`, `ai.py`) | **Thật** (từ CP3) | `deepseek/deepseek-v4.1-flash` qua OpenRouter, temperature 0 |
| Kiểm giỏ (`validate_cart`, `safe_mains`, `feasibility`) | **Thật** | Code tất định, không gọi LLM: món ngoài menu, nhãn dị ứng qua mọi nguyên liệu (gồm nước dùng, nước chấm), món chay, số suất, tổng sau ship |
| Khoá ràng buộc | **Thật** | Ràng buộc dị ứng / chay chỉ thêm được, không gỡ được qua chat; người đặt xác nhận hồ sơ trước khi lập giỏ |
| Phí ship (`shipping_fee`) | **Mô phỏng** | 15.000đ trong 2 km đầu, +5.000đ mỗi km tiếp theo, theo `distance_km` của quán mẫu |
| Menu quán (`data/dataset_mon_an_viet.json`) | **Mô phỏng** | 100 món, 10 quán, 174 nguyên liệu, 10 loại nhãn dị ứng; công thức demo cố định, chi tiết tại [data/DATA_CARD.md](data/DATA_CARD.md) |
| Đoạn chat trong bộ câu thử | **Mô phỏng** | Dựng từ tình huống trong khảo sát (9/20 câu dẫn về mã phản hồi) và tự viết |
| Đặt đơn, thanh toán, GrabFood / ShopeeFood | **Không làm** | Ngoài lát cắt (`spec.md` §4) |

## Kết quả

| | Số | Nguồn |
|---|---|---|
| Bằng chứng pain | Khảo sát 20/23 người qua sàng lọc, 13/20 phải sửa món, đổi quán hoặc không đặt được · phỏng vấn 3 người ngoài nhóm, 3/3 phải hỏi lại hoặc sửa giỏ | [evidence/summary.md](evidence/summary.md) |
| Đánh giá | Lượt 1 → lượt 2: **14/20 (70%) → 15/20 (75%)** · lượt 3 thêm 18/20 (90%), chưa đạt trọn chuẩn (ràng buộc ăn uống 5/6) · 0 giỏ vi phạm ở cả 3 lượt | [eval/report.md](eval/report.md), [eval/README.md](eval/README.md) |
| Chi phí | **$0,0029 / task thành công** (DeepSeek V4.1 Flash, tỉ lệ đạt 75% lượt 2) · $2,03 / tháng ở kịch bản cơ sở 200 người | [cost/cost-estimate.md](cost/cost-estimate.md) |

## Dùng AI vào việc gì

Chi tiết từng việc: [docs/ai-usage.md](docs/ai-usage.md). Coding agent đọc [AGENTS.md](AGENTS.md).

- **Lương:** dùng Claude Code để viết agent, prompt và các bản sửa lỗi giữa ba lượt đánh giá, đề xuất điểm cột `pass`, viết phí ship theo khoảng cách và báo cáo đánh giá; Lương duyệt từng thay đổi và từng điểm trước khi commit.
- **Cường:** dùng Codex để viết khung CP2, rà câu hỏi khảo sát, tổng hợp số liệu khảo sát, soạn benchmark và cập nhật tài liệu; hai agent chấm thử độc lập 5 output mô phỏng CP2.
- **Dũng:** *(Dũng bổ sung)*
- **Tú:** *(Tú bổ sung)*
- Không dùng AI để tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát hay sửa kết quả các lượt đã chạy.

## Bảy hạng mục bắt buộc — nằm ở file nào

| # | Hạng mục | File |
|---|---|---|
| 1 | Bằng chứng pain | `evidence/` (tổng hợp ở [evidence/summary.md](evidence/summary.md)) |
| 2 | Impact có số | `spec.md` §2 |
| 3 | Thiết kế giải pháp | `spec.md` §4 |
| 4 | Bản chạy thử làm trọn lát cắt | `codebase/`, `server/`, `frontend/` · lệnh ở mục "Lệnh" |
| 5 | Định nghĩa "tốt" + bộ câu thử | [data/DATA_CARD.md](data/DATA_CARD.md) · `eval/` |
| 6 | Mô phỏng chi phí khi dùng thật | `cost/` |
| 7 | Slide + demo + video dự phòng | [demo-slides.pdf](demo-slides.pdf) ở thư mục gốc repo (dàn ý: `slides/outline.md`) · video CP4: [Google Drive](https://drive.google.com/file/d/1CMf3zfUAsNhWSvOaJuHrElhSdF42p5EU/view?usp=drive_link) |
| + | *Bonus:* người dùng thử | `validation/log.md` (chưa có phiên dùng thử) |
