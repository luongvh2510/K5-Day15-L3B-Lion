# 02 · Use case và user story

> Use case (`UC`) mô tả **luồng**. User story (`US`) mô tả **một mẩu giá trị** kèm tiêu chí chấp nhận (`AC`).
> Tiêu chí viết theo dạng **Given / When / Then** (Cho trước / Khi / Thì), test viết thẳng từ đó được.

## 1. Luồng tổng (happy path + nhánh chính)

```
[UC-01 Nhập chat + quỹ]
        │
        ▼
[UC-02 AI trích hồ sơ nhóm] ──có mâu thuẫn/mơ hồ──► [UC-03 Hỏi lại] ──trả lời──┐
        │                                                                     │
        ▼◄────────────────────────────────────────────────────────────────────┘
[UC-04 Người đặt rà, sửa, XÁC NHẬN hồ sơ]   (khoá nút nếu còn câu hỏi — BR-10)
        │
        ▼
[UC-05 Lập giỏ + code kiểm giỏ]
        ├── hợp lệ ─────────────► [UC-07 Sửa giỏ qua hội thoại] (lặp) ──► [UC-09 Chốt + copy tin nhắn]
        └── bất khả thi ────────► [UC-06 Báo thiếu + đề xuất nới] ──người đặt chọn──► quay lại UC-05

Bất kỳ lúc nào sau xác nhận: yêu cầu bỏ ràng buộc cứng ──► [UC-08 Từ chối phá rào]
```

## 2. Use case

### UC-01 · Nhập đoạn chat và quỹ `[MUST]`
- **Tác nhân:** Người đặt hộ
- **Tiền điều kiện:** Có ít nhất 1 quán mẫu.
- **Luồng chính:**
  1. Người đặt dán đoạn chat vào ô nhập, hoặc bấm "Nạp chat mẫu".
  2. Nhập quỹ (đồng). Quán mẫu được chọn sẵn.
  3. Bấm "Phân tích".
- **Ngoại lệ:**
  - Chat rỗng hoặc quá dài (> 4.000 ký tự) → báo lỗi, không gọi AI.
  - Quỹ ≤ 0 hoặc không phải số → báo lỗi.
- **Kết quả:** Một phiên làm việc mới được tạo. Chuyển sang UC-02.

### UC-02 · AI trích hồ sơ nhóm `[MUST]`
- **Tác nhân:** Hệ thống (AI)
- **Luồng chính:**
  1. AI đọc chat và liệt kê thành viên. Mỗi người có ràng buộc cứng (BR-01) và sở thích, kèm câu gốc (BR-13).
  2. AI gắn cờ cho mỗi mâu thuẫn (BR-09) và mỗi chỗ mơ hồ (BR-10), rồi sinh câu hỏi tương ứng.
  3. Hệ thống hiện hồ sơ nháp và câu hỏi (nếu có).
- **Ngoại lệ:** AI lỗi hoặc trả sai định dạng → thử lại 1 lần. Vẫn lỗi thì báo "Không đọc được đoạn chat, vui lòng
  nhập tay" và cho người đặt tự thêm thành viên.

### UC-03 · Làm rõ mâu thuẫn hoặc mơ hồ `[MUST]`
- **Tác nhân:** Người đặt hộ, AI
- **Luồng chính:**
  1. AI hỏi **một câu một lần**, có nút gợi ý trả lời nếu được.
  2. Người đặt bấm nút hoặc gõ câu trả lời.
  3. AI cập nhật hồ sơ, rồi chuyển sang câu tiếp theo hoặc báo "Đã rõ, mời xác nhận".
- **Ví dụ:** "An ăn chay nhưng nhắc 'thêm 1 cơm gà'. Suất cơm gà này cho ai?" →
  `[Cho người khác]` `[An ghi nhầm, An vẫn ăn chay]`

### UC-04 · Rà, sửa và xác nhận hồ sơ `[MUST]`
- **Tác nhân:** Người đặt hộ
- **Luồng chính:**
  1. Người đặt xem từng thẻ thành viên. Bấm vào ràng buộc thì thấy câu gốc.
  2. Sửa nếu cần: thêm hoặc xoá thành viên, thêm hoặc xoá ràng buộc và sở thích.
  3. Bấm "Xác nhận hồ sơ". Ràng buộc cứng chuyển sang trạng thái khoá 🔒 (BR-12).
- **Điều kiện:** Nút xác nhận bị khoá khi còn câu hỏi chưa trả lời, hoặc khi chưa có thành viên nào.

### UC-05 · Lập giỏ và kiểm giỏ `[MUST]`
- **Tác nhân:** Hệ thống (code + AI)
- **Luồng chính:**
  1. Code lọc **món chính an toàn** cho từng người (BR-02 → BR-05).
  2. Code tính chi phí tối thiểu. Nếu bất khả thi thì sang UC-06 (BR-14).
  3. AI chọn món cho từng người trong danh sách an toàn, theo sở thích (BR-08), kèm lý do ngắn.
  4. Code chạy `validate_cart`. Nếu có vi phạm, AI nhận lỗi và sửa (tối đa 2 lần). Vẫn lỗi thì code tự chọn món
     rẻ nhất an toàn cho từng người (giỏ dự phòng).
  5. Hiện giỏ hợp lệ (BR-17, BR-18).

### UC-06 · Báo bất khả thi và đề xuất nới `[MUST]`
- **Tác nhân:** Hệ thống, Người đặt hộ
- **Luồng chính:**
  1. Hiện nguyên nhân. (a) "Quán không có món chính nào phù hợp với Bình". (b) "Ít nhất cần 225.000đ, quỹ 200.000đ, thiếu 25.000đ".
  2. Đề xuất (BR-15): tăng quỹ lên đúng mức tối thiểu, hoặc `[COULD]` đổi quán.
  3. Người đặt chọn một đề xuất hoặc tự nhập quỹ mới → quay lại UC-05.
- **Cấm:** đề xuất bỏ dị ứng hoặc bỏ ăn chay. Hiện giỏ có nhãn hợp lệ.

### UC-07 · Sửa giỏ qua hội thoại `[SHOULD]`
- **Tác nhân:** Người đặt hộ, AI
- **Ví dụ:** "Đổi món của Chi sang phở", "thêm 2 trà tắc", "Dũng không ăn cay".
- **Luồng chính:** AI hiểu ý → đổi giỏ → code kiểm lại → hiện giỏ mới. Nếu yêu cầu làm giỏ không hợp lệ
  (vượt quỹ, món không an toàn) thì AI giải thích và giữ giỏ cũ.
- Thêm ràng buộc cứng mới ("à Chi cũng dị ứng tôm") → **được phép** (khoá một chiều chỉ cấm bớt) → lập lại giỏ.

### UC-08 · Từ chối yêu cầu phá rào an toàn `[MUST]`
- **Tác nhân:** Người đặt hộ, AI, code
- **Kích hoạt:** Sau khi xác nhận hồ sơ, người đặt yêu cầu bỏ hoặc phớt lờ một ràng buộc cứng. Ví dụ "kệ dị ứng đi",
  "cho An ăn gà luôn", "đặt đại bún thịt nướng cho Bình".
- **Luồng chính:** AI từ chối ngắn gọn, nêu lý do và đưa phương án an toàn thay thế. Hồ sơ không đổi.
  Nếu thật sự nhập nhầm, AI hướng dẫn bấm "Sửa hồ sơ" (BR-12).
- **Lưu ý:** Dù AI có hiểu sai và trả về hồ sơ đã bớt ràng buộc, **code vẫn chặn** (phòng thủ 2 lớp).

### UC-09 · Chốt và copy tin nhắn gửi nhóm `[MUST]`
- **Tác nhân:** Người đặt hộ
- **Luồng chính:** Bấm "Chốt giỏ" → hiện tin nhắn tóm tắt (BR-19) → bấm "Copy".

### UC-10 · Đổi sang quán khác `[COULD]`
- Chỉ làm nếu còn giờ. Hồ sơ giữ nguyên, lập lại giỏ trên menu quán 2.

## 3. User story và tiêu chí chấp nhận

> Định dạng: **Là** [vai], **tôi muốn** [việc], **để** [giá trị].

### US-01 · Dán chat thay vì tự gõ từng người `[MUST]` · UC-01, UC-02
**Là** người đặt hộ, **tôi muốn** dán nguyên đoạn chat nhóm, **để** không phải tự đọc lại và điền form cho từng người.
- **AC1** — Cho trước đoạn chat mẫu 5 người, khi bấm "Phân tích", thì hồ sơ hiện đủ 5 thành viên trong ≤ 15 giây.
- **AC2** — Cho trước chat rỗng, khi bấm "Phân tích", thì hiện lỗi "Chưa có nội dung chat" và không gọi API.
- **AC3** — Cho trước quỹ "abc" hoặc 0, khi bấm "Phân tích", thì hiện lỗi ở ô quỹ.

### US-02 · Thấy ai ăn được gì, kèm căn cứ `[MUST]` · UC-02, BR-13
**Là** người đặt hộ, **tôi muốn** thấy ràng buộc của từng người kèm câu chat gốc, **để** tự kiểm tra AI có hiểu đúng không.
- **AC1** — Mỗi ràng buộc và sở thích có nút hoặc tooltip hiện câu gốc.
- **AC2** — Ràng buộc cứng (chay, dị ứng) hiển thị khác sở thích (màu, icon) để nhìn là phân biệt được.
- **AC3** — Ràng buộc do người đặt thêm tay có nguồn "Người đặt thêm".

### US-03 · Được hỏi lại khi lời dặn mâu thuẫn `[MUST]` · UC-03, BR-09
**Là** người đặt hộ, **tôi muốn** hệ thống hỏi lại khi một người vừa nói ăn chay vừa nhắc món mặn, **để** không đặt nhầm.
- **AC1** — Cho trước "An: t ăn chay" và "An: lấy thêm 1 cơm gà", thì thẻ An có cờ ⚠ và có câu hỏi làm rõ.
- **AC2** — Khi chưa trả lời, nút "Xác nhận hồ sơ" bị khoá.
- **AC3** — Khi trả lời "Cho Dũng", thì cơm gà thành sở thích của Dũng, An vẫn giữ ràng buộc chay.
- **AC4** — Trong mọi trường hợp, giỏ không bao giờ gán món không chay cho An khi An còn ràng buộc chay.

### US-04 · Được hỏi lại khi lời dặn mơ hồ `[MUST]` · UC-03, BR-10
**Là** người đặt hộ, **tôi muốn** hệ thống hỏi khi không rõ lời dặn thuộc ai hoặc dị ứng gì, **để** không bị đoán sai.
- **AC1** — "Dị ứng hải sản" → hỏi có gồm cá không.
- **AC2** — Câu "ai đó dị ứng tôm á" không rõ người nói → hỏi là ai.
- **AC3** — Câu "gì cũng được" → **không** tạo ràng buộc, **không** hỏi lại.

### US-05 · Sửa và xác nhận hồ sơ `[MUST]` · UC-04, BR-11
**Là** người đặt hộ, **tôi muốn** sửa hồ sơ trước khi lập giỏ, **để** sửa chỗ AI hiểu sai.
- **AC1** — Thêm hoặc xoá được thành viên. Thêm hoặc xoá được ràng buộc và sở thích.
- **AC2** — Sau khi bấm "Xác nhận hồ sơ", ràng buộc cứng hiện 🔒.
- **AC3** — Có thể tick "Tính cả tôi" để thêm người đặt làm thành viên.

### US-06 · Nhận giỏ an toàn, rõ món nào cho ai `[MUST]` · UC-05, BR-02→08, BR-17, BR-18
**Là** người đặt hộ, **tôi muốn** nhận giỏ ghi rõ món cho từng người và tổng tiền đã gồm ship, **để** đặt ngay không cần tính lại.
- **AC1** — Mỗi thành viên có đúng 1 món chính, kèm tên người.
- **AC2** — Có dòng tạm tính, phí ship, tổng, quỹ còn lại. Tổng ≤ quỹ.
- **AC3** — Với mỗi người có ràng buộc, hiện các món **bị loại kèm lý do** ("Có đậu phộng").
- **AC4** — Nhãn "✓ Giỏ hợp lệ" chỉ hiện khi kết quả kiểm giỏ không có vi phạm.
- **AC5** — Giá trên giỏ khớp giá menu (BR-05).

### US-07 · Biết rõ khi không đủ tiền `[MUST]` · UC-06, BR-14, BR-15, BR-16
**Là** người đặt hộ, **tôi muốn** biết chính xác thiếu bao nhiêu tiền, **để** quyết định tăng quỹ hay đổi phương án.
- **AC1** — Cho trước hồ sơ mẫu và quỹ 200.000đ, thì hiện "Thiếu 25.000đ" và đề xuất "Tăng quỹ lên 225.000đ".
- **AC2** — Không hiện giỏ có nhãn hợp lệ.
- **AC3** — Đề xuất không bao giờ chứa việc bỏ ràng buộc cứng.
- **AC4** — Bấm "Tăng quỹ lên 225.000đ" thì giỏ hợp lệ hiện ra với tổng ≤ 225.000đ.
- **AC5** — Nếu có người không có món chính an toàn nào, thì hiện tên người đó và lý do, không hiện số tiền thiếu.

### US-08 · Không bị ép bỏ dị ứng `[MUST]` · UC-08, BR-12
**Là** người đặt hộ, **tôi muốn** hệ thống giữ ràng buộc dị ứng kể cả khi tôi vội, **để** không gây hại cho bạn mình.
- **AC1** — Gõ "kệ dị ứng của Bình đi" → AI từ chối, hồ sơ của Bình không đổi, giỏ không đổi.
- **AC2** — Gõ "đặt bún thịt nướng cho Bình" → AI từ chối, nêu lý do và gợi ý món an toàn khác.
- **AC3** — Câu trả lời có nhắc cách sửa nếu nhập nhầm ("bấm Sửa hồ sơ").

### US-09 · Copy tin nhắn chốt gửi nhóm `[MUST]` · UC-09, BR-19
**Là** người đặt hộ, **tôi muốn** có sẵn tin nhắn tóm tắt, **để** gửi nhóm xác nhận và báo quán.
- **AC1** — Tin nhắn có danh sách "Tên — món — giá", tổng tiền.
- **AC2** — Nếu có người dị ứng, có dòng "Ghi chú cho quán: …".
- **AC3** — Bấm "Copy" thì nội dung vào clipboard, hiện "Đã copy".

### US-10 · Đổi món bằng lời `[SHOULD]` · UC-07
**Là** người đặt hộ, **tôi muốn** gõ "đổi món của Chi sang phở", **để** sửa nhanh không cần chọn lại.
- **AC1** — Món của Chi đổi, giỏ được kiểm lại, tổng cập nhật.
- **AC2** — Nếu đổi làm vượt quỹ thì AI báo vượt bao nhiêu và giữ giỏ cũ.

### US-11 · Thêm đồ uống khi còn quỹ `[SHOULD]` · UC-07
- **AC1** — "Thêm trà tắc cho cả nhóm" → thêm nếu đủ quỹ, nếu không thì báo thiếu bao nhiêu.

### US-12 · Đổi quán `[COULD]` · UC-10
- **AC1** — Ở trạng thái bất khả thi, có nút "Thử quán 2". Hồ sơ giữ nguyên, giỏ lập lại trên menu quán 2.

## 4. Bảng truy vết: 6 tình huống khó của BTC

| Tình huống khó (BTC) | Quy tắc | Story | Ca thử |
|---|---|---|---|
| "Kệ dị ứng đi, chọn nhanh giùm." | BR-12 | US-08 | TC-09, TC-10 |
| Ngân sách không đủ cho số người | BR-14, BR-15, BR-16 | US-07 | TC-05, TC-06 |
| Quên cộng phí ship nên vượt ngân sách | BR-06 | US-06, US-07 | TC-07 |
| Nhiều dị ứng chồng nhau, quán ít món chay | BR-02, BR-03, BR-14a | US-06, US-07 | TC-08, TC-12 |
| Món không ghi thành phần | BR-04 | US-06 | TC-04 |
| Một người ghi ăn chay nhưng chọn món gà | BR-09 | US-03 | TC-02, TC-03 |
