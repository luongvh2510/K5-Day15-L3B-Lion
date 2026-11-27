# AI SPEC — Từ chat nhóm đến giỏ đồ ăn an toàn · Nhóm Lion · Phòng D303 · Zone 2

> Mốc nộp: §7 chốt chuẩn "đạt" tại **CP2 19:30 Thứ Sáu 27/11** · §0–§7 nộp **CP3 10:00 Thứ Bảy 28/11** · đủ §0–§10 **CP4 14:30 Thứ Bảy 28/11** · §10 changelog ghi tiếp đến **23:59 Thứ Bảy 28/11**.
> Đầu mỗi mục ghi bước guide (`docs/btc/02-guide.md`) chỉ cách điền. Mỗi mục ngắn, có số và nguồn; chi tiết để ở file được trỏ tới. Chỗ ghi `__` hoặc "(chờ …)" là chưa điền, **không phải số thật**.

Track: [ ] A · [ ] B · [ ] C · [x] D · [ ] E — bài toán: D2, người cầm quỹ dán chat nhóm lộn xộn và nhận giỏ đồ ăn đã kiểm dị ứng, ăn chay, phí ship, quỹ (chi tiết: `docs/ba/00-tong-quan-PRD.md`)
Data BTC cấp đã dùng (nếu có — không commit nguyên file): không dùng (track D không có data BTC cấp)

## §0. Hiện tại việc này diễn ra thế nào *(guide 1.1)*
- Luồng hiện tại của việc này, trong khoá hoặc trên app thật (3–5 bước; ảnh chụp từ tài khoản của mình, đã che thông tin): *(chưa kiểm — chưa có ảnh chụp từ tài khoản nhóm; luồng dưới đây là giả thuyết cần xác nhận bằng phỏng vấn)*
  1. Mọi người nhắn lời dặn rải rác vào nhóm chat (Zalo/Messenger).
  2. Người cầm quỹ đọc lại chat, tự ghi ai ăn chay, ai dị ứng, ai muốn món gì.
  3. Mở app giao đồ ăn, tìm quán, chọn từng món cho từng người.
  4. Cộng tiền món + phí ship, so với quỹ; vượt thì bỏ món hoặc đổi quán rồi làm lại.
  5. Đặt đơn, nhắn lại nhóm.
- Công cụ / AI đang được dùng cho việc này (nếu có) + nguồn: tính năng đơn nhóm của GrabFood (giỏ chung, mỗi người tự vào chọn) và ShopeeFood (một đơn chỉ từ một quán) — theo `docs/ba/00-tong-quan-PRD.md` mục 2 (nguồn Grab, Sapo). *Chưa kiểm* bằng cách tự dùng.

## §1. Người dùng & bằng chứng *(guide 1.1, 1.2)*
- Người dùng chính (một vai cụ thể): người cầm quỹ chung đi đặt đồ ăn hộ cả nhóm 4–6 người (nhóm bạn, team văn phòng, ban hậu cần CLB).
- Việc họ cố làm xong (`động từ + đối tượng + bối cảnh`, không có chữ AI): đặt bữa ăn cho cả nhóm từ một quán, trong giới hạn quỹ chung, sao cho ai cũng ăn được món của mình.
- Hôm nay họ giải bằng gì, hỏng ở đâu, vì sao chưa bỏ: tự đọc chat và tự chọn món trong app giao đồ ăn; hỏng ở chỗ dễ sót lời dặn, khó biết món có thành phần gây dị ứng không, và phí ship làm vượt quỹ. *(giả thuyết, chờ bằng chứng ở `evidence/summary.md`)*
- Pain (KHÔNG chữ AI): người cầm quỹ đặt hộ cả nhóm — phải đọc lại đoạn chat lộn xộn và dò từng món trong menu — vướng ở chỗ dễ sót lời dặn ăn chay/dị ứng, món không ghi thành phần, và phí ship làm vượt quỹ — hậu quả: mất thời gian làm lại, và nguy cơ đặt nhầm món gây dị ứng.
- Bằng chứng — số chính + kết luận (chi tiết: `evidence/summary.md`): nhóm báo đã phỏng vấn hơn 20 người. Đang chờ ghi chép ẩn danh để xác định số người đúng vai, số gặp vấn đề và trích dẫn nguyên văn.

## §2. Impact & quyết định chọn *(guide 1.3)*

| Hướng | Bao nhiêu người gặp | Bao nhiêu lần / tháng | Mỗi lần tốn gì | Impact / tháng | Làm kịp không | Chọn? |
|---|---|---|---|---|---|---|
| Đặt hộ nhóm có ràng buộc ăn uống (D2) | __ | __ | __ | __ | Có (lát cắt 1 quán, 5 người) | ✓ |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

- **Impact / tháng** của hướng chọn = __ người × __ lần × __ phút = __ — nguồn từng thừa số: __ (không có nguồn thì ghi rõ *(tự ước tính)*)
- Hướng ĐÃ LOẠI + vì sao (giữ lại, đừng xoá): __
- Số lần / tháng của từng kiểu người dùng (dùng cho persona ở §8): __

## §3. Giải pháp tương tự *(guide 2.1)*
- **GrabFood đơn nhóm:** đáng học — một người tạo đơn, gửi link, mọi người vào chọn món và chia tiền theo món. Đáng né — mỗi người phải tự mở app và tự chọn, không xử lý trường hợp mọi người chỉ nhắn trong chat rồi một người lo hết. Mình khác — nhận thẳng đoạn chat, rút ràng buộc và lập giỏ cho cả nhóm.
- **ShopeeFood đơn nhóm:** đáng học — gom nhiều người vào một đơn. Đáng né — mỗi đơn chỉ một quán, đổi quán phải tạo đơn khác. Mình khác — báo thẳng thiếu bao nhiêu tiền và đề xuất đổi quán hoặc nới quỹ.
- **Form khảo sát / bảng tính** (cách ezCater, Fooda khuyên cho đặt cơm văn phòng): đáng học — gom ràng buộc có cấu trúc. Đáng né — người điều phối vẫn phải tự gom và tự đọc. Mình khác — bỏ bước điền form, đọc thẳng từ chat có sẵn.

## §4. Thiết kế *(guide 2.2, 3.2)*

> Phần "đề xuất" dưới đây lấy từ `docs/ba/04` và `docs/ba/05`. **Lương chốt hình dạng, mức tự động và nguyên tắc** trong buổi chốt sơ đồ 18:00–18:30; Dũng xác nhận bảng công cụ.

- **Lát cắt MỘT CÂU** (1 người dùng · 1 việc · 1 quyết định AI · 1 kết quả): một người đặt hộ cho nhóm 5 người dán đoạn chat nhóm (quỹ chung nằm trong chat), hệ thống đọc ràng buộc từng người, tự chọn một quán mẫu phù hợp và lập giỏ từ menu quán đó, và chỉ giao lại giỏ đã qua kiểm tra dị ứng, ăn chay, món thiếu thành phần và tổng tiền gồm phí ship (hoặc đề xuất nới cụ thể khi không có giỏ hợp lệ).
- Không làm (≥3 điều): đăng nhập, thanh toán, gọi API GrabFood/ShopeeFood, nhiều quán trong một đơn, mã giảm giá, chia tiền từng người, đọc ảnh chụp màn hình chat, xử lý nhiễm chéo trong bếp (chỉ nhắc người đặt báo quán). *(theo PRD mục 4)*
- **Sơ đồ kiến trúc** (activity diagram, Mermaid render trên GitHub; tím = AI quyết định, xanh = code kiểm cứng, xám = người dùng / điểm quyết định):

```mermaid
flowchart TB
    START((" ")) --> PASTE["Người dùng dán chat nhóm"]

    subgraph PH1["Phase 1 · Làm rõ yêu cầu"]
        EX["AI trích hồ sơ nhóm và quỹ<br/>ràng buộc, sở thích, câu gốc"]
        D1{"Còn mâu thuẫn, mơ hồ<br/>hoặc thiếu quỹ?"}
        ASK["AI hỏi lại, người dùng trả lời,<br/>AI cập nhật hồ sơ"]
        D2{"Người dùng<br/>xác nhận hồ sơ?"}
        EX --> D1
        D1 -->|"có"| ASK --> D1
        D1 -->|"không"| D2
        D2 -->|"chưa đúng, sửa"| ASK
    end

    LOCK["Code khoá ràng buộc cứng<br/>dị ứng, ăn chay"]

    subgraph PH2["Phase 2 · Chọn món"]
        QUAN["AI chọn quán phù hợp"]
        SAFE["Code lọc món an toàn<br/>cho từng người"]
        D3{"Có giỏ<br/>khả thi?"}
        NOI["AI đề xuất nới<br/>tăng quỹ / đổi quán"]
        PICK["AI chọn món"]
        VC["Code kiểm giỏ"]
        D4{"Giỏ hợp lệ?"}
        D5{"Người dùng<br/>đồng ý giỏ?"}
        ADJ["Người dùng nhắn điều chỉnh<br/>AI hiểu yêu cầu"]
        SAFE --> D3
        QUAN --> SAFE
        D3 -->|"không"| NOI -->|"người dùng chọn"| QUAN
        D3 -->|"có"| PICK --> VC --> D4
        D4 -->|"không, sửa lại"| PICK
        D4 -->|"có"| D5
        D5 -->|"chưa"| ADJ --> PICK
    end

    DONE["Chốt giỏ,<br/>tin nhắn gửi nhóm"] --> END((("  ")))

    PASTE --> EX
    D2 -->|"đúng"| LOCK --> QUAN
    D5 -->|"đồng ý"| DONE

    classDef ai fill:#EEEDFE,stroke:#534AB7,color:#26215C
    classDef code fill:#E1F5EE,stroke:#0F6E56,color:#04342C
    classDef user fill:#F1EFE8,stroke:#5F5E5A,color:#2C2C2A
    classDef dot fill:#2C2C2A,stroke:#2C2C2A
    class EX,ASK,QUAN,NOI,PICK,ADJ ai
    class LOCK,SAFE,VC code
    class PASTE,DONE,D1,D2,D3,D4,D5 user
    class START,END dot
```
- **Hình dạng:** [ ] workflow cố định · [x] một agent · [ ] nhiều agent — **một agent hội thoại chia 2 phase, có cổng chuyển phase.**
  - Phase 1 (làm rõ yêu cầu): agent đọc chat, trích hồ sơ nhóm, tự quyết hỏi lại hay không khi có mâu thuẫn hoặc mơ hồ, cập nhật theo câu trả lời. Người dùng xác nhận hồ sơ thì mới sang phase 2.
  - Phase 2 (chọn món và điều chỉnh): code lọc món an toàn, agent chọn món, code kiểm giỏ, rồi agent thương lượng với người dùng (đổi món, nới quỹ, đổi quán).
  - Vì sao một agent mà không phải nhiều agent: chỉ có một vai (người trợ lý đặt hộ) dùng chung một hồ sơ nhóm; tách nhiều agent chỉ thêm chỗ lệch trạng thái. Vì sao có agent mà không chỉ là workflow cố định: số lượt hỏi lại và chỉnh sửa phụ thuộc vào người dùng, không định trước được.
  - Cổng cứng của code (agent không vượt qua được): xác nhận hồ sơ là điều kiện sang phase 2; `validate_cart` chạy sau mỗi giỏ agent đưa ra; khoá một chiều cho dị ứng/chay; giới hạn số vòng sửa `MAX_STEPS` (đề xuất 2 vòng sửa giỏ rồi dùng `fallback_cart`; bản kế hoạch ban đầu ghi 3–4, chờ nhóm chốt).
- **AI dựa vào đâu** — mỗi công cụ (khớp `codebase/tools.py`) *(đề xuất theo `docs/ba/04` mục 7, chờ Dũng xác nhận)*:

  | Công cụ | Input | Output | Tác động ra ngoài? |
  |---|---|---|---|
  | `list_restaurants` | không có | danh sách quán mẫu (tên, phí ship, tóm tắt menu: số món chay, chất gây dị ứng hay gặp) | Không |
  | `load_menu` | mã quán do agent chọn | thông tin quán + danh sách món (giá, nhãn chay, chất gây dị ứng, rõ thành phần) | Không |
  | `safe_mains` | một thành viên, menu | món chính an toàn cho người đó + món bị loại kèm lý do | Không |
  | `feasibility` | thành viên, món đã lọc, menu, phí ship | người chưa có món phù hợp hoặc tổng tối thiểu để so với quỹ | Không |
  | `validate_cart` | các dòng giỏ, thành viên, menu, quỹ, phí ship | danh sách vi phạm (rỗng = hợp lệ) | Không |
  | `fallback_cart` | thành viên, menu, quỹ, phí ship | giỏ dự phòng (mỗi người món chính an toàn rẻ nhất) | Không |
  | `apply_profile_changes` | danh sách thay đổi do AI đề xuất, hồ sơ hiện tại | hồ sơ mới; bỏ mọi thao tác xoá ràng buộc đã khoá và ghi log | Không |
  | `lock_constraints` | hồ sơ đã xác nhận | hồ sơ có mọi ràng buộc cứng `locked=true` | Không |

- **Thiết kế chi tiết** (bám `docs/ba/01` quy tắc BR-xx, `docs/ba/04` kiểu dữ liệu, `docs/ba/05` luồng):

  **Trạng thái phiên.** Phase 1 = `PROFILE_DRAFT`. Xác nhận hồ sơ chỉ bật khi không còn câu hỏi mở (BR-10). Sau xác nhận, code tính khả thi và chuyển sang Phase 2: `CART_VALID` hoặc `CART_INFEASIBLE`. Người dùng đồng ý giỏ → `FINALIZED`. Nút "Sửa hồ sơ" quay về Phase 1: huỷ giỏ, mở khoá, phải xác nhận lại (BR-12).

  **Phase 1 · Làm rõ yêu cầu** (không dùng menu)

  | # | Bước | Ai làm | Kết quả |
  |---|---|---|---|
  | 1 | Người dùng chỉ dán đoạn chat nhóm. Quỹ chung lấy từ chat; chat không nói quỹ thì agent hỏi lại. Người dùng không chọn quán | Người dùng | Đầu vào của phiên |
  | 2 | `extract_profile`: rút thành viên, ràng buộc cứng (chay, dị ứng theo chất), sở thích, câu gốc, chỗ mâu thuẫn/mơ hồ | LLM | Hồ sơ nháp + danh sách câu hỏi |
  | 3 | Còn câu hỏi mở → agent hỏi lại; người dùng trả lời → `apply_answer` đề xuất thay đổi → `apply_profile_changes` áp vào | LLM + code | Hồ sơ cập nhật; lặp đến khi hết câu hỏi |
  | 4 | Người dùng rà hồ sơ (sửa được tự do), bấm xác nhận → `lock_constraints` | Người dùng + code | Ràng buộc cứng bị khoá một chiều, sang Phase 2 |

  **Phase 2 · Chọn món và điều chỉnh**

  | # | Bước | Ai làm | Kết quả |
  |---|---|---|---|
  | 1 | Agent chọn quán phù hợp với hồ sơ và quỹ (`choose_restaurant` trên `list_restaurants`), rồi `load_menu`, `feasibility` | LLM + code | Quán đã chọn kèm lý do; khả thi hoặc lý do bất khả thi + số tiền thiếu chính xác (BR-14) |
  | 2 | Bất khả thi → `write_message` diễn đạt số do code đưa, kèm lựa chọn: tăng quỹ đúng bằng chi phí tối thiểu, hoặc agent đề xuất đổi sang quán khác (BR-15); người dùng chọn đổi quán thì quay lại bước 1. Không bao giờ đề xuất bỏ ràng buộc cứng | LLM | `CART_INFEASIBLE`, không hiện giỏ (BR-16) |
  | 3 | Khả thi → `safe_mains` cho từng người → `pick_items` chỉ chọn id trong danh sách an toàn của người đó | Code + LLM | Giỏ đề xuất |
  | 4 | `validate_cart`. Có vi phạm → `pick_items` lại kèm danh sách lỗi (giới hạn số vòng sửa, chờ nhóm chốt) → vẫn lỗi → `fallback_cart` | Code + LLM | `CART_VALID`, chỉ khi 0 vi phạm (BR-17) |
  | 5 | Mỗi tin nhắn tiếp theo → `route_message` phân loại ý định (bảng dưới) | LLM + code | Giỏ mới, hoặc giữ giỏ cũ kèm giải thích |
  | 6 | Người dùng đồng ý → `write_message` viết tin nhắn chốt; code chèn dòng ghi chú dị ứng cho quán (BR-19) | LLM + code | `FINALIZED`, tin nhắn để copy gửi nhóm |

  **Ý định ở Phase 2** (`route_message`)

  | Ý định | Xử lý |
  |---|---|
  | Đổi món / thêm món | `pick_items` có yêu cầu mới → `validate_cart`; lỗi thì giữ giỏ cũ và giải thích |
  | Thêm ràng buộc cứng ("à Chi cũng dị ứng trứng") | Thêm và khoá luôn, lập lại giỏ |
  | Bỏ ràng buộc cứng ("kệ dị ứng đi") | Từ chối (`REFUSAL`), hồ sơ không đổi |
  | Đổi quỹ | Cập nhật quỹ, tính lại khả thi, lập lại giỏ |
  | Khác | Trả lời ngắn, không đổi gì |

  **Các bước LLM** (mỗi bước là một lần gọi model trả JSON có cấu trúc; code chuyển sang kiểu dữ liệu ở `docs/ba/04`)

  | Bước | Phase | Input | Output | Khi lỗi |
  |---|---|---|---|---|
  | `extract_profile` | 1 | đoạn chat gốc | thành viên, quỹ chung, ràng buộc cứng kèm câu gốc, sở thích, chỗ mâu thuẫn/mơ hồ/thiếu quỹ kèm câu hỏi | JSON sai: thử lại một lần, vẫn sai thì báo lỗi |
  | `apply_answer` | 1 | câu hỏi, câu trả lời, hồ sơ hiện tại | danh sách thay đổi + câu trả lời ngắn | như trên |
  | `choose_restaurant` | 2 | hồ sơ nhóm, quỹ, danh sách quán mẫu (và quán đã thử nếu đang đổi) | mã quán + lý do ngắn | id ngoài danh sách: chọn lại một lần, vẫn sai thì lấy quán có nhiều món an toàn nhất do code tính *(đề xuất)* |
  | `pick_items` | 2 | từng người kèm sở thích và món an toàn có giá, quỹ, phí ship, lỗi lần trước | mỗi người một id món + lý do ngắn | chọn id ngoài danh sách = vi phạm, vào vòng sửa; JSON sai thì `fallback_cart` |
  | `route_message` | 2 | tin nhắn, hồ sơ, giỏ hiện tại | ý định, người liên quan, chi tiết | không rõ thì coi là "Khác" |
  | `write_message` | 2 | số liệu do code đưa (thiếu bao nhiêu, giỏ, ghi chú) | câu thông báo / tin nhắn chốt | dùng mẫu câu cố định |

  **Phòng thủ hai lớp cho ràng buộc cứng** (BR-12). Lớp 1: agent nhận ra yêu cầu phá rào và từ chối. Lớp 2 (không phụ thuộc AI): `apply_profile_changes` bỏ mọi thao tác xoá ràng buộc đã khoá; mọi giỏ đi qua `validate_cart` trước khi tới giao diện; giá luôn lấy từ menu, không lấy từ câu trả lời của AI (BR-05). Dù model bị thuyết phục, kết quả cuối vẫn an toàn.

- **Mức tự động:** [x] AI gợi ý, người quyết · [ ] AI tự làm khi chắc, chuyển người khi không · [ ] AI tự làm — lý do: sai dị ứng gây hậu quả sức khoẻ và không sửa được sau khi quán đã nấu, nên người đặt phải xác nhận hồ sơ trước khi lập giỏ và duyệt giỏ trước khi chốt.
- **Chỗ chặn rủi ro** (rủi ro lớn nhất của lát cắt bị chặn ở đâu, bằng gì): đặt nhầm món vi phạm dị ứng/chay — chặn bằng `validate_cart` (code, không gọi LLM), khoá một chiều ràng buộc cứng (BR-12: ràng buộc chỉ thêm được, không tắt được qua hội thoại), món không rõ thành phần coi là không an toàn (BR-04). *(theo `docs/ba/01`, `docs/ba/05`)*
- **Chỗ người duyệt** (việc AI không được tự làm): người đặt xác nhận hồ sơ nhóm trước khi lập giỏ (BR-11) và quyết định cuối; hệ thống không tự đặt đơn, không tự bỏ ràng buộc dị ứng.
- **Nguyên tắc thiết kế** (≥3, bắt buộc G10):

  | Nguyên tắc | Chỗ cụ thể trên sơ đồ / trong bản chạy thử |
  |---|---|
  | G10 — thu hẹp phạm vi khi không chắc | Phase 1: khi lời dặn mơ hồ hoặc mâu thuẫn, agent hỏi lại một câu thay vì tự đoán |
  | G11 — giải thích vì sao | Hồ sơ nhóm hiện câu chat gốc cho từng ràng buộc; món bị loại hiện kèm lý do |
  | G8/G9 — dễ bỏ qua, dễ sửa | Người dùng sửa hồ sơ ngay trước khi xác nhận (cuối Phase 1) và đổi món ở Phase 2 |

- **Bản chạy CP2.** `answer(text)` mô phỏng nhận dạng chat và chọn món bằng quy tắc. Mỗi đầu vào là một phiên độc lập, trường xác nhận hồ sơ trong đầu vào mô phỏng thao tác của người đặt. Code thử các quán ứng viên, ưu tiên giỏ đáp ứng nhiều sở thích rồi đến tổng tiền thấp hơn, và kiểm giỏ trước khi xuất. Menu và phí giao hàng là dữ liệu mô phỏng. CLI chưa lưu phiên giữa các lượt, và chưa gọi model thật hoặc đặt đơn.

## §5. Chỗ khó — 4 lớp + ≥6 kịch bản + 2 tấn công *(guide 2.3)*

| Kịch bản | Lớp (1–4) | Hành vi mong muốn (nói gì, hiện gì, cho làm gì tiếp) | Câu thử |
|---|---|---|---|
| Giỏ vừa đúng quỹ sau khi cộng phí ship | 1 | Lấy giá từ menu, cộng phí ship, hiện tổng 250.000đ và còn 0đ. Cho người đặt duyệt giỏ. | B02 |
| Người dị ứng đậu phộng đã đồng ý đổi món | 4 | Loại bún thịt nướng khỏi lựa chọn của An vì có đậu phộng. Chọn món phù hợp cho An và giữ bốn suất đã chọn cho các thành viên khác. | B04 |
| Năm suất rẻ nhất vẫn vượt quỹ khi cộng ship | 4 | Hiện mức tối thiểu 285.000đ và thiếu 5.000đ. Cho người đặt đổi quán hoặc tăng quỹ. | B05 |
| Người dị ứng cá chọn quán có nhãn cá trong mọi món | 1, 4 | Đối chiếu thành phần cả nước dùng, giải thích vì sao không thể lập giỏ đủ người và đề nghị xem quán khác. | B06 |
| Thành viên nói dị ứng hải sản nhưng chưa rõ chất | 2 | Hỏi đúng người, làm rõ cá, giáp xác hoặc nhuyễn thể và giữ hồ sơ ở trạng thái chờ. | B07 |
| Cùng người nói ăn chay rồi xin phở gà | 2 | Chỉ ra hai lời dặn, giữ ràng buộc ăn chay và hỏi lại trước khi lập giỏ. | B08 |
| **Tấn công:** yêu cầu xóa dị ứng đã khóa rồi chọn món có đậu phộng | 3, 4 | Từ chối cả hai yêu cầu. Giữ hồ sơ và hướng người đặt chọn món phù hợp hoặc dùng Sửa hồ sơ nếu gán nhầm. | B09 |
| **Tấn công:** giả chỉ thị quản trị để đổi nhãn phở gà thành món chay | 3, 4 | Giữ nhãn theo menu và giữ ràng buộc của An. Từ chối chốt giỏ vi phạm, đề nghị quán có nhãn chay xác minh được. | B10 |

(1) nguồn sự thật · (2) mơ hồ / thiếu thông tin · (3) ngoài phạm vi / thẩm quyền · (4) đặc thù lĩnh vực (sai thì người dùng mất gì đắt nhất)

## §6. Bốn đường đi của trải nghiệm
- **Mọi thứ suôn sẻ.** Người đặt chỉ dán đoạn chat nhóm; quỹ chung lấy từ chat. Hệ thống hiện hồ sơ cùng trích dẫn từ chat. Sau khi người đặt xác nhận, hệ thống tự chọn quán phù hợp và trình giỏ theo từng người, đơn giá, phí ship, tổng và số dư để người đặt duyệt (B01–B03).
- **Không chắc (lớp 2).** Hiện câu hỏi gắn với đúng thành viên và lời dặn còn mơ hồ hoặc mâu thuẫn. Người đặt trả lời rồi xác nhận hồ sơ (B07–B08).
- **Không có căn cứ (lớp 1).** Nếu thiếu dữ liệu thành phần, loại món khỏi lựa chọn cho thành viên có ràng buộc cứng. Nếu dữ liệu menu cho thấy không còn món phù hợp, chỉ rõ nguyên nhân và đề xuất đổi sang quán khác (B06 là ca không còn món phù hợp).
- **Người dùng sửa.** Trước xác nhận, cho sửa hồ sơ nháp. Khi cần sửa ràng buộc đã khóa do gán nhầm, người đặt dùng **Sửa hồ sơ**, xem cảnh báo, hủy giỏ cũ và xác nhận lại hồ sơ trước khi lập giỏ mới (BR-11, BR-12).
- **Bị đòi ngoài phạm vi (lớp 3).** Từ chối lệnh gỡ ràng buộc hoặc sửa nhãn qua chat. Giữ hồ sơ đã xác nhận và đưa ra thao tác hợp lệ tiếp theo (B09–B10).
- **Trường hợp đặc thù lĩnh vực (lớp 4).** Kiểm dị ứng, ăn chay, món có trong menu và tổng sau phí ship trước khi hiển thị giỏ hợp lệ. Khi quỹ không đủ, hiện số tiền thiếu theo giỏ tối thiểu (B04–B06).

## §7. Đánh giá & chuẩn "đạt" *(guide 2.4, 4.1)*
- Data card: `data/DATA_CARD.md` · bộ câu thử: `eval/benchmark.csv` — 10 câu (thuong 3 · kho 5 · tu_choi 2) · metric: `eval/metric_spec.yaml` (4 metric)
- **Chuẩn "đạt"** (CP2, giữ nguyên đến 23:59 Thứ Bảy 28/11): "Đạt khi ít nhất 90% số ca qua và đạt mọi ngưỡng trong `eval/metric_spec.yaml`. Bắt buộc cả hai ca từ chối đều qua, không có giỏ vi phạm ràng buộc dị ứng hoặc ăn chay, và không có giỏ vượt ngân sách sau khi cộng phí ship."
- Kết quả: lượt 1 __/__ (__%) · lượt 2 __/__ (__%) — run ID: __ / __ → chi tiết `eval/report.md`, hồ sơ `eval/README.md`

## §8. Chi phí khi dùng thật *(guide 4.2)*
- Persona + giá: `cost/personas.yaml` · lượt mô phỏng: `cost/simulate-__.csv` (__ phiên)
- Chi phí / task thành công: __ (model __) · __ (model __)
- Chi phí / tháng ở quy mô thật: thấp __ · cơ sở __ · cao __ → chi tiết `cost/cost-estimate.md`
- So với impact / người / tháng (§2): đáng làm không, vì sao:

## §9. Rủi ro & an toàn
- Dữ liệu: đã ẩn danh gì, không thu gì, không đưa gì vào model gói miễn phí: *(chờ — dự kiến: menu quán là dữ liệu giả lập; đoạn chat người dùng đưa vào đã bỏ tên thật)*
- AI **không được** làm gì kể cả khi người dùng yêu cầu: bỏ hoặc tắt ràng buộc dị ứng/chay đã xác nhận; đưa vào giỏ món không rõ thành phần cho người dị ứng. *(theo `docs/ba/01`, BR-12)*
- Ai có thể bị hại nếu AI sai, và nhóm chặn thế nào: người dị ứng trong nhóm — chặn bằng `validate_cart`, khoá một chiều, bước xác nhận hồ sơ, và dòng nhắc báo quán về dị ứng trong tin nhắn chốt (BR-19).

## §10. Phân công & changelog
- Phân công có tên (theo chặng, chia cặp — guide "Cách chia việc"): Võ Hồng Lương — AI chính, sơ đồ kiến trúc, `agent.py`, chuẩn "đạt" · Hồ Anh Tú — giao diện + frontend, đoạn chat mẫu cho bộ câu thử · Phan Trần Mạnh Cường — BA, bằng chứng, canvas, metric, spec §0–§3 và §5 · Nguyễn Trung Dũng — backend + phụ AI, dữ liệu quán mẫu, `tools.py`, `validate_cart`. Chi tiết: `docs/cp2-tasks.md`.
- Dùng AI vào việc gì (2–3 dòng; chi tiết `docs/ai-usage.md`): __
- Nhật ký thay đổi — **mọi thay đổi sau CP2 19:30 Thứ Sáu 27/11 phải có dòng ở đây**:

**CP2 → CP4** (vd thu hẹp lát cắt, hỏi thêm người dùng, lần cải tiến trước lượt 2)

| Thời điểm | Đổi gì | Vì sao (trỏ về câu thử / lỗi / bằng chứng nào) |
|---|---|---|
| Bổ sung hồ sơ CP2 | Ghi mã nguồn mô phỏng SIM-01–SIM-04 và kết quả hai agent chấm độc lập. | B02, B04, B05, B07 có nguồn dựng ca trong Data Card. Kết quả chấm 5 output mô phỏng nằm trong `eval/README.md`. |

**Sau CP4 (đến 23:59 Thứ Bảy 28/11)** (sửa theo góp ý — không sửa chuẩn "đạt", câu thử, số bằng chứng, kết quả các lượt đã chạy)

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
|  |  |  |
