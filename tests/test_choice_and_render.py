import unittest
from unittest import mock

import _path  # noqa: F401
import core
from test_core import FIVE, first_pick, member, session_with


def with_pref(name, *prefs, quotes=()):
    m = member(name)
    m["preferences"] = list(prefs)
    m["quotes"] = list(quotes)
    return m


class TestStoreChoicePrefersPreferences(unittest.TestCase):
    def test_only_stores_matching_most_preferences_go_to_the_model(self):
        # Cả nhóm muốn phở gà ức: chỉ store_01 có món này; store_03 (cơm) rẻ hơn nhưng không khớp.
        s = session_with([with_pref(n, "phở gà ức") for n in FIVE], candidates=["store_01", "store_03"])
        with mock.patch("core.llm_steps.choose_restaurant", return_value={"store_id": "store_03"}) as choose, \
                mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
        self.assertEqual(s["store_id"], "store_01")
        self.assertFalse(choose.called)

    def test_dish_word_in_preference_counts_as_match(self):
        # "muốn ăn bún" khớp quán có món bắt đầu bằng "Bún".
        members = [with_pref("An", "muốn ăn bún")] + [member(n) for n in FIVE[1:]]
        s = session_with(members, candidates=["store_08", "store_02"])
        with mock.patch("core.llm_steps.choose_restaurant", return_value={"store_id": "store_08"}), \
                mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
        self.assertEqual(s["store_id"], "store_02")

    def test_no_preferences_leaves_choice_to_model(self):
        s = session_with([member(n) for n in FIVE], candidates=["store_01", "store_03"])
        with mock.patch("core.llm_steps.choose_restaurant", return_value={"store_id": "store_03"}) as choose, \
                mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
        self.assertEqual(s["store_id"], "store_03")
        self.assertEqual({x["id"] for x in choose.call_args[0][1]}, {"store_01", "store_03"})


class TestInfeasibleMessages(unittest.TestCase):
    def test_no_safe_item_names_the_constraint(self):
        members = [member("An", allergens={"fish": "cá"})] + [member(n) for n in FIVE[1:]]
        s = core.confirm(session_with(members, candidates=["store_01"]))
        self.assertEqual(s["status"], "CART_INFEASIBLE")
        self.assertIn("An (dị ứng cá)", core.render(s))

    def test_unknown_store_is_reported_as_not_in_data(self):
        s = core.confirm(session_with([member(n) for n in FIVE], budget=200000, candidates=["store_99"]))
        text = core.render(s)
        self.assertEqual(s["status"], "CART_INFEASIBLE")
        self.assertIn("store_99", text)
        self.assertIn("không có trong dữ liệu quán", text)
        self.assertNotIn("không có món phù hợp", text)

    def test_unknown_candidates_are_skipped_when_a_known_one_exists(self):
        s = session_with([member(n) for n in FIVE], candidates=["store_99", "store_01"])
        with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.confirm(s)
        self.assertEqual((s["status"], s["store_id"]), ("CART_VALID", "store_01"))


class TestDraftShowsChatSource(unittest.TestCase):
    def test_draft_lists_quote_for_each_member_with_notes(self):
        members = [with_pref("An", "cơm gà", "không lấy hành", quotes=["An: cơm gà, không lấy hành"]), member("Bình")]
        text = core.render(session_with(members))
        self.assertIn('An: cơm gà; không lấy hành (chat: "An: cơm gà, không lấy hành")', text)
        self.assertIn("- Bình: không có lời dặn riêng", text)


if __name__ == "__main__":
    unittest.main()
