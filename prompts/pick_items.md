Bạn chọn món chính cho từng người trong nhóm. Chỉ trả về một object JSON.

Mỗi người chỉ được chọn đúng một món, và chỉ được chọn mã món nằm trong danh sách món an toàn của chính người đó (code đã lọc theo ăn chay và dị ứng). Không tự viết giá.
Ưu tiên: (1) tổng món cộng phí ship không vượt quỹ; (2) đáp ứng sở thích của từng người; (3) tổng rẻ hơn. Không cần tiêu hết quỹ.
Nếu có danh sách lỗi của lần chọn trước, sửa đúng các lỗi đó.

Định dạng: {"picks": [{"member": "tên", "item_id": "mã món", "reason": "tối đa 12 từ"}]}
