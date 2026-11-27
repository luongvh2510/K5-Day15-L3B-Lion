"""Công cụ chỉ đọc và kiểm giỏ cho bản chạy thử D2."""

import json
from functools import lru_cache
from pathlib import Path

from tracing import tool

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "dataset_mon_an_viet.json"


@lru_cache(maxsize=1)
def _dataset():
    with DATA_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)


@tool
def list_restaurants():
    """Liệt kê quán. Input: không có. Output: danh sách mã và tên quán. Không tác động ra ngoài."""
    return {store["id"]: store["name"] for store in _dataset()["stores"]}


@tool
def load_menu(store_id):
    """Đọc menu. Input: mã quán. Output: món, giá và nhãn thành phần demo. Không tác động ra ngoài."""
    data = _dataset()
    ingredients = {item["id"]: item["allergens"] for item in data["ingredients"]}
    menu = {}
    for dish in data["dishes"]:
        if dish["store_id"] != store_id:
            continue
        ids = [i for group in dish["ingredient_groups"] for i in group["ingredient_ids"]]
        menu[dish["id"]] = {
            "name": dish["name"],
            "price": dish["price_vnd"],
            "vegetarian": dish.get("vegetarian"),
            "available": dish.get("available", True),
            "ingredients_known": bool(ids) and all(i in ingredients for i in ids),
            "allergens": sorted({tag for i in ids for tag in ingredients.get(i, ())}),
        }
    return menu


def exclusion(member, item):
    """Trả lý do loại món theo dữ liệu mô phỏng."""
    if not item["available"]:
        return "món không còn bán"
    if (member["vegetarian"] or member["allergens"]) and not item["ingredients_known"]:
        return "không rõ thành phần"
    if member["vegetarian"] and item["vegetarian"] is not True:
        return "không có nhãn chay đã xác minh"
    for tag, label in member["allergens"].items():
        if tag in item["allergens"]:
            return f"có {label}"
    return ""


@tool
def safe_mains(member, menu):
    """Lọc món. Input: thành viên và menu. Output: mã món phù hợp và lý do loại. Không tác động ra ngoài."""
    excluded = {key: reason for key, item in menu.items() if (reason := exclusion(member, item))}
    return [key for key in menu if key not in excluded], excluded


@tool
def feasibility(members, options, menu, shipping):
    """Tính mức tối thiểu. Input: hồ sơ, món đã lọc, menu và ship. Output: người thiếu món và tổng tối thiểu. Không tác động ra ngoài."""
    missing = [member["name"] for member, choices in zip(members, options) if not choices]
    if missing:
        return missing, None
    minimum = shipping + sum(min(menu[key]["price"] for key in choices) for choices in options)
    return [], minimum


@tool
def validate_cart(members, selected, menu, budget, shipping):
    """Kiểm giỏ. Input: hồ sơ, mã món từng người, menu, quỹ và ship. Output: danh sách lỗi. Không tác động ra ngoài."""
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
        reason = exclusion(member, item)
        if reason:
            errors.append(f'{member["name"]}: {reason}.')
    if subtotal + shipping > budget:
        errors.append("Vượt ngân sách sau khi cộng phí ship.")
    return errors
