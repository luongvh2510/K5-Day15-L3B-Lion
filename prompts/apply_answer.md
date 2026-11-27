Bạn cập nhật hồ sơ nhóm đặt đồ ăn theo câu trả lời của người đặt cho một câu hỏi. Chỉ trả về một object JSON.

Trả danh sách thay đổi, không trả lại hồ sơ. Các phép được dùng:
ADD_MEMBER(member), SET_VEGETARIAN(member), UNSET_VEGETARIAN(member), ADD_ALLERGEN(member, tag, label), REMOVE_ALLERGEN(member, tag), ADD_PREFERENCE(member, text), SET_BUDGET(amount), RESOLVE_QUESTION(question_id).
Tag dị ứng chỉ được là một trong: {ALLERGEN_TAGS}. Câu trả lời đã làm rõ câu hỏi thì luôn có RESOLVE_QUESTION. Câu trả lời vẫn chưa rõ thì không RESOLVE.

Định dạng:
{"changes": [{"op": "ADD_PREFERENCE", "member": "Tuấn", "text": "cơm sườn"}, {"op": "RESOLVE_QUESTION", "question_id": "q1"}],
 "reply": "một câu ngắn xác nhận đã ghi nhận gì"}
