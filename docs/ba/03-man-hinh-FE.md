# 03 · Màn hình và luồng FE

> Cho người làm FE (kiêm BE). Làm **trước bằng mock**, dữ liệu theo đúng [04](04-hop-dong-du-lieu-API.md).
> Stack do bạn chọn. Tài liệu không phụ thuộc framework.
>
> **Cập nhật 28/11:** người đặt **chỉ dán chat** — không có ô quỹ, không có dropdown quán. Quỹ đọc từ chat; quán do
> agent chọn sau khi xác nhận và hiện ở Phase 2 kèm nút "Đổi quán". Mock thật nằm ở [`mocks/`](mocks/).
> Một số phần tử chưa có dữ liệu từ API (nguồn theo dòng, cờ, nút trả lời nhanh) được ghi rõ bên dưới.

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
│  🍱 Đặt đơn nhóm   ·  Quỹ: 300.000đ (từ chat)  ·  Quán: Xôi Nếp Ban Mai (agent chọn) │
│  Bước: ① Nhập chat ── ② Xác nhận hồ sơ ── ③ Giỏ hàng ── ④ Chốt                 │
├────────────────────────────────┬─────────────────────────────────────────────┤
│ CỘT TRÁI: HỘI THOẠI            │ CỘT PHẢI: THAY ĐỔI THEO TRẠNG THÁI           │
│                                │                                             │
│ [Ô dán chat nhóm …………………… ]   │  (A) Nhập: hướng dẫn + nút "Nạp chat mẫu"    │
│ [Nạp chat mẫu] [Phân tích ▶]   │  (B) PROFILE_DRAFT: thẻ hồ sơ từng người     │
│                                │  (C) CART_VALID: giỏ hàng + món bị loại      │
│ 🤖 ❓ An ơi, bạn nói ăn chay…   │  (D) CART_INFEASIBLE: báo thiếu + đề xuất    │
│    nhưng xin thêm cơm gà…     │  (E) FINALIZED: tin nhắn chốt + nút Copy     │
│ 👤 Cơm gà cho Dũng, An vẫn chay│                                             │
│ 🤖 Đã ghi nhận…                 │                                             │
│                                │                                             │
│ [Nhập tin nhắn……………] [Gửi]     │                                             │
└────────────────────────────────┴─────────────────────────────────────────────┘
```

Mobile: 2 cột xếp chồng, cột phải lên trên, hội thoại thu gọn ở dưới.

## 3. Các trạng thái cột phải

### (A) Chưa có phiên
- Ô dán chat (textarea, giới hạn 4.000 ký tự, có bộ đếm). **Không có ô quỹ, không có dropdown quán** *(cập nhật 28/11)*.
  Gợi ý định dạng dưới ô: "Tên một dòng, tin nhắn dòng sau. Nhớ ghi quỹ chung trong chat."
- Nút **"Nạp chat mẫu"** đổ `CHAT-01` (file 06, định dạng mới) vào ô. **Bắt buộc có**, vì demo dùng nút này.
- Nút **"Phân tích"** gọi `POST /sessions {chat_text}`. Trong lúc chờ (5–20 giây): spinner "Đang đọc đoạn chat…", khoá nút.
- Lỗi phía client: chat rỗng hoặc > 4.000 ký tự → hiện dưới ô, không gọi API (US-01).
- Chat không nêu quỹ → API trả câu hỏi "Quỹ chung của nhóm là bao nhiêu?"; người đặt trả lời ở ô nhập tin.

### (B) `PROFILE_DRAFT` — Hồ sơ nhóm
Mỗi thành viên một thẻ:

```
┌ An ─────────────────────────────── ⚠ Mâu thuẫn ┐
│ 🌱 Ăn chay                              [×]     │
│ Câu gốc: "An: t ăn chay nha, nhớ đó"            │
│ Sở thích: —                                     │
│ [+ Thêm ràng buộc] [+ Thêm sở thích]            │
└─────────────────────────────────────────────────┘
```

- **Ràng buộc cứng** (chip đậm, màu cam hoặc đỏ) khác **sở thích** (chip nhạt) (US-02 AC2).
- **Câu gốc:** hiện danh sách `member.quotes` dưới thẻ (US-02 AC1). API **chưa** gắn câu gốc vào từng ràng buộc
  (`source.line`, `source.quote` = `null`) nên chưa làm được "bấm nguồn → bôi vàng dòng N" *(cập nhật 28/11)*.
  Nguồn `HOST` thì hiện "Người đặt thêm".
- Cờ ⚠/❓: API chưa trả `flags` *(cập nhật 28/11)*. Thay bằng: thẻ có câu hỏi `OPEN` với `member_id` của người đó thì hiện ❓.
- Sửa hồ sơ: thêm hoặc xoá người, thêm hoặc xoá chip. Mỗi lần sửa gọi `PATCH /members` với toàn bộ danh sách.
  - Thêm ràng buộc cứng: chọn "Ăn chay" hoặc "Dị ứng" + dropdown **10 chất** (mục 5 của file 04). *(cập nhật 28/11)*
- Thêm người (kể cả người đặt) bằng nút **"+ Thêm người"** → `PATCH /members`, người mới có `origin: HOST_ADDED`. *(cập nhật 28/11)*
- Nút **"Xác nhận hồ sơ"**: `disabled` khi `can_confirm == false`. Tooltip lúc khoá: "Còn N câu hỏi cần trả lời".
  Bấm thì gọi `POST /confirm` (spinner "Đang lập giỏ…").

### (C) `CART_VALID` — Giỏ hàng
```
🏪 Xôi Nếp Ban Mai · 0,9 km · "Xôi nếp ăn sáng…"            [Đổi quán]
✓ Giỏ hợp lệ — Đã kiểm theo yêu cầu đã xác nhận và menu quán
┌─────────────────────────────────────────────────────┐
│ Chi   Xôi đậu xanh                         21.000đ   │
│       (reason của AI)                                │
│ An 🌱 Xôi đậu xanh                         21.000đ   │
│ Bình⚠ Xôi đậu xanh                         21.000đ   │
│ …                                                    │
├─────────────────────────────────────────────────────┤
│ Tạm tính 119.000đ · Ship 15.000đ · Tổng 134.000đ     │
│ [██████████░░░░░░░░░░░░░░] 134.000 / 300.000đ        │
│ Còn lại 166.000đ                                     │
└─────────────────────────────────────────────────────┘
▸ Món bị loại (8) — mở ra: "An: Xôi gà xé — không chay: có Ức gà, Nước mắm cá cơm và muối (BR-02)"
🔒 Hồ sơ đã khoá  [Sửa hồ sơ]   [Chốt giỏ ▶]
```
- Nhãn "✓ Giỏ hợp lệ" **chỉ hiện khi** `validation.ok == true` (BR-17). Trường hợp `ok == false` không nên
  xảy ra. Nếu xảy ra thì hiện "Giỏ chưa hợp lệ" kèm danh sách `violations`, ẩn nút Chốt.
- Thẻ quán lấy từ `restaurant` (tên, `distance_km`, `summary`). Nút **"Đổi quán"** → `POST /actions {action:{type:"CHANGE_RESTAURANT"}}` *(cập nhật 28/11)*.
- `note` của dòng hiện luôn `null` (dữ liệu không có món thiếu thành phần); vẫn nên hiển thị nếu có.
- `built_by == "FALLBACK"` thì hiện ghi chú nhỏ (mục 5 của file 04).
- **"Sửa hồ sơ"** mở hộp xác nhận: "Giỏ hiện tại sẽ bị huỷ và bạn phải xác nhận lại hồ sơ. Tiếp tục?" → `POST /reopen`.
- **Thanh ngân sách:** xanh khi ≤ 90% quỹ, vàng khi > 90%.

### (D) `CART_INFEASIBLE` — Chưa khả thi
```
⛔ Chưa khả thi
Chưa lập được giỏ ở Xôi Nếp Ban Mai: tối thiểu 120.000đ gồm phí ship, quỹ 100.000đ, thiếu 20.000đ.
[Tăng quỹ lên 120.000đ]  [Đổi quán]     ← mỗi option là 1 nút → POST /actions
```
- `kind == NO_SAFE_ITEM`: hiện tên người trong `members_without_option`, ví dụ "Quán không có món chính nào phù hợp với Bình".
- **Không hiện giỏ, không hiện nhãn hợp lệ** (BR-16).
- Không có ô quỹ ở header *(cập nhật 28/11)*. Muốn đổi quỹ khác số đề xuất: gõ vào ô chat ("quỹ 150k") hoặc FE làm
  ô nhập nhỏ cạnh nút rồi gọi `POST /actions` với `SET_BUDGET`.

### (E) `FINALIZED`
- Khung chữ hiện `final_message` (giữ xuống dòng) và nút **"Copy"** → toast "Đã copy" (US-09).
- Nút "Làm đơn mới" xoá phiên, về (A).

## 4. Cột trái: hội thoại

| `message.kind` | Hiển thị |
|---|---|
| `INFO`, `TEXT` | Bong bóng bình thường |
| `QUESTION` | Bong bóng có viền. API chưa trả `options` và `question_id` (luôn rỗng/`null`) *(cập nhật 28/11)* → không có nút trả lời nhanh, người đặt gõ câu trả lời |
| `REFUSAL` | Bong bóng nền đỏ nhạt, icon 🛡️ |

- Gửi tin: `POST /messages { text }` (chỉ có `text`). *(cập nhật 28/11)*
- Tin đầu tiên của phiên là đoạn chat đã dán (`role:"user"`): nên thu gọn thành "Đoạn chat đã dán (N dòng)".
- Trong lúc chờ AI (5–20 giây mỗi lượt): bong bóng "…" và khoá ô nhập.
- Ô nhập khoá ở trạng thái (A) và `FINALIZED`.

## 5. Câu chữ (microcopy) đã chốt

| Chỗ | Câu |
|---|---|
| Nhãn giỏ | ✓ Giỏ hợp lệ — Đã kiểm theo yêu cầu đã xác nhận và menu quán |
| Nút xác nhận bị khoá | Còn {N} câu hỏi cần trả lời |
| Hộp sửa hồ sơ | Giỏ hiện tại sẽ bị huỷ và bạn phải xác nhận lại hồ sơ. Tiếp tục? |
| Lỗi AI (502) / lỗi hệ thống (500) | Hệ thống AI tạm thời không phản hồi, vui lòng thử lại. [Thử lại] |
| Ô chat trống | Dán đoạn chat nhóm vào đây (Zalo, Messenger…). Tên một dòng, tin nhắn dòng sau; nhớ có quỹ chung |

**Không dùng:** "an toàn 100%", "đảm bảo tuyệt đối", "AI đã kiểm".

## 6. Danh sách mock (theo mục 6 của file 04) *(cập nhật 28/11)*

Đã có sẵn trong [`docs/ba/mocks/`](mocks/), sinh từ API thật; chép sang `frontend/mocks/` là dùng được.


| File | Dùng để dựng |
|---|---|
| `mocks/restaurants.json`, `mocks/menu_store_08.json` | Thẻ quán, xem menu (không còn dropdown quán) |
| `mocks/session_draft.json` | (B) có câu hỏi, nút xác nhận khoá |
| `mocks/session_draft_answered.json` | (B) đã trả lời, nút xác nhận mở |
| `mocks/session_cart_valid.json` | (C) |
| `mocks/session_infeasible.json` | (D) |
| `mocks/session_refusal.json` | (C) + bong bóng REFUSAL |
| `mocks/session_finalized.json` | (E) |
| `mocks/error_ai.json` | Lỗi 502 (FE tự tạo theo mẫu ở file 04 mục 6) |

Mẹo khi dùng mock: mỗi nút bấm chuyển sang file mock kế tiếp theo kịch bản demo ở mục 7 của file 00. Nhờ vậy FE
demo được toàn bộ luồng trước khi có BE.

## 7. Checklist FE xong

- [ ] Đủ 5 trạng thái (A)–(E) + trạng thái lỗi, chạy được bằng mock.
- [ ] Nút xác nhận khoá đúng theo `can_confirm`.
- [ ] Thấy câu chat gốc của từng người (`member.quotes`).
- [ ] Không tự tính tiền, không tự quyết định hợp lệ.
- [ ] Đổi `USE_MOCK=false` gọi được API thật mà không sửa component.
