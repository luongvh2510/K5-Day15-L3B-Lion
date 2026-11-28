# 01 · Nghiệp vụ và quy tắc (`BR-xx`)

> File quan trọng nhất về nghiệp vụ. Code kiểm giỏ (`validate_cart`) và prompt AI đều phải bám đúng các quy tắc này.
> Muốn đổi quy tắc nào thì báo BA, không tự đổi trong code.
>
> **Cập nhật 28/11** theo thiết kế mới và dữ liệu thật `data/dataset_mon_an_viet.json`: đầu vào chỉ là đoạn chat
> (quỹ đọc từ chat, quán do agent chọn), định dạng chat mới, ăn chay suy từ nguyên liệu (BR-02), 10 mã dị ứng theo
> dữ liệu (mục 4), phí ship tính theo `distance_km` của quán, chỉ có món chính. Các dòng đã đổi có ghi *(cập nhật 28/11)*.

## 1. Thuật ngữ

| Thuật ngữ | Nghĩa trong sản phẩm |
|---|---|
| **Người đặt hộ** | Người dùng duy nhất. Người cầm quỹ, dán đoạn chat, xác nhận, chốt đơn. **Không chọn quán**: agent chọn *(cập nhật 28/11)* |
| **Thành viên** | Một người sẽ được đặt 1 suất. Có thể gồm cả người đặt hộ |
| **Đoạn chat** | Văn bản người đặt dán vào, dạng **tên một dòng, tin nhắn ở dòng sau** (`Tên1⏎Tin nhắn 1⏎Tên2⏎Tin nhắn 2`); một tin có thể nhiều dòng. Quỹ chung nằm trong chat *(cập nhật 28/11)* |
| **Hồ sơ nhóm** | Danh sách thành viên kèm ràng buộc và sở thích của từng người |
| **Ràng buộc cứng** | Điều **bắt buộc** đúng: ăn chay, dị ứng. Vi phạm thì giỏ không hợp lệ |
| **Sở thích (ràng buộc mềm)** | Điều nên đáp ứng nếu được: "muốn ăn bún", "món có nước", "không cay" |
| **Suất** | Món chính của một thành viên. Mỗi thành viên có đúng 1 suất |
| **Món phụ / đồ uống** | ~~Món không phải món chính~~ — dữ liệu thật **không có** món phụ/đồ uống, POC bỏ phần này *(cập nhật 28/11)* |
| **Quỹ** | Số tiền tối đa cho cả đơn, **đã gồm phí ship** |
| **Món an toàn (với 1 người)** | Món không vi phạm ràng buộc cứng nào của người đó |
| **Giỏ hợp lệ** | Giỏ mà `validate_cart` trả về 0 vi phạm |
| **Bất khả thi** | Không tồn tại giỏ hợp lệ với hồ sơ, menu và quỹ hiện tại |
| **Câu gốc** | Đoạn trích nguyên văn từ chat làm căn cứ cho một ràng buộc hoặc sở thích |

## 2. Dữ liệu menu (nghiệp vụ)

Mỗi món có các trường sau (schema kỹ thuật ở [04](04-hop-dong-du-lieu-API.md)). *(cập nhật 28/11: theo dữ liệu thật)*

| Trường | Ý nghĩa nghiệp vụ |
|---|---|
| Tên, giá | Giá tính bằng đồng (VND), số nguyên |
| Loại | Mọi món là **món chính** (dữ liệu không có món phụ, đồ uống) |
| Nguyên liệu | Danh sách nguyên liệu theo nhóm (thịt, hải sản, trứng, sữa, rau, gia vị…). **Không có nhãn chay** — code suy ra (BR-02) |
| Chất gây dị ứng | Suy từ nguyên liệu, kèm tên nguyên liệu gây ra, ví dụ `peanut` ← "Đậu phộng rang" |
| Rõ thành phần | `false` nếu không có nguyên liệu. Dữ liệu hiện tại: mọi món đều rõ |
| Còn bán | `false` thì không được đưa vào giỏ |

Phí ship: dữ liệu không có trường phí, POC **tính theo `distance_km` của quán: 15.000đ cho 2 km đầu, mỗi km tiếp theo (làm tròn lên) +5.000đ** (mô phỏng, `tools.shipping_fee`). 7 quán trong 2 km là 15.000đ; store_04, store_05, store_09 là 20.000đ; store_10 (3,1 km) là 25.000đ *(cập nhật 28/11)*. Dữ liệu có 10 quán, mỗi quán 10 món.

## 3. Quy tắc nghiệp vụ

### Nhóm A: Ràng buộc an toàn (code kiểm, không có ngoại lệ)

| Mã | Quy tắc | Ai thực thi |
|---|---|---|
| **BR-01** | Có 2 loại ràng buộc cứng: **ăn chay** và **dị ứng (theo chất)**. Mọi lời dặn khác là sở thích mềm. | AI phân loại, người đặt xác nhận |
| **BR-02** | Người ăn chay chỉ được gán **món chay thuần**, do code suy từ nguyên liệu: **không** có nguyên liệu nhóm thịt, hải sản, **trứng, sữa**, và không có gia vị nguồn động vật (nước mắm, mắm tôm, mắm ruốc Huế, mắm cá linh/cá lóc, dầu hào). Mật ong không tính. Lý do loại ghi rõ nguyên liệu, ví dụ "không chay: có Ức gà". *(cập nhật 28/11: bản đầu dùng nhãn chay của quán, dữ liệu thật không có nhãn này)* | Code |
| **BR-03** | Món có chất gây dị ứng mà một thành viên bị dị ứng thì **không được gán cho thành viên đó**. | Code |
| **BR-04** | Món **không rõ thành phần** không được gán cho người có **bất kỳ** dị ứng nào, cũng không cho người ăn chay. Người không có ràng buộc cứng vẫn được gán, kèm ghi chú "quán không ghi thành phần". | Code |
| **BR-05** | Món phải **có trong menu** và **còn bán**. **Giá lấy từ menu**, không lấy từ câu trả lời của AI. | Code |

### Nhóm B: Tiền và số suất

| Mã | Quy tắc | Ai thực thi |
|---|---|---|
| **BR-06** | **Tổng = Σ(giá × số lượng) + phí ship**. Tổng phải **≤ quỹ**. POC không tính giảm giá, phí dịch vụ hay tip. | Code |
| **BR-07** | Mỗi thành viên đã xác nhận có **đúng 1 món chính**. *(cập nhật 28/11: không có món phụ/đồ uống)* | Code |
| **BR-08** | Thứ tự ưu tiên khi chọn món: (1) hợp lệ → (2) đáp ứng nhiều sở thích nhất → (3) tổng rẻ hơn. Không cần tiêu hết quỹ. | AI chọn trong danh sách code đã lọc |

### Nhóm C: Hồ sơ nhóm và hội thoại

| Mã | Quy tắc | Ai thực thi |
|---|---|---|
| **BR-09** | Khi lời dặn **mâu thuẫn** với ràng buộc cứng của **cùng người**, ví dụ An ăn chay nhưng nhắc "cơm gà": ràng buộc cứng **thắng tạm thời**. Hệ thống **hỏi lại**, không tự gán món vi phạm, không tự xoá ràng buộc. | AI phát hiện và hỏi, code chặn |
| **BR-10** | Khi lời dặn **mơ hồ**, hệ thống hỏi lại, **không đoán**. Các trường hợp mơ hồ: không rõ thuộc ai, dị ứng không rõ chất ("dị ứng hải sản" có gồm cá không?), không rõ có phải ràng buộc cứng không ("dạo này hạn chế đồ chiên"). **Còn câu hỏi chưa trả lời thì không cho xác nhận hồ sơ.** | AI hỏi, FE khoá nút |
| **BR-11** | Người đặt **phải xác nhận hồ sơ** trước khi lập giỏ. Hồ sơ phải có **quỹ**; chat không nêu quỹ thì hệ thống hỏi "Quỹ chung của nhóm là bao nhiêu?" và khoá xác nhận tới khi có *(cập nhật 28/11)*. Trước khi xác nhận, người đặt được sửa tự do: thêm hoặc bớt người, thêm hoặc bớt ràng buộc. | FE + BE |
| **BR-12** | **Khoá một chiều:** sau khi xác nhận, ràng buộc cứng **chỉ được thêm, không được bớt qua hội thoại**. Câu như "kệ dị ứng đi", "cứ cho An ăn gà" bị từ chối. Muốn bớt thật (vì AI gán nhầm) thì người đặt bấm **"Sửa hồ sơ"** trên UI, có cảnh báo. Khi đó giỏ hiện tại bị huỷ và hồ sơ phải xác nhận lại. | Code chặn, AI giải thích |
| **BR-13** | Mỗi ràng buộc và sở thích phải có **câu gốc** trích từ chat. Ràng buộc do người đặt tự thêm thì ghi nguồn "Người đặt thêm". *(cập nhật 28/11: hiện câu gốc mới gom theo **người** (`Member.quotes`), chưa gắn tới từng ràng buộc; không còn bước code kiểm câu gốc)* | AI trích, FE hiện |

### Nhóm D: Bất khả thi và đề xuất nới

| Mã | Quy tắc | Ai thực thi |
|---|---|---|
| **BR-14** | **Bất khả thi do code xác định**, không do AI. Có 2 loại: **(a)** có thành viên **không có món chính an toàn nào**, hoặc **(b)** **chi phí tối thiểu** = Σ(món chính an toàn rẻ nhất của mỗi người) + phí ship **> quỹ**. Thông báo phải nêu nguyên nhân và **số tiền thiếu chính xác** = chi phí tối thiểu − quỹ. | Code tính, AI diễn đạt |
| **BR-15** | Chỉ được đề xuất nới **quỹ** hoặc **sở thích mềm**, hoặc **đổi quán** (agent chọn quán khác, đã làm) *(cập nhật 28/11)*. **Không bao giờ** đề xuất nới ràng buộc cứng. Đề xuất tăng quỹ phải đưa ra **con số cụ thể** = chi phí tối thiểu. | AI đề xuất, code cung cấp số |
| **BR-16** | Khi bất khả thi, UI **không hiển thị** giỏ có nhãn "hợp lệ". Chỉ hiện trạng thái "Chưa khả thi". | FE |

### Nhóm E: Hiển thị và đầu ra

| Mã | Quy tắc | Ai thực thi |
|---|---|---|
| **BR-17** | Nhãn **"✓ Giỏ hợp lệ"** chỉ hiện khi `validate_cart` không trả lỗi (API: `validation.ok == true`). Câu chữ: "Đã kiểm theo yêu cầu đã xác nhận và menu quán". | FE |
| **BR-18** | Giỏ phải ghi rõ **món nào cho ai**, giá từng món, tạm tính, phí ship, tổng, quỹ còn lại. Có danh sách **món bị loại kèm lý do** cho người có ràng buộc. | BE + FE |
| **BR-19** | Tin nhắn chốt gửi nhóm phải liệt kê món theo người, tổng tiền, và **luôn có dòng ghi chú cho quán** nếu nhóm có người dị ứng, ví dụ "Ghi chú quán: suất của Bình không đậu phộng, kể cả nước chấm". Lý do: hệ thống không kiểm được nhiễm chéo trong bếp. | AI viết, code chèn dòng ghi chú |

## 4. Danh mục mã chất gây dị ứng (POC)

*(cập nhật 28/11: lấy đúng 10 mã `allergen_types` của dữ liệu thật. Bỏ `TREE_NUT`, `SHELLFISH`, `OTHER`; thêm `CRUSTACEAN`, `MOLLUSC`, `CELERY`.
Menu dùng chữ thường `peanut`, hồ sơ/API viết hoa `PEANUT`.)*

| Mã | Tên hiển thị | Ví dụ cách nói trong chat |
|---|---|---|
| `PEANUT` | Đậu phộng | "đậu phộng", "lạc", "đậu phộng rang" |
| `SOY` | Đậu nành | "đậu nành", "đậu hũ", "tàu hũ", "nước tương" |
| `WHEAT` | Lúa mì / gluten | "gluten", "bột mì" |
| `EGG` | Trứng | "trứng" |
| `MILK` | Sữa | "sữa", "lactose" |
| `FISH` | Cá | "cá" (lưu ý: nước mắm có `fish`) |
| `CRUSTACEAN` | Giáp xác (tôm, cua, ghẹ) | "tôm", "cua" |
| `MOLLUSC` | Nhuyễn thể (mực, nghêu, sò, hàu) | "mực", "nghêu", "hàu" |
| `SESAME` | Mè / vừng | "mè", "vừng" |
| `CELERY` | Cần tây | "cần tây" |

- "Hải sản" là **mơ hồ** (cá? tôm cua? mực?) → hệ thống hỏi lại, không tự gán (BR-10).
- Dị ứng ngoài 10 mã (ví dụ "hạt điều") → hệ thống **hỏi lại**, không tạo ràng buộc, vì menu không có dữ liệu để kiểm.
  Người đặt cũng không thêm được mã lạ qua form (API trả 400).

## 5. Ví dụ áp quy tắc

*(cập nhật 28/11: ví dụ cũ dùng menu mẫu `r1` không còn dùng; thay bằng quán thật `store_08` — Xôi Nếp Ban Mai.)*

Hồ sơ: An (chay), Bình (dị ứng `PEANUT`), Chi, Dũng, Hà. Quỹ 300.000đ, phí ship 15.000đ.

| Món (store_08) | Giá | Chay (code suy) | Dị ứng | An | Bình | Chi/Dũng/Hà |
|---|---|---|---|---|---|---|
| Xôi đậu xanh (`dish_077`) | 21k | ✓ | — | ✅ | ✅ | ✅ |
| Xôi gà xé (`dish_071`) | 35k | ✗ (Ức gà, nước mắm) | fish, soy, wheat | ❌ BR-02 | ✅ | ✅ |
| Xôi lạc (`dish_078`) | 22k | ✓ | peanut, sesame | ✅ | ❌ BR-03 | ✅ |
| Xôi xéo (`dish_076`) | 24k | ✗ | — | ❌ BR-02 | ✅ | ✅ |

Chi phí tối thiểu = Σ món an toàn rẻ nhất của mỗi người + ship. Với 5 người ở `store_08`:
5 × 21k + 15k = **120.000đ** → quỹ 300k khả thi; quỹ 100k bất khả thi, **thiếu 20.000đ** (BR-14b).
Số liệu khớp mẫu [`mocks/session_infeasible.json`](mocks/session_infeasible.json).
