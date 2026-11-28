import unittest
from unittest import mock

import _path  # noqa: F401
import core
from test_core import first_pick, member, session_with


def valid_session_after_all_veg_stores_tried():
    """An ăn chay: chỉ store_08 và store_09 có món chay. Lập giỏ ở store_08 rồi đổi sang store_09."""
    s = session_with([member("An", vegetarian=True)])
    with mock.patch("core.llm_steps.choose_restaurant", return_value={"store_id": "store_08"}), \
            mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
        s = core.confirm(s)
        s = core.change_restaurant(s)
    return s


def valid_session_with_one_feasible_store():
    s = session_with([member("An", vegetarian=True)], candidates=["store_01", "store_09"])
    with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
        return core.confirm(s)


class TestChangeRestaurantKeepsValidCart(unittest.TestCase):
    def test_switches_when_another_store_fits(self):
        s = valid_session_after_all_veg_stores_tried()
        self.assertEqual((s["status"], s["store_id"]), ("CART_VALID", "store_09"))

    def test_action_keeps_cart_when_no_other_store_fits(self):
        s = valid_session_with_one_feasible_store()
        cart = s["cart"]
        with mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.change_restaurant(s)
        self.assertEqual((s["status"], s["store_id"], s["cart"]), ("CART_VALID", "store_09", cart))
        self.assertEqual(s["messages"][-1]["kind"], "INFO")
        self.assertIn("ăn chay", s["messages"][-1]["text"])
        self.assertIn("giữ giỏ", s["messages"][-1]["text"])

    def test_chat_keeps_cart_when_no_other_store_fits(self):
        s = valid_session_with_one_feasible_store()
        cart = s["cart"]
        route = {"intent": "CHANGE_RESTAURANT", "member": None, "detail": "đổi quán", "amount": None, "tag": None}
        with mock.patch("core.llm_steps.route_message", return_value=route), \
                mock.patch("core.llm_steps.pick_items", side_effect=first_pick):
            s = core.send(s, "đổi quán khác đi")
        self.assertEqual((s["status"], s["store_id"], s["cart"]), ("CART_VALID", "store_09", cart))
        self.assertIn("giữ giỏ", s["messages"][-1]["text"])

    def test_explicit_store_still_shows_why_it_fails(self):
        s = valid_session_after_all_veg_stores_tried()
        s = core.change_restaurant(s, "store_01")
        self.assertEqual((s["status"], s["store_id"]), ("CART_INFEASIBLE", "store_01"))


if __name__ == "__main__":
    unittest.main()
