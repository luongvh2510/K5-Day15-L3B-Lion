# 04 · Hợp đồng dữ liệu và API

> **File để FE, BE và AI cùng bám vào.** FE làm trước bằng các JSON mẫu ở mục 6. Khi BE xong, chỉ cần đổi nguồn
> dữ liệu từ mock sang API thật, **không đổi hình dạng JSON**.
> Muốn đổi schema thì báo BA và ghi vào mục 8 "Nhật ký thay đổi".
>
> **Cập nhật 28/11:** file này đã viết lại theo **API thật** (`server/api.py`, `codebase/core.py`, `codebase/tools.py`)
> và dữ liệu thật `data/dataset_mon_an_viet.json`. Các chỗ khác bản đầu được ghi ở mục 8.
> Trường đánh dấu **(chưa có)** đã có trong hình dạng JSON nhưng hiện luôn trả giá trị rỗng/`null`; FE vẫn nên xử lý được.

## 1. Nguyên tắc chung

- **Mọi API thay đổi phiên đều trả về toàn bộ `SessionState`.** FE chỉ cần render lại từ object này, không phải tự ghép.
- Tiền: số nguyên, đơn vị **đồng** (`300000`, không phải `300` hay `"300k"`). FE tự định dạng `300.000đ`.
- ID: chuỗi. Tên trường: `snake_case`. Thời gian: ISO 8601 (UTC, đuôi `Z`).
- Enum viết HOA. Tên hiển thị tiếng Việt do FE ánh xạ (mục 5).
- Trạng thái nào được gọi API nào: xem mục 3.
- **Người đặt chỉ dán đoạn chat.** Quỹ được đọc từ chat (thiếu thì hệ thống hỏi). **Quán do agent tự chọn** sau khi
  xác nhận hồ sơ; người đặt không chọn quán lúc đầu, chỉ có thể bấm "Đổi quán" ở Phase 2.

## 2. Kiểu dữ liệu

### 2.1 Menu

```ts
Restaurant {
  id: string                // "store_08"
  name: string              // "Xôi Nếp Ban Mai"
  menu_type: string         // "xoi" | "pho" | "bun" | "com" | "mi" | "mien" | "hu_tieu" | "banh_canh" | "banh_mi" | "chao"
  summary: string           // mô tả ngắn của quán
  distance_km: number       // 0.9
  shipping_fee: number      // 15000 — dữ liệu không có phí ship, POC dùng cố định 15.000đ cho mọi quán
}

MenuItem {                  // mọi món trong dữ liệu đều là món chính (1 suất/người), không có món phụ/đồ uống
  id: string                // "dish_071"
  name: string              // "Xôi gà xé"
  price: number             // 35000
  ingredients: string[]     // mã nguyên liệu: ["sticky_rice", "chicken_breast", "fish_sauce", ...]
  allergens: Allergen[]     // chữ thường: ["fish", "soy", "wheat"]
  allergen_sources: { [tag: string]: string[] }   // {"fish": ["Nước mắm cá cơm và muối"]} — tên nguyên liệu gây dị ứng
  animal_ingredients: string[]  // tên nguyên liệu nguồn động vật: ["Ức gà", "Nước mắm cá cơm và muối"]
  vegetarian: boolean       // code TỰ SUY từ nguyên liệu (BR-02), không phải nhãn của quán
  available: boolean
  ingredients_known: boolean    // false → BR-04 (dữ liệu hiện tại: mọi món đều true)
}

// Mã dị ứng lấy đúng theo dữ liệu (allergen_types), 10 mã, CHỮ THƯỜNG ở menu:
Allergen = "fish" | "crustacean" | "mollusc" | "egg" | "milk" | "wheat" | "soy" | "peanut" | "sesame" | "celery"
// Trong hồ sơ (HardConstraint.allergen) cùng mã nhưng VIẾT HOA: "PEANUT", "CRUSTACEAN", ...
// Không còn TREE_NUT, SHELLFISH, OTHER. Dị ứng ngoài 10 mã → hệ thống hỏi lại, không tạo ràng buộc.
```

### 2.2 Hồ sơ nhóm

```ts
ChatLine {                  // (chưa có) chat_lines hiện luôn là []
  line: number
  speaker: string | null
  text: string
}

Source {
  kind: "CHAT" | "HOST"     // HOST = người đặt tự thêm qua PATCH /members
  line: number | null       // (chưa có) luôn null
  quote: string | null      // (chưa có) luôn null — câu gốc hiện nằm ở Member.quotes
}

HardConstraint {
  id: string                // "m2-vegetarian", "m3-peanut"
  type: "VEGETARIAN" | "ALLERGY"
  allergen: string | null   // mã viết hoa, bắt buộc khi type=ALLERGY: "PEANUT"
  note: null                // không dùng (bỏ OTHER)
  source: Source
  locked: boolean           // true sau khi xác nhận hồ sơ (BR-12)
}

Preference {
  id: string                // "m4-p1"
  text: string              // "cơm gà", "muốn ăn bún"
  source: Source
}

Member {
  id: string                // "m1", "m2"… theo thứ tự xuất hiện; KHÔNG ổn định nếu PATCH đổi thứ tự/xoá người
  name: string
  origin: "CHAT" | "HOST_ADDED"
  hard_constraints: HardConstraint[]
  preferences: Preference[]
  flags: []                 // (chưa có) luôn [] — mâu thuẫn/mơ hồ chỉ thể hiện qua questions
  quotes: string[]          // MỚI: các câu chat gốc của người này, dạng "An: t ăn chay nha, nhớ đó"
}

Question {
  id: string                // "q1"
  member_id: string | null
  text: string
  options: []               // (chưa có) luôn [] → người đặt tự gõ câu trả lời
  status: "OPEN" | "ANSWERED"
}
```

### 2.3 Hội thoại

```ts
Message {
  id: string                // "msg1"
  role: "user" | "assistant"
  kind: "TEXT" | "QUESTION" | "REFUSAL" | "INFO"   // FE tô màu khác cho REFUSAL
  text: string
  question_id: null         // (chưa có) luôn null, kể cả kind=QUESTION
  turn: number              // MỚI: lượt xử lý tạo ra tin này (tăng mỗi lần confirm/messages/finalize)
  created_at: string
}
```

Tin đầu tiên của phiên là đoạn chat người đặt dán (`role:"user"`, `kind:"TEXT"`).

### 2.4 Giỏ, kiểm giỏ, bất khả thi

```ts
CartLine {
  member_id: string
  menu_item_id: string      // "dish_077"
  name: string
  type: "MAIN"              // luôn MAIN
  unit_price: number        // LẤY TỪ MENU (BR-05)
  qty: 1
  line_total: number
  reason: string | null     // lý do AI chọn, ngắn
  note: null                // không dùng (dữ liệu không có món thiếu thành phần)
}

ExcludedItem {
  member_id: string
  menu_item_id: string
  name: string
  reasons: { rule: string, text: string }[]
  // rule: "BR-02" (không chay) | "BR-03" (dị ứng) | "BR-04" (không rõ thành phần) | "BR-05" (hết món)
  // text do code sinh, nêu nguyên liệu: "không chay: có Ức gà, Nước mắm cá cơm và muối"
  //                                     "dị ứng đậu phộng: có Đậu phộng rang"
}

Cart {
  lines: CartLine[]
  subtotal: number
  shipping_fee: number
  total: number             // subtotal + shipping_fee
  budget: number
  remaining: number         // budget - total (≥ 0)
  excluded: ExcludedItem[]  // mọi món bị loại, chỉ cho thành viên có ràng buộc cứng
  built_by: "AI" | "FALLBACK"
}

Validation {
  ok: boolean               // hiện luôn true khi có cart (giỏ chỉ được tạo sau khi validate_cart không lỗi)
  violations: []
}

Action =
  | { type: "SET_BUDGET", budget: number }
  | { type: "CHANGE_RESTAURANT", restaurant_id?: string }   // không gửi restaurant_id → agent tự chọn quán khác;
  //   nếu đang CART_VALID mà không quán nào khác lập được giỏ thì GIỮ giỏ cũ và thêm tin INFO "…giữ giỏ ở {quán}".
  //   Có restaurant_id → luôn lập giỏ ở quán đó (có thể ra CART_INFEASIBLE để người đặt thấy lý do).

Infeasible {
  kind: "NO_SAFE_ITEM" | "OVER_BUDGET"
  members_without_option: string[]   // member_id, khi kind=NO_SAFE_ITEM
  min_total: number | null           // khi kind=OVER_BUDGET, đã gồm ship
  shortfall: number | null           // min_total - budget
  message: string                    // câu do code viết, có số liệu
  options: { id: "budget" | "restaurant", label: string, action: Action }[]
  // OVER_BUDGET: [Tăng quỹ lên {min_total}] + [Đổi quán]; NO_SAFE_ITEM: chỉ [Đổi quán]
}
```

### 2.5 Trạng thái phiên — object FE render

```ts
SessionStatus = "PROFILE_DRAFT" | "CART_VALID" | "CART_INFEASIBLE" | "FINALIZED"

SessionState {
  session_id: string
  status: SessionStatus
  restaurant: Restaurant | null   // null ở PROFILE_DRAFT (chưa chọn quán)
  budget: number | null           // null nếu chat không nêu quỹ (khi đó có câu hỏi về quỹ)
  chat_lines: []                  // (chưa có)
  members: Member[]
  questions: Question[]
  can_confirm: boolean            // = status==PROFILE_DRAFT && có thành viên && có quỹ && không còn question OPEN
  messages: Message[]
  cart: Cart | null               // có khi CART_VALID / FINALIZED
  validation: Validation | null
  infeasible: Infeasible | null   // có khi CART_INFEASIBLE
  final_message: string | null    // có khi FINALIZED
}
```

## 3. Máy trạng thái

```
                 POST /sessions
                       │
                       ▼
               ┌───────────────┐  PATCH /members, POST /messages (trả lời câu hỏi)
               │ PROFILE_DRAFT │◄──────────────────────────────┐
               └───────┬───────┘                               │
          POST /confirm│ (chỉ khi can_confirm)                 │ POST /reopen
                       ▼                                       │ (huỷ giỏ, mở khoá)
       agent chọn quán → code tính khả thi                     │
            ▼                           ▼                      │
     ┌────────────┐  POST /actions ┌─────────────────┐         │
     │ CART_VALID │◄─SET_BUDGET /──│ CART_INFEASIBLE │─────────┤
     └─────┬──────┘ CHANGE_REST.   └─────────────────┘         │
           │  POST /messages (đổi món, thêm ràng buộc, đổi quỹ, đổi quán) ─ tự quay về VALID/INFEASIBLE
           │──────────────────────────────────────────────────►┘
           │ POST /finalize
           ▼
     ┌───────────┐
     │ FINALIZED │
     └───────────┘
```

| API | PROFILE_DRAFT | CART_VALID | CART_INFEASIBLE | FINALIZED |
|---|:---:|:---:|:---:|:---:|
| `PATCH /members` | ✅ | ❌ 409 | ❌ 409 | ❌ 409 |
| `POST /messages` | ✅ trả lời câu hỏi, bổ sung hồ sơ | ✅ sửa giỏ | ✅ | ❌ 409 |
| `POST /confirm` | ✅ nếu `can_confirm` | ❌ 409 | ❌ 409 | ❌ 409 |
| `POST /reopen` | ❌ 409 | ✅ | ✅ | ❌ 409 |
| `POST /actions` | ❌ 409 | ✅ | ✅ | ❌ 409 |
| `POST /finalize` | ❌ 409 | ✅ | ❌ 409 | ❌ 409 |

## 4. Endpoint

Gốc: `http://127.0.0.1:8000/api` (chạy `python run.py`, chọn `2`). Có CORS `*`.
Mọi response lỗi có dạng: `{ "error": { "code": "STRING", "message": "câu tiếng Việt" } }`.

| Method | Path | Body | Trả về | Ghi chú |
|---|---|---|---|---|
| GET | `/restaurants` | — | `Restaurant[]` | 10 quán |
| GET | `/restaurants/{id}/menu` | — | `{ restaurant, items: MenuItem[] }` | |
| POST | `/sessions` | `{ chat_text }` | `SessionState` | Chỉ có đoạn chat. Gọi AI trích hồ sơ + quỹ. Mất 5–20 giây |
| GET | `/sessions/{id}` | — | `SessionState` | Không bị chặn khi phiên đang chờ AI |
| POST | `/sessions/{id}/messages` | `{ text }` | `SessionState` | Câu trả lời / yêu cầu gõ tự do. Không có `question_id`, `option_id` |
| PATCH | `/sessions/{id}/members` | `{ members: Member[] }` | `SessionState` | Thay toàn bộ danh sách. Mỗi member cần `name`, `hard_constraints[{type, allergen}]`, `preferences[{text}]`. Ràng buộc mới có `source.kind="HOST"` |
| POST | `/sessions/{id}/confirm` | — | `SessionState` | Khoá ràng buộc → agent chọn quán → lập giỏ → `CART_VALID` / `CART_INFEASIBLE` |
| POST | `/sessions/{id}/reopen` | — | `SessionState` | Về `PROFILE_DRAFT`, `cart=null`, `restaurant=null`, mở khoá |
| POST | `/sessions/{id}/actions` | `{ action: Action }` | `SessionState` | Chọn đề xuất nới (tăng quỹ / đổi quán) |
| POST | `/sessions/{id}/finalize` | — | `SessionState` | Sinh `final_message` |
| POST | `/debug/validate-cart` | `{ store_id, members, selected, budget, shipping }` | `string[]` | Danh sách lỗi (rỗng = hợp lệ). `selected`: mảng dish id theo thứ tự `members` |

Mã lỗi:

| HTTP | `code` | Khi nào |
|---|---|---|
| 400 | `INVALID_INPUT` | Chat rỗng hoặc > 4.000 ký tự, JSON sai, quỹ ≤ 0, mã dị ứng ngoài 10 mã, tên trùng |
| 404 | `NOT_FOUND` | Sai session, quán hoặc đường dẫn |
| 409 | `INVALID_STATE` | Gọi API không hợp trạng thái (bảng mục 3), kể cả PATCH khi hồ sơ đã khoá |
| 500 | `INTERNAL` | Lỗi hệ thống không lường trước. FE hiện "Thử lại" |
| 502 | `AI_UNAVAILABLE` | LLM lỗi sau khi đã thử lại. FE hiện "Thử lại" |

> Bỏ `409 HARD_CONSTRAINT_LOCKED`: sau khi xác nhận, `PATCH /members` luôn trả `409 INVALID_STATE`;
> muốn bớt ràng buộc phải `POST /reopen` trước (BR-12).

## 5. Ánh xạ hiển thị cho FE

| Enum | Hiển thị |
|---|---|
| `VEGETARIAN` | 🌱 Ăn chay (thuần: không thịt, cá, hải sản, trứng, sữa, mắm) |
| `ALLERGY` + `PEANUT` / `SOY` / `WHEAT` / `EGG` / `MILK` / `FISH` / `CRUSTACEAN` / `MOLLUSC` / `SESAME` / `CELERY` | ⚠️ Dị ứng đậu phộng / đậu nành / lúa mì / trứng / sữa / cá / giáp xác (tôm, cua) / nhuyễn thể (mực, nghêu, hàu) / mè / cần tây |
| `REFUSAL` | 🛡️ bong bóng nền đỏ nhạt |
| `built_by: FALLBACK` | (nhỏ) "Giỏ dự phòng: chọn món rẻ nhất an toàn" |

## 6. JSON mẫu (dùng làm mock cho FE)

Các file trong [`mocks/`](mocks/) được **sinh từ API thật với model thật** (28/11, `deepseek/deepseek-v4.1-flash`),
chạy kịch bản demo ở file 00 mục 7. Dùng thẳng làm mock; khi nối API thật không cần đổi component.

| File | Trạng thái | Nội dung |
|---|---|---|
| [`session_draft.json`](mocks/session_draft.json) | `PROFILE_DRAFT` | Vừa phân tích xong, 1 câu hỏi về An (chay nhưng nhắc cơm gà), `can_confirm=false` |
| [`session_draft_answered.json`](mocks/session_draft_answered.json) | `PROFILE_DRAFT` | Đã trả lời "cơm gà cho Dũng", `can_confirm=true` |
| [`session_cart_valid.json`](mocks/session_cart_valid.json) | `CART_VALID` | Agent chọn `store_08`, giỏ 5 suất, tổng 134.000đ, có `excluded` kèm nguyên liệu |
| [`session_refusal.json`](mocks/session_refusal.json) | `CART_VALID` | Sau câu "kệ dị ứng của Bình đi": tin `REFUSAL`, giỏ giữ nguyên |
| [`session_finalized.json`](mocks/session_finalized.json) | `FINALIZED` | Có `final_message` |
| [`session_infeasible.json`](mocks/session_infeasible.json) | `CART_INFEASIBLE` | Quỹ 100k: `OVER_BUDGET`, `min_total=120000`, `shortfall=20000`, 2 nút |
| [`restaurants.json`](mocks/restaurants.json) | — | `GET /restaurants` |
| [`menu_store_08.json`](mocks/menu_store_08.json) | — | `GET /restaurants/store_08/menu` |

Đoạn chat dùng để sinh mẫu (định dạng: tên một dòng, tin nhắn dòng sau; một tin có thể nhiều dòng):

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

Lỗi 502 (mock `error_ai.json` FE tự tạo):

```json
{ "error": { "code": "AI_UNAVAILABLE", "message": "Hệ thống AI tạm thời không phản hồi, vui lòng thử lại." } }
```

> Lưu ý khi đọc mẫu: `message`/`final_message` hiện định dạng tiền kiểu `120,000đ` (dấu phẩy); FE chỉ hiển thị nguyên văn.
> Trong ví dụ này chỉ 2 quán có món chay, nên agent chọn quán xôi dù Hà muốn bún (sở thích mềm, BR-08).

## 7. Hàm code dùng chung (Python, `codebase/tools.py` và `codebase/core.py`)

```python
# tools.py — không gọi LLM
def list_restaurants() -> list[dict]: ...                       # [{id, name, menu_type, summary, distance_km}]
def load_menu(store_id: str) -> dict[str, dict]: ...             # {dish_id: MenuItem không có id}
def dish_exclusion(member: dict, item: dict) -> str: ...        # "" nếu an toàn, ngược lại lý do
def safe_mains(member, menu) -> tuple[list[str], dict[str, str]]: ...   # (id an toàn, {id: lý do loại})
def feasibility(members, options, menu, shipping) -> tuple[list[str], int | None]: ...  # (người không có món, chi phí tối thiểu)
def validate_cart(members, selected, menu, budget, shipping) -> list[str]: ...          # [] = hợp lệ (BR-02..07)
def shipping_fee(store_id) -> int: ...                           # 15000
def store_summary(store_id, members, budget, shipping) -> dict: ...  # {id, name, safe_counts, min_total}

# core.py — luồng phiên; mọi hàm nhận và trả dict session
start(chat_text) · confirm(s) · send(s, text) · finalize(s) · render(s)
reopen(s) · edit_profile(s, members) · set_budget(s, amount) · change_restaurant(s, store_id=None)
```

Không có `fallback_cart` riêng: `core._plan_cart` sau 2 lần AI chọn sai sẽ tự lấy món an toàn rẻ nhất cho từng người
rồi kiểm lại (`built_by="FALLBACK"`).

## 8. Nhật ký thay đổi

| Ngày | Ai | Thay đổi |
|---|---|---|
| 27/11/2026 | BA | Bản đầu |
| 28/11/2026 | AI (Lương) | Viết lại theo API thật. **Đầu vào:** `POST /sessions` chỉ còn `{chat_text}` (bỏ `budget`, `restaurant_id`, `include_host`); quỹ đọc từ chat, quán do agent chọn khi xác nhận (`restaurant`=`null` ở Phase 1). **Menu:** id `store_xx`/`dish_xxx` theo dữ liệu thật; mọi món là món chính (bỏ `SIDE`/`DRINK`); thêm `ingredients`, `allergen_sources`, `animal_ingredients`; `vegetarian` do code suy từ nguyên liệu; ship cố định 15.000đ. **Dị ứng:** 10 mã theo dữ liệu (thêm `CRUSTACEAN`, `MOLLUSC`, `CELERY`; bỏ `TREE_NUT`, `SHELLFISH`, `OTHER`). **Hồ sơ:** thêm `Member.quotes`; `chat_lines`, `flags`, `source.line/quote`, `question.options`, `message.question_id` chưa có. **Hội thoại:** thêm `Message.turn`; `/messages` chỉ nhận `{text}`. **Hành động:** `CHANGE_RESTAURANT` không cần `restaurant_id`; option id `budget`/`restaurant`. **Lỗi:** thêm `500 INTERNAL`, bỏ `HARD_CONSTRAINT_LOCKED`. **Debug:** `validate-cart` nhận `{store_id, members, selected, budget, shipping}` trả `string[]`. Mock chuyển sang thư mục `mocks/` sinh từ API thật |
