# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Cùng bộ 20 câu thử (`eval/benchmark.csv`), cùng model `deepseek/deepseek-v4.1-flash` qua OpenRouter, cùng cách chấm: người chấm 1/0 theo `pass_criterion` và `eval/metric_spec.yaml`, chỉ đọc output (không tính phần chỉ có trong trace). Chấm ở rubric R5 (lượt 1 → lượt 2). Lượt 3 chạy thêm trước CP4, ghi ở mục 5.
> Số lấy từ `python run.py score eval/run-N.csv`. Không sửa chuẩn "đạt", không bỏ câu trượt, không sửa `expected`, không sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261128-082642` | 14/20 | 70% | 4/4 | 8/14 | 2/2 | **chưa** — tổng < 90%, `rang_buoc_an_uong` 5/6 |
| 2 | `run-2@20261128-090040` | 15/20 | 75% | 3/4 | 10/14 | 2/2 | **chưa** — tổng < 90%, `rang_buoc_an_uong` 5/6, `ty_le_ca_dat` 8/10 |
| 3 *(thêm)* | `run-3@20261128-091232` | 18/20 | 90% | 4/4 | 12/14 | 2/2 | **chưa** — tổng đạt 90% nhưng `rang_buoc_an_uong` 5/6 |

Chi tiết từng metric theo chuẩn đã chốt ở CP2:

| Metric | Ngưỡng | Lượt 1 | Lượt 2 | Lượt 3 |
|---|---|---|---|---|
| `rang_buoc_an_uong` (B04, B06–B10) | 100% (6/6) | 5/6 ✗ (B06) | 5/6 ✗ (B06) | 5/6 ✗ (B04) |
| `gio_dung_menu_va_ngan_sach` (B01–B04) | ≥ 3/4, 0 giỏ vượt quỹ | 4/4 ✓ | 3/4 ✓ (B01) | 3/4 ✓ (B04) |
| `xu_ly_dung_khi_chua_the_chot` (B05–B10) | ≥ 5/6, B09 và B10 đạt | 5/6 ✓ | 5/6 ✓ | 6/6 ✓ |
| `ty_le_ca_dat` (10 ca CP2) | ≥ 9/10 | 9/10 ✓ | 8/10 ✗ | 9/10 ✓ |
| Điều kiện cứng: 2 ca từ chối qua · 0 giỏ vi phạm dị ứng/chay · 0 giỏ vượt quỹ | bắt buộc | ✓ | ✓ | ✓ |

Ở cả ba lượt, **không có giỏ nào vi phạm dị ứng, ăn chay hay vượt quỹ** — các câu trượt đều là hỏi lại thiếu, báo thiếu căn cứ hoặc dừng sai chỗ, không phải giỏ nguy hiểm.

Kết quả từng câu: `eval/run-1.csv`, `eval/run-2.csv`, `eval/run-3.csv` (cột `ghi_chu` ghi lý do từng câu trượt). Trace: `traces/run-1.jsonl`, `traces/run-2.jsonl`, `traces/run-3.jsonl`.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| **Trích xuất chat sai** — bỏ sót người, gộp hai lựa chọn mâu thuẫn, đoán món từ ảnh thay vì hỏi lại | 3 | B14, B16, B17 |
| **Câu báo thiếu căn cứ** — báo không lập được giỏ nhưng không nói vì sao (chất dị ứng, mã quán sai) | 2 | B06, B20 |
| **Hồ sơ nháp không truy được về chat** — liệt kê lời dặn nhưng không kèm câu chat gốc | 1 | B12 |

**≥3 lỗi cụ thể:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| B14 | Hồ sơ 5 người đã xác nhận, quỹ 285.000đ, ứng viên store_10 (3,1 km) và store_01 (0,7 km); cả 5 người nhắn "món nào cũng được" | `Hồ sơ nháp, quỹ 285,000đ:` rồi dừng, không có thành viên nào | Model trả `members: []` vì prompt ghi "'Gì cũng được' không tạo gì" — hiểu thành không tạo cả thành viên. Không có hồ sơ thì không lập được giỏ, cả luồng dừng |
| B16 | Chat gom từ hai kênh: An và Chi nhắn "cơm gà xối mỡ", sau đó lại nhắn "cơm gà luộc" | Hồ sơ nháp ghi cả hai cho An và Chi (`cơm gà xối mỡ; cơm gà luộc`), không hỏi lại | Hai lựa chọn mâu thuẫn bị gộp thành hai sở thích, người đặt có thể đặt nhầm món — đúng tình huống PH08 trong khảo sát |
| B06 | An dị ứng cá, ứng viên duy nhất store_01 (mọi món có nước mắm cá) | `không có món phù hợp cho An. Đề xuất đổi sang quán khác.` | Đúng hành vi (không lập giỏ, không gán món có cá) nhưng không nêu lý do dị ứng cá, người đặt không biết vì sao phải đổi quán |
| B20 | Ứng viên store_99 (không có trong dữ liệu) | `không có món phù hợp cho An, Bình, Chi, Dũng, Hà` | Báo sai nguyên nhân: lỗi là mã quán không tồn tại, không phải thiếu món an toàn |

## 3. Một lần cải tiến (lượt 1 → lượt 2)

- **Nhắm vào nhóm lỗi:** *trích xuất chat sai* (B14, B16, B17).
- **Vì sao là nhóm đau nhất với người dùng:** hồ sơ là đầu vào của mọi bước sau. Trích xuất sai thì giỏ sai hoặc luồng dừng hẳn (B14), và đây đúng là pain chính trong bằng chứng: 3/3 người phỏng vấn và 11/17 người khảo sát phải hỏi lại, sửa giỏ hoặc đổi quán vì yêu cầu trong chat không rõ.
- **Đã sửa gì** (commit `21c1358`):
  1. `prompts/extract_profile.md`: mỗi người gửi tin là một thành viên kể cả khi chỉ nhắn "gì cũng được"; một người gửi hai món khác nhau mà không nói "thêm" thì hỏi lại người đó; tin nhắn chỉ là ảnh, sticker, link thì hỏi lại tên món.
  2. `codebase/llm_steps.py`: nếu model vẫn trả danh sách thành viên rỗng, code lấy mỗi người gửi ở dòng `Tên: nội dung` làm thành viên không ràng buộc (bỏ dòng giờ và link). 3 test mới trong `tests/test_llm_steps.py`.
- **Kết quả:** nhóm lỗi trích xuất 0/3 → **2/3** (B14, B16 đạt; B17 hỏi đúng An gõ lại tên món nhưng output không hiện ghi chú "đừng lấy hành tây" nên vẫn 0) · tổng **70% → 75%**.
- **Câu tệ đi sau khi sửa:** **B01** (đạt → trượt). Trích xuất giống hệt lượt 1, nhưng bước chọn quán lần này chọn store_03 (cơm tấm rẻ hơn) thay vì store_01 dù cả nhóm muốn phở gà. Bản sửa không đụng bước chọn quán; đây là model trả lời khác nhau giữa các lần chạy, làm lộ lỗi *chọn quán chưa xét sở thích* (cũng thấy khi chạy thử giao diện: người muốn ăn bún nhưng agent chọn quán xôi).

## 4. Còn lại

- **Model không ổn định giữa các lần chạy — nguy hiểm nhất còn lại.** Cùng input, cùng prompt, temperature 0 vẫn ra kết quả khác: B01 đạt ở lượt 1 và 3 nhưng trượt ở lượt 2; B04 đạt ở lượt 1 và 2 nhưng ở lượt 3 model tự thêm câu hỏi "An muốn đổi sang món gì?" dù hồ sơ đã xác nhận. Mỗi câu mới chạy một lần mỗi lượt, nên chưa đo được tỉ lệ dao động. Code kiểm cứng giỏ vẫn chặn được mọi giỏ vi phạm dị ứng, chay và quỹ, nên dao động làm hỏng trải nghiệm (hỏi thừa, chọn quán kém) chứ chưa tạo giỏ nguy hiểm.
- **B17:** khi còn câu hỏi mở, output chỉ in câu hỏi, không in các lời dặn đã ghi. Trace cho thấy hồ sơ vẫn giữ "đừng lấy hành tây", nhưng người đặt không thấy. Chưa sửa vì in cả hồ sơ kèm câu hỏi dễ làm B08 bị hiểu là đã gán phở gà cho người ăn chay.
- **Chưa kiểm ngoài bộ câu thử:** chưa có phần giữ riêng (held-out); các bản sửa ở lượt 2 và 3 được viết sau khi đọc câu trượt, nên 90% của lượt 3 có thể lạc quan hơn thực tế.
- **Nếu có thêm 1 tuần:** chạy mỗi câu ≥3 lần để đo dao động và thêm bước kiểm khi model tự sinh câu hỏi thừa sau khi hồ sơ đã xác nhận; dựng thêm 10 câu giữ riêng từ ghi chép phỏng vấn P1–P3 (hết món sau khi đặt, mã giảm giá hết lượt, ăn chay nhờ quán dùng chảo riêng); hiển thị lời dặn đã ghi cùng câu hỏi mở; tắt phần suy luận dài của model để giảm thời gian chờ 10–40 giây mỗi bước.

## 5. Lượt 3 (chạy thêm trước CP4, không thay lượt 2 để chấm R5)

- **Đọc câu trượt của lượt 2** (B01, B06, B12, B17, B20) và sửa ba nhóm còn lại trong `codebase/core.py` (commit `24915ef`, 7 test mới trong `tests/test_choice_and_render.py`):
  1. *Chọn quán chưa xét sở thích* (B01): trước khi model chọn, code đếm số người có lời dặn khớp món của từng quán khả thi và chỉ đưa các quán khớp nhiều người nhất cho model.
  2. *Câu báo thiếu căn cứ* (B06, B20): câu báo nêu ràng buộc, ví dụ "An (dị ứng cá)"; mã quán không có trong dữ liệu được báo riêng, và bị bỏ qua nếu danh sách còn quán hợp lệ.
  3. *Hồ sơ nháp không truy được về chat* (B12): mỗi người có lời dặn được in kèm `(chat: "…")`.
- **Kết quả:** 15/20 → **18/20 (90%)**. B01, B06, B12, B20 lên đạt; B04 rớt (model tự thêm câu hỏi, xem mục 4); B17 vẫn trượt.
- Lượt 3 vẫn **chưa đạt trọn chuẩn** vì `rang_buoc_an_uong` còn 5/6 (B04).
