# D2 · Đặt đơn nhóm có ràng buộc ăn uống — Bộ tài liệu nghiệp vụ

> POC 1 ngày. Tài liệu viết theo kiểu **PRD gọn chia nhiều file**, không phải SRS đầy đủ.
> Mục tiêu: mỗi người đọc 5–10 phút là bắt tay làm được phần của mình.

## Vì sao PRD chia file mà không viết SRS?

| | PRD chia file (chọn) | SRS đầy đủ |
|---|---|---|
| Độ dài | Mỗi file 1–3 trang | 30–100 trang |
| Hợp với | POC, hackathon, nhóm nhỏ | Dự án nhiều tháng, có hợp đồng |
| Cách đọc | Mỗi vai đọc đúng file của mình | Đọc tuần tự từ đầu |
| Cập nhật | Sửa 1 file, các file khác dẫn chiếu theo mã | Phải rà cả tài liệu |

Phần "kỹ thuật" của SRS (schema, API, trạng thái) nhóm vẫn cần — gom vào file `04` (hợp đồng dữ liệu).
Đó là phần duy nhất cần **chính xác tuyệt đối**, vì FE làm trước bằng mock rồi mới nối BE/AI.

## Đọc file nào?

| File | Nội dung | Cả nhóm | AI (2 người) | BE + FE |
|---|---|:---:|:---:|:---:|
| [00-tong-quan-PRD.md](00-tong-quan-PRD.md) | Bài toán, phạm vi, chỉ số, demo, kế hoạch | ✅ đọc đầu tiên | | |
| [01-nghiep-vu-va-quy-tac.md](01-nghiep-vu-va-quy-tac.md) | Thuật ngữ, quy tắc nghiệp vụ `BR-xx` | ✅ | ✅✅ | ✅ |
| [02-use-case-user-story.md](02-use-case-user-story.md) | Use case `UC-xx`, user story `US-xx`, tiêu chí chấp nhận | ✅ | ✅ | ✅ |
| [03-man-hinh-FE.md](03-man-hinh-FE.md) | Bố cục, trạng thái màn hình, câu chữ, mock | | | ✅✅ |
| [04-hop-dong-du-lieu-API.md](04-hop-dong-du-lieu-API.md) | Schema, endpoint, mã lỗi, JSON mẫu | | ✅✅ | ✅✅ |
| [05-AI-agent.md](05-AI-agent.md) | AI quyết định gì / code quyết định gì, tool, prompt, chia việc 2 người AI | | ✅✅ | |
| [06-du-lieu-mau-va-test.md](06-du-lieu-mau-va-test.md) | Menu mẫu, đoạn chat mẫu, bộ ca thử có đáp án, cách chấm | | ✅✅ | ✅ (menu) |

## Quy ước mã (để dẫn chiếu chéo)

- `BR-xx` — quy tắc nghiệp vụ (file 01). **Code phải tuân theo, không ai tự đổi.**
- `UC-xx` — use case (file 02).
- `US-xx` — user story kèm tiêu chí chấp nhận `AC` (file 02).
- `TC-xx` — ca kiểm thử (file 06).
- `[MUST]` / `[SHOULD]` / `[COULD]` — mức ưu tiên. Hết giờ thì bỏ từ dưới lên.

## Quy tắc sửa tài liệu

1. BA (người giữ bộ tài liệu) là người duy nhất sửa `01` và `04`. Ai cần đổi thì nhắn BA.
2. Khi code và tài liệu lệch nhau trong lúc build: **báo BA ngay**, quyết định 1 bên rồi sửa bên còn lại.
3. Đổi schema ở `04` → ghi vào mục "Nhật ký thay đổi" cuối file `04`, báo cả nhóm.
