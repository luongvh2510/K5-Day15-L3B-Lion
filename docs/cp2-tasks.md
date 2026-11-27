# CP2 — việc của từng người (hạn 19:30 Thứ Sáu 27/11)

Hướng dẫn gốc: `docs/btc/02-guide.md` mục 2.1–2.5. Dùng AI thoải mái, nhưng ai cũng phải giải thích được phần của mình. Không commit `.env`. Không bịa số hay trích dẫn (chưa có nguồn thì ghi "tự ước tính").

## Cả nhóm (17:30–18:50)
1. 17:30 Báo kết quả 1 cuộc hỏi / 1 form đã gửi, chốt lát cắt.
2. Mỗi người thử 1 app gần giống, ghi 1 điều đáng học + 1 điều đáng né.
3. 18:00 Chốt sơ đồ kiến trúc, 18:40 chốt ≥6 kịch bản khó + 2 tấn công.

## Lương — AI chính, đội trưởng
- `spec.md` §4: sơ đồ kiến trúc, mức tự động, ≥3 nguyên tắc (có G10).
- `codebase/agent.py`: khung chạy hết luồng với AI giả.
- `spec.md` §7: chốt chuẩn "đạt" (commit trước 19:30).
- Kiểm tổng (`python run.py check`), merge main, nộp form CP2.

## Tú — giao diện + frontend
- Vẽ sơ đồ bản sạch cho `spec.md` §4; thêm cột "hiện gì / làm gì tiếp" cho từng kịch bản §5.
- Viết ≥6 đoạn chat mẫu vào `eval/benchmark.csv` (xoá dòng mẫu B01–B03).
- Chấm thử 5 output cùng Cường (khớp ≥4/5) và review chéo benchmark.

## Cường — BA
- `canvas.md`: dòng 4 (số đầu + 1 trích dẫn thật), dòng "Đã đổi gì so với CP1".
- `evidence/summary.md`: nguồn bằng chứng và đã làm đến đâu.
- `spec.md` §0–§3 và §5.
- `eval/metric_spec.yaml` (≥3 metric) + ≥4 câu benchmark; nháp chuẩn "đạt" cho Lương.

## Dũng — backend + phụ AI
- Dữ liệu 3 quán mẫu (có seed) + `data/DATA_CARD.md`.
- `codebase/tools.py`: `lay_menu`, `validate_cart` (dị ứng, chay, thiếu thành phần, ngoài menu, vượt quỹ gồm ship).
- Nối tools vào `agent.py` cùng Lương; review benchmark xem kiểm được bằng code không.

## Trước 19:30
`python run.py check` hết cảnh báo benchmark/metric · `python run.py` chạy hết luồng · merge vào `main` · mở link repo bằng cửa sổ ẩn danh.
