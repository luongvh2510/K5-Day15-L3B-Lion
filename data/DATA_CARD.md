# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (bài mẫu, thông báo mẫu, đoạn transcript…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

## Dataset 1 · Menu món Việt mô phỏng

| | |
|---|---|
| Dùng để làm gì | Làm menu tham chiếu để lập và kiểm giỏ D2, đối chiếu giá và thành phần khi chấm 10 ca CP2. |
| Từ đâu | [`dataset_mon_an_viet.json`](dataset_mon_an_viet.json) do người dùng cung cấp cho dự án. Mỗi món là một công thức demo cố định. `source_ids` dẫn tới danh mục tham khảo trong JSON, có thể là công thức tương tự hoặc nguồn cho một thành phần. |
| Xử lý khi dựng benchmark | Hệ thống chọn quán từ menu mô phỏng, lấy đơn giá từ `price_vnd` và hợp các nhãn `allergens` qua mọi `ingredient_ids` trong suất, gồm cả nước dùng và nước chấm. Mỗi bản ghi món được dùng như một suất chính trong ca CP2. Chat, trạng thái hồ sơ, ngân sách và phí ship được ghi trong từng ca. |
| Số bản ghi | 100 món (mỗi món một suất), 10 quán, 174 nguyên liệu, 13 nhóm nguyên liệu, 10 loại nhãn dị ứng và 97 mục tham khảo. Đã kiểm ID không trùng trong từng danh mục và các tham chiếu món → quán, nguyên liệu, nguồn đều tồn tại. |
| Phiên bản | Snapshot CP2. SHA-256: `3d63e16b7145051bd01988914802c7c664c20cfebd0e94b8dd45b64c75685d2d`. |
| Nhãn | `synthetic`. Tên quán, giá, khoảng cách và URL ảnh là mô phỏng. Chat và phí ship trong benchmark do nhóm tự viết. |
| Giới hạn | File không có trường nhãn chay, tồn món, phí ship hay xác minh đầy đủ thành phần. Không có dữ liệu nhiễm chéo trong bếp. Mảng nhãn rỗng chỉ có nghĩa là chưa ghi nhận nhãn trong bộ dữ liệu. |

**Cách tạo và phạm vi kiểm:** Metadata mô tả cách mô hình hóa món theo công thức demo; file chưa ghi prompt/script, seed, người kiểm hoặc số món đã kiểm tay khi tạo. Các ca CP2 được soạn theo quy tắc nghiệp vụ và tra giá, thành phần trong snapshot. Nhãn nguồn của các ca này là `tu_viet`.

## Nguồn dựng các tình huống mô phỏng

Bốn tình huống dưới đây được soạn từ quy tắc nghiệp vụ và snapshot menu. Việc dựng ca là thủ công, không dùng seed. Tình huống phỏng vấn được thống kê riêng trong [hồ sơ bằng chứng](../evidence/summary.md).

| Mã nguồn | Ca | Dữ liệu dùng để dựng ca |
|---|---|---|
| SIM-01 | B02 | BR-05–07. Chọn ngưỡng vừa đủ: 5 suất `dish_021` × 48.000đ + 10.000đ phí ship mô phỏng = 250.000đ. |
| SIM-02 | B04 | BR-03 và BR-08. Dùng `dish_016` có `roasted_peanut`, tạo tình huống một người cần đổi món còn bốn người giữ món ban đầu. |
| SIM-03 | B05 | BR-06 và BR-14. Dùng giá thấp nhất ở `store_01` là 54.000đ/suất, cộng 15.000đ phí ship mô phỏng. Đặt quỹ thấp hơn tổng tối thiểu 5.000đ để kiểm phần báo thiếu. |
| SIM-04 | B07 | BR-10. Tạo lời nhắn “mình dị ứng hải sản” để kiểm câu hỏi làm rõ, đối chiếu ba nhãn `fish`, `crustacean` và `mollusc` trong JSON. |
