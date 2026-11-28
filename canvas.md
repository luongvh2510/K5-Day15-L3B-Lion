# Canvas — Lion · Track D

> CP2 · Lion · D2 đặt đơn nhóm có ràng buộc ăn uống.

| # | Dòng | Nhóm điền |
|---|---|---|
| 1 | Track + lát cắt dự kiến | **Track D (Thương mại điện tử)**, hướng D2: từ đoạn chat nhóm lộn xộn ra giỏ đồ ăn an toàn, có hội thoại nhiều lượt. Lát cắt: một người đặt hộ cho nhóm 5 người, từ đoạn chat nhóm và quỹ chung 250k–300k đến một giỏ hàng đã kiểm. |
| 2 | Người dùng chính | Người cầm quỹ chung đi đặt đồ ăn hộ cả nhóm 4–6 người (nhóm bạn, team văn phòng, ban hậu cần CLB). Họ đặt trọn gói một đơn và mọi người chỉ nhắn rải rác vào nhóm Zalo/Messenger. |
| 3 | Pain một câu | Người cầm quỹ đặt hộ phải đọc lại chat để tránh sót lời dặn ăn chay, dị ứng và theo dõi tổng tiền gồm phí ship. Nếu phát hiện vấn đề muộn, họ phải chọn món lại hoặc đổi quán. Thời gian 15–20 phút mỗi lần là *tự ước tính*, đang chờ kiểm chứng. |
| 4 | Bằng chứng và tiến độ CP3 | **17/20** người trong bảng khảo sát từng đặt hộ nhóm trong 30 ngày qua. Trong 17 người này, **11/17** phải sửa món, đổi quán hoặc không đặt được ở lần gần nhất, và **5/17** báo sót lời dặn. **Phỏng vấn 3 người ngoài nhóm** (nguồn đạt ngưỡng): **3/3** phải hỏi lại, sửa giỏ hoặc đổi quán, **2/3** có người ăn chay hoặc dị ứng. Xem số đếm, trích dẫn và điều kiện còn thiếu tại [evidence/summary.md](evidence/summary.md). |
| 5 | **Lát cắt MỘT CÂU** | Một người đặt hộ nhóm 5 người chỉ dán đoạn chat nhóm (quỹ chung 250.000–300.000đ nằm trong chat). Hệ thống đọc ràng buộc, hỏi lại khi cần, tự chọn một quán phù hợp rồi trả giỏ đề xuất đã kiểm sau khi hồ sơ được xác nhận, hoặc giải thích vì sao chưa thể lập giỏ và đề xuất tăng quỹ hay đổi quán. |
| 6 | AI tự làm đến đâu + lý do | AI tự đọc chat, trích ràng buộc, chọn món và thương lượng. Code kiểm cứng mọi giỏ (dị ứng, chay, giá, phí ship), và AI không được tự bỏ ràng buộc dị ứng. Lý do: sai dị ứng gây hậu quả sức khoẻ, người cầm quỹ không đủ thời gian soát lại từng món. |
| 7 | Phân công có tên | **Võ Hồng Lương (đội trưởng):** AI chính, đọc chat, lập giỏ, thương lượng đa lượt · **Nguyễn Trung Dũng:** backend, dữ liệu quán mẫu, code kiểm giỏ, bộ test, phụ AI · **Hồ Anh Tú:** thiết kế giao diện và frontend · **Phan Trần Mạnh Cường:** BA, bằng chứng pain, impact, kịch bản demo, slide. Chặng khám phá: cả nhóm cùng phỏng vấn và khảo sát. |

### Đã đổi gì so với CP1

- Đầu vào chỉ còn đoạn chat nhóm: quỹ chung lấy từ chat (chat không nói thì hỏi lại), người đặt không tự chọn quán. Hệ thống tự chọn quán phù hợp và có thể đề xuất đổi quán khi không lập được giỏ.
- Chia luồng thành 2 phase: Phase 1 làm rõ yêu cầu cả nhóm (hỏi lại khi mâu thuẫn hoặc mơ hồ, người đặt xác nhận hồ sơ); Phase 2 chọn món và điều chỉnh theo tin nhắn của người đặt. Chỉ lập giỏ sau khi hồ sơ được xác nhận.
- Chuyển các rủi ro dị ứng, ăn chay và phí ship thành 10 ca thử và 4 metric. Chốt ngưỡng 90% cùng các điều kiện bắt buộc trong §7 của [spec.md](spec.md).
