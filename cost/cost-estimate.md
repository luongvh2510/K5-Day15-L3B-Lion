# Chi phí khi dùng thật

## 1. Đầu vào

- **Persona:** [personas.yaml](personas.yaml), từ Q2 [khảo sát](../evidence/survey/results.csv), N = 20 người qua Q1: 7/20 đặt 2–3 lần, 8/20 đặt 4–5 lần, 5/20 đặt 6–8 lần trong 30 ngày. Tần suất lần lượt 18/7, 36/8, 34/5 lượt/người/tháng là trung bình từng nhóm. Số lượt hỏi/phiên = 1 *(tự ước tính)*; input benchmark là một lượt độc lập, chưa đại diện đủ cho hội thoại thực.
- **Số người dùng hoạt động:** thấp 50 · cơ sở 200 · cao 500 người/tháng *(tự ước tính, chưa có số người dùng thật; không xem mẫu khảo sát là quy mô thị trường)*.
- **Giá USD/1 triệu token, xem 28/11/2026:** [DeepSeek V4.1 Flash qua OpenRouter, Fireworks standard](https://openrouter.ai/deepseek/deepseek-v4.1-flash), vào $0,30 · ra $1,20; [GPT-4.1 mini qua OpenRouter](https://openrouter.ai/openai/gpt-4.1-mini), vào $0,40 · ra $1,60. Không tính ưu đãi cache; OpenRouter có thể định tuyến qua nhà cung cấp có giá khác, nên giá Fireworks là kịch bản tham chiếu chứ không phải hóa đơn thực tế.
- **Tỉ lệ đạt bắt buộc:** 15/20 = **75%**, [lượt 2](../eval/run-2.csv), run ID `run-2@20261128-090040`, model `deepseek/deepseek-v4.1-flash`. Chỉ định `--rate-from eval/run-2.csv` để không tự lấy 90% của lượt 3.
- Đo token bằng DeepSeek V4.1 Flash; mức GPT-4.1 mini là phép áp giá lên cùng số token, không phải token hay tỉ lệ thành công đã đo bằng GPT-4.1 mini.

## 2. Kết quả mô phỏng

Lượt chạy thật: [simulate-1.csv](simulate-1.csv) · [bảng gốc](simulate-1-summary.md) · [trace](../traces/simulate-1.jsonl) · run ID `simulate-1@20261128-103318` · **50 phiên** · seed 42 · 0 phiên lỗi. Trước đó đã chạy `--try` 10 phiên; lượt thử không tính vào kết quả nộp.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dat_2_3_lan | 21 | 1 | 2028 | 1148 | 1.6 | 20.1 |
| dat_4_5_lan | 19 | 1 | 1862 | 1249 | 1.4 | 17.8 |
| dat_6_8_lan | 10 | 1 | 2859 | 1570 | 2.0 | 31.8 |

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | / tháng — thấp (50 người) | / tháng — cơ sở (200 người) | / tháng — cao (500 người) | / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek/deepseek-v4.1-flash (vào 0.3 · ra 1.2 $/1M) | $0.0022 | $0.0029 | $0.0029 | $0.5076 | $2.03 | $5.08 | $0.0102 |
| openai/gpt-4.1-mini (vào 0.4 · ra 1.6 $/1M) | $0.0029 | $0.0038 | $0.0038 | $0.6768 | $2.71 | $6.77 | $0.0135 |

Chi phí/task thành công = chi phí trung bình/phiên ÷ **0,75**; đây là tỷ lệ của lượt đánh giá 2, không phải tỷ lệ thành công được đo lại trong 50 phiên chi phí. Lượt 2 và code mô phỏng cùng model nhưng khác phiên bản code (xem [eval/README.md](../eval/README.md)), nên tỷ lệ này là giả định theo rubric, không phải chất lượng được chứng minh của phiên bản hiện tại. Bảng tính chi phí API, chưa gồm hosting, nhân công và chi phí thực tế do routing/cache.

## 3. So với impact

Theo [spec.md §2](../spec.md#2-impact--quyết-định-chọn-guide-13), phân nhóm D2 có khoảng 680 phút/30 ngày cho 9 người, tương đương khoảng **75,6 phút/người/30 ngày** *(tự ước tính từ dữ liệu mẫu)*. Đây là thời gian toàn quy trình, **không phải** thời gian tiết kiệm đã đo; cũng chưa có giá trị tiền quy đổi.

**Kết luận một dòng — đáng làm không: có, xét riêng chi phí model.** Kịch bản cơ sở tốn **$0,0102/người/tháng** (DeepSeek; $0,0135 nếu dùng GPT-4.1 mini), rất nhỏ so với **75,6 phút/người/30 ngày** người đặt hộ đang bỏ ra cho toàn quy trình. Chỉ cần công cụ bớt được vài phút mỗi tháng là đã hơn chi phí model. Điều chưa biết: chưa đo số phút tiết kiệm được thật, và bảng chưa gồm hosting, nhân công.
