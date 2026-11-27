"""Luồng D2 CP2 dùng bộ đọc chat mô phỏng và kiểm giỏ bằng code."""

import re
import unicodedata

from tools import feasibility, list_restaurants, load_menu, safe_mains, validate_cart
from tracing import note

SHIPPING_DEFAULT = 15_000
ALLERGENS = {
    "peanut": ("đậu phộng", "lạc"),
    "fish": ("cá",),
    "soy": ("đậu nành", "đậu hũ", "tàu hũ"),
    "wheat": ("lúa mì", "bột mì", "gluten"),
    "egg": ("trứng",),
    "milk": ("sữa",),
    "sesame": ("mè", "vừng"),
    "celery": ("cần tây",),
    "crustacean": ("giáp xác", "tôm", "cua"),
    "mollusc": ("nhuyễn thể", "mực", "ốc", "hàu"),
}


def _normalize(text):
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def _mentions(text, term):
    return re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) is not None


def _money(text, label):
    match = re.search(
        rf"(?:{label})\s*[:=]?\s*(\d+(?:[.,]\d{{3}})*)(?:\s*(k|nghìn|ngàn|đ|đồng))?(?!\w)",
        text,
    )
    if match:
        value = match[1].replace(".", "").replace(",", "")
        return int(value) * (1000 if match[2] in {"k", "nghìn", "ngàn"} else 1)
    return None


def _read_chat(chat):
    members = {}
    for line in re.split(r"[|\n]+", chat):
        name, sep, message = line.strip().partition(":")
        name = name.strip()
        if not sep or not name or len(name) > 35:
            continue
        member = members.setdefault(_normalize(name), {
            "name": name, "vegetarian": False, "allergens": {},
            "diets": [], "preferences": [], "questions": [],
        })
        for raw in re.split(r"[;!.?]+", message):
            words = _normalize(raw)
            if not words:
                continue
            if "dị ứng" in words:
                details = words.split("dị ứng", 1)[1].strip()
                details = re.split(r",\s*(?:chọn|tìm|gợi ý|lấy)\b", details, maxsplit=1)[0]
                tags = {tag: aliases[0] for tag, aliases in ALLERGENS.items()
                        if any(_mentions(details, term) for term in aliases)}
                remainder = details
                for aliases in ALLERGENS.values():
                    for term in aliases:
                        remainder = re.sub(r"(?<!\w)" + re.escape(term) + r"(?!\w)", " ", remainder)
                for word in ("với", "và", "cả"):
                    remainder = re.sub(rf"\b{word}\b", " ", remainder)
                if not tags or re.search(r"\w", remainder):
                    member["questions"].append(
                        f'{name}, bạn dị ứng cụ thể với chất nào? Nếu là hải sản, '
                        'xin làm rõ cá, tôm/cua (giáp xác), mực/ốc (nhuyễn thể) hoặc nhóm khác.'
                    )
                member["allergens"].update(tags)
                member["diets"].append(raw.strip())
            elif "ăn chay" in words:
                member["vegetarian"] = True
                member["diets"].append(raw.strip())
                if re.search(r"\b(gà|bò|heo|cá|tôm|cua|sườn|thịt)\b", words):
                    member["preferences"].append(words)
            elif not any(term in words for term in ("nào cũng được", "gì cũng được", "đổi khỏi")):
                member["preferences"].append(words)
        if member["vegetarian"] and any(
            re.search(r"\b(gà|bò|heo|cá|tôm|cua|sườn|thịt)\b", pref)
            for pref in member["preferences"]
        ):
            question = (
                f'{name} nói ăn chay nhưng cũng dặn "{member["preferences"][-1]}". '
                "Món đó cho ai? Mình giữ ràng buộc ăn chay trong lúc chờ xác nhận."
            )
            if question not in member["questions"]:
                member["questions"].append(question)
    return list(members.values())


def _best_items(members, options, menu, limit):
    # Giữ một phương án tốt nhất cho mỗi tạm tính, tối đa hóa sở thích rồi giảm giá.
    states = {0: (0, ())}
    for member, choices in zip(members, options):
        scores = {
            key: int(any(_mentions(preference, _normalize(menu[key]["name"]))
                         for preference in member["preferences"]))
            for key in choices
        }
        following = {}
        for subtotal, (score, selected) in states.items():
            for key in choices:
                price = subtotal + menu[key]["price"]
                candidate = score + scores[key], (*selected, key)
                if price <= limit and (price not in following or candidate[0] > following[price][0]):
                    following[price] = candidate
        states = following
    if not states:
        return None
    subtotal = min(states, key=lambda price: (-states[price][0], price))
    score, selected = states[subtotal]
    return score, subtotal, selected


def _choose_cart(members, stores, budget, shipping):
    carts, minimums, blocked = [], [], {}
    for store_id in stores:
        menu = load_menu(store_id)
        filtered = [safe_mains(member, menu) for member in members]
        options = [choices for choices, _ in filtered]
        missing, minimum = feasibility(members, options, menu, shipping)
        if missing:
            reasons = {
                member["name"]: sorted(set(excluded.values()))
                for member, (_, excluded) in zip(members, filtered) if member["name"] in missing
            }
            blocked[store_id] = ", ".join(
                f'{name} ({", ".join(reasons[name]) or "không có món trong menu"})' for name in missing
            )
            continue
        minimums.append(minimum)
        if minimum <= budget:
            result = _best_items(members, options, menu, budget - shipping)
            if result:
                score, subtotal, selected = result
                carts.append((-score, subtotal, store_id, selected, menu, filtered))
    if not carts:
        if minimums and min(minimums) > budget:
            minimum = min(minimums)
            return f"Chưa khả thi: cần tối thiểu {minimum:,}đ gồm phí ship, thiếu {minimum-budget:,}đ. Có thể tăng quỹ hoặc thử quán khác."
        if minimums:
            return "Chưa lập được giỏ đã kiểm. Vui lòng xem lại hồ sơ và menu."
        details = "; ".join(f"{key}: {reason}" for key, reason in blocked.items())
        return f"Chưa khả thi: không đủ món phù hợp theo menu đã khai báo. {details}. Hãy thử quán khác có dữ liệu thành phần phù hợp."

    _, subtotal, store_id, selected, menu, filtered = min(carts, key=lambda cart: cart[:3])
    errors = validate_cart(members, selected, menu, budget, shipping)
    if errors:
        return "Chưa lập được giỏ đã kiểm: " + " ".join(errors)
    lines = [f"Giỏ hợp lệ theo dữ liệu mô phỏng · hệ thống chọn {stores[store_id]} ({store_id})."]
    for member, key, (_, excluded) in zip(members, selected, filtered):
        item = menu[key]
        warning = "" if item["ingredients_known"] else " (quán không ghi thành phần)"
        lines.append(f'{member["name"]}: 1 × {item["name"]} ({key}) · {item["price"]:,}đ{warning}')
        if excluded and (member["vegetarian"] or member["allergens"]):
            lines.append("  Loại: " + "; ".join(
                f'{menu[key]["name"]} ({key}) {reason}' for key, reason in excluded.items()
            ))
    total = subtotal + shipping
    lines.append(
        f"Tạm tính {subtotal:,}đ · phí ship mô phỏng {shipping:,}đ · "
        f"tổng {total:,}đ · còn {budget-total:,}đ. Vui lòng duyệt giỏ."
    )
    if any(member["allergens"] for member in members):
        lines.append("Menu mô phỏng chưa có thông tin nhiễm chéo. Hãy xác nhận thành phần với quán trước khi đặt.")
    return "\n".join(lines)


def answer(text: str) -> dict:
    """Nhận một phiên dưới dạng chuỗi và trả kết quả hiển thị."""
    note("CP2: bộ đọc chat mô phỏng, không gọi model")
    plain = _normalize(text)
    parts = re.split(r"\bchat\s*:", text, maxsplit=1, flags=re.IGNORECASE)
    header = _normalize(parts[0]) if len(parts) == 2 else ""
    if re.search(r"hồ sơ đã xác nhận và (?:khóa|khoá)\b", header or plain) and "yêu cầu tiếp theo" in plain:
        return {"output": (
            "Từ chối thực hiện yêu cầu qua chat. Ràng buộc dị ứng và ăn chay đã khóa; "
            "giữ nguyên hồ sơ, nhãn menu và món đã chọn. "
            "Hãy chọn món hoặc quán có thông tin thành phần phù hợp. "
            "Nếu hồ sơ gán nhầm, dùng Sửa hồ sơ rồi xác nhận lại."
        )}
    budget = _money(plain, "ngân sách|quỹ chung|quỹ")
    shipping = _money(header, "phí ship mô phỏng|phí ship")
    shipping = SHIPPING_DEFAULT if shipping is None else shipping
    chat = parts[-1].strip()
    chat = re.sub(r"\.\s*(?:Tự chọn quán và lập giỏ nhóm|Lập giỏ nhóm|Phân tích chat rồi lập giỏ nếu đủ thông tin)\.?\s*$", "", chat, flags=re.IGNORECASE)
    members = _read_chat(chat)
    questions = [question for member in members for question in member["questions"]]
    if len(members) != 5:
        questions.append("Bản CP2 cần chat của đúng 5 người, mỗi lời dặn viết theo dạng Tên: lời nhắn.")
    if budget is None or budget <= 0:
        questions.append("Quỹ chung của nhóm là bao nhiêu đồng?")
    if questions:
        return {"output": "\n".join(questions)}
    if "đã xác nhận hồ sơ" not in header and "hồ sơ đã xác nhận" not in header:
        profile = "\n".join(f'{m["name"]}: {"; ".join(m["diets"] + m["preferences"]) or "chưa có lời dặn riêng"}' for m in members)
        return {"output": f"Hồ sơ nháp, quỹ {budget:,}đ:\n{profile}\nVui lòng xác nhận hồ sơ trước khi lập giỏ."}
    stores = list_restaurants()
    scope = re.search(r"quán ứng viên:\s*(store_\d+(?:\s*,\s*store_\d+)*)", header)
    if scope:
        candidates = [key.strip() for key in scope[1].split(",")]
        stores = {key: stores[key] for key in candidates if key in stores}
    if not stores:
        return {"output": "Danh sách thử chưa có quán có trong menu. Vui lòng kiểm tra lại."}
    return {"output": _choose_cart(members, stores, budget, shipping)}
