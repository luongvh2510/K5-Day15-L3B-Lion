"""Các bước LLM của agent D2. Mỗi hàm nhận tham số, gọi call_model, trả dict đúng schema.

Không đọc/ghi DB, không tự kiểm giỏ, không chuyển trạng thái phiên — việc đó ở core.py.
"""

import json
import re
from pathlib import Path

from ai import call_model

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


class AIUnavailable(Exception):
    """Model lỗi hoặc trả JSON sai sau khi đã thử lại."""


def parse_json(text):
    """Lấy object JSON đầu tiên trong chữ model trả về (bỏ ``` và chữ thừa)."""
    text = re.sub(r"```(?:json)?", "", text or "")
    start = text.find("{")
    while start != -1:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text[start:])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
        start = text.find("{", start + 1)
    raise ValueError("không có JSON object")


def call_json(system, user, required):
    """Gọi model, parse JSON; thiếu khoá hoặc lỗi thì thử lại một lần, vẫn lỗi thì AIUnavailable."""
    prompt = user
    for attempt in range(2):
        try:
            data = parse_json(call_model(system, prompt)["text"])
            if all(key in data for key in required):
                return data
        except (ValueError, RuntimeError, OSError, KeyError, TypeError, IndexError):
            pass
        prompt = user + "\n\nChỉ trả JSON hợp lệ có các khoá: " + ", ".join(required)
    raise AIUnavailable("model không trả JSON hợp lệ")


def _prompt(name):
    return (PROMPTS / (name + ".md")).read_text(encoding="utf-8")


OPS = {"ADD_MEMBER", "SET_VEGETARIAN", "UNSET_VEGETARIAN", "ADD_ALLERGEN", "REMOVE_ALLERGEN",
       "ADD_PREFERENCE", "SET_BUDGET", "RESOLVE_QUESTION"}


def _allergen_tags():
    from tools import _lookups
    return _lookups()[2]


def _system(name):
    tags = _allergen_tags()
    return _prompt(name).replace("{ALLERGEN_TAGS}", ", ".join("%s (%s)" % (k, v) for k, v in tags.items()))


def parse_amount(value):
    """Số tiền dương từ int hoặc chuỗi ("300k", "300.000", "300000đ"); không đọc được thì None."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value) if value > 0 else None
    match = re.search(r"(\d+(?:[.,]\d{3})*)\s*(k|nghìn|ngàn)?", str(value).lower())
    if not match:
        return None
    amount = int(match[1].replace(".", "").replace(",", ""))
    amount = amount * 1000 if match[2] else amount
    return amount if amount > 0 else None


_number = parse_amount


def clean_name(name):
    import unicodedata
    return " ".join(unicodedata.normalize("NFC", str(name or "")).split())


def extract_profile(chat_text):
    """Phase 1: đọc chat → {budget, members, questions}. Gộp tên trùng; tag dị ứng ngoài danh mục thành câu hỏi."""
    data = call_json(_system("extract_profile"), "Đoạn chat:\n" + chat_text, ["members"])
    tags = _allergen_tags()
    members, by_key, questions = [], {}, []
    for raw in data.get("members") or []:
        if not isinstance(raw, dict):
            continue
        name = clean_name(raw.get("name"))
        if not name:
            continue
        m = by_key.get(name.casefold())
        if m is None:
            m = {"name": name, "vegetarian": False, "allergens": {}, "preferences": [], "quotes": []}
            by_key[name.casefold()] = m
            members.append(m)
        m["vegetarian"] = m["vegetarian"] or bool(raw.get("vegetarian"))
        for a in raw.get("allergens") or []:
            tag, label = (a.get("tag"), a.get("label")) if isinstance(a, dict) else (a, None)
            tag = str(tag or "").strip().lower()
            if tag in tags:
                m["allergens"][tag] = str(label or tags[tag]).strip()
            else:
                questions.append({"member": name, "text": "%s dị ứng chính xác với chất gì (%s)?" % (name, label or tag)})
        m["preferences"] += [str(x) for x in raw.get("preferences") or [] if isinstance(x, (str, int))]
        m["quotes"] += [str(x) for x in raw.get("quotes") or [] if isinstance(x, (str, int))]
    for q in data.get("questions") or []:
        if isinstance(q, dict) and q.get("text"):
            who = clean_name(q.get("member")) or None
            questions.append({"member": who, "text": str(q["text"])})
    budget = parse_amount(data.get("budget"))
    if budget is None and not any(q["member"] is None and "quỹ" in q["text"].lower() for q in questions):
        questions.append({"member": None, "text": BUDGET_QUESTION})
    for i, q in enumerate(questions, 1):
        q.update(id="q%d" % i, status="OPEN")
    return {"budget": budget, "members": members, "questions": questions}


BUDGET_QUESTION = "Quỹ chung của nhóm là bao nhiêu?"


def apply_answer(profile, question, answer):
    """Phase 1: câu trả lời của người đặt → {changes, reply}. Phép lạ bị bỏ."""
    user = "Hồ sơ hiện tại:\n%s\n\nCâu hỏi (%s): %s\nCâu trả lời: %s" % (
        json.dumps(profile, ensure_ascii=False), question.get("id"), question.get("text"), answer)
    data = call_json(_system("apply_answer"), user, ["changes"])
    changes = [c for c in data.get("changes") or [] if isinstance(c, dict) and c.get("op") in OPS]
    return {"changes": changes, "reply": str(data.get("reply") or "")}


INTENTS = {"CHANGE_ITEM", "ADD_HARD", "REMOVE_HARD", "CHANGE_BUDGET", "CHANGE_RESTAURANT", "OTHER"}


def choose_restaurant(profile, stores, tried):
    """Phase 2: chọn một quán trong danh sách đã tính sẵn → {store_id, reason}."""
    user = "Hồ sơ nhóm:\n%s\n\nQuán (đã loại các quán đã thử %s):\n%s" % (
        json.dumps(profile, ensure_ascii=False), tried, json.dumps(stores, ensure_ascii=False))
    data = call_json(_system("choose_restaurant"), user, ["store_id"])
    return {"store_id": str(data.get("store_id") or ""), "reason": str(data.get("reason") or "")}


def pick_items(members, options, budget, shipping, errors):
    """Phase 2: chọn một món cho mỗi người trong danh sách an toàn → {picks}."""
    user = "Thành viên:\n%s\n\nMón an toàn từng người:\n%s\n\nQuỹ: %d đồng · phí ship: %d đồng\nLỗi lần trước: %s" % (
        json.dumps(members, ensure_ascii=False), json.dumps(options, ensure_ascii=False), budget, shipping,
        "; ".join(errors) if errors else "không có")
    data = call_json(_system("pick_items"), user, ["picks"])
    picks = [p for p in data.get("picks") or [] if isinstance(p, dict) and p.get("member") and p.get("item_id")]
    return {"picks": picks}


def route_message(text, profile, cart):
    """Phase 2: phân loại tin nhắn → {intent, member, detail, amount, tag}. Không rõ thì OTHER."""
    user = "Hồ sơ:\n%s\n\nGiỏ hiện tại:\n%s\n\nTin nhắn: %s" % (
        json.dumps(profile, ensure_ascii=False), json.dumps(cart, ensure_ascii=False), text)
    data = call_json(_system("route_message"), user, ["intent"])
    intent = data.get("intent") if data.get("intent") in INTENTS else "OTHER"
    return {"intent": intent, "member": data.get("member"), "detail": str(data.get("detail") or ""),
            "amount": _number(data.get("amount")), "tag": (data.get("tag") or None)}
