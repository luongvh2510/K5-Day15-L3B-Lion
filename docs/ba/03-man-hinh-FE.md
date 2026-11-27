# 03 · Màn hình và luồng FE

> Cho người làm FE (kiêm BE). Làm **trước bằng mock**, dữ liệu theo đúng [04](04-hop-dong-du-lieu-API.md).
> Stack do bạn chọn. Tài liệu không phụ thuộc framework.

## 1. Nguyên tắc

1. **Một trang, render theo `SessionState.status`.** Không tự giữ logic nghiệp vụ trên FE. Mọi quyết định
   (hợp lệ, khả thi, khoá) đều lấy từ API.
2. **Lớp gọi API có công tắc mock.** Ví dụ `USE_MOCK=true` thì đọc file JSON trong `mocks/`, `false` thì gọi `/api`.
   Đổi công tắc là xong việc tích hợp.
3. **Không tự tính tiền trên FE.** Hiện đúng `subtotal`, `shipping_fee`, `total`, `remaining` từ API.
4. Giao diện tiếng Việt, định dạng tiền `280.000đ`.

## 2. Bố cục (desktop, 2 cột)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  🍱 Đặt đơn nhóm   ·  Quán: [Quán Cơm Nhà Mẫu ▾]  ·  Quỹ: [300.000]đ           │
│  Bước: ① Nhập chat ── ② Xác nhận hồ sơ ── ③ Giỏ hàng ── ④ Chốt                 │
├────────────────────────────────┬─────────────────────────────────────────────┤
│ CỘT TRÁI: HỘI THOẠI            │ CỘT PHẢI: THAY ĐỔI THEO TRẠNG THÁI           │
│                                │                                             │
│ [Ô dán chat nhóm …………………… ]   │  (A) Nhập: hướng dẫn + nút "Nạp chat mẫu"    │
│ [Nạp chat mẫu] [Phân tích ▶]   │  (B) PROFILE_DRAFT: thẻ hồ sơ từng người     │
│                                │  (C) CART_VALID: giỏ hàng + món bị loại      │
│ 🤖 Mình đọc được 5 người…      │  (D) CART_INFEASIBLE: báo thiếu + đề xuất    │
│ 🤖 ❓ Suất cơm gà này cho ai?  │  (E) FINALIZED: tin nhắn chốt + nút Copy     │
│    [Cho người khác] [An nhầm]  │                                             │
│ 👤 Cho Dũng, An vẫn ăn chay    │                                             │
│                                │                                             │
│ [Nhập tin nhắn……………] [Gửi]     │                                             │
└────────────────────────────────┴─────────────────────────────────────────────┘
```

Mobile: 2 cột xếp chồng, cột phải lên trên, hội thoại thu gọn ở dưới.

## 3. Các trạng thái cột phải

### (A) Chưa có phiên
- Ô dán chat (textarea, giới hạn 4.000 ký tự, có bộ đếm), ô quỹ, dropdown quán.
- Nút **"Nạp chat mẫu"** đổ `CHAT-01` (file 06) vào ô và đặt quỹ 300.000. **Bắt buộc có**, vì demo dùng nút này.
- Nút **"Phân tích"** gọi `POST /sessions`. Trong lúc chờ (5–15 giây): spinner kèm câu "Đang đọc đoạn chat…", khoá nút.
- Lỗi phía client: chat rỗng, quỹ không hợp lệ → hiện dưới ô, không gọi API (US-01).

### (B) `PROFILE_DRAFT` — Hồ sơ nhóm
Mỗi thành viên một thẻ:

```
┌ An ─────────────────────────────── ⚠ Mâu thuẫn ┐
│ 🌱 Ăn chay              [nguồn: dòng 2] [×]     │
│ Sở thích: —                                     │
│ [+ Thêm ràng buộc] [+ Thêm sở thích]            │
└─────────────────────────────────────────────────┘
```

- **Ràng buộc cứng** (chip đậm, màu cam hoặc đỏ) khác **sở thích** (chip nhạt) (US-02 AC2).
- Bấm **[nguồn: dòng N]** thì bôi vàng dòng N trong đoạn chat gốc. Đoạn chat gốc hiện ở panel thu gọn hoặc
  tooltip hiện `quote` (US-02 AC1). Nguồn `HOST` thì hiện "Người đặt thêm".
- Cờ ⚠/❓ trên thẻ. Bấm vào cờ thì cuộn tới câu hỏi tương ứng ở cột trái.
- Sửa hồ sơ: thêm hoặc xoá người, thêm hoặc xoá chip. Mỗi lần sửa gọi `PATCH /members` với toàn bộ danh sách.
  - Thêm ràng buộc cứng: chọn "Ăn chay" hoặc "Dị ứng" + dropdown chất (mục 5 của file 04).
- Checkbox **"Tính cả tôi"** + ô tên → thêm thành viên `origin: HOST_ADDED`.
- Nút **"Xác nhận hồ sơ"**: `disabled` khi `can_confirm == false`. Tooltip lúc khoá: "Còn N câu hỏi cần trả lời".
  Bấm thì gọi `POST /confirm` (spinner "Đang lập giỏ…").

### (C) `CART_VALID` — Giỏ hàng
```
✓ Giỏ hợp lệ — Đã kiểm theo yêu cầu đã xác nhận và menu quán
┌─────────────────────────────────────────────────────┐
│ Chi   Cơm sườn nướng                       50.000đ   │
│       Chi ăn gì cũng được                            │
│ An 🌱 Cơm đậu hũ sốt nấm                   45.000đ   │
│ Bình⚠ Phở bò                               60.000đ   │
│ …                                                    │
├─────────────────────────────────────────────────────┤
│ Tạm tính 260.000đ · Ship 20.000đ · Tổng 280.000đ     │
│ [██████████████████████░░] 280.000 / 300.000đ        │
│ Còn lại 20.000đ                                      │
└─────────────────────────────────────────────────────┘
▸ Món bị loại (3)   — mở ra: "Bình: Bún thịt nướng — Có đậu phộng (BR-03)"
🔒 Hồ sơ đã khoá  [Sửa hồ sơ]   [Chốt giỏ ▶]
```
- Nhãn "✓ Giỏ hợp lệ" **chỉ hiện khi** `validation.ok == true` (BR-17). Trường hợp `ok == false` không nên
  xảy ra. Nếu xảy ra thì hiện "Giỏ chưa hợp lệ" kèm danh sách `violations`, ẩn nút Chốt.
- `note` của dòng (ví dụ "Quán không ghi thành phần") hiện bằng chữ nhỏ màu xám.
- `built_by == "FALLBACK"` thì hiện ghi chú nhỏ (mục 5 của file 04).
- **"Sửa hồ sơ"** mở hộp xác nhận: "Giỏ hiện tại sẽ bị huỷ và bạn phải xác nhận lại hồ sơ. Tiếp tục?" → `POST /reopen`.
- **Thanh ngân sách:** xanh khi ≤ 90% quỹ, vàng khi > 90%.

### (D) `CART_INFEASIBLE` — Chưa khả thi
```
⛔ Chưa khả thi
Với quán này, 5 suất an toàn rẻ nhất + ship 20.000đ = 225.000đ.
Quỹ 200.000đ → thiếu 25.000đ.
[Tăng quỹ lên 225.000đ]     ← mỗi option là 1 nút → POST /actions
```
- `kind == NO_SAFE_ITEM`: hiện tên người trong `members_without_option`, ví dụ "Quán không có món chính nào phù hợp với Bình".
- **Không hiện giỏ, không hiện nhãn hợp lệ** (BR-16).
- Ô quỹ ở header vẫn sửa được. Đổi quỹ ở trạng thái này cũng gọi `POST /actions` với `SET_BUDGET`.

### (E) `FINALIZED`
- Khung chữ hiện `final_message` (giữ xuống dòng) và nút **"Copy"** → toast "Đã copy" (US-09).
- Nút "Làm đơn mới" xoá phiên, về (A).

## 4. Cột trái: hội thoại

| `message.kind` | Hiển thị |
|---|---|
| `INFO`, `TEXT` | Bong bóng bình thường |
| `QUESTION` | Bong bóng có viền, kèm nút cho từng `options` của câu hỏi (`question_id`). Câu đã `ANSWERED` thì ẩn nút |
| `REFUSAL` | Bong bóng nền đỏ nhạt, icon 🛡️ |

- Gửi tin: `POST /messages { text }`. Bấm nút trả lời: `{ text: label, question_id, option_id }`.
- Trong lúc chờ AI: bong bóng "…" và khoá ô nhập.
- Ô nhập khoá ở trạng thái (A) và `FINALIZED`.

## 5. Câu chữ (microcopy) đã chốt

| Chỗ | Câu |
|---|---|
| Nhãn giỏ | ✓ Giỏ hợp lệ — Đã kiểm theo yêu cầu đã xác nhận và menu quán |
| Nút xác nhận bị khoá | Còn {N} câu hỏi cần trả lời |
| Hộp sửa hồ sơ | Giỏ hiện tại sẽ bị huỷ và bạn phải xác nhận lại hồ sơ. Tiếp tục? |
| Lỗi AI | Chưa đọc được đoạn chat. [Thử lại] |
| Ô chat trống | Dán đoạn chat nhóm vào đây (Zalo, Messenger…) |

**Không dùng:** "an toàn 100%", "đảm bảo tuyệt đối", "AI đã kiểm".

## 6. Danh sách mock cần có (theo mục 6 của file 04)

| File | Dùng để dựng |
|---|---|
| `mocks/menu_r1.json` | Dropdown quán, có thể hiện menu |
| `mocks/session_draft.json` | (B) có câu hỏi, nút xác nhận khoá |
| `mocks/session_draft_answered.json` | (B) đã trả lời, nút xác nhận mở |
| `mocks/session_cart_valid.json` | (C) |
| `mocks/session_infeasible.json` | (D) |
| `mocks/session_refusal.json` | (C) + bong bóng REFUSAL |
| `mocks/session_finalized.json` | (E) |
| `mocks/error_ai.json` | Lỗi 502 |

Mẹo khi dùng mock: mỗi nút bấm chuyển sang file mock kế tiếp theo kịch bản demo ở mục 7 của file 00. Nhờ vậy FE
demo được toàn bộ luồng trước khi có BE.

## 7. Checklist FE xong

- [ ] Đủ 5 trạng thái (A)–(E) + trạng thái lỗi, chạy được bằng mock.
- [ ] Nút xác nhận khoá đúng theo `can_confirm`.
- [ ] Bấm nguồn thì thấy câu chat gốc.
- [ ] Không tự tính tiền, không tự quyết định hợp lệ.
- [ ] Đổi `USE_MOCK=false` gọi được API thật mà không sửa component.
