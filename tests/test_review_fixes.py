"""Test tái hiện các lỗi do review toàn nhánh tìm ra."""
import unittest
from unittest import mock

import _path  # noqa: F401
import agent
import core
import llm_steps
from test_core import FIVE, first_pick, member, profile, session_with
from test_llm_steps import reply


class TestReviewFixes(unittest.TestCase):
    def test_duplicate_member_names_merged(self):
        out = ('{"budget": 300000, "members": [{"name": "An", "vegetarian": false, "allergens": []},'
               '{"name": " an ", "vegetarian": false, "allergens": [{"tag": "peanut", "label": "đậu phộng"}]}], "questions": []}')
        with mock.patch("llm_steps.call_model", return_value=reply(out)):
            p = llm_steps.extract_profile("chat")
        self.assertEqual(len(p["members"]), 1)
        self.assertEqual(p["members"][0]["allergens"], {"peanut": "đậu phộng"})

    def test_duplicate_names_never_give_unsafe_cart(self):
        members = [member("An", allergens={"peanut": "đậu phộng"}), member("An")] + [member(n) for n in FIVE[1:]]
        s = session_with(members, candidates=["store_02"])
        bad = {"picks": [{"member": "An", "item_id": "dish_016", "reason": "x"}]}
        with mock.patch("core.llm_steps.pick_items", return_value=bad):
            s = core.confirm(s)
        if s["status"] == "CART_VALID":
            menu = core.tools.load_menu("store_02")
            self.assertEqual(core.tools.validate_cart(s["profile"]["members"], [l["item_id"] for l in s["cart"]["lines"]],
                                                      menu, 300000, 15000), [])

    def test_unknown_allergen_tag_rejected(self):
        p = profile([member("An")])
        new, dropped = core.apply_changes(p, [{"op": "ADD_ALLERGEN", "member": "An", "tag": "shellfish"}], locked=False)
        self.assertEqual(new["members"][0]["allergens"], {})
        self.assertEqual(len(dropped), 1)

    def test_add_hard_unknown_tag_asks(self):
        s = session_with([member(n) for n in FIVE], candidates=["store_01"])
        with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
        before = s["cart"]
        route = {"intent": "ADD_HARD", "member": "An", "detail": "dị ứng hải sản", "amount": None, "tag": "shellfish"}
        with mock.patch("core.llm_steps.route_message", return_value=route):
            s = core.send(s, "An dị ứng hải sản")
        self.assertEqual(s["messages"][-1]["kind"], "QUESTION")
        self.assertEqual(s["cart"], before)

    def test_add_hard_without_tag_asks(self):
        s = session_with([member(n) for n in FIVE], candidates=["store_01"])
        with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
        route = {"intent": "ADD_HARD", "member": "An", "detail": "dị ứng gì đó", "amount": None, "tag": None}
        with mock.patch("core.llm_steps.route_message", return_value=route):
            s = core.send(s, "An bị dị ứng")
        self.assertIs(s["profile"]["members"][0]["vegetarian"], False)
        self.assertEqual(s["messages"][-1]["kind"], "QUESTION")

    def test_locked_header_forces_lock(self):
        q = [{"id": "q1", "member": "An", "text": "?", "status": "OPEN"}]
        p = profile([member("An", allergens={"peanut": "đậu phộng"})] + [member(n) for n in FIVE[1:]], questions=q)
        remove = {"changes": [{"op": "REMOVE_ALLERGEN", "member": "An", "tag": "peanut"}], "reply": ""}
        route = {"intent": "REMOVE_HARD", "member": "An", "detail": "", "amount": None, "tag": "peanut"}
        text = ("Quán store_02. Ngân sách 300000đ. Phí ship mô phỏng 15000đ. Hồ sơ đã xác nhận và khóa: An dị ứng đậu phộng. "
                "Yêu cầu tiếp theo của người đặt: Kệ dị ứng của An đi.")
        with mock.patch("core.llm_steps.extract_profile", return_value=p), \
             mock.patch("core.llm_steps.apply_answer", return_value=remove), \
             mock.patch("core.llm_steps.route_message", return_value=route), \
             mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            out = agent.answer(text)["output"]
        self.assertIn("Không thể bỏ", out)

    def test_render_draft_without_budget(self):
        s = session_with([member("An")], budget=None)
        s["profile"]["questions"] = []
        self.assertIn("quỹ", core.render(s).lower())

    def test_answer_resolving_budget_question_without_amount_reasks(self):
        q = [{"id": "q1", "member": None, "text": "Quỹ chung của nhóm là bao nhiêu?", "status": "OPEN"}]
        s = session_with([member("An")], budget=None, questions=q)
        with mock.patch("core.llm_steps.apply_answer",
                        return_value={"changes": [{"op": "RESOLVE_QUESTION", "question_id": "q1"}], "reply": ""}):
            s = core.send(s, "không biết")
        self.assertTrue(core.open_questions(s["profile"]))
        core.render(s)

    def test_extract_profile_tolerates_string_allergens(self):
        out = '{"budget": "300k", "members": [{"name": "An", "allergens": ["peanut"]}, "rác"], "questions": ["rác"]}'
        with mock.patch("llm_steps.call_model", return_value=reply(out)):
            p = llm_steps.extract_profile("chat")
        self.assertEqual(p["budget"], 300000)
        self.assertEqual(list(p["members"][0]["allergens"]), ["peanut"])

    def test_set_budget_accepts_300k(self):
        new, _ = core.apply_changes(profile([member("An")], budget=None), [{"op": "SET_BUDGET", "amount": "300k"}], locked=False)
        self.assertEqual(new["budget"], 300000)

    def test_draft_message_without_question_goes_to_apply_answer(self):
        s = session_with([member("An"), member("Chi")])
        change = {"changes": [{"op": "ADD_ALLERGEN", "member": "Chi", "tag": "egg", "label": "trứng"}], "reply": "ok"}
        with mock.patch("core.llm_steps.apply_answer", return_value=change):
            s = core.send(s, "Chi dị ứng trứng")
        self.assertEqual(s["profile"]["members"][1]["allergens"], {"egg": "trứng"})

    def test_change_item_to_excluded_dish_refused(self):
        members = [member("An", allergens={"peanut": "đậu phộng"})] + [member(n) for n in FIVE[1:]]
        s = session_with(members, candidates=["store_02"])
        with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
        before = s["cart"]
        route = {"intent": "CHANGE_ITEM", "member": "An", "detail": "gán bún thịt nướng dish_016", "amount": None, "tag": None}
        with mock.patch("core.llm_steps.route_message", return_value=route):
            s = core.send(s, "gán bún thịt nướng cho An")
        self.assertEqual(s["messages"][-1]["kind"], "REFUSAL")
        self.assertEqual(s["cart"], before)


if __name__ == "__main__":
    unittest.main()


class TestRenderTurn(unittest.TestCase):
    def test_render_hides_info_from_previous_turn(self):
        s = session_with([member(n) for n in FIVE], candidates=["store_01"])
        s["messages"].append({"role": "assistant", "kind": "INFO", "text": "Đã ghi nhận lượt trước", "turn": s.get("turn", 0)})
        with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
        self.assertNotIn("Đã ghi nhận lượt trước", core.render(s))
