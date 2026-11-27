# Hướng dẫn nối Frontend với Backend (cho Tú)

> Đọc kèm: [docs/ba/04-hop-dong-du-lieu-API.md](ba/04-hop-dong-du-lieu-API.md) (schema đầy đủ, bảng lỗi) và
> [docs/ba/03-man-hinh-FE.md](ba/03-man-hinh-FE.md) (bố cục, câu chữ). File này là **cách làm thực tế** để FE chạy
> được với API thật; chỗ nào khác hai file kia thì theo file 04 (đã cập nhật theo code ngày 28/11).
>
> Trạng thái backend: API thật chạy được, đã test qua HTTP với model thật (33/33 bước, 28/11). FE chưa có trong repo.

## 1. Bức tranh chung

```
Trình duyệt (FE của Tú)  ──HTTP/JSON──►  server/api.py  ──►  codebase/core.py (agent)  ──►  OpenRouter (LLM)
                                              │
                                              └──► sessions.sqlite3 (lưu phiên)
```

- **Agent nằm ở backend.** FE không gọi model, không giữ API key, không tự lọc món hay tính tiền.
- Mọi API thay đổi phiên đều trả về **toàn bộ `SessionState`** → FE chỉ cần `setState(response)` rồi render lại.
- FE render theo `state.status`: `PROFILE_DRAFT` → `CART_VALID` / `CART_INFEASIBLE` → `FINALIZED`.

## 2. Chạy backend trên máy

Cần Python 3.10+, không cần cài thư viện. Trong thư mục repo:

```powershell
python run.py
```

Chọn `2` (API web). Hoặc mở thẳng chế độ API:

```powershell
$env:LION_MODE = "web"; python run.py
```

- API ở **`http://127.0.0.1:8000/api`**. Dừng bằng Ctrl+C.
- Cần file `.env` có key OpenRouter (xin Lương; **không commit, không gửi lên nhóm chat công khai**).
  Chưa có key thì mọi API cần AI trả `502 AI_UNAVAILABLE` — vẫn dùng mock để làm giao diện được (mục 4).
- Server bật **CORS `*`**, FE chạy ở cổng nào (Vite 5173, CRA 3000…) cũng gọi được.
- Kiểm nhanh: mở `http://127.0.0.1:8000/api/restaurants` trên trình duyệt, thấy JSON 10 quán là được.

## 3. Lớp gọi API (một file, có công tắc mock)

Ví dụ JavaScript thuần (React/Vue/Svelte đều dùng được):

```js
// src/api.js
const BASE = import.meta.env?.VITE_API_BASE ?? "http://127.0.0.1:8000/api";
const USE_MOCK = (import.meta.env?.VITE_USE_MOCK ?? "false") === "true";

export class ApiError extends Error {
  constructor(status, code, message) { super(message); this.status = status; this.code = code; }
}

async function call(method, path, body) {
  if (USE_MOCK) return mockCall(method, path, body);
  let res;
  try {
    res = await fetch(BASE + path, {
      method,
      headers: body ? { "Content-Type": "application/json" } : {},
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, "NETWORK", "Không kết nối được máy chủ. Kiểm tra backend đã chạy chưa.");
  }
  const data = await res.json();
  if (!res.ok) throw new ApiError(res.status, data.error?.code, data.error?.message);
  return data;
}

export const api = {
  restaurants:   ()          => call("GET",   "/restaurants"),
  menu:          (id)        => call("GET",   `/restaurants/${id}/menu`),
  createSession: (chatText)  => call("POST",  "/sessions", { chat_text: chatText }),
  getSession:    (sid)       => call("GET",   `/sessions/${sid}`),
  sendMessage:   (sid, text) => call("POST",  `/sessions/${sid}/messages`, { text }),
  editMembers:   (sid, members) => call("PATCH", `/sessions/${sid}/members`, { members }),
  confirm:       (sid)       => call("POST",  `/sessions/${sid}/confirm`),
  reopen:        (sid)       => call("POST",  `/sessions/${sid}/reopen`),
  action:        (sid, action) => call("POST", `/sessions/${sid}/actions`, { action }),
  finalize:      (sid)       => call("POST",  `/sessions/${sid}/finalize`),
};
```

Mock: chép thư mục [`docs/ba/mocks/`](ba/mocks/) vào `public/mocks/` của FE. Các file này **sinh từ API thật**,
nên khi tắt mock không phải sửa component.

```js
// Chuyển mock theo kịch bản demo: mỗi thao tác trả file kế tiếp.
async function mockCall(method, path) {
  const pick = (f) => fetch(`/mocks/${f}`).then((r) => r.json());
  if (path === "/restaurants") return pick("restaurants.json");
  if (path.endsWith("/menu")) return pick("menu_store_08.json");
  if (path === "/sessions") return pick("session_draft.json");
  if (path.endsWith("/messages")) return pick(mockStep++ === 0 ? "session_draft_answered.json" : "session_refusal.json");
  if (path.endsWith("/confirm")) return pick("session_cart_valid.json");
  if (path.endsWith("/finalize")) return pick("session_finalized.json");
  if (path.endsWith("/actions")) return pick("session_cart_valid.json");
  return pick("session_draft.json");
}
let mockStep = 0;
```

Muốn xem màn "chưa khả thi" thì trả `session_infeasible.json` cho `/confirm`.

## 4. Luồng màn hình ↔ API

| Người dùng làm | Gọi | Sau khi có response |
|---|---|---|
| Mở trang | (không gọi) | Màn (A): ô dán chat + nút "Nạp chat mẫu" + "Phân tích" |
| Bấm "Phân tích" | `createSession(chatText)` | Lưu `session_id` (vào `localStorage` để F5 không mất), render (B) |
| Gõ câu trả lời / yêu cầu | `sendMessage(sid, text)` | Render lại từ state mới |
| Sửa thẻ thành viên (thêm/xoá người, chip) | `editMembers(sid, members)` | Chỉ khi `status=PROFILE_DRAFT` |
| Bấm "Xác nhận hồ sơ" | `confirm(sid)` | Chỉ bật khi `state.can_confirm`. Ra (C) hoặc (D) |
| Bấm "Sửa hồ sơ" | `reopen(sid)` | Hỏi xác nhận trước: "Giỏ hiện tại sẽ bị huỷ và bạn phải xác nhận lại hồ sơ. Tiếp tục?" |
| Bấm nút đề xuất ở (D) | `action(sid, option.action)` | Gửi nguyên `option.action` lấy từ `state.infeasible.options` |
| Bấm "Đổi quán" ở (C) | `action(sid, {type: "CHANGE_RESTAURANT"})` | Nếu không còn quán khác phù hợp, giỏ **giữ nguyên** và có tin `INFO` báo lý do |
| Bấm "Chốt giỏ" | `finalize(sid)` | Màn (E): hiện `final_message` + nút Copy |
| F5 trang | `getSession(sid)` | Khôi phục đúng chỗ đang làm |
| "Làm đơn mới" | (không gọi) | Xoá `session_id`, về (A) |

**Ô dán chat:** định dạng *tên một dòng, tin nhắn dòng sau* (một tin có thể nhiều dòng). Quỹ chung nằm trong chat.
**Không có ô quỹ, không có dropdown chọn quán** — agent chọn quán sau khi xác nhận. Đoạn chat cho nút "Nạp chat mẫu":

```text
Chi
12h đặt cơm trưa nha mn, quỹ chung 300k nhé
An
t ăn chay nha, nhớ đó
Bình
mình dị ứng đậu phộng nặng lắm, đừng có gì dính đậu phộng nha
Dũng
gì cũng được, nhanh lên đói rồi 😭
An
à lấy thêm 1 cơm gà nha
Hà
mình muốn ăn bún
```

## 5. Render từ `SessionState` — những trường cần dùng

| Chỗ hiển thị | Lấy từ | Ghi chú |
|---|---|---|
| Quỹ ở header | `state.budget` | `null` khi chat chưa nêu quỹ (có câu hỏi về quỹ) |
| Thẻ quán | `state.restaurant` (`name`, `distance_km`, `summary`, `shipping_fee`) | `null` ở Phase 1 |
| Thẻ thành viên | `state.members[]` | Chip cứng: `hard_constraints` (🔒 khi `locked`); chip mềm: `preferences` |
| Câu gốc của người | `member.quotes[]` | Chưa có câu gốc theo từng ràng buộc |
| Câu hỏi mở | `state.questions.filter(q => q.status === "OPEN")` | Thẻ có câu hỏi mở của người đó (`member_id`) thì hiện ❓ |
| Nút xác nhận | `state.can_confirm` | Tooltip khi khoá: "Còn {N} câu hỏi cần trả lời" |
| Hội thoại | `state.messages[]` | Tin đầu (`role:"user"`) là đoạn chat đã dán → thu gọn. `kind:"REFUSAL"` → nền đỏ nhạt 🛡️ |
| Giỏ | `state.cart.lines[]` | `member_id` → tên qua `members`; giá `unit_price` |
| Tiền | `cart.subtotal`, `shipping_fee`, `total`, `remaining`, `budget` | **Không tự cộng.** Định dạng `toLocaleString("vi-VN") + "đ"` |
| Món bị loại | `cart.excluded[]` → `reasons[].text` | Thu gọn, mặc định hiện 3 dòng |
| Nhãn "✓ Giỏ hợp lệ" | `state.validation?.ok === true` | Câu: "Đã kiểm theo yêu cầu đã xác nhận và menu quán" |
| Chưa khả thi | `state.infeasible` (`message`, `options[]`) | Không hiện giỏ, không hiện nhãn hợp lệ |
| Tin chốt | `state.final_message` | Giữ xuống dòng (`white-space: pre-wrap`) |

Mã dị ứng → chữ hiển thị (dùng cho chip và dropdown thêm dị ứng, đúng 10 mã):

```js
export const ALLERGEN_LABEL = {
  PEANUT: "đậu phộng", SOY: "đậu nành", WHEAT: "lúa mì", EGG: "trứng", MILK: "sữa",
  FISH: "cá", CRUSTACEAN: "giáp xác (tôm, cua)", MOLLUSC: "nhuyễn thể (mực, nghêu, hàu)",
  SESAME: "mè", CELERY: "cần tây",
};
```

**`PATCH /members`** gửi toàn bộ danh sách, mỗi người tối thiểu:

```json
{ "members": [
  { "name": "Khoa",
    "hard_constraints": [ { "type": "ALLERGY", "allergen": "CRUSTACEAN" } ],
    "preferences": [ { "text": "món có nước" } ] }
] }
```

Gửi lại nguyên object `member` lấy từ state (đã sửa chip) cũng được; server chỉ đọc `name`, `hard_constraints`, `preferences`.
Mã dị ứng ngoài 10 mã hoặc tên trùng → `400`.

## 6. Chờ AI và xử lý lỗi

- **Mỗi lượt có AI mất 5–40 giây** (lúc mạng/nhà cung cấp chậm có thể lâu hơn). Các API có AI:
  `createSession`, `sendMessage`, `confirm`, `action` (khi phải lập lại giỏ). `reopen`, `editMembers`, `finalize`, `getSession` gần như tức thì.
  - Khoá nút và ô nhập, hiện spinner có chữ: "Đang đọc đoạn chat…", "Đang chọn quán và lập giỏ…", bong bóng "…".
  - **Không đặt timeout ngắn ở `fetch`** (tối thiểu 120 giây), không tự gửi lại khi đang chờ.
- Lỗi:

| `status` / `code` | FE làm gì |
|---|---|
| `400 INVALID_INPUT` | Hiện `message` dưới ô nhập / form |
| `404 NOT_FOUND` (phiên) | Xoá `session_id` đã lưu, về màn (A) |
| `409 INVALID_STATE` | Gọi `getSession(sid)` rồi render lại (thường do nút bấm lệch trạng thái) |
| `502 AI_UNAVAILABLE`, `500 INTERNAL` | Hiện "Hệ thống AI tạm thời không phản hồi, vui lòng thử lại." + nút **Thử lại** (gửi lại đúng request). Phiên **không đổi** khi lỗi |
| `NETWORK` (fetch lỗi) | "Không kết nối được máy chủ" — kiểm backend đã chạy |

- Chặn ở client trước khi gọi: chat rỗng, chat > 4.000 ký tự (hiện bộ đếm).

## 7. Những thứ API chưa có (đừng dựng UI phụ thuộc vào)

| Trường | Hiện trả | Làm tạm |
|---|---|---|
| `chat_lines` | `[]` | Hiện lại đoạn chat từ tin nhắn đầu tiên trong `messages` |
| `source.line`, `source.quote` | `null` | Hiện `member.quotes` dưới thẻ, bỏ tính năng "bấm nguồn → bôi vàng dòng" |
| `flags` | `[]` | Dùng câu hỏi `OPEN` theo `member_id` để hiện ❓ |
| `question.options`, `message.question_id` | `[]` / `null` | Không có nút trả lời nhanh, người đặt gõ câu trả lời |
| Tiền trong `message`, `final_message` | dạng `120,000đ` | Hiện nguyên văn; tiền ở giỏ thì FE tự định dạng từ số |

Cần thêm trường nào thì báo Lương/Dũng, **đừng tự suy từ chuỗi** trong `message`.

## 8. Checklist nối xong

- [ ] Chạy được bằng mock (`VITE_USE_MOCK=true`) đủ 5 màn (A)–(E) + màn lỗi.
- [ ] Đổi sang API thật (`VITE_USE_MOCK=false`), backend chạy, đi hết kịch bản demo với "Nạp chat mẫu":
      phân tích → trả lời câu hỏi về An → xác nhận → gõ "kệ dị ứng của Bình đi" (thấy 🛡️ từ chối) → chốt → Copy.
- [ ] Chat không ghi quỹ → thấy câu hỏi quỹ, nút xác nhận khoá; trả lời "quỹ 200k" → mở khoá.
- [ ] Chat ghi quỹ 100k → màn (D) với nút "Tăng quỹ lên …" và "Đổi quán"; bấm tăng quỹ → ra giỏ.
- [ ] "Sửa hồ sơ" → hộp xác nhận → về Phase 1, giỏ mất, chip hết 🔒.
- [ ] F5 giữa chừng vẫn quay lại đúng phiên.
- [ ] Không chỗ nào FE tự tính tiền hoặc tự quyết "hợp lệ".
- [ ] Không có API key trong code FE.
