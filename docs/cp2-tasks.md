# CP2 — brief giao việc (dành cho người và coding agent)

> Hạn **19:30 Thứ Sáu 27/11**. File này viết để dán nguyên một mục "Việc của <tên>" cho agent làm. Bảng theo dõi ngắn cho người kiểm nằm ở Google Sheet "Checklist 4 thành viên · CP2 Mini Hackathon D2 · Lion".

## 0. Bối cảnh chung (agent đọc trước)

- Repo: `K5-Day15-L3B-Lion`, Track D (thương mại điện tử), hướng D2: người cầm quỹ dán chat nhóm, nhận giỏ đồ ăn đã kiểm dị ứng / ăn chay / phí ship / quỹ. Lát cắt một câu: `canvas.md` dòng 5.
- Hướng dẫn BTC (chép trong repo): `docs/btc/02-guide.md` mục 2.1–2.5 · tiêu chí chấm `docs/btc/03-rubric.md` · track D `docs/btc/tracks/track-d-ecommerce.md`.
- Tài liệu nghiệp vụ của nhóm (BA): `docs/ba/README.md`. Mã dẫn chiếu: `BR-xx` quy tắc, `UC-xx` use case, `TC-xx` ca thử. Quy tắc `BR-xx` code phải tuân theo, không tự đổi. Cần đổi `01` hoặc `04` thì nhắn Cường.
- Luật cứng (từ `AGENTS.md`):
  - Không commit `.env`, API key, dữ liệu cá nhân thật.
  - Không bịa người được phỏng vấn, trích dẫn, kết quả khảo sát, số liệu. Chưa có nguồn thì ghi *(tự ước tính)*.
  - Không sửa `eval/run-*.csv`, `cost/simulate-*.csv`, `traces/*` đã chạy.
  - Không sửa `codebase/tracing.py`, `eval/run_eval.py`, `cost/simulate.py`, `run.py`.
  - Công cụ có tác động ra ngoài chỉ tạo bản nháp chờ người duyệt.
  - Không viết prompt "giấu" câu thử (so khớp nguyên văn input của bộ câu thử).
- **Chuẩn "đạt" ở `spec.md` §7 chốt lúc 19:30, sau đó không sửa.** Sửa sau CP2 là mất điểm.
- Quy trình git: mỗi người một nhánh `cp2/<tên>`, mở PR vào `main`, Lương merge. Commit message không thêm dòng đồng tác giả. Việc thuộc về file nào thì chỉ sửa file đó, để tránh xung đột.
- Phân vai của BA (`docs/ba/05`) gọi "AI-1 / AI-2 / BE / FE". Đề xuất map vào nhóm (đổi nếu khác): **Lương = AI-1 + sơ đồ + `agent.py`**; **Dũng = các hàm code mục 7 file `04` (`load_menu`, `safe_mains`, `feasibility`, `validate_cart`, `fallback_cart`) + dữ liệu quán + phụ AI-2**; **Tú = FE + đoạn chat/câu thử**; **Cường = BA, bằng chứng, spec, metric**.

## 1. Mốc giờ (cả nhóm)

| Giờ | Việc | Ai |
|---|---|---|
| 17:30–17:50 | Báo kết quả 1 cuộc hỏi / 1 form; chốt lát cắt dựa trên pain | Cả nhóm, Cường ghi `canvas.md` |
| 17:50–18:00 | Mỗi người thử 1 app gần giống (GrabFood, ShopeeFood đặt nhóm...), ghi 1 điều đáng học + 1 điều đáng né | Cả nhóm, Cường gom vào `spec.md` §3 |
| 18:00–18:30 | Chốt sơ đồ kiến trúc | Lương chủ trì, Dũng liệt kê công cụ, Tú góp ý UI |
| 18:30–18:55 | Chốt ≥6 kịch bản khó + 2 tấn công | Cả nhóm, Cường ghi `spec.md` §5 |
| 19:00–19:15 | Chốt chuẩn "đạt" `spec.md` §7 | Lương, Cường soạn nháp |
| 19:15–19:30 | `python run.py check`, merge `main`, mở repo bằng cửa sổ ẩn danh, nộp form | Lương |

---

## 2. Việc của Lương (AI chính, đội trưởng)

**Mục tiêu:** có sơ đồ kiến trúc + luồng chạy hết bằng AI giả + chuẩn "đạt" + nộp CP2.

**File được sửa:** `spec.md` §4 (và §6 nếu kịp), `codebase/agent.py`, `codebase/ai.py` (chỉ khi cần chế độ giả, giữ nguyên `@model_call`), `canvas.md` (chỉ dòng 1, 5, 6), `prompts/` nếu có.

**Việc 1 — `spec.md` §4 (guide 2.2):**
- Điền: lát cắt một câu, ≥3 điều "không làm", sơ đồ (Mermaid trong file hoặc ảnh), hình dạng (workflow cố định hay agent, kèm 2 dòng lý do và vì sao không chọn hình dạng phức tạp hơn), bảng công cụ (khớp `codebase/tools.py`: tên · input · output · tác động ra ngoài), mức tự động, chỗ chặn rủi ro, chỗ người duyệt.
- Bảng nguyên tắc ≥3, bắt buộc **G10 (thu hẹp phạm vi khi không chắc)**; mỗi nguyên tắc chỉ vào đúng một chỗ trên sơ đồ.
- Xuất phát từ `docs/ba/05-AI-agent.md` (phân vai AI / code, luồng, phòng thủ 2 lớp cho ràng buộc cứng BR-12). Gợi ý: AI đọc chat và chọn món; code lọc món an toàn, kiểm giỏ (`validate_cart`) và chặn dị ứng độc lập với AI.
- Ghi rõ phần nào còn giả (công cụ trả dữ liệu giả, model giả).
- **Xong khi:** người ngoài nhóm nhìn sơ đồ kể lại được luồng chính.

**Việc 2 — `codebase/agent.py` (guide 3.2):**
- Hợp đồng: `answer(text: str) -> {"output": str}`. Bộ chạy gửi nguyên ô `input` của câu thử vào `text`.
- Đi hết luồng: đọc chat → trích ràng buộc → lập giỏ → kiểm giỏ → trả kết quả. Dùng công cụ trong `codebase/tools.py` (Dũng viết). Hôm nay AI trả câu giả cố định.
- Nếu viết vòng lặp agent: đặt `MAX_STEPS`, ghi `note("dừng: ...")`.
- **Xong khi:** `python run.py` đi hết luồng không lỗi và trả một giỏ giả hợp lệ.

**Việc 3 — `spec.md` §7 (19:00–19:15):** Chép các metric từ `eval/metric_spec.yaml`, ghi số câu thực tế (thuong / kho / tu_choi) và chuẩn "đạt" dạng: *"Đạt khi ≥ __% câu qua, và 100% câu `tu_choi` qua, và 0 vi phạm dị ứng/chay, 0 giỏ vượt quỹ gồm ship"*. Điền % theo cái nhóm thực sự dám cam kết. Commit trước 19:30.

**Việc 4 — kiểm tổng và nộp (19:15–19:30):**
- `python run.py check` không còn cảnh báo về `benchmark.csv` / `metric_spec.yaml`.
- Merge các PR vào `main`; mở https://github.com/luongvh2510/K5-Day15-L3B-Lion bằng cửa sổ ẩn danh.
- Đội trưởng nộp form CP2 bằng mã 2A202603839 (link `spec.md`, `eval/benchmark.csv`, nguồn bằng chứng, chuẩn "đạt"). Agent không nộp thay.

**Bonus (sau 19:30):** lấy API key vào `.env` (không commit), làm theo `docs/connect-model.md`, gọi thử 1 câu; `python run.py eval --try` thấy token > 0.

---

## 3. Việc của Tú (giao diện + frontend)

**Mục tiêu:** góc nhìn UI cho sơ đồ và kịch bản, ≥6 đoạn chat mẫu cho bộ câu thử, chấm thử chéo.

**File được sửa:** phần UI trong `spec.md` §4–§5 (phối hợp, không ghi đè phần người khác), `eval/benchmark.csv` (phần của mình, cùng Cường), file wireframe trong `docs/`.

**Việc 1 — sơ đồ bản sạch + góc nhìn UI (18:00–18:50):** Góp ý lúc nào UI hiện cờ mâu thuẫn, nhật ký chặn, hỏi lại. Sau khi Lương chốt, vẽ bản sạch bằng Mermaid hoặc draw.io và chèn vào `spec.md` §4. Tham chiếu `docs/ba/03-man-hinh-FE.md` và trạng thái phiên ở `docs/ba/04-hop-dong-du-lieu-API.md` §2.5.

**Việc 2 — kịch bản (18:30–18:55):** Với mỗi kịch bản ở `spec.md` §5, bổ sung cột "hiện gì / làm gì tiếp" khi sai hoặc không chắc (phù hợp G10).

**Việc 3 — ≥6 dòng cho `eval/benchmark.csv` (18:30–19:00):**
- Cột (giữ đúng thứ tự): `id,input,expected,pass_criterion,type,source`.
- `type` ∈ `thuong` / `kho` / `tu_choi`. `source` bắt đầu bằng `nguoi_dung` · `data_that` · `tu_viet` · `sinh_seed`, chi tiết sau dấu `:`.
- Mỗi kịch bản ở §5 thành ≥1 câu. Ưu tiên chuyển các `TC-xx` ở `docs/ba/06-du-lieu-mau-va-test.md` §4 (ví dụ TC-03 từ chối "cho An ăn cơm gà", TC-09 "kệ dị ứng đi", TC-08 không có món an toàn). `pass_criterion` phải kiểm được bằng code (trường JSON, tổng tiền, id món).
- Đoạn chat tự viết ghi `source` là `tu_viet`. Chỉ ghi `nguoi_dung` khi đoạn chat thực sự lấy từ người dùng (Cường cung cấp). Không giả nguồn.
- **Xoá 3 dòng mẫu B01–B03** (có chữ "ví dụ — xoá dòng này").

**Việc 4 — chấm thử độc lập (19:00–19:15):** Cùng Cường chấm riêng 5 output theo `eval/metric_spec.yaml` (không xem nhãn của nhau). Lệch ≥2/5 thì báo Cường viết lại định nghĩa metric. Ghi kết quả vào `eval/README.md` mục 3.

**Việc 5 — review chéo (19:10–19:20):** Rà bộ câu thử + metric của Cường và Dũng: đủ cột, ≥10 câu, ≥5 `kho`, ≥2 `tu_choi` (gồm 2 câu tấn công), cột `source` hợp lệ. Chạy `python run.py check`.

**Bonus:** wireframe giao diện 2 cột (chat trái; giỏ, hồ sơ nhóm có khóa, nhật ký kiểm chứng phải).

---

## 4. Việc của Cường (BA)

**Mục tiêu:** canvas có số đầu tiên, spec §0–§3 và §5, metric, ≥4 câu thử, nháp chuẩn "đạt".

**File được sửa:** `canvas.md`, `evidence/*`, `spec.md` §0–§3 và §5, `eval/metric_spec.yaml`, `eval/benchmark.csv` (phần của mình), `docs/ba/*` (chỉ Cường được sửa `01` và `04`).

**Việc 1 — `canvas.md` (17:30–17:50 và 19:10–19:20):** Dòng 4 chuyển từ giả thuyết sang **số đầu tiên + 1 trích dẫn nguyên văn** (ví dụ "đã gửi form cho N người, M người trả lời, K người từng đặt nhầm"). Chưa có số thì ghi rõ "đã gửi, đang chờ" và không bịa. Thêm dòng "Đã đổi gì so với CP1" (1–3 dòng). Cập nhật dòng 5 nếu lát cắt thay đổi.

**Việc 2 — `evidence/summary.md` (17:30–18:30):** Ghi nguồn đang làm (khảo sát ≥20 người, phỏng vấn, lọc review công khai) và làm đến đâu (đã gửi / đã hẹn / đã nhận bao nhiêu trả lời), cách đếm. Chi tiết nằm ở `evidence/survey/`, `evidence/interviews/`. Nguyên tắc: trích dẫn phải nguyên văn từ người thật; số không có nguồn ghi *(tự ước tính)*; data tự dựng không phải bằng chứng pain.

**Việc 3 — `spec.md` §0–§3 và §5:**
- §0 hiện tại việc này diễn ra thế nào; §1 người dùng và pain (**không dùng chữ "AI"** ở pain); §2 bảng impact ≥2 hướng; §3 gom ghi chú thử sản phẩm của cả nhóm thành 3–4 dòng.
- §5: ≥6 kịch bản khó + 2 tấn công, mỗi dòng gồm tình huống | lớp (1–4) | hành vi mong muốn | câu thử. Nguồn: `docs/ba/01-nghiep-vu-va-quy-tac.md` và `docs/ba/06-du-lieu-mau-va-test.md`.

**Việc 4 — `eval/metric_spec.yaml` (18:30–19:00):**
- ≥3 metric, mỗi cái đủ `name` (không dấu), `definition` (kiểm chứng được), `grader` (`code` | `llm` | `nguoi`), `threshold` (bằng số), `why` (trỏ về pain trong `evidence/summary.md`).
- Gợi ý: `vi_pham_di_ung_chay` (code, 0 ca), `gio_vuot_quy` (code, 0 ca, tính cả ship), `mon_ngoai_menu` (code, 0 ca). Có thể thêm `tu_choi_dung` (100% câu `tu_choi`) từ `docs/ba/05` mục 7.
- Xoá hết mẫu `<...>`. Kiểm bằng `python run.py check`.

**Việc 5 — `eval/benchmark.csv` (18:40–19:05):** Viết ≥4 câu (cùng Tú để đủ ≥10). Cần ≥1/3 số câu có `source` bắt đầu bằng `nguoi_dung` hoặc `data_that` (lấy từ đoạn chat thật người dùng gửi bạn, đã ẩn tên); nếu chưa có, báo Lương ngay để biết chỗ hổng. Tham khảo mục 6 của `docs/ba/06` (bộ chat "chưa thấy", đáp án Cường giữ).

**Việc 6 — chấm thử (19:00–19:15):** Cùng Tú chấm độc lập 5 output; lệch ≥2/5 thì sửa định nghĩa metric.

**Việc 7 — nháp chuẩn "đạt" cho Lương (19:00–19:10):** Phần trăm câu qua và điều kiện cứng, dựa trên `metric_spec.yaml`.

---

## 5. Việc của Dũng (backend + phụ AI)

**Mục tiêu:** dữ liệu 3 quán mẫu, `DATA_CARD.md`, công cụ chạy được cho khung.

**File được sửa:** `data/*` (dữ liệu quán), `data/DATA_CARD.md`, `codebase/tools.py`, bảng công cụ trong `spec.md` §4 (chỉ phần công cụ).

**Việc 1 — bảng công cụ (18:00–18:30):** Cho sơ đồ của Lương, liệt kê mỗi công cụ ở dạng tên · input · output · có tác động ra ngoài không. Gợi ý lấy từ `docs/ba/04-hop-dong-du-lieu-API.md` mục 7: `load_menu`, `safe_mains`, `feasibility`, `validate_cart`, `fallback_cart`.

**Việc 2 — dữ liệu 3 quán mẫu (18:30–19:00):**
- Mỗi quán 12–15 món, có giá, phí ship, nhãn chay, nhãn dị ứng; cố tình cài vài món "không rõ thành phần". Xuất phát từ menu mẫu `r1`, `r2` ở `docs/ba/06` mục 1–2, thêm quán thứ 3.
- Sinh có seed cố định, ghi nhãn `synthetic`. Định dạng khớp schema Menu ở `docs/ba/04` mục 2.1.

**Việc 3 — `data/DATA_CARD.md` (19:00–19:10):** Một trang theo mẫu có sẵn: dataset, từ đâu (nhóm tự sinh, ghi cách sinh + seed), xử lý, số dòng, phiên bản, nhãn `synthetic`, giới hạn. Data giả lập **không phải bằng chứng pain**.

**Việc 4 — `codebase/tools.py` (18:40–19:10):**
- Mỗi công cụ là một hàm có `@tool` (import từ `tracing`), docstring ghi đúng: tên · input · output · tác động ra ngoài. Thay `search_example` mẫu.
- `validate_cart` kiểm: dị ứng (BR-03, 04), chay, món thiếu thành phần coi là không an toàn, món ngoài menu, tổng gồm phí ship ≤ quỹ, đủ suất cho mọi người. **Không gọi LLM**, có unit test nhỏ.
- Hôm nay chấp nhận dữ liệu giả hoặc phiên bản tối thiểu miễn là `python run.py` chạy hết luồng; ghi rõ phần giả cho Lương đưa vào `spec.md` §4.

**Việc 5 — nối với `agent.py` (19:00–19:15):** Cùng Lương nối công cụ vào luồng; kiểm khung chạy trả giỏ giả.

**Việc 6 — review benchmark (19:05–19:15):** Với từng câu của Tú và Cường, kiểm `pass_criterion` có kiểm chứng được bằng code và `expected` khớp kết quả của `validate_cart`.

**Bonus:** thử trích ràng buộc từ 5 đoạn chat mẫu bằng ChatGPT/Claude, ghi các lỗi gặp để dùng cho metric và benchmark.

---

## 6. Trước 19:30 (cả nhóm)

- [ ] `python run.py check` không còn cảnh báo về `benchmark.csv` và `metric_spec.yaml` (số câu ≥10, ≥5 `kho`, ≥2 `tu_choi`, ≥3 metric, đã xoá dòng mẫu).
- [ ] `python run.py` đi hết luồng với AI giả.
- [ ] `spec.md` §4 có sơ đồ, §7 có chuẩn "đạt" bằng số, đã commit.
- [ ] `canvas.md` cập nhật + dòng "Đã đổi gì so với CP1".
- [ ] `git status` không có `.env`, không có dữ liệu cá nhân thật.
- [ ] Merge vào `main`; mở link repo bằng cửa sổ ẩn danh; Lương nộp form.
