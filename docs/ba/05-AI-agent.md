# 05 · AI agent

> Cho 2 người làm AI. Đọc trước [01](01-nghiep-vu-va-quy-tac.md) (quy tắc) và [04](04-hop-dong-du-lieu-API.md) (schema).

## 1. Nguyên tắc phân vai

> **AI đọc hiểu, chọn và giải thích. Code lọc, tính tiền, kiểm và chặn.**
> Câu hỏi "giỏ này có an toàn không" và "có đủ tiền không" **không bao giờ** do LLM trả lời.

| Việc | AI | Code | Ghi chú |
|---|:---:|:---:|---|
| Tách đoạn chat thành dòng `ChatLine` | | ✅ | Regex `Tên: …` hoặc `[Tên] …`. Dòng không tách được thì `speaker=null` |
| Rút thành viên, ràng buộc, sở thích kèm câu gốc | ✅ | | AI-1 |
| Kiểm câu gốc có thật trong chat | | ✅ | `quote` phải là chuỗi con của dòng `line`. Sai thì bỏ ràng buộc đó và gắn cờ AMBIGUOUS |
| Phát hiện mâu thuẫn, mơ hồ và viết câu hỏi | ✅ | | AI-1 |
| Cập nhật hồ sơ theo câu trả lời | ✅ | ✅ | AI đề xuất thay đổi, code áp và kiểm khoá (BR-12) |
| Lọc món an toàn từng người | | ✅ | `safe_mains` |
| Xác định bất khả thi, số tiền thiếu | | ✅ | `feasibility` (BR-14) |
| Chọn món theo sở thích **trong danh sách đã lọc** | ✅ | | AI-2 |
| Kiểm giỏ | | ✅ | `validate_cart` |
| Sửa giỏ khi có vi phạm | ✅ | | Tối đa 2 lần, sau đó `fallback_cart` |
| Hiểu ý người đặt trong hội thoại | ✅ | | AI-2 (router) |
| Từ chối phá rào | ✅ | ✅ | AI viết lời từ chối. **Code chặn độc lập** |
| Viết câu báo bất khả thi, tin nhắn chốt | ✅ | ✅ | Số liệu do code đưa vào, AI chỉ diễn đạt. Dòng ghi chú cho quán do code chèn (BR-19) |

## 2. Chia việc 2 người AI

| | **AI-1: Hiểu đoạn chat** | **AI-2: Giỏ hàng + hội thoại** |
|---|---|---|
| Phần làm | Trích hồ sơ (UC-02), câu hỏi làm rõ (UC-03), cập nhật hồ sơ khi người đặt trả lời | Hàm code ở mục 7 của file 04, chọn món (UC-05), router hội thoại (UC-07, UC-08), lời báo bất khả thi, tin nhắn chốt |
| Prompt | `prompts/extract_profile.md`, `prompts/apply_answer.md` | `prompts/pick_items.md`, `prompts/route_message.md`, `prompts/write_message.md` |
| Ca thử chính | TC-01, TC-02, TC-11, TC-13 → TC-16 | TC-03 → TC-10, TC-12, TC-17, TC-18 |
| Bàn giao | Hàm `extract_profile(chat_lines) -> ExtractResult` | Hàm `build_cart(...)`, `handle_message(...)` |

Hai người chạy độc lập được ngay: AI-1 test trên đoạn chat ở file 06, AI-2 test bằng hồ sơ đã xác nhận viết tay
(file 06, cột "Hồ sơ đáp án").

## 3. Luồng xử lý

```
POST /sessions
  parse_chat (code) ──► extract_profile (LLM, AI-1) ──► verify_quotes (code)
                                                   └──► SessionState PROFILE_DRAFT (+ questions)

POST /messages ở PROFILE_DRAFT
  có question_id? ─► apply_answer (LLM, AI-1) ─► profile_diff ─► áp vào hồ sơ (code)

POST /confirm
  lock_constraints (code)
  feasibility (code) ── bất khả thi ──► write_message(infeasible) ──► CART_INFEASIBLE
        │ khả thi
        ▼
  safe = safe_mains(m) cho từng người (code)
  pick_items(members, safe, budget) (LLM, AI-2)
  validate_cart (code) ── lỗi ──► pick_items + danh sách lỗi (tối đa 2 lần) ── vẫn lỗi ──► fallback_cart
        │ ok
        ▼
  CART_VALID

POST /messages ở CART_VALID / CART_INFEASIBLE
  route_message (LLM, AI-2) ──► intent
     CHANGE_ITEM / ADD_ITEM   ─► pick_items có ràng buộc mới ─► validate_cart ─► ok: giỏ mới | lỗi: giữ giỏ cũ + giải thích
     ADD_HARD_CONSTRAINT      ─► thêm vào hồ sơ (khoá luôn) ─► lập lại giỏ
     REMOVE_HARD_CONSTRAINT   ─► TỪ CHỐI (REFUSAL), hồ sơ không đổi
     CHANGE_BUDGET            ─► SET_BUDGET ─► lập lại giỏ
     OTHER                    ─► trả lời ngắn, không đổi gì
```

Có thể dựng bằng LangGraph (như template) hoặc hàm Python tuần tự. Với POC 1 ngày, **hàm tuần tự là đủ**.
Mỗi bước LLM là một lần gọi trả về JSON có cấu trúc (structured output).

## 4. Đầu ra LLM (schema nhỏ, code chuyển sang schema API)

### 4.1 `extract_profile` (AI-1)
```json
{
  "members": [
    { "name": "An",
      "hard_constraints": [ { "type": "VEGETARIAN", "allergen": null, "note": null, "line": 2, "quote": "t ăn chay nha" } ],
      "preferences": [] }
  ],
  "issues": [
    { "type": "CONFLICT", "member": "An", "lines": [2, 5],
      "message": "Nói ăn chay nhưng nhắc \"lấy thêm 1 cơm gà\"",
      "question": "An nói ăn chay nhưng lại nhắc \"lấy thêm 1 cơm gà\". Suất cơm gà này cho ai?",
      "options": ["Cho người khác trong nhóm", "An ghi nhầm, An vẫn ăn chay"] }
  ]
}
```

Prompt phải dặn rõ:
- **Ràng buộc cứng chỉ có 2 loại** (BR-01). "Không cay", "ít dầu", "kiêng đồ chiên" là sở thích. Nếu người nói dùng
  từ mạnh ("tuyệt đối không", "bị bệnh") mà không thuộc 2 loại trên thì tạo issue `AMBIGUOUS` để hỏi.
- `quote` phải **chép nguyên văn** từ chat, không diễn đạt lại.
- **Không đoán.** Không rõ ai nói, không rõ chất, không rõ là cho ai → tạo issue, không tạo ràng buộc.
- "Gì cũng được", "sao cũng được" → không tạo gì.
- Người chỉ được nhắc tên ("đặt thêm cho Hà nữa") cũng là thành viên.
- Lời dặn nói thay người khác ("Bình dị ứng tôm đó") → gán cho người được nhắc, `quote` là câu đó.
- Prompt **không chép ví dụ từ bộ ca thử** (tránh học thuộc). Ví dụ trong prompt dùng tên và món khác.

### 4.2 `apply_answer` (AI-1)
Đầu vào: câu hỏi, câu trả lời, hồ sơ hiện tại. Đầu ra là **danh sách thay đổi**, không phải hồ sơ mới:
```json
{ "changes": [
    { "op": "ADD_PREFERENCE", "member": "Dũng", "text": "cơm gà" },
    { "op": "RESOLVE_ISSUE", "question_id": "q1" }
  ],
  "reply": "Đã ghi: cơm gà cho Dũng, An vẫn ăn chay." }
```
Phép được phép dùng: `ADD_MEMBER`, `ADD_HARD`, `REMOVE_HARD`, `ADD_PREFERENCE`, `REMOVE_PREFERENCE`, `RESOLVE_ISSUE`.
`REMOVE_HARD` **chỉ được nhận** ở `PROFILE_DRAFT` (chưa khoá).

### 4.3 `pick_items` (AI-2)
Đầu vào: mỗi người kèm sở thích và **danh sách món chính an toàn có giá**, quỹ, phí ship, các lỗi của lần trước (nếu có).
```json
{ "picks": [ { "member": "Bình", "menu_item_id": "M05", "reason": "Món có nước, không có đậu phộng" } ] }
```
Prompt dặn: **chỉ chọn id có trong danh sách của người đó**. Không tự viết giá. Câu `reason` ≤ 12 từ.

### 4.4 `route_message` (AI-2)
```json
{ "intent": "REMOVE_HARD_CONSTRAINT", "member": "Bình", "detail": "bỏ dị ứng đậu phộng" }
```
Intent: `CHANGE_ITEM`, `ADD_ITEM`, `ADD_HARD_CONSTRAINT`, `REMOVE_HARD_CONSTRAINT`, `CHANGE_BUDGET`, `OTHER`.
Câu "đặt bún thịt nướng cho Bình" là `CHANGE_ITEM`. Code thấy món không an toàn thì sẽ từ chối (BR-03),
nên router **không cần** tự đoán việc này có phá rào hay không.

## 5. Phòng thủ 2 lớp cho ràng buộc cứng (BR-12)

Lớp 1 là AI nhận ra và từ chối. Lớp 2 là code, **không phụ thuộc AI**:

1. Sau khi xác nhận, mọi thay đổi hồ sơ đi qua `apply_profile_changes()`. Hàm này **bỏ mọi phép `REMOVE_HARD`**
   với ràng buộc `locked=true` và ghi log.
2. Mọi giỏ đi qua `validate_cart` trước khi trả FE. Món vi phạm thì không bao giờ tới được UI với nhãn hợp lệ.
3. API `PATCH /members` trả `409 HARD_CONSTRAINT_LOCKED` nếu danh sách mới thiếu ràng buộc đã khoá.

→ Dù LLM bị "thuyết phục" bởi câu "kệ dị ứng đi", kết quả cuối vẫn an toàn.

## 6. Xử lý lỗi LLM

| Lỗi | Xử lý |
|---|---|
| JSON sai schema | Thử lại 1 lần với thông báo lỗi schema. Vẫn sai: `extract` → 502 `AI_UNAVAILABLE`; `pick_items` → `fallback_cart` |
| `pick_items` chọn id ngoài danh sách | Coi là vi phạm và đưa vào vòng sửa |
| Quá thời gian (> 20 giây) | Như JSON sai |
| `quote` không có trong chat | Bỏ ràng buộc đó, gắn issue `AMBIGUOUS` "Mình không chắc về lời dặn của X" |

## 7. Chấm AI (chi tiết ca thử ở file 06)

| Chỉ số | Cách tính | Ai chạy |
|---|---|---|
| Recall ràng buộc cứng | Số ràng buộc đáp án tìm được / tổng số ràng buộc đáp án (khớp người + loại + chất) | AI-1 |
| Precision ràng buộc cứng | Số đúng / tổng số AI tạo ra | AI-1 |
| Phát hiện issue | Số ca có cài mâu thuẫn hoặc mơ hồ mà AI tạo issue đúng người | AI-1 |
| Hỏi thừa | Số issue AI tạo ở ca không có gì để hỏi | AI-1 |
| Giỏ vi phạm lọt ra UI | Phải = 0 (code chấm) | AI-2 |
| Tỷ lệ phải dùng fallback | Càng thấp càng tốt | AI-2 |
| Từ chối đúng | Ca phá rào (TC-09, TC-10) có REFUSAL và hồ sơ không đổi | AI-2 |
| Số lần gọi LLM và chi phí mỗi phiên | Đếm trong log | Cả hai |

> Ước tính số lần gọi LLM trước khi chạy cả bộ: khoảng 18 ca × 2–4 lần gọi mỗi ca ≈ **55 lần gọi**.
> Sau khi sửa lỗi, **chỉ chạy lại các ca hỏng**.
