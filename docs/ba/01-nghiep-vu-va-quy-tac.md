# 01 · Nghiệp vụ và quy tắc (`BR-xx`)

> File quan trọng nhất về nghiệp vụ. Code kiểm giỏ (`validate_cart`) và prompt AI đều phải bám đúng các quy tắc này.
> Muốn đổi quy tắc nào thì báo BA, không tự đổi trong code.

## 1. Thuật ngữ

| Thuật ngữ | Nghĩa trong sản phẩm |
|---|---|
| **Người đặt hộ** | Người dùng duy nhất. Người cầm quỹ, dán đoạn chat, xác nhận, chốt đơn |
| **Thành viên** | Một người sẽ được đặt 1 suất. Có thể gồm cả người đặt hộ |
| **Đoạn chat** | Văn bản người đặt dán vào, mỗi dòng có dạng `Tên: nội dung` hoặc `[Tên] nội dung` |
| **Hồ sơ nhóm** | Danh sách thành viên kèm ràng buộc và sở thích của từng người |
| **Ràng buộc cứng** | Điều **bắt buộc** đúng: ăn chay, dị ứng. Vi phạm thì giỏ không hợp lệ |
| **Sở thích (ràng buộc mềm)** | Điều nên đáp ứng nếu được: "muốn ăn bún", "món có nước", "không cay" |
| **Suất** | Món chính của một thành viên. Mỗi thành viên có đúng 1 suất |
| **Món phụ / đồ uống** | Món không phải món chính, có thể thêm nếu còn quỹ |
| **Quỹ** | Số tiền tối đa cho cả đơn, **đã gồm phí ship** |
| **Món an toàn (với 1 người)** | Món không vi phạm ràng buộc cứng nào của người đó |
| **Giỏ hợp lệ** | Giỏ mà `validate_cart` trả về 0 vi phạm |
| **Bất khả thi** | Không tồn tại giỏ hợp lệ với hồ sơ, menu và quỹ hiện tại |
| **Câu gốc** | Đoạn trích nguyên văn từ chat làm căn cứ cho một ràng buộc hoặc sở thích |

## 2. Dữ liệu menu (nghiệp vụ)

Mỗi món có các trường sau (schema kỹ thuật ở [04](04-hop-dong-du-lieu-API.md)):

| Trường | Ý nghĩa nghiệp vụ |
|---|---|
| Tên, giá | Giá tính bằng đồng (VND), số nguyên |
| Loại | `MAIN` (món chính), `SIDE` (món phụ), `DRINK` (đồ uống) |
| Nhãn chay | `true` = quán ghi rõ là món chay. `false` = không chay. `null` = không rõ |
| Chất gây dị ứng | Danh sách mã chất có trong món, ví dụ `PEANUT`, `SOY` |
| Rõ thành phần | `false` nếu quán không ghi thành phần. Khi đó danh sách dị ứng **không đáng tin** |
| Còn bán | `false` thì không được đưa vào giỏ |

Phí ship: một số cố định cho mỗi quán (POC không tính theo khoảng cách).

## 3. Quy tắc nghiệp vụ

### Nhóm A: Ràng buộc an toàn (code kiểm, không có ngoại lệ)

| Mã | Quy tắc | Ai thực thi |
|---|---|---|
| **BR-01** | Có 2 loại ràng buộc cứng: **ăn chay** và **dị ứng (theo chất)**. Mọi lời dặn khác là sở thích mềm. | AI phân loại, người đặt xác nhận |
| **BR-02** | Người ăn chay chỉ được gán món có **nhãn chay = `true`**. Nhãn `null` (không rõ) được coi là **không chay**. | Code |
| **BR-03** | Món có chất gây dị ứng mà một thành viên bị dị ứng thì **không được gán cho thành viên đó**. | Code |
| **BR-04** | Món **không rõ thành phần** không được gán cho người có **bất kỳ** dị ứng nào, cũng không cho người ăn chay. Người không có ràng buộc cứng vẫn được gán, kèm ghi chú "quán không ghi thành phần". | Code |
| **BR-05** | Món phải **có trong menu** và **còn bán**. **Giá lấy từ menu**, không lấy từ câu trả lời của AI. | Code |

### Nhóm B: Tiền và số suất

| Mã | Quy tắc | Ai thực thi |
|---|---|---|
| **BR-06** | **Tổng = Σ(giá × số lượng) + phí ship**. Tổng phải **≤ quỹ**. POC không tính giảm giá, phí dịch vụ hay tip. | Code |
| **BR-07** | Mỗi thành viên đã xác nhận có **đúng 1 món chính**. Món phụ và đồ uống không bắt buộc, cũng phải tuân BR-02 → BR-05 với người được gán. | Code |
| **BR-08** | Thứ tự ưu tiên khi chọn món: (1) hợp lệ → (2) đáp ứng nhiều sở thích nhất → (3) tổng rẻ hơn. Không cần tiêu hết quỹ. | AI chọn trong danh sách code đã lọc |

### Nhóm C: Hồ sơ nhóm và hội thoại

| Mã | Quy tắc | Ai thực thi |
|---|---|---|
| **BR-09** | Khi lời dặn **mâu thuẫn** với ràng buộc cứng của **cùng người**, ví dụ An ăn chay nhưng nhắc "cơm gà": ràng buộc cứng **thắng tạm thời**. Hệ thống **hỏi lại**, không tự gán món vi phạm, không tự xoá ràng buộc. | AI phát hiện và hỏi, code chặn |
| **BR-10** | Khi lời dặn **mơ hồ**, hệ thống hỏi lại, **không đoán**. Các trường hợp mơ hồ: không rõ thuộc ai, dị ứng không rõ chất ("dị ứng hải sản" có gồm cá không?), không rõ có phải ràng buộc cứng không ("dạo này hạn chế đồ chiên"). **Còn câu hỏi chưa trả lời thì không cho xác nhận hồ sơ.** | AI hỏi, FE khoá nút |
| **BR-11** | Người đặt **phải xác nhận hồ sơ** trước khi lập giỏ. Trước khi xác nhận, người đặt được sửa tự do: thêm hoặc bớt người, thêm hoặc bớt ràng buộc. | FE + BE |
| **BR-12** | **Khoá một chiều:** sau khi xác nhận, ràng buộc cứng **chỉ được thêm, không được bớt qua hội thoại**. Câu như "kệ dị ứng đi", "cứ cho An ăn gà" bị từ chối. Muốn bớt thật (vì AI gán nhầm) thì người đặt bấm **"Sửa hồ sơ"** trên UI, có cảnh báo. Khi đó giỏ hiện tại bị huỷ và hồ sơ phải xác nhận lại. | Code chặn, AI giải thích |
| **BR-13** | Mỗi ràng buộc và sở thích phải có **câu gốc** trích từ chat. Ràng buộc do người đặt tự thêm thì ghi nguồn "Người đặt thêm". | AI trích, FE hiện |

### Nhóm D: Bất khả thi và đề xuất nới

| Mã | Quy tắc | Ai thực thi |
|---|---|---|
| **BR-14** | **Bất khả thi do code xác định**, không do AI. Có 2 loại: **(a)** có thành viên **không có món chính an toàn nào**, hoặc **(b)** **chi phí tối thiểu** = Σ(món chính an toàn rẻ nhất của mỗi người) + phí ship **> quỹ**. Thông báo phải nêu nguyên nhân và **số tiền thiếu chính xác** = chi phí tối thiểu − quỹ. | Code tính, AI diễn đạt |
| **BR-15** | Chỉ được đề xuất nới **quỹ** hoặc **sở thích mềm**, hoặc bớt món phụ/đồ uống. Với `[COULD]` thì thêm đổi quán. **Không bao giờ** đề xuất nới ràng buộc cứng. Đề xuất tăng quỹ phải đưa ra **con số cụ thể** = chi phí tối thiểu. | AI đề xuất, code cung cấp số |
| **BR-16** | Khi bất khả thi, UI **không hiển thị** giỏ có nhãn "hợp lệ". Chỉ hiện trạng thái "Chưa khả thi". | FE |

### Nhóm E: Hiển thị và đầu ra

| Mã | Quy tắc | Ai thực thi |
|---|---|---|
| **BR-17** | Nhãn **"✓ Giỏ hợp lệ"** chỉ hiện khi `validate_cart.ok == true`. Câu chữ: "Đã kiểm theo yêu cầu đã xác nhận và menu quán". | FE |
| **BR-18** | Giỏ phải ghi rõ **món nào cho ai**, giá từng món, tạm tính, phí ship, tổng, quỹ còn lại. Có danh sách **món bị loại kèm lý do** cho người có ràng buộc. | BE + FE |
| **BR-19** | Tin nhắn chốt gửi nhóm phải liệt kê món theo người, tổng tiền, và **luôn có dòng ghi chú cho quán** nếu nhóm có người dị ứng, ví dụ "Ghi chú quán: suất của Bình không đậu phộng, kể cả nước chấm". Lý do: hệ thống không kiểm được nhiễm chéo trong bếp. | AI viết, code chèn dòng ghi chú |

## 4. Danh mục mã chất gây dị ứng (POC)

| Mã | Tên hiển thị | Ví dụ cách nói trong chat |
|---|---|---|
| `PEANUT` | Đậu phộng | "đậu phộng", "lạc", "đậu phộng rang" |
| `TREE_NUT` | Hạt cây (điều, óc chó, hạnh nhân…) | "hạt điều", "các loại hạt" → **mơ hồ, hỏi lại** |
| `SOY` | Đậu nành | "đậu nành", "đậu hũ", "tàu hũ" |
| `WHEAT` | Lúa mì / gluten | "gluten", "bột mì" |
| `EGG` | Trứng | "trứng" |
| `MILK` | Sữa | "sữa", "lactose" |
| `SHELLFISH` | Giáp xác, nhuyễn thể (tôm, cua, mực…) | "tôm", "hải sản" → **mơ hồ, hỏi có gồm cá không** |
| `FISH` | Cá | "cá", "nước mắm"? → **mơ hồ, hỏi lại** |
| `SESAME` | Mè / vừng | "mè", "vừng" |

Dị ứng ngoài danh mục: AI ghi `OTHER` kèm mô tả, và **hỏi lại** vì menu không có nhãn tương ứng.
Code coi món **không rõ thành phần** là không an toàn với `OTHER`. Món rõ thành phần không có cách kiểm `OTHER`
nên cũng chặn để an toàn, và người đặt được báo lý do.

## 5. Ví dụ áp quy tắc

Hồ sơ: An (chay), Bình (dị ứng `PEANUT`), Chi, Dũng, Tôi. Quỹ 300.000đ, phí ship 20.000đ.

| Món | Giá | Chay | Dị ứng | Rõ TP | An | Bình | Chi/Dũng/Tôi |
|---|---|---|---|---|---|---|---|
| Cơm đậu hũ sốt nấm | 45k | ✓ | SOY | ✓ | ✅ | ✅ | ✅ |
| Gỏi cuốn chay (món phụ) | 30k | ✓ | PEANUT | ✓ | ✅ | ❌ BR-03 | ✅ |
| Bún thịt nướng | 50k | ✗ | PEANUT | ✓ | ❌ BR-02 | ❌ BR-03 | ✅ |
| Bún trộn đặc biệt | 55k | ? | ? | ✗ | ❌ BR-04 | ❌ BR-04 | ✅ (ghi chú) |
| Cơm gà xối mỡ | 55k | ✗ | — | ✓ | ❌ BR-02 | ✅ | ✅ |

Chi phí tối thiểu = An 45k + Bình 40k + 3 × 40k + ship 20k = **225.000đ** (40k là món Xôi gà, món chính rẻ nhất; menu đầy đủ ở file 06).
Quỹ 300k thì khả thi. Quỹ 200k thì bất khả thi, **thiếu 25.000đ** (BR-14b).
