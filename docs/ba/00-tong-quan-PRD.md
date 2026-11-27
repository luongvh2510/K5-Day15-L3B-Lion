# 00 · Tổng quan sản phẩm (PRD)

> Đọc đầu tiên. Các quy tắc chi tiết nằm ở [01](01-nghiep-vu-va-quy-tac.md), luồng ở [02](02-use-case-user-story.md).

## 1. Bài toán trong một câu

Một người **cầm quỹ chung** đặt đồ ăn hộ cả nhóm. Lời dặn của mọi người nằm rải rác trong đoạn chat nhóm.
Sản phẩm đọc đoạn chat, rút ra **ai ăn được gì**, rồi lập một giỏ hàng từ menu **một quán**. Giỏ này được
code kiểm lại: không phạm dị ứng, đúng món chay, tổng tiền gồm phí ship không vượt quỹ. Nếu không có giỏ nào
đáp ứng được, sản phẩm nói thẳng là thiếu bao nhiêu và đề xuất cách nới. Sản phẩm không bịa món.

## 2. Vì sao đây là vấn đề thật (pain point)

**Người gặp vấn đề:** người đặt hộ, cầm quỹ chung. Ví dụ: nhóm bạn, team văn phòng đặt cơm trưa, ban hậu cần CLB.

**App hiện có chưa giải quyết tình huống này:**
- Tính năng đặt đơn nhóm của GrabFood hoạt động như **giỏ chung**. Chủ đơn gửi link, từng người tự vào chọn món,
  rồi chia tiền theo món, chia đều hoặc chủ đơn trả hết ([Grab](https://www.grab.com/inside-grab/stories/grabfood-delivery-group-order/),
  [Grab VN](https://www.grab.com/vn/campaign/gioi-thieu-tinh-nang-dat-don-nhom-group-order-cua-grabfood/)).
  Cách này cần **mỗi người tự mở app và tự chọn**. Nó không xử lý trường hợp mọi người chỉ nhắn vài câu
  vào nhóm chat ("tao ăn chay", "dị ứng đậu phộng", "gì cũng được") rồi để một người lo hết.
- Đơn của ShopeeFood chỉ đặt được từ **một quán**. Muốn đổi quán thì phải tạo đơn khác
  ([Sapo](https://www.sapo.vn/blog/don-nhom-shopee-food)).
- Các nền tảng đặt cơm văn phòng ở nước ngoài coi **thu thập ràng buộc ăn uống** là việc tốn công nhất. Họ khuyên
  dùng form khảo sát hoặc bảng tính ([ezCater](https://ezcater.com/lunchrush/?p=38988),
  [Fooda](https://www.fooda.com/blog/lunch-for-large-groups)). Nghĩa là người điều phối vẫn phải tự gom và tự đọc.

**Ba nỗi khổ của người đặt hộ:**
1. **Đọc chat lộn xộn:** dễ sót lời dặn dị ứng, hoặc bối rối khi một người vừa nói ăn chay vừa nhắc cơm gà.
2. **Rủi ro ẩn trong menu:** món nghe lành nhưng nước chấm hoặc topping có đậu phộng, có món quán không ghi thành phần.
   Sai món dị ứng là hậu quả sức khoẻ thật. Hội dị ứng Úc khuyên người dị ứng ghi rõ dị ứng trong đơn online
   và hỏi quán về nhiễm chéo ([Allergy & Anaphylaxis Australia](https://allergyfacts.org.au/?p=11730)).
3. **Vỡ ngân sách vì phí ship:** chọn gần xong, cộng thêm ship thì vượt quỹ. Bỏ món thì thiếu suất, nên phải dò lại từ đầu.

> ⚠️ **Bằng chứng còn thiếu, BA cần bổ sung trước khi pitch:** các nguồn trên là blog của nhà cung cấp.
> Nhóm nên tự xin **3–5 đoạn chat đặt đồ ăn thật** từ nhóm Zalo/Messenger của bạn bè (bỏ tên thật),
> kèm 2–3 câu phỏng vấn ngắn: "lần gần nhất đặt hộ mất bao lâu?", "có từng đặt nhầm món dị ứng hoặc chay không?".

## 3. Người dùng và vai trò

| Vai | Là ai | Tương tác với hệ thống |
|---|---|---|
| **Người đặt hộ** | Người cầm quỹ, dán chat, quyết định cuối | Trực tiếp, là người dùng duy nhất của POC |
| Thành viên nhóm | Người nhắn lời dặn trong chat | Gián tiếp, chỉ qua đoạn chat được dán vào |
| Quán | Nguồn menu, giá, phí ship | Không tương tác. Dữ liệu menu là dữ liệu mẫu |

## 4. Phạm vi POC

Theo lát cắt BTC gợi ý: **1 người đặt hộ · 5 người · quỹ 300k · 1 người ăn chay · 1 người dị ứng đậu phộng.**
*(cập nhật 28/11: dùng dữ liệu thật 10 quán × 10 món; agent tự chọn 1 quán cho cả đơn.)*

### Làm `[MUST]`
- Dán đoạn chat nhóm (quỹ nằm trong chat). **Agent tự chọn quán**, người đặt có thể bấm "Đổi quán". *(cập nhật 28/11)*
- AI trích hồ sơ nhóm: danh sách người, ràng buộc cứng (chay, dị ứng), sở thích mềm. Mỗi ý kèm **câu chat gốc**.
- AI phát hiện mâu thuẫn và chỗ mơ hồ rồi **hỏi lại** người đặt.
- Người đặt **rà và xác nhận** hồ sơ trước khi lập giỏ. Đây là chốt chặn bắt buộc.
- Lập giỏ: mỗi người 1 món chính. Code kiểm cứng dị ứng, chay, món không rõ thành phần, tổng gồm ship.
- Bất khả thi: báo đúng số tiền thiếu và nguyên nhân, đề xuất nới.
- Từ chối yêu cầu phá rào an toàn ("kệ dị ứng đi").
- Xuất tin nhắn chốt đơn để copy gửi lại nhóm.

### Làm nếu còn giờ `[SHOULD]` / `[COULD]`
- `[SHOULD]` Sửa giỏ qua hội thoại ("đổi món của Chi sang phở").
- ~~`[SHOULD]` Thêm đồ uống hoặc món phụ khi còn dư quỹ.~~ Bỏ: dữ liệu không có món phụ/đồ uống *(cập nhật 28/11)*.
- Đổi quán khi quán hiện tại bất khả thi hoặc người đặt muốn — **đã làm** *(cập nhật 28/11)*.

### Không làm
Đăng nhập, thanh toán, gọi API GrabFood/ShopeeFood, nhiều quán trong một đơn, mã giảm giá, chia tiền từng người,
nhiễm chéo trong bếp (chỉ nhắc người đặt báo quán), đọc ảnh chụp màn hình chat.

## 5. AI làm gì, code làm gì (tóm tắt)

| AI (LLM) | Code (chính xác, không tin AI) |
|---|---|
| Đọc chat, rút ra người, ràng buộc, sở thích, quỹ, kèm câu gốc | Cung cấp menu, giá, nguyên liệu, phí ship; suy món chay và chất dị ứng từ nguyên liệu |
| Phát hiện mâu thuẫn hoặc mơ hồ, đặt câu hỏi làm rõ | Lọc món an toàn cho từng người |
| Chọn quán và món hợp sở thích **trong danh sách code đã lọc** | `validate_cart`: kiểm từng quy tắc, cộng tiền |
| Giải thích, đề xuất nới, từ chối lịch sự | Tính chi phí tối thiểu để xác định bất khả thi |
| Hiểu yêu cầu sửa giỏ nhiều lượt | Khoá một chiều cho ràng buộc cứng |

Chi tiết ở [05-AI-agent.md](05-AI-agent.md).

## 6. Chỉ số thành công (đo trên bộ ca thử ở [06](06-du-lieu-mau-va-test.md))

| Chỉ số | Mục tiêu POC | Cách đo |
|---|---|---|
| Giỏ hiển thị "hợp lệ" mà vi phạm ràng buộc cứng đã xác nhận | **0** | Code chấm |
| Trích ràng buộc cứng đúng người (recall) | ≥ 95% | So với đáp án |
| Trích ràng buộc cứng gán nhầm hoặc bịa (precision) | ≥ 95% | So với đáp án |
| Phát hiện mâu thuẫn hoặc mơ hồ cần hỏi lại | ≥ 80% ca có cài | So với đáp án |
| Kết luận bất khả thi đúng, số tiền thiếu đúng | 100% | Code chấm |
| Thời gian từ dán chat đến giỏ chốt so với làm bằng form | Đo thật, **không hứa trước** | 3–5 người thử |

> Không dùng câu "an toàn 100%" hay "dưới 1 phút" khi pitch nếu chưa đo.
> Nhãn trên UI ghi: **"Đã kiểm theo yêu cầu đã xác nhận và menu quán."**

**Đối chứng:** chuẩn bị một form thường (bảng 5 dòng: tên, chay hay không, dị ứng, món) dùng cùng menu.
Cho người thử làm cả hai cách với cùng đoạn chat. Đo thời gian, số lời dặn bị sót và số lỗi.
Nếu hai cách ngang nhau thì AI chưa chứng minh được giá trị. Phải biết trước khi BGK hỏi.

## 7. Kịch bản demo (90 giây)

1. Bấm **"Nạp chat mẫu"**. Đoạn chat 5 người hiện ra (quỹ 300k nằm trong chat). Bấm **Phân tích**. *(cập nhật 28/11)*
2. Hồ sơ nhóm hiện bên phải: **An** có nhãn chay và câu hỏi ❓ "nhắc cơm gà". **Bình** có nhãn dị ứng đậu phộng.
   Mỗi thẻ có câu chat gốc của người đó.
3. AI hỏi: *"An nói ăn chay nhưng lại nhắc 'thêm 1 cơm gà'. Suất cơm gà này cho ai?"*
   Người đặt trả lời: *"Cho Dũng, An vẫn ăn chay."* Hồ sơ cập nhật.
4. Bấm **Xác nhận hồ sơ**. Ràng buộc khoá 🔒, **agent chọn quán** (ví dụ Xôi Nếp Ban Mai) và lập giỏ: 5 suất, mỗi
   suất ghi cho ai. Danh sách **món bị loại có lý do theo nguyên liệu** ("Xôi lạc: dị ứng đậu phộng"). Tổng gồm ship 15.000đ, nhãn ✓ hợp lệ.
5. Gõ: *"Kệ dị ứng của Bình đi, đặt bún thịt nướng cho nhanh."* AI từ chối, ràng buộc của Bình giữ nguyên.
6. (Nếu còn giờ) Phiên khác với chat ghi quỹ 100k: hệ thống báo **"thiếu 20.000đ"**, đề xuất tăng quỹ lên 120k hoặc đổi quán. Không hiện giỏ hợp lệ. *(cập nhật 28/11)*
7. Bấm **Copy tin nhắn chốt** để gửi lại nhóm.

## 8. Kế hoạch theo hướng "FE trước"

"FE trước" **không có nghĩa** là BE và AI ngồi chờ. Cả nhóm làm song song dựa trên **hợp đồng dữ liệu ở file 04**.

| Giờ | BA | FE + BE (1 người) | AI-1 (trích xuất) | AI-2 (giỏ + hội thoại) |
|---|---|---|---|---|
| 0–1 | Chốt file 04 + JSON mock | Đọc 00, 03, 04 | Đọc 01, 05, 06 | Đọc 01, 05, 06 |
| 1–5 | Viết đoạn chat test và đáp án, phỏng vấn | **FE chạy bằng mock** cho đủ các trạng thái | Prompt trích hồ sơ, chạy offline trên chat test | `menu`, `safe_items`, `validate_cart`, `min_cost` (Python thuần) + chọn món |
| 5 | **Mốc 1:** FE gọi API thật, BE trả extraction giả | Dựng API (FastAPI) bọc các hàm của AI-2 | | |
| 5–8 | Chạy thử, ghi lỗi | Nối API | Nối extraction vào API | Router hội thoại, từ chối phá rào |
| 8 | **Mốc 2: chạy xuyên suốt** dán chat → xác nhận → giỏ hoặc báo thiếu tiền | | | |
| 8–12 | Đối chứng với form | Sửa UI | Sửa lỗi trích | Sửa lỗi giỏ |
| 12–14 | Slide, kịch bản demo | Ổn định demo | Bảng kết quả eval | |

> **Đề xuất chia việc:** một người vừa làm FE vừa làm BE là điểm nghẽn. Nên để **AI-2 viết các hàm code kiểm giỏ**
> (Python thuần, không phụ thuộc web). Người BE chỉ bọc các hàm đó thành API. Nhờ vậy validator có test riêng
> từ sớm, không phụ thuộc FE.

## 9. Rủi ro và cách giảm

| Rủi ro | Hậu quả | Giảm thiểu |
|---|---|---|
| AI đọc sót lời dặn dị ứng | Code duyệt một giỏ "hợp lệ" nhưng sai với thực tế | Bước xác nhận hồ sơ bắt buộc (BR-11), hiện câu gốc (BR-13) |
| Menu không ghi thành phần | Gán món nguy hiểm | Món không rõ thành phần coi là không an toàn (BR-04) |
| Nhiễm chéo trong bếp | Ngoài khả năng hệ thống | Tin nhắn chốt luôn có dòng nhắc báo quán về dị ứng (BR-19) |
| LLM trả JSON lỗi hoặc chậm | Demo treo | Thử lại 1 lần, sau đó dùng giỏ dự phòng do code chọn (rẻ nhất) |
| BGK tự viết đoạn chat lạ | Lộ lỗi trích xuất | Luyện với 5 đoạn chat "chưa thấy" do BA viết riêng |

## 10. Nguồn tham khảo

- Grab, đặt đơn nhóm: [Inside Grab](https://www.grab.com/inside-grab/stories/grabfood-delivery-group-order/), [Grab VN](https://www.grab.com/vn/campaign/gioi-thieu-tinh-nang-dat-don-nhom-group-order-cua-grabfood/), [Điều khoản Group Order VN](https://www.grab.com/vn/en/terms-policies/group-order-terms-of-use)
- ShopeeFood, đơn nhóm: [Sapo](https://www.sapo.vn/blog/don-nhom-shopee-food)
- Đặt cơm văn phòng và ràng buộc ăn uống: [ezCater](https://ezcater.com/lunchrush/?p=38988), [Fooda](https://www.fooda.com/blog/lunch-for-large-groups), [Waiter.com](https://www.waiter.com/blog/special-diets/how-to-handle-dietary-restrictions-for-office-catering)
- Dị ứng khi đặt đồ ăn online: [Allergy & Anaphylaxis Australia](https://allergyfacts.org.au/?p=11730), [UK FSA](https://www.food.gov.uk/sites/default/files/media/document/SME%20allergen%20provision%20in%20the%20non-prepacked%20sector.pdf)
- Nghiên cứu liên quan: agent đặt món có bộ kiểm ràng buộc ([arXiv 2607.18261](https://arxiv.org/pdf/2607.18261)); LLM trích yếu tố quyết định từ chat nhóm ([arXiv 2601.05582](https://arxiv.org/pdf/2601.05582v1)); trích ràng buộc cứng rồi lọc trước khi sinh ([arXiv 2610.07886](https://arxiv.org/pdf/2610.07886))
- Ghi nhãn hàng hoá VN: [NĐ 43/2017](https://thuvienphapluat.vn/van-ban/EN/Thuong-mai/Decree-43-2017-ND-CP-on-good-labels/348247/tieng-anh.aspx), [NĐ 111/2021](https://thuvienphapluat.vn/van-ban/thuong-mai/Nghi-dinh-111-2021-ND-CP-sua-doi-Nghi-dinh-43-2017-ND-CP-497099.aspx). Các nghị định này áp dụng cho **thực phẩm bao gói sẵn**, không áp dụng cho món ở quán. Vì vậy dữ liệu menu quán thường thiếu thành phần. Đây là lý do có BR-04. Nhóm chưa kiểm danh mục chất gây dị ứng cụ thể trong phụ lục, nên **không tuyên bố tuân thủ pháp lý**.
