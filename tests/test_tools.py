import unittest

import _path  # noqa: F401
import tools

ALL_STORES = ["store_%02d" % i for i in range(1, 11)]


class TestTools(unittest.TestCase):
    def test_vegan_dish_detected(self):
        self.assertIs(tools.load_menu("store_09")["dish_090"]["vegetarian"], True)

    def test_egg_dish_not_vegetarian(self):
        item = tools.load_menu("store_05")["dish_049"]
        self.assertIs(item["vegetarian"], False)
        self.assertIn("Trứng gà", item["animal_ingredients"])

    def test_fish_sauce_makes_dish_not_vegetarian(self):
        item = tools.load_menu("store_01")["dish_009"]
        self.assertIs(item["vegetarian"], False)
        self.assertIn("Nước mắm cá cơm và muối", item["animal_ingredients"])

    def test_only_four_vegetarian_dishes(self):
        found = {key for store in ALL_STORES for key, item in tools.load_menu(store).items() if item["vegetarian"]}
        self.assertEqual(found, {"dish_077", "dish_078", "dish_080", "dish_090"})

    def test_peanut_reason_names_ingredient(self):
        member = {"name": "An", "vegetarian": False, "allergens": {"peanut": "đậu phộng"}}
        item = tools.load_menu("store_02")["dish_016"]
        self.assertEqual(tools.dish_exclusion(member, item), "dị ứng đậu phộng: có Đậu phộng rang")

    def test_store_summary_no_safe_item(self):
        members = [{"name": "An", "vegetarian": True, "allergens": {}}]
        summary = tools.store_summary("store_01", members, 300000, 15000)
        self.assertEqual(summary["safe_counts"]["An"], 0)
        self.assertIsNone(summary["min_total"])

    def test_list_restaurants_shape(self):
        stores = tools.list_restaurants()
        self.assertEqual(len(stores), 10)
        self.assertEqual(set(stores[0]), {"id", "name", "menu_type", "summary", "distance_km"})

    def test_shipping_fee_default(self):
        self.assertEqual(tools.shipping_fee("store_01"), 15000)


if __name__ == "__main__":
    unittest.main()
