# Tóm tắt mô phỏng simulate-1@20261128-103318

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dat_2_3_lan | 21 | 1 | 2028 | 1148 | 1.6 | 20.1 |
| dat_4_5_lan | 19 | 1 | 1862 | 1249 | 1.4 | 17.8 |
| dat_6_8_lan | 10 | 1 | 2859 | 1570 | 2.0 | 31.8 |

Tỉ lệ đạt dùng để tính: 15/20 (75%) — lượt run-2@20261128-090040

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (50 người) | Chi phí / tháng — cơ sở (200 người) | Chi phí / tháng — cao (500 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek/deepseek-v4.1-flash (vào 0.3 · ra 1.2 $/1M) | $0.0022 | $0.0029 | $0.0029 | $0.5076 | $2.03 | $5.08 | $0.0102 |
| openai/gpt-4.1-mini (vào 0.4 · ra 1.6 $/1M) | $0.0029 | $0.0038 | $0.0038 | $0.6768 | $2.71 | $6.77 | $0.0135 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.0) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: deepseek/deepseek-v4.1-flash. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
