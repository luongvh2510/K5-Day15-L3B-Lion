# 04 · Hợp đồng dữ liệu và API

> **File để FE, BE và AI cùng bám vào.** FE làm trước bằng các JSON mẫu ở mục 6. Khi BE xong, chỉ cần đổi nguồn
> dữ liệu từ mock sang API thật, **không đổi hình dạng JSON**.
> Muốn đổi schema thì báo BA và ghi vào mục 8 "Nhật ký thay đổi".

## 1. Nguyên tắc chung

- **Mọi API thay đổi phiên đều trả về toàn bộ `SessionState`.** FE chỉ cần render lại từ object này, không phải tự ghép.
- Tiền: số nguyên, đơn vị **đồng** (`300000`, không phải `300` hay `"300k"`). FE tự định dạng `300.000đ`.
- ID: chuỗi. Tên trường: `snake_case`. Thời gian: ISO 8601.
- Enum viết HOA. Tên hiển thị tiếng Việt do FE ánh xạ (mục 5).
- Trạng thái nào được gọi API nào: xem mục 3.

## 2. Kiểu dữ liệu

### 2.1 Menu

```ts
Restaurant {
  id: string                // "r1"
  name: string              // "Quán Cơm Nhà Mẫu"
  shipping_fee: number      // 20000
}

MenuItem {
  id: string                // "M06"
  name: string              // "Cơm đậu hũ sốt nấm"
  price: number             // 45000
  type: "MAIN" | "SIDE" | "DRINK"
  vegetarian: boolean | null      // null = không rõ → coi là KHÔNG chay (BR-02)
  allergens: Allergen[]           // ["SOY"]
  ingredients_known: boolean      // false → BR-04
  available: boolean
}

Allergen = "PEANUT" | "TREE_NUT" | "SOY" | "WHEAT" | "EGG" | "MILK"
         | "SHELLFISH" | "FISH" | "SESAME" | "OTHER"
```

### 2.2 Hồ sơ nhóm

```ts
ChatLine {
  line: number              // số dòng, bắt đầu từ 1
  speaker: string | null    // "An"; null nếu không tách được người nói
  text: string
}

Source {
  kind: "CHAT" | "HOST"     // HOST = người đặt tự thêm hoặc trả lời câu hỏi
  line: number | null       // dòng chat gốc (kind=CHAT)
  quote: string | null      // trích nguyên văn
}

HardConstraint {
  id: string
  type: "VEGETARIAN" | "ALLERGY"
  allergen: Allergen | null // bắt buộc khi type=ALLERGY
  note: string | null       // mô tả khi allergen=OTHER
  source: Source
  locked: boolean           // true sau khi xác nhận hồ sơ (BR-12)
}

Preference {
  id: string
  text: string              // "muốn ăn bún", "món có nước"
  source: Source
}

Flag {
  type: "CONFLICT" | "AMBIGUOUS"
  message: string           // "Nói ăn chay nhưng nhắc 'cơm gà'"
  question_id: string
}

Member {
  id: string                // "m1"
  name: string
  origin: "CHAT" | "HOST_ADDED"
  hard_constraints: HardConstraint[]
  preferences: Preference[]
  flags: Flag[]             // chỉ còn cờ của câu hỏi chưa trả lời
}

Question {
  id: string
  member_id: string | null
  text: string
  options: { id: string, label: string }[]   // có thể rỗng → người đặt tự gõ
  status: "OPEN" | "ANSWERED"
}
```

### 2.3 Hội thoại

```ts
Message {
  id: string
  role: "user" | "assistant"
  kind: "TEXT" | "QUESTION" | "REFUSAL" | "INFO"   // FE tô màu khác cho REFUSAL
  text: string
  question_id: string | null
  created_at: string
}
```

### 2.4 Giỏ, kiểm giỏ, bất khả thi

```ts
CartLine {
  member_id: string
  menu_item_id: string
  name: string
  type: "MAIN" | "SIDE" | "DRINK"
  unit_price: number        // LẤY TỪ MENU (BR-05)
  qty: number
  line_total: number
  reason: string | null     // "Món có nước, không có đậu phộng"
  note: string | null       // "Quán không ghi thành phần" (BR-04)
}

ExcludedItem {
  member_id: string
  menu_item_id: string
  name: string
  reasons: { rule: string, text: string }[]   // [{rule:"BR-03", text:"Có đậu phộng"}]
}

Cart {
  lines: CartLine[]
  subtotal: number
  shipping_fee: number
  total: number             // subtotal + shipping_fee
  budget: number
  remaining: number         // budget - total (≥ 0 khi hợp lệ)
  excluded: ExcludedItem[]  // chỉ món chính, chỉ cho thành viên có ràng buộc cứng
  built_by: "AI" | "FALLBACK"
}

Violation {
  code: "NOT_IN_MENU" | "UNAVAILABLE" | "PRICE_MISMATCH" | "NOT_VEGETARIAN"
      | "ALLERGEN" | "UNKNOWN_INGREDIENTS" | "MISSING_MAIN" | "EXTRA_MAIN"
      | "UNKNOWN_MEMBER" | "OVER_BUDGET"
  rule: string              // "BR-03"
  member_id: string | null
  menu_item_id: string | null
  message: string
}

Validation {
  ok: boolean               // true ⇔ violations rỗng
  violations: Violation[]
}

Action =
  | { type: "SET_BUDGET", budget: number }
  | { type: "CHANGE_RESTAURANT", restaurant_id: string }     // [COULD]

Infeasible {
  kind: "NO_SAFE_ITEM" | "OVER_BUDGET"
  members_without_option: string[]   // member_id, khi kind=NO_SAFE_ITEM
  min_total: number | null           // khi kind=OVER_BUDGET
  shortfall: number | null           // min_total - budget
  message: string                    // câu AI viết, đã có số liệu từ code
  options: { id: string, label: string, action: Action }[]
}
```

### 2.5 Trạng thái phiên — object FE render

```ts
SessionStatus = "PROFILE_DRAFT" | "CART_VALID" | "CART_INFEASIBLE" | "FINALIZED"

SessionState {
  session_id: string
  status: SessionStatus
  restaurant: Restaurant
  budget: number
  chat_lines: ChatLine[]
  members: Member[]
  questions: Question[]
  can_confirm: boolean      // = status==PROFILE_DRAFT && members.length>0 && không có question OPEN
  messages: Message[]
  cart: Cart | null         // có khi CART_VALID / FINALIZED
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
            ┌──── code tính khả thi ────┐                      │
            ▼                           ▼                      │
     ┌────────────┐  POST /actions ┌─────────────────┐         │
     │ CART_VALID │◄───SET_BUDGET──│ CART_INFEASIBLE │─────────┤
     └─────┬──────┘                └─────────────────┘         │
           │  POST /messages (sửa giỏ, thêm ràng buộc) ─ tự quay về VALID/INFEASIBLE
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
| `POST /messages` | ✅ trả lời câu hỏi | ✅ sửa giỏ | ✅ | ❌ 409 |
| `POST /confirm` | ✅ nếu `can_confirm` | ❌ 409 | ❌ 409 | ❌ 409 |
| `POST /reopen` | ❌ 409 | ✅ | ✅ | ❌ 409 |
| `POST /actions` | ❌ 409 | ✅ | ✅ | ❌ 409 |
| `POST /finalize` | ❌ 409 | ✅ | ❌ 409 | ❌ 409 |

## 4. Endpoint

Gốc: `/api`. Mọi response lỗi có dạng: `{ "error": { "code": "STRING", "message": "câu tiếng Việt" } }`.

| Method | Path | Body | Trả về | Ghi chú |
|---|---|---|---|---|
| GET | `/restaurants` | — | `Restaurant[]` | |
| GET | `/restaurants/{id}/menu` | — | `{ restaurant, items: MenuItem[] }` | |
| POST | `/sessions` | `{ chat_text, budget, restaurant_id, include_host?: {name} }` | `SessionState` | Gọi AI trích hồ sơ (UC-02). Có thể mất 5–15 giây |
| GET | `/sessions/{id}` | — | `SessionState` | |
| POST | `/sessions/{id}/messages` | `{ text, question_id?, option_id? }` | `SessionState` | Bấm nút trả lời thì gửi `option_id` + `label` vào `text` |
| PATCH | `/sessions/{id}/members` | `{ members: Member[] }` | `SessionState` | Thay toàn bộ danh sách. Ràng buộc mới tạo bởi FE có `source.kind="HOST"` |
| POST | `/sessions/{id}/confirm` | — | `SessionState` | Khoá ràng buộc → lập giỏ → `CART_VALID` hoặc `CART_INFEASIBLE` |
| POST | `/sessions/{id}/reopen` | — | `SessionState` | Về `PROFILE_DRAFT`, `cart=null`, mở khoá |
| POST | `/sessions/{id}/actions` | `{ action: Action }` | `SessionState` | Chọn đề xuất nới |
| POST | `/sessions/{id}/finalize` | — | `SessionState` | Sinh `final_message` |
| POST | `/debug/validate-cart` | `{ lines, members, restaurant_id, budget }` | `Validation` | Dùng để test validator |

Mã lỗi:

| HTTP | `code` | Khi nào |
|---|---|---|
| 400 | `INVALID_INPUT` | Chat rỗng, quỹ ≤ 0, quá 4.000 ký tự |
| 404 | `NOT_FOUND` | Sai session hoặc quán |
| 409 | `INVALID_STATE` | Gọi API không hợp trạng thái (bảng mục 3) |
| 409 | `HARD_CONSTRAINT_LOCKED` | PATCH hoặc cập nhật làm mất ràng buộc đã khoá (BR-12) |
| 502 | `AI_UNAVAILABLE` | LLM lỗi sau khi đã thử lại. FE hiện "Thử lại" |

## 5. Ánh xạ hiển thị cho FE

| Enum | Hiển thị |
|---|---|
| `VEGETARIAN` | 🌱 Ăn chay |
| `ALLERGY` + `PEANUT` | ⚠️ Dị ứng đậu phộng |
| `ALLERGY` + `TREE_NUT` / `SOY` / `WHEAT` / `EGG` / `MILK` / `SHELLFISH` / `FISH` / `SESAME` | ⚠️ Dị ứng hạt cây / đậu nành / lúa mì / trứng / sữa / tôm cua mực / cá / mè |
| `ALLERGY` + `OTHER` | ⚠️ Dị ứng: {note} |
| `CONFLICT` / `AMBIGUOUS` | ⚠ Mâu thuẫn / ❓ Chưa rõ |
| `MAIN` / `SIDE` / `DRINK` | Món chính / Món phụ / Đồ uống |
| `built_by: FALLBACK` | (nhỏ) "Giỏ dự phòng: chọn món rẻ nhất an toàn" |

## 6. JSON mẫu (dùng làm mock cho FE)

Dữ liệu đầy đủ của menu và đoạn chat ở [06](06-du-lieu-mau-va-test.md) (`r1`, `CHAT-01`).
Gợi ý: lưu mỗi mẫu dưới đây thành một file trong `frontend/mocks/`.

### 6.1 `session_draft.json` — vừa phân tích xong, còn 1 câu hỏi

```json
{
  "session_id": "s_demo",
  "status": "PROFILE_DRAFT",
  "restaurant": { "id": "r1", "name": "Quán Cơm Nhà Mẫu", "shipping_fee": 20000 },
  "budget": 300000,
  "chat_lines": [
    { "line": 1, "speaker": "Chi", "text": "12h đặt cơm trưa nha mn, quỹ chung 300k nhé" },
    { "line": 2, "speaker": "An", "text": "t ăn chay nha, nhớ đó" },
    { "line": 3, "speaker": "Bình", "text": "mình dị ứng đậu phộng nặng lắm, đừng có gì dính đậu phộng nha" },
    { "line": 4, "speaker": "Dũng", "text": "gì cũng được, nhanh lên đói rồi 😭" },
    { "line": 5, "speaker": "An", "text": "à lấy thêm 1 cơm gà nha" },
    { "line": 6, "speaker": "Hà", "text": "mình muốn ăn bún" },
    { "line": 7, "speaker": "Bình", "text": "cho mình món có nước nha" },
    { "line": 8, "speaker": "Chi", "text": "mình ăn gì cũng được" }
  ],
  "members": [
    {
      "id": "m1", "name": "Chi", "origin": "CHAT",
      "hard_constraints": [], "preferences": [], "flags": []
    },
    {
      "id": "m2", "name": "An", "origin": "CHAT",
      "hard_constraints": [
        { "id": "c1", "type": "VEGETARIAN", "allergen": null, "note": null,
          "source": { "kind": "CHAT", "line": 2, "quote": "t ăn chay nha" }, "locked": false }
      ],
      "preferences": [],
      "flags": [
        { "type": "CONFLICT", "message": "Nói ăn chay nhưng nhắc \"lấy thêm 1 cơm gà\"", "question_id": "q1" }
      ]
    },
    {
      "id": "m3", "name": "Bình", "origin": "CHAT",
      "hard_constraints": [
        { "id": "c2", "type": "ALLERGY", "allergen": "PEANUT", "note": null,
          "source": { "kind": "CHAT", "line": 3, "quote": "mình dị ứng đậu phộng nặng lắm" }, "locked": false }
      ],
      "preferences": [
        { "id": "p1", "text": "món có nước", "source": { "kind": "CHAT", "line": 7, "quote": "cho mình món có nước nha" } }
      ],
      "flags": []
    },
    {
      "id": "m4", "name": "Dũng", "origin": "CHAT",
      "hard_constraints": [], "preferences": [], "flags": []
    },
    {
      "id": "m5", "name": "Hà", "origin": "CHAT",
      "hard_constraints": [],
      "preferences": [
        { "id": "p2", "text": "muốn ăn bún", "source": { "kind": "CHAT", "line": 6, "quote": "mình muốn ăn bún" } }
      ],
      "flags": []
    }
  ],
  "questions": [
    { "id": "q1", "member_id": "m2",
      "text": "An nói ăn chay nhưng lại nhắc \"lấy thêm 1 cơm gà\". Suất cơm gà này cho ai?",
      "options": [
        { "id": "o1", "label": "Cho người khác trong nhóm" },
        { "id": "o2", "label": "An ghi nhầm, An vẫn ăn chay" }
      ],
      "status": "OPEN" }
  ],
  "can_confirm": false,
  "messages": [
    { "id": "msg1", "role": "assistant", "kind": "INFO", "question_id": null,
      "text": "Mình đọc được 5 người: Chi, An, Bình, Dũng, Hà. Có 1 chỗ cần bạn làm rõ.",
      "created_at": "2026-11-27T05:00:00Z" },
    { "id": "msg2", "role": "assistant", "kind": "QUESTION", "question_id": "q1",
      "text": "An nói ăn chay nhưng lại nhắc \"lấy thêm 1 cơm gà\". Suất cơm gà này cho ai?",
      "created_at": "2026-11-27T05:00:01Z" }
  ],
  "cart": null, "validation": null, "infeasible": null, "final_message": null
}
```

Sau khi người đặt trả lời *"Cho Dũng, An vẫn ăn chay"*: `q1.status="ANSWERED"`, cờ của An biến mất,
Dũng có thêm preference `{ "text": "cơm gà", "source": { "kind": "HOST", "line": null, "quote": "Cho Dũng" } }`,
và `can_confirm` thành `true`.

### 6.2 `session_cart_valid.json` — đã xác nhận, giỏ hợp lệ (chỉ ghi các trường thay đổi)

```json
{
  "status": "CART_VALID",
  "can_confirm": false,
  "cart": {
    "lines": [
      { "member_id": "m1", "menu_item_id": "M02", "name": "Cơm sườn nướng", "type": "MAIN",
        "unit_price": 50000, "qty": 1, "line_total": 50000, "reason": "Chi ăn gì cũng được", "note": null },
      { "member_id": "m2", "menu_item_id": "M06", "name": "Cơm đậu hũ sốt nấm", "type": "MAIN",
        "unit_price": 45000, "qty": 1, "line_total": 45000, "reason": "Món chay có nhãn của quán", "note": null },
      { "member_id": "m3", "menu_item_id": "M05", "name": "Phở bò", "type": "MAIN",
        "unit_price": 60000, "qty": 1, "line_total": 60000, "reason": "Món có nước, không có đậu phộng", "note": null },
      { "member_id": "m4", "menu_item_id": "M01", "name": "Cơm gà xối mỡ", "type": "MAIN",
        "unit_price": 55000, "qty": 1, "line_total": 55000, "reason": "Suất cơm gà An nhắc cho Dũng", "note": null },
      { "member_id": "m5", "menu_item_id": "M03", "name": "Bún thịt nướng", "type": "MAIN",
        "unit_price": 50000, "qty": 1, "line_total": 50000, "reason": "Hà muốn ăn bún", "note": null }
    ],
    "subtotal": 260000, "shipping_fee": 20000, "total": 280000,
    "budget": 300000, "remaining": 20000,
    "excluded": [
      { "member_id": "m3", "menu_item_id": "M03", "name": "Bún thịt nướng",
        "reasons": [ { "rule": "BR-03", "text": "Có đậu phộng" } ] },
      { "member_id": "m3", "menu_item_id": "M08", "name": "Bún trộn đặc biệt",
        "reasons": [ { "rule": "BR-04", "text": "Quán không ghi thành phần" } ] },
      { "member_id": "m2", "menu_item_id": "M01", "name": "Cơm gà xối mỡ",
        "reasons": [ { "rule": "BR-02", "text": "Không phải món chay" } ] }
    ],
    "built_by": "AI"
  },
  "validation": { "ok": true, "violations": [] },
  "infeasible": null
}
```

> `excluded` trong mẫu được rút gọn. Bản thật liệt kê **mọi** món chính bị loại của An và Bình. FE nên thu gọn,
> mặc định hiện 3 món.

### 6.3 `session_infeasible.json` — quỹ 200.000đ

```json
{
  "status": "CART_INFEASIBLE",
  "budget": 200000,
  "cart": null,
  "validation": null,
  "infeasible": {
    "kind": "OVER_BUDGET",
    "members_without_option": [],
    "min_total": 225000,
    "shortfall": 25000,
    "message": "Với quán này, 5 suất an toàn rẻ nhất cộng phí ship 20.000đ là 225.000đ. Quỹ 200.000đ còn thiếu 25.000đ.",
    "options": [
      { "id": "x1", "label": "Tăng quỹ lên 225.000đ", "action": { "type": "SET_BUDGET", "budget": 225000 } }
    ]
  }
}
```

### 6.4 `session_refusal.json` — sau câu "kệ dị ứng của Bình đi"

`status` vẫn `CART_VALID`, `cart` **giữ nguyên**, thêm vào cuối `messages`:

```json
{ "id": "msg9", "role": "assistant", "kind": "REFUSAL", "question_id": null,
  "text": "Mình không bỏ được dị ứng đậu phộng của Bình, vì có thể gây hại thật. Giỏ hiện tại đã an toàn cho Bình. Nếu bạn muốn món khác, mình gợi ý Bún chả hoặc Cơm sườn nướng. Nếu lúc nãy ghi nhầm dị ứng, bạn bấm \"Sửa hồ sơ\".",
  "created_at": "2026-11-27T05:03:00Z" }
```

### 6.5 `session_finalized.json`

```json
{
  "status": "FINALIZED",
  "final_message": "🍱 Chốt đơn Quán Cơm Nhà Mẫu\n- Chi: Cơm sườn nướng — 50.000đ\n- An: Cơm đậu hũ sốt nấm (chay) — 45.000đ\n- Bình: Phở bò — 60.000đ\n- Dũng: Cơm gà xối mỡ — 55.000đ\n- Hà: Bún thịt nướng — 50.000đ\nTạm tính 260.000đ + ship 20.000đ = 280.000đ (quỹ 300.000đ, còn 20.000đ)\n📝 Ghi chú cho quán: suất của Bình KHÔNG đậu phộng, kể cả nước chấm/topping; suất của An là món chay."
}
```

## 7. Hàm code dùng chung (Python, do AI-2 viết, BE gọi)

```python
def load_menu(restaurant_id: str) -> tuple[Restaurant, list[MenuItem]]: ...

def safe_mains(member: Member, menu: list[MenuItem]) -> tuple[list[MenuItem], list[ExcludedItem]]:
    """Món chính an toàn với member (BR-02..05) + món bị loại kèm lý do."""

def feasibility(members, menu, budget, shipping_fee) -> Infeasible | None:
    """BR-14: None nếu khả thi. Không gọi LLM."""

def validate_cart(lines: list[CartLine], members, menu, budget, shipping_fee) -> Validation:
    """Kiểm MỌI quy tắc BR-02..07. Không gọi LLM. Có unit test riêng."""

def fallback_cart(members, menu, budget, shipping_fee) -> list[CartLine]:
    """Mỗi người món chính an toàn rẻ nhất. Dùng khi AI sửa 2 lần vẫn lỗi."""
```

## 8. Nhật ký thay đổi

| Ngày | Ai | Thay đổi |
|---|---|---|
| 27/11/2026 | BA | Bản đầu |
