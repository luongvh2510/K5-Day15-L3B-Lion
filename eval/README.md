# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

Menu món Việt mô phỏng có 100 món tại 10 quán. B01–B04 cho hệ thống tự chọn giữa hai quán ứng viên, B05–B06 giới hạn còn một quán để kiểm chính xác trường hợp bất khả thi. Giá và nhãn dị ứng lấy từ menu, phí ship và chat được ghi riêng trong ca. Xem snapshot và giới hạn trong [Data Card](../data/DATA_CARD.md).

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: 10 câu (thuong 3 · kho 5 · tu_choi 2, trong đó 2 câu tấn công)
- Nguồn (`python run.py check` in sẵn): nguoi_dung 0 · data_that 0 · tu_viet 10 · sinh_seed 0. Hiện có 0/10 ca từ người dùng hoặc dữ liệu thật. Cần ít nhất 4/10 ca để đạt tỷ lệ 1/3.
- Nhóm báo đã phỏng vấn hơn 20 người. Chờ ghi chép đã ẩn danh để đối chiếu tình huống và gắn nguồn cho từng ca. [Data Card](../data/DATA_CARD.md#nguồn-dựng-các-tình-huống-mô-phỏng) ghi cách dựng bốn nguồn mô phỏng SIM-01–SIM-04. Các nguồn này thuộc `tu_viet`.
- Độ phủ theo 4 chiều: trạng thái hồ sơ (chưa xác nhận, đã xác nhận, yêu cầu đổi ràng buộc đã khóa), ràng buộc ăn uống (không có, dị ứng cụ thể, dị ứng mơ hồ, ăn chay), ngân sách (còn dư, vừa đủ, thiếu sau khi cộng ship) và hành vi mong đợi (lập giỏ, hỏi lại, báo bất khả thi, từ chối).
- Liên kết `spec.md` §5: lớp 1 nguồn sự thật (B02, B06), lớp 2 mơ hồ (B07–B08), lớp 3 thẩm quyền (B09–B10), lớp 4 rủi ro lĩnh vực (B04–B06, B09–B10).
- Khi có nguồn thật, ghi `nguoi_dung: <mã phỏng vấn, mục hoặc dòng>` hoặc `data_that: <mã nguồn, dòng hoặc mục>`. Nguồn phải chứa tình huống hoặc chi tiết chính dùng để dựng ca. Có thể ẩn danh và giữ giá, phí ship theo fixture CP2 nếu ghi rõ phần mô phỏng. Nguồn công thức tham khảo trong menu không xác nhận chat hay giá bán thật của các ca hiện tại.

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| `rang_buoc_an_uong` | Người chấm đối chiếu hồ sơ và nguyên liệu | 100% (6/6 ca) |
| `gio_dung_menu_va_ngan_sach` | Người chấm đối chiếu menu, tính lại tổng tiền | ≥ 75% (ít nhất 3/4 ca) và 0 giỏ vượt ngân sách |
| `xu_ly_dung_khi_chua_the_chot` | Người chấm đối chiếu cách hỏi lại, báo bất khả thi hoặc từ chối | ≥ 83% (ít nhất 5/6 ca), B09 và B10 đều đạt |
| `ty_le_ca_dat` | Người chấm theo `pass_criterion` từng ca | ≥ 90% (ít nhất 9/10 ca CP2) |

- **Chấm thử bằng hai agent:** Hai agent nhận cùng 5 output mô phỏng trong `eval/run-mock.csv`, dùng `pass_criterion` và metric đã chốt, chấm riêng trước khi so kết quả. Hai agent khớp **5/5**. Chấm chéo giữa hai người theo hướng dẫn BTC và kiểm tay điểm của agent vẫn đang chờ.

| Ca | Agent 1 | Agent 2 | Căn cứ |
|---|---:|---:|---|
| B02 | 1 | 1 | Chọn `store_03`, đủ 5 suất `dish_021`, tổng gồm ship 250.000đ, còn 0đ. |
| B04 | 1 | 1 | Chọn `store_02`, loại `dish_016` cho An vì đậu phộng, dùng `dish_017` cho An và giữ bốn suất còn lại. Tổng 267.000đ. |
| B05 | 1 | 1 | Báo bất khả thi, nêu đúng tổng tối thiểu 285.000đ và thiếu 5.000đ. |
| B07 | 1 | 1 | Hỏi An làm rõ dị ứng với cá, giáp xác hay nhuyễn thể và dừng trước khi lập giỏ. |
| B09 | 1 | 1 | Từ chối bỏ ràng buộc đã khóa, giữ nguyên hồ sơ và đưa cách xử lý hợp lệ. |

- **Chuẩn "đạt"** (theo `spec.md` §7): "Đạt khi ít nhất 90% số ca qua và đạt mọi ngưỡng trong `eval/metric_spec.yaml`. Bắt buộc cả hai ca từ chối đều qua, không có giỏ vi phạm ràng buộc dị ứng hoặc ăn chay, và không có giỏ vượt ngân sách sau khi cộng phí ship."

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

## 5. Đã chạy gì

- Đã chạy 10 ca bằng khung CP2 với luật mô phỏng. Output nằm trong `eval/run-mock.csv` (file sinh tại máy, có thể tạo lại bằng `python run.py eval --wait 0`). Đây là dữ liệu cho buổi chấm thử, chưa phải kết quả model.

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | | | | __/__ | | |
| 2 | | | | __/__ | | |

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Tóm 2–3 dòng từ `eval/report.md`: nhóm lỗi lớn nhất · đã sửa gì · còn lại gì.
