# Lion — Từ chat nhóm đến giỏ đồ ăn an toàn

**Thành viên, lớp, track:** xem [TEAMS.md](TEAMS.md) · **Canvas:** [canvas.md](canvas.md)

**Track D (Thương mại điện tử), hướng D2.**

**Bài toán:** Một người cầm quỹ chung 250k–300k đặt đồ ăn hộ cả nhóm 5 người, trong khi mọi người chỉ nhắn rải rác vào nhóm chat (có người ăn chay, có người dị ứng đậu phộng, có người giục đặt nhanh). Người đặt phải tự đọc hết tin nhắn, dò từng món trong menu rồi cộng cả phí ship, nên dễ sót dặn dò, vượt quỹ và phải làm lại.

**Lát cắt:** Một người đặt hộ cho nhóm 5 người dán đoạn chat và quỹ chung. Sau khi họ xác nhận hồ sơ, hệ thống tự chọn quán và trả giỏ đã kiểm theo menu hoặc giải thích vì sao chưa thể lập giỏ.

## Chạy khung CP2

Chạy `python run.py` và dán dòng sau:

```text
Quỹ 300.000đ. Chat: An: phở gà ức | Bình: phở gà ức | Chi: phở gà ức | Dũng: phở gà ức | Hà: phở gà ức
```

Đọc hồ sơ nháp. Để mô phỏng xác nhận, nhập lại dòng đó với tiền tố `Hồ sơ đã xác nhận. `. Hệ thống tự tìm quán từ menu mẫu, kiểm giỏ và trả giỏ đề xuất để duyệt. CLI xử lý từng dòng như một phiên độc lập. Bản CP2 dùng luật mô phỏng thay cho model và phí ship mặc định 15.000đ nếu ca không quy định.

Chạy `python run.py check` để kiểm cấu trúc bộ đánh giá. `python run.py eval --wait 0` chạy qua benchmark và ghi `eval/run-mock.csv` cho bản CP2, có thông báo lượt mô phỏng không được tính là lượt đánh giá model.
