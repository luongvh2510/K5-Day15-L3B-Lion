import unittest
from unittest import mock

import _path  # noqa: F401
import core


def member(name, vegetarian=False, allergens=None):
    return {"name": name, "vegetarian": vegetarian, "allergens": dict(allergens or {}), "preferences": [], "quotes": []}


def profile(members, budget=300000, questions=None):
    return {"budget": budget, "members": members, "questions": questions or []}


class TestProfile(unittest.TestCase):
    def test_locked_allergen_cannot_be_removed(self):
        p = profile([member("Bình", allergens={"peanut": "đậu phộng"})])
        new, dropped = core.apply_changes(p, [{"op": "REMOVE_ALLERGEN", "member": "Bình", "tag": "peanut"}], locked=True)
        self.assertEqual(new["members"][0]["allergens"], {"peanut": "đậu phộng"})
        self.assertEqual(len(dropped), 1)

    def test_unlocked_allergen_can_be_removed(self):
        p = profile([member("Bình", allergens={"peanut": "đậu phộng"})])
        new, dropped = core.apply_changes(p, [{"op": "REMOVE_ALLERGEN", "member": "Bình", "tag": "peanut"}], locked=False)
        self.assertEqual(new["members"][0]["allergens"], {})
        self.assertEqual(dropped, [])
        self.assertEqual(p["members"][0]["allergens"], {"peanut": "đậu phộng"})

    def test_missing_budget_blocks_confirm(self):
        self.assertFalse(core.can_confirm(profile([member("An")], budget=None)))

    def test_open_question_blocks_confirm(self):
        q = [{"id": "q1", "member": "An", "text": "?", "status": "OPEN"}]
        self.assertFalse(core.can_confirm(profile([member("An")], questions=q)))
        self.assertTrue(core.can_confirm(profile([member("An")])))


if __name__ == "__main__":
    unittest.main()


def first_pick(members, options, budget, shipping, errors):
    return {"picks": [{"member": m["name"], "item_id": options[m["name"]][0]["id"], "reason": "test"} for m in members]}


def session_with(members, budget=300000, candidates=None, questions=None):
    with mock.patch("core.llm_steps.extract_profile", return_value=profile(members, budget, questions)):
        return core.start("chat", shipping=15000, candidates=candidates)


FIVE = ["An", "Bình", "Chi", "Dũng", "Hà"]


class TestFlow(unittest.TestCase):
    def test_confirm_blocked_with_open_question(self):
        q = [{"id": "q1", "member": "An", "text": "?", "status": "OPEN"}]
        s = core.confirm(session_with([member("An")], questions=q, candidates=["store_01"]))
        self.assertEqual(s["status"], "PROFILE_DRAFT")
        self.assertIsNone(s["cart"])

    def test_valid_cart_for_five_people(self):
        s = session_with([member(n) for n in FIVE], candidates=["store_01"])
        pick = {"picks": [{"member": n, "item_id": "dish_009", "reason": "x"} for n in FIVE]}
        with mock.patch("core.llm_steps.pick_items", return_value=pick):
            s = core.confirm(s)
        self.assertEqual(s["status"], "CART_VALID")
        self.assertEqual(s["cart"]["total"], 285000)
        self.assertEqual(s["cart"]["remaining"], 15000)
        self.assertEqual(s["cart"]["built_by"], "AI")

    def test_over_budget_reports_shortfall(self):
        s = session_with([member(n) for n in FIVE], budget=280000, candidates=["store_01"])
        with mock.patch("core.llm_steps.pick_items") as pick:
            s = core.confirm(s)
        self.assertEqual(s["status"], "CART_INFEASIBLE")
        self.assertEqual(s["infeasible"]["min_total"], 285000)
        self.assertEqual(s["infeasible"]["shortfall"], 5000)
        pick.assert_not_called()

    def test_pick_outside_safe_list_falls_back(self):
        members = [member("An", allergens={"peanut": "đậu phộng"})] + [member(n) for n in FIVE[1:]]
        s = session_with(members, candidates=["store_02"])
        bad = {"picks": [{"member": n, "item_id": "dish_016", "reason": "x"} for n in FIVE]}
        with mock.patch("core.llm_steps.pick_items", return_value=bad) as pick:
            s = core.confirm(s)
        self.assertEqual(pick.call_count, core.MAX_REPAIR + 1)
        self.assertEqual(s["status"], "CART_VALID")
        self.assertEqual(s["cart"]["built_by"], "FALLBACK")
        an = next(l for l in s["cart"]["lines"] if l["member"] == "An")
        self.assertNotEqual(an["item_id"], "dish_016")
        menu = core.tools.load_menu("store_02")
        self.assertEqual(core.tools.validate_cart(s["profile"]["members"], [l["item_id"] for l in s["cart"]["lines"]], menu, 300000, 15000), [])

    def test_remove_hard_after_lock_is_refused(self):
        members = [member("An", allergens={"peanut": "đậu phộng"})] + [member(n) for n in FIVE[1:]]
        s = session_with(members, candidates=["store_02"])
        with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
        before = s["cart"]
        route = {"intent": "REMOVE_HARD", "member": "An", "detail": "bỏ dị ứng", "amount": None, "tag": "peanut"}
        with mock.patch("core.llm_steps.route_message", return_value=route):
            s = core.send(s, "kệ dị ứng của An đi")
        self.assertEqual(s["messages"][-1]["kind"], "REFUSAL")
        self.assertEqual(s["profile"]["members"][0]["allergens"], {"peanut": "đậu phộng"})
        self.assertEqual(s["cart"], before)

    def test_add_hard_rebuilds_cart(self):
        s = session_with([member(n) for n in FIVE], candidates=["store_01"])
        with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
            route = {"intent": "ADD_HARD", "member": "Chi", "detail": "dị ứng trứng", "amount": None, "tag": "egg"}
            with mock.patch("core.llm_steps.route_message", return_value=route):
                s = core.send(s, "à Chi cũng dị ứng trứng")
        chi = next(m for m in s["profile"]["members"] if m["name"] == "Chi")
        self.assertIn("egg", chi["allergens"])
        menu = core.tools.load_menu("store_01")
        self.assertEqual(core.tools.validate_cart(s["profile"]["members"], [l["item_id"] for l in s["cart"]["lines"]], menu, 300000, 15000), [])

    def test_vegetarian_member_gets_vegan_dish(self):
        members = [member("An", vegetarian=True)] + [member(n) for n in FIVE[1:]]
        with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(session_with(members, candidates=["store_08"]))
        an = next(l for l in s["cart"]["lines"] if l["member"] == "An")
        self.assertIn(an["item_id"], {"dish_077", "dish_078", "dish_080"})
        s = core.confirm(session_with(members, candidates=["store_01"]))
        self.assertEqual(s["status"], "CART_INFEASIBLE")
        self.assertEqual(s["infeasible"]["kind"], "NO_SAFE_ITEM")
        self.assertEqual(s["infeasible"]["members"], ["An"])

    def test_render_valid_cart_mentions_total_and_check(self):
        s = session_with([member(n) for n in FIVE], candidates=["store_01"])
        with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
        text = core.render(s)
        self.assertIn("Đã kiểm theo yêu cầu đã xác nhận và menu quán", text)
        self.assertIn("%s" % format(s["cart"]["total"], ","), text)
