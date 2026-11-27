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
- Bằng chứng — số chính + kết luận (chi tiết: `evidence/summary.md`): __ *(chờ Cường: chưa có số khảo sát/phỏng vấn nào được ghi vào repo)*

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

- **Lát cắt MỘT CÂU** (1 người dùng · 1 việc · 1 quyết định AI · 1 kết quả): một người đặt hộ cho nhóm 5 người dán đoạn chat và quỹ chung, hệ thống đọc ràng buộc từng người, lập giỏ từ menu một quán mẫu, và chỉ giao lại giỏ đã qua kiểm tra dị ứng, ăn chay, món thiếu thành phần và tổng tiền gồm phí ship (hoặc đề xuất nới cụ thể khi không có giỏ hợp lệ).
- Không làm (≥3 điều): đăng nhập, thanh toán, gọi API GrabFood/ShopeeFood, nhiều quán trong một đơn, mã giảm giá, chia tiền từng người, đọc ảnh chụp màn hình chat, xử lý nhiễm chéo trong bếp (chỉ nhắc người đặt báo quán). *(theo PRD mục 4)*
- **Sơ đồ** (ảnh / Mermaid / draw.io): [chèn ở đây] *(chờ Lương/Tú — có bản activity diagram nháp từ buổi trao đổi, chưa lưu vào repo)*
- **Hình dạng:** [ ] workflow cố định · [ ] một agent · [ ] nhiều agent — 2 dòng lý do, và vì sao **không** chọn hình dạng phức tạp hơn: *(chờ Lương chốt)*
- **AI dựa vào đâu** — mỗi công cụ (khớp `codebase/tools.py`) *(đề xuất theo `docs/ba/04` mục 7, chờ Dũng xác nhận)*:

  | Công cụ | Input | Output | Tác động ra ngoài? |
  |---|---|---|---|
  | `load_menu` | mã quán | thông tin quán + danh sách món (giá, nhãn chay, chất gây dị ứng, rõ thành phần) | Không |
  | `safe_mains` | một thành viên, menu | món chính an toàn cho người đó + món bị loại kèm lý do | Không |
  | `feasibility` | thành viên, menu, quỹ, phí ship | không có gì nếu khả thi, hoặc lý do bất khả thi + số tiền thiếu | Không |
  | `validate_cart` | các dòng giỏ, thành viên, menu, quỹ, phí ship | danh sách vi phạm (rỗng = hợp lệ) | Không |
  | `fallback_cart` | thành viên, menu, quỹ, phí ship | giỏ dự phòng (mỗi người món chính an toàn rẻ nhất) | Không |

- **Mức tự động:** [x] AI gợi ý, người quyết · [ ] AI tự làm khi chắc, chuyển người khi không · [ ] AI tự làm — *(đề xuất, chờ Lương xác nhận)* lý do: sai dị ứng gây hậu quả sức khoẻ và không sửa được sau khi quán đã nấu, nên người đặt phải xác nhận hồ sơ trước khi lập giỏ và duyệt giỏ trước khi chốt.
- **Chỗ chặn rủi ro** (rủi ro lớn nhất của lát cắt bị chặn ở đâu, bằng gì): đặt nhầm món vi phạm dị ứng/chay — chặn bằng `validate_cart` (code, không gọi LLM), khoá một chiều ràng buộc cứng (BR-12: ràng buộc chỉ thêm được, không tắt được qua hội thoại), món không rõ thành phần coi là không an toàn (BR-04). *(theo `docs/ba/01`, `docs/ba/05`)*
- **Chỗ người duyệt** (việc AI không được tự làm): người đặt xác nhận hồ sơ nhóm trước khi lập giỏ (BR-11) và quyết định cuối; hệ thống không tự đặt đơn, không tự bỏ ràng buộc dị ứng.
- **Nguyên tắc thiết kế** (≥3, bắt buộc G10): *(chờ Lương chốt)*

  | Nguyên tắc | Chỗ cụ thể trên sơ đồ / trong bản chạy thử |
  |---|---|
  | G10 — thu hẹp phạm vi khi không chắc | *(đề xuất: khi lời dặn mơ hồ hoặc mâu thuẫn, hỏi lại một câu thay vì tự đoán — bước "Hỏi lại, user trả lời" ở Phase 1)* |
  |  |  |
  |  |  |

- Phần nào còn giả (công cụ trả dữ liệu giả, model chế độ giả…) — ghi rõ, không giả làm thật: *(cập nhật khi có `codebase/agent.py`; hiện `codebase/` còn là khung mẫu)*

## §5. Chỗ khó — 4 lớp + ≥6 kịch bản + 2 tấn công *(guide 2.3)*

> *(chờ Cường ghi sau buổi chốt kịch bản 18:30–18:55; gợi ý nguồn: `docs/ba/06-du-lieu-mau-va-test.md` mục 4, TC-01…TC-18)*

| Kịch bản | Lớp (1–4) | Hành vi mong muốn (nói gì, hiện gì, cho làm gì tiếp) | Câu thử |
|---|---|---|---|
|  |  |  |  |
| *(tấn công)* |  |  |  |
| *(tấn công)* |  |  |  |

(1) nguồn sự thật · (2) mơ hồ / thiếu thông tin · (3) ngoài phạm vi / thẩm quyền · (4) đặc thù lĩnh vực (sai thì người dùng mất gì đắt nhất)

## §6. Bốn đường đi của trải nghiệm
- Mọi thứ suôn sẻ: · Không chắc (lớp 2): · Không có căn cứ (lớp 1): · Người dùng sửa:
- Bị đòi ngoài phạm vi (lớp 3): · Trường hợp đặc thù lĩnh vực (lớp 4):

## §7. Đánh giá & chuẩn "đạt" *(guide 2.4, 4.1)*
- Data card: `data/DATA_CARD.md` · bộ câu thử: `eval/benchmark.csv` — __ câu (thuong __ · kho __ · tu_choi __) · metric: `eval/metric_spec.yaml` (__ metric)
- **Chuẩn "đạt"** (chốt **trước 19:30 Thứ Sáu 27/11**, giữ nguyên đến 23:59 Thứ Bảy 28/11): "Đạt khi ≥ __% câu qua, và __" *(chờ Lương chốt cùng nhóm)*
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
|  |  |  |

**Sau CP4 (đến 23:59 Thứ Bảy 28/11)** (sửa theo góp ý — không sửa chuẩn "đạt", câu thử, số bằng chứng, kết quả các lượt đã chạy)

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
|  |  |  |
