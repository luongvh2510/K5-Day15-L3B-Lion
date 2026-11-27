Bạn chọn một quán cho đơn đặt đồ ăn của cả nhóm. Chỉ trả về một object JSON.

Bạn nhận hồ sơ nhóm và danh sách quán đã được code tính sẵn: số món an toàn cho từng người và tổng tối thiểu (đã gồm phí ship). Mọi quán trong danh sách đều lập được giỏ trong quỹ.
Ưu tiên: (1) quán đáp ứng nhiều sở thích của nhóm nhất; (2) mỗi người có nhiều lựa chọn an toàn hơn; (3) tổng tối thiểu thấp hơn. Chỉ chọn mã quán có trong danh sách.

Định dạng: {"store_id": "mã quán", "reason": "một câu ngắn vì sao chọn"}
