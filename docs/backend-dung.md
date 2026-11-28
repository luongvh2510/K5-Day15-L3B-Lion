# Backend D2 — việc của Dũng

> Viết ngày 27/11 cho nhánh `ai-agent` (commit `f9b9e90`). Đọc kèm: `spec.md` §4 (thiết kế 2 phase), `docs/ba/04-hop-dong-du-lieu-API.md` (kiểu dữ liệu, endpoint, mã lỗi), `docs/ba/01-nghiep-vu-va-quy-tac.md` (BR-xx).
> File này dùng được để dán cho agent của Dũng. Mục 8 là danh sách việc theo thứ tự.

## 1. Ranh giới: ai sở hữu gì

| Phần | Người | File |
|---|---|---|
| Agent AI: các bước LLM, prompt, luồng 2 phase | Lương | `codebase/llm_steps.py`, `prompts/*.md`, `codebase/core.py`, `codebase/agent.py`, `codebase/ai.py` |
| Công cụ kiểm cứng (không gọi LLM) | **Dũng** | `codebase/tools.py` |
| API, lưu phiên/DB, phục vụ frontend | **Dũng** | `server/` (mới), `codebase/store.py` (mới) |
| Giao diện | Tú | (thư mục FE của Tú) |

Quy tắc:
- **Backend không viết lại luồng.** Mọi quyết định "phiên đi tiếp thế nào" nằm trong `core.py`. API chỉ nhận request → gọi đúng hàm của `core.py` → lưu phiên → trả JSON.
- **Không gọi LLM từ backend**, không viết prompt, không đoán ý người dùng bằng regex.
- **Frontend không gọi model, không tự kiểm giỏ.** Mọi thứ đi qua API (API key chỉ nằm phía server, trong `.env`).
- Cần đổi chữ ký hàm của `core.py` thì nhắn Lương; cần đổi `docs/ba/01` hoặc `04` thì nhắn Cường.

```
FE (Tú) ──HTTP──► server/ (Dũng) ──► core.py (Lương) ──► llm_steps.py → ai.py → model
                        │                    └──────────► tools.py (Dũng)
                        └── store.py (Dũng): lưu / đọc Session
```

## 2. Việc cần làm ngay: review `tools.py`

Lương đã sửa `codebase/tools.py` trên nhánh `ai-agent` (chưa hỏi trước — Dũng xem và quyết giữ hay sửa). Có test trong `tests/test_tools.py`. Thay đổi:

- **Món chay suy ra từ thành phần** (data không có trường chay). Chay = không có nguyên liệu nhóm `meat`, `seafood`, `egg`, `dairy`, và không có 6 gia vị động vật `fish_sauce`, `shrimp_paste`, `shrimp_paste_hue`, `fermented_gourami`, `fermented_snakehead`, `oyster_sauce`. Không trứng sữa là quyết định của nhóm 27/11. Kết quả: chỉ 4/100 món chay (`dish_077`, `dish_078`, `dish_080` ở store_08; `dish_090` ở store_09).
- `list_restaurants()` giờ trả **danh sách** `[{id, name, menu_type, summary, distance_km}]` (trước là dict `{id: name}`).
- `load_menu(store_id)` trả thêm `ingredients`, `allergen_sources` (tag → tên nguyên liệu), `animal_ingredients`, `vegetarian`.
- `dish_exclusion(member, item)` thay `exclusion`: lý do ghi theo nguyên liệu, vd `"dị ứng đậu phộng: có Đậu phộng rang"`, `"không chay: có Nước mắm cá cơm và muối, ..."`.
- Mới: `shipping_fee(store_id)` (theo `distance_km`: 15.000đ cho 2 km đầu, mỗi km tiếp theo (làm tròn lên) +5.000đ), `store_summary(store_id, members, budget, shipping)` → `{id, name, safe_counts, min_total}`.
- `safe_mains`, `feasibility`, `validate_cart` giữ chữ ký cũ.

Nếu Dũng đổi tên hay kiểu trả về của các hàm trên, phải sửa `core.py` cùng lúc và chạy lại test (mục 7).

## 3. Hàm của `core.py` mà backend gọi

Phiên là một dict `Session` (lưu được nguyên văn bằng `json.dumps`):

```python
Session = {
  "id": str,                       # 8 ký tự hex
  "status": "PROFILE_DRAFT" | "CART_VALID" | "CART_INFEASIBLE" | "FINALIZED",
  "profile": {
    "budget": int | None,          # quỹ chung, đồng
    "members": [{"name": str, "vegetarian": bool, "allergens": {tag: nhãn},
                 "preferences": [str], "quotes": [str]}],
    "questions": [{"id": "q1", "member": str | None, "text": str, "status": "OPEN" | "ANSWERED"}]
  },
  "locked": bool,                  # True sau khi xác nhận (BR-12)
  "shipping": int | None,          # None = dùng tools.shipping_fee
  "candidates": [store_id] | None, # None = mọi quán
  "store_id": str | None,          # quán agent đã chọn
  "tried": [store_id],             # quán đã đổi khỏi
  "cart": None | {"lines": [{"member", "item_id", "name", "price", "reason"}],
                  "subtotal", "shipping", "total", "budget", "remaining",
                  "excluded": {tên: {item_id: lý do}}, "built_by": "AI" | "FALLBACK"},
  "infeasible": None | {"kind": "NO_SAFE_ITEM" | "OVER_BUDGET", "members": [tên],
                        "min_total": int | None, "shortfall": int | None},
  "messages": [{"role": "user" | "assistant", "kind": "TEXT" | "QUESTION" | "REFUSAL" | "INFO", "text": str}]
}
```

| Hàm | Khi nào | Ghi chú |
|---|---|---|
| `core.start(chat_text)` | Người dùng dán chat | Gọi LLM (5–20 giây). **Người dùng chỉ dán chat**: không chọn quán, không nhập quỹ (quỹ đọc từ chat, thiếu thì có câu hỏi). Tham số `shipping`, `candidates`, `budget` chỉ dùng cho eval, API không truyền |
| `core.send(session, text)` | Mỗi tin nhắn của người dùng | `PROFILE_DRAFT`: trả lời câu hỏi / bổ sung hồ sơ. Các trạng thái giỏ: đổi món, thêm dị ứng, đổi quỹ, đổi quán, từ chối phá rào |
| `core.confirm(session)` | Bấm "Xác nhận hồ sơ" | Chỉ chạy khi `can_confirm(session["profile"])` (có người, có quỹ, hết câu hỏi mở); không đủ thì thêm message `QUESTION` và giữ `PROFILE_DRAFT` |
| `core.finalize(session)` | Bấm "Chốt giỏ" | Chỉ khi `CART_VALID` → `FINALIZED` |
| `core.render(session)` | Cần câu chữ tổng hợp (vd tin nhắn chốt để copy) | Trả chuỗi; FE nên tự render từ các trường có cấu trúc |
| `core.can_confirm(profile)` | Bật/tắt nút xác nhận | |
| `core.open_questions(profile)` | Hiện câu hỏi | |

Các hàm **sửa trực tiếp** dict phiên được truyền vào và trả lại chính nó. Backend: đọc phiên từ DB → gọi hàm → ghi lại phiên.

Lỗi: `llm_steps.AIUnavailable` khi model lỗi sau khi đã thử lại → trả `502 AI_UNAVAILABLE` (theo `docs/ba/04` §4), không đổi phiên đã lưu.

## 4. API cần dựng

Gốc `/api`. Lỗi dạng `{"error": {"code": "...", "message": "câu tiếng Việt"}}`. Bảng dưới là bản đã chỉnh từ `docs/ba/04` §4 theo thiết kế mới (người dùng không chọn quán, không nhập quỹ).

| Method | Path | Body | Gọi | Trả |
|---|---|---|---|---|
| POST | `/sessions` | `{chat_text}` | `core.start(chat_text)` | `SessionState` |
| GET | `/sessions/{id}` | — | đọc DB | `SessionState` |
| POST | `/sessions/{id}/messages` | `{text}` | `core.send(s, text)` | `SessionState` |
| POST | `/sessions/{id}/confirm` | — | `core.confirm(s)` | `SessionState` |
| POST | `/sessions/{id}/finalize` | — | `core.finalize(s)` | `SessionState` (+ `final_message` = `core.render(s)`) |
| GET | `/restaurants` | — | `tools.list_restaurants()` | danh sách quán |
| GET | `/restaurants/{id}/menu` | — | `tools.load_menu(id)` | menu |
| POST | `/debug/validate-cart` | `{members, selected, store_id, budget, shipping}` | `tools.validate_cart(...)` | danh sách lỗi |

Mã lỗi: `400 INVALID_INPUT` (chat rỗng hoặc quá 4.000 ký tự) · `404 NOT_FOUND` · `409 INVALID_STATE` (vd `confirm` khi không ở `PROFILE_DRAFT`) · `502 AI_UNAVAILABLE`.

**Chưa có trong `core.py` — cần Lương thêm trước khi làm endpoint tương ứng** (đừng tự viết logic trong API):
- `POST /sessions/{id}/reopen` (nút "Sửa hồ sơ", BR-12: huỷ giỏ, mở khoá, về `PROFILE_DRAFT`) → cần `core.reopen(session)`.
- `PATCH /sessions/{id}/members` (FE sửa hồ sơ nháp bằng form) → cần `core.edit_profile(session, members)`, chặn xoá ràng buộc đã khoá (`409 HARD_CONSTRAINT_LOCKED`).
- `POST /sessions/{id}/actions` (bấm nút "Tăng quỹ lên X" / "Đổi quán") → cần `core.set_budget(session, amount)` và `core.change_restaurant(session)`. Tạm thời FE có thể gửi tin nhắn chữ qua `/messages`.

## 5. Ánh xạ `Session` → `SessionState` cho frontend

FE của Tú render theo `SessionState` trong `docs/ba/04` §2.5 (có JSON mẫu ở §6 để làm mock). Backend chuyển như sau:

| `SessionState` | Lấy từ `Session` |
|---|---|
| `session_id`, `status` | `id`, `status` |
| `restaurant` | `tools.list_restaurants()` tìm theo `store_id` (+ `shipping_fee`) ; `null` khi chưa chọn |
| `budget` | `profile.budget` |
| `members[]` | `profile.members[]`: `vegetarian` → ràng buộc `VEGETARIAN`; mỗi `allergens{tag: nhãn}` → ràng buộc `ALLERGY` (tag viết hoa); `locked` = `session.locked`; `quotes` → `source.quote` |
| `questions[]` | `profile.questions[]` |
| `can_confirm` | `status == "PROFILE_DRAFT" and core.can_confirm(profile)` |
| `messages[]` | `messages[]` (thêm `id`, `created_at` khi lưu) |
| `cart` | `cart` (`lines[].member` là tên; nếu FE cần `member_id` thì backend sinh id ổn định theo thứ tự thành viên) |
| `validation` | `{"ok": status == "CART_VALID", "violations": []}` — giỏ chỉ được lưu khi đã qua `validate_cart` |
| `infeasible` | `infeasible`; thêm `options` cho nút: `OVER_BUDGET` → "Tăng quỹ lên `min_total`" + "Đổi quán"; `NO_SAFE_ITEM` → "Đổi quán" |
| `final_message` | `core.render(s)` khi `FINALIZED` |

Tag dị ứng trong data là chữ thường (`peanut`, `fish`, `crustacean`, `mollusc`, `egg`, `milk`, `wheat`, `soy`, `sesame`, `celery`). `docs/ba/04` dùng chữ hoa và có `SHELLFISH`, `TREE_NUT` — **khác data**, cần thống nhất với Cường trước khi FE hiển thị.

## 6. Lưu phiên

- Hiện `core.SESSIONS` là dict trong bộ nhớ (mất khi tắt server). Dựng `codebase/store.py` với `save(session)`, `load(session_id) -> Session`, rồi để API dùng store thay vì `core.SESSIONS`.
- POC: SQLite (`sqlite3` có sẵn trong Python) với bảng `sessions(id TEXT PRIMARY KEY, data TEXT, updated_at TEXT)`, `data` là `json.dumps(session, ensure_ascii=False)`. Không cần ORM.
- Không lưu dữ liệu cá nhân thật vào repo; file DB để ngoài git (thêm vào `.gitignore`).
- Một phiên chỉ được xử lý một request tại một thời điểm (khoá theo `session_id`), vì `core` sửa dict tại chỗ.

## 7. Chạy và kiểm

- Framework gợi ý: FastAPI + uvicorn (theo `docs/ba/04`). Thêm vào `requirements.txt` và ghi lệnh cài vào `README.md`. Khung còn lại vẫn chỉ dùng thư viện chuẩn.
- **`python run.py` phải là lệnh duy nhất chạy sản phẩm.** `run.py` là file khung không được sửa, nó chạy `codebase/app.py`. Khi có server, sửa `codebase/app.py` để có cách mở server (vd `python run.py` hỏi chọn CLI hay web) — báo Lương vì `app.py` hiện là CLI demo của Lương.
- Test hiện có: `python -X utf8 -m unittest discover -s tests` (46 test, phải luôn xanh). Thêm test API ở `tests/test_api.py` (dùng `fastapi.testclient`), patch `core.llm_steps.*` để không gọi model thật — xem cách làm trong `tests/test_core.py`.
- `python run.py eval` gọi thẳng `agent.answer()` → `core`, không qua API, nên backend hỏng không làm hỏng lượt chấm.
- Không commit `.env`, API key.

## 8. Thứ tự việc

| # | Việc | Xong khi |
|---|---|---|
| 1 | Review `tools.py` (mục 2), giữ hoặc sửa, chạy test | 46 test xanh; Dũng nhắn Lương kết quả |
| 2 | Mock API cho Tú: `POST /sessions`, `/messages`, `/confirm`, `/finalize`, `GET /sessions/{id}` trả JSON mẫu `docs/ba/04` §6 | Tú gọi được từ FE |
| 3 | `store.py` (SQLite) + nối API vào `core.start/send/confirm/finalize` + ánh xạ mục 5 | Dán chat thật qua API ra hồ sơ/câu hỏi; xác nhận ra giỏ (cần model thật trong `.env`) |
| 4 | Lỗi và trạng thái: 400/404/409/502 | Có test cho từng mã |
| 5 | Sau khi Lương thêm hàm (mục 4): `/reopen`, `PATCH /members`, `/actions` | FE bấm được "Sửa hồ sơ", "Tăng quỹ", "Đổi quán" |
| 6 | Cách mở server qua `python run.py` (phối hợp Lương) | Một lệnh chạy được cả sản phẩm cho video demo |
