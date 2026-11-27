# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (bài mẫu, thông báo mẫu, đoạn transcript…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

## Dataset 1 · Menu món Việt mô phỏng

| | |
|---|---|
| Dùng để làm gì | Làm menu tham chiếu để lập và kiểm giỏ D2, đối chiếu giá và thành phần khi chấm 10 ca CP2. |
| Từ đâu | [`dataset_mon_an_viet.json`](dataset_mon_an_viet.json) do người dùng cung cấp cho dự án. Mỗi món là một công thức demo cố định. `source_ids` dẫn tới danh mục tham khảo trong JSON, có thể là công thức tương tự hoặc nguồn cho một thành phần. |
| Xử lý khi dựng benchmark | Lọc món theo `store_id`, lấy đơn giá từ `price_vnd`, hợp các nhãn `allergens` qua mọi `ingredient_ids` trong suất, gồm cả nước dùng và nước chấm. Mỗi bản ghi món được dùng như một suất chính trong ca CP2. Chat, trạng thái hồ sơ, ngân sách và phí ship được ghi trong từng ca. |
| Số bản ghi | 100 món (mỗi món một suất), 10 quán, 174 nguyên liệu, 13 nhóm nguyên liệu, 10 loại nhãn dị ứng và 97 mục tham khảo. Đã kiểm ID không trùng trong từng danh mục và các tham chiếu món → quán, nguyên liệu, nguồn đều tồn tại. |
| Phiên bản | Snapshot CP2. SHA-256: `3d63e16b7145051bd01988914802c7c664c20cfebd0e94b8dd45b64c75685d2d`. |
| Nhãn | `synthetic`. Tên quán, giá, khoảng cách và URL ảnh là mô phỏng. Chat và phí ship trong benchmark do nhóm tự viết. |
| Giới hạn | File không có trường nhãn chay, tồn món, phí ship hay xác minh đầy đủ thành phần. Không có dữ liệu nhiễm chéo trong bếp. Mảng nhãn rỗng chỉ có nghĩa là chưa ghi nhận nhãn trong bộ dữ liệu. |

**Cách tạo và phạm vi kiểm:** Metadata mô tả cách mô hình hóa món theo công thức demo; file chưa ghi prompt/script, seed, người kiểm hoặc số món đã kiểm tay khi tạo. Các ca CP2 được soạn theo quy tắc nghiệp vụ và tra giá, thành phần trong snapshot. Nhãn nguồn của các ca này là `tu_viet`.
