"""Công cụ chỉ đọc và kiểm giỏ cho D2, suy ra từ data/dataset_mon_an_viet.json."""

import json
import math
from functools import lru_cache
from pathlib import Path

from tracing import tool

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "dataset_mon_an_viet.json"

# Ăn chay = không có nguyên liệu động vật, kể cả trứng và sữa (chốt 27/11).
ANIMAL_CATEGORIES = {"meat", "seafood", "egg", "dairy"}
ANIMAL_CONDIMENTS = {"fish_sauce", "shrimp_paste", "shrimp_paste_hue", "fermented_gourami",
                     "fermented_snakehead", "oyster_sauce"}
SHIPPING_DEFAULT = 15_000  # mức cơ bản cho SHIPPING_BASE_KM đầu
SHIPPING_BASE_KM = 2
SHIPPING_PER_KM = 5_000


@lru_cache(maxsize=1)
def _dataset():
    with DATA_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)


@lru_cache(maxsize=1)
def _lookups():
    data = _dataset()
    ingredients = {item["id"]: item for item in data["ingredients"]}
    category = {i: c["id"] for c in data["ingredient_categories"] for i in c["ingredient_ids"]}
    allergen_names = {a["id"]: a["name"] for a in data["allergen_types"]}
    return ingredients, category, allergen_names


@tool
def list_restaurants():
    """Liệt kê quán. Input: không có. Output: [{id, name, menu_type, summary, distance_km}]. Không tác động ra ngoài."""
    return [{key: store.get(key) for key in ("id", "name", "menu_type", "summary", "distance_km")}
            for store in _dataset()["stores"]]


@tool
def load_menu(store_id):
    """Đọc menu một quán. Input: mã quán. Output: {dish_id: món kèm giá, nguyên liệu, dị ứng, chay suy ra}. Không tác động ra ngoài."""
    ingredients, category, _ = _lookups()
    menu = {}
    for dish in _dataset()["dishes"]:
        if dish["store_id"] != store_id:
            continue
        ids = [i for group in dish["ingredient_groups"] for i in group["ingredient_ids"]]
        sources = {}
        for i in ids:
            for tag in ingredients.get(i, {}).get("allergens", ()):
                names = sources.setdefault(tag, [])
                if ingredients[i]["name"] not in names:
                    names.append(ingredients[i]["name"])
        animal = []
        for i in ids:
            if (category.get(i) in ANIMAL_CATEGORIES or i in ANIMAL_CONDIMENTS) and ingredients[i]["name"] not in animal:
                animal.append(ingredients[i]["name"])
        menu[dish["id"]] = {
            "name": dish["name"],
            "price": dish["price_vnd"],
            "ingredients": ids,
            "allergens": sorted(sources),
            "allergen_sources": sources,
            "animal_ingredients": animal,
            "vegetarian": not animal,
            "available": dish.get("available", True),
            "ingredients_known": bool(ids) and all(i in ingredients for i in ids),
        }
    return menu


def dish_exclusion(member, item):
    """Lý do loại món cho một thành viên; chuỗi rỗng nếu an toàn."""
    if not item["available"]:
        return "món không còn bán"
    if (member.get("vegetarian") or member.get("allergens")) and not item["ingredients_known"]:
        return "không rõ thành phần"
    if member.get("vegetarian") and not item["vegetarian"]:
        return "không chay: có " + ", ".join(item["animal_ingredients"][:3])
    for tag, label in member.get("allergens", {}).items():
        if tag in item["allergens"]:
            return "dị ứng %s: có %s" % (label, ", ".join(item["allergen_sources"][tag]))
    return ""


@tool
def safe_mains(member, menu):
    """Lọc món an toàn. Input: thành viên và menu. Output: (mã món an toàn, {mã món: lý do loại}). Không tác động ra ngoài."""
    excluded = {key: reason for key, item in menu.items() if (reason := dish_exclusion(member, item))}
    return [key for key in menu if key not in excluded], excluded


@tool
def feasibility(members, options, menu, shipping):
    """Tính mức tối thiểu. Input: hồ sơ, món đã lọc từng người, menu, ship. Output: (tên người thiếu món, tổng tối thiểu hoặc None). Không tác động ra ngoài."""
    missing = [member["name"] for member, choices in zip(members, options) if not choices]
    if missing:
        return missing, None
    minimum = shipping + sum(min(menu[key]["price"] for key in choices) for choices in options)
    return [], minimum


@tool
def validate_cart(members, selected, menu, budget, shipping):
    """Kiểm giỏ. Input: hồ sơ, mã món từng người, menu, quỹ, ship. Output: danh sách lỗi (rỗng = hợp lệ). Không tác động ra ngoài."""
    if len(selected) != len(members):
        return ["Số suất không khớp số người."]
    errors = []
    subtotal = 0
    for member, key in zip(members, selected):
        if key not in menu:
            errors.append(f'{member["name"]}: món ngoài menu.')
            continue
        item = menu[key]
        subtotal += item["price"]
        reason = dish_exclusion(member, item)
        if reason:
            errors.append(f'{member["name"]}: {reason}.')
    if subtotal + shipping > budget:
        errors.append("Vượt ngân sách sau khi cộng phí ship.")
    return errors


@tool
def shipping_fee(store_id):
    """Phí ship mô phỏng theo distance_km. Input: mã quán. Output: số đồng. Không tác động ra ngoài.

    15.000đ cho 2 km đầu, mỗi km tiếp theo (làm tròn lên) cộng 5.000đ. Quán không có khoảng cách dùng mức cơ bản."""
    store = next((s for s in _dataset()["stores"] if s["id"] == store_id), None)
    km = (store or {}).get("distance_km")
    if km is None or km <= SHIPPING_BASE_KM:
        return SHIPPING_DEFAULT
    return SHIPPING_DEFAULT + SHIPPING_PER_KM * math.ceil(round(km - SHIPPING_BASE_KM, 6))


@tool
def store_summary(store_id, members, budget, shipping):
    """Tóm tắt một quán cho hồ sơ. Input: mã quán, hồ sơ, quỹ, ship. Output: {id, name, safe_counts, min_total}. Không tác động ra ngoài."""
    menu = load_menu(store_id)
    options = [safe_mains(member, menu)[0] for member in members]
    _, minimum = feasibility(members, options, menu, shipping)
    name = next((s["name"] for s in _dataset()["stores"] if s["id"] == store_id), store_id)
    return {"id": store_id, "name": name,
            "safe_counts": {m["name"]: len(o) for m, o in zip(members, options)},
            "min_total": minimum}
