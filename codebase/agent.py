"""Lớp mỏng cho `python run.py eval`: mỗi ô input của câu thử là một phiên độc lập.

Chỉ đọc các trường cấu trúc của ô input (quán ứng viên, ngân sách, phí ship, trạng thái hồ sơ,
yêu cầu tiếp theo) rồi chạy đúng luồng trong core.py — không so khớp nội dung câu thử.
"""

import re

import core
from llm_steps import AIUnavailable
from tracing import note

UNAVAILABLE = "Hệ thống AI tạm thời không phản hồi, vui lòng thử lại."


def _money(text, label):
    match = re.search(r"(?:%s)\s*[:=]?\s*(\d+(?:[.,]\d{3})*)\s*(k|nghìn|ngàn)?" % label, text, re.IGNORECASE)
    if not match:
        return None
    value = int(match[1].replace(".", "").replace(",", ""))
    return value * 1000 if match[2] else value


def _parse(text):
    parts = re.split(r"\bchat\s*:", text, maxsplit=1, flags=re.IGNORECASE)
    head, chat = (parts[0], parts[1]) if len(parts) == 2 else (text, "")
    followup = None
    split = re.split(r"yêu cầu tiếp theo của người đặt\s*:", text, maxsplit=1, flags=re.IGNORECASE)
    if len(split) == 2:
        followup = split[1].strip()
    stores = re.search(r"quán(?:\s+ứng viên)?\s*:?\s*(store_\d+(?:\s*,\s*store_\d+)*)", head, re.IGNORECASE)
    candidates = [s.strip() for s in stores[1].split(",")] if stores else None
    if chat:
        chat = re.sub(r"\.\s*(tự chọn quán và lập giỏ nhóm|lập giỏ nhóm|phân tích chat rồi lập giỏ nếu đủ thông tin)\.?\s*$",
                      "", chat.strip(), flags=re.IGNORECASE)
        chat_text = "\n".join(part.strip() for part in chat.split("|") if part.strip())
    else:
        locked = re.search(r"(?:khóa|khoá)\s*:\s*(.*?)(?:yêu cầu tiếp theo|$)", text, re.IGNORECASE | re.DOTALL)
        chat_text = (locked[1] if locked else text).strip()
    confirmed = re.search(r"đã xác nhận", head, re.IGNORECASE) is not None
    locked = re.search(r"đã xác nhận và (?:khóa|khoá)", head, re.IGNORECASE) is not None
    return {"candidates": candidates, "budget": _money(head, "ngân sách|quỹ chung|quỹ"),
            "shipping": _money(head, "phí ship mô phỏng|phí ship"), "chat_text": chat_text,
            "confirmed": confirmed, "locked": locked, "followup": followup}


def answer(text: str) -> dict:
    """Một câu thử → một phiên: start → (confirm) → (send) → render."""
    note("D2: agent 2 phase (core.py)")
    case = _parse(text)
    try:
        session = core.start(case["chat_text"], shipping=case["shipping"], candidates=case["candidates"],
                             budget=case["budget"])
        if case["locked"]:
            # Ô input khẳng định hồ sơ đã xác nhận và khoá: mọi câu hỏi coi như đã được người đặt trả lời.
            for q in session["profile"]["questions"]:
                q["status"] = "ANSWERED"
        if case["confirmed"]:
            session = core.confirm(session)
        if case["followup"] and not (case["locked"] and session["status"] == "PROFILE_DRAFT"):
            session = core.send(session, case["followup"])
        return {"output": core.render(session)}
    except AIUnavailable:
        return {"output": UNAVAILABLE}
