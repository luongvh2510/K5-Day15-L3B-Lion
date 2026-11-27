"""Bộ điều phối 2 phase của agent D2. Phiên lưu trong bộ nhớ (Dũng thay bằng DB sau)."""

import copy
import uuid

import llm_steps
import tools

MAX_REPAIR = 2
SESSIONS = {}
LOCK_PROTECTED = {"UNSET_VEGETARIAN", "REMOVE_ALLERGEN"}


# ---------- hồ sơ ----------

def _find(profile, name):
    key = (name or "").strip().casefold()
    return next((m for m in profile["members"] if m["name"].casefold() == key), None)


def apply_changes(profile, changes, locked):
    """Áp thay đổi lên bản sao hồ sơ. Đã khoá thì bỏ mọi phép gỡ ràng buộc cứng (BR-12)."""
    new = copy.deepcopy(profile)
    dropped = []
    for change in changes:
        op = change.get("op")
        if locked and op in LOCK_PROTECTED:
            dropped.append(change)
            continue
        if op == "SET_BUDGET":
            amount = llm_steps.parse_amount(change.get("amount"))
            if amount:
                new["budget"] = amount
            else:
                dropped.append(change)
            continue
        if op == "ADD_ALLERGEN" and change.get("tag") not in tools._lookups()[2]:
            dropped.append(change)
            continue
        if op == "RESOLVE_QUESTION":
            for q in new.get("questions", []):
                if q["id"] == change.get("question_id"):
                    q["status"] = "ANSWERED"
            continue
        m = _find(new, change.get("member"))
        if op == "ADD_MEMBER":
            if m is None and change.get("member"):
                new["members"].append({"name": change["member"], "vegetarian": False, "allergens": {},
                                       "preferences": [], "quotes": []})
            continue
        if m is None:
            dropped.append(change)
            continue
        if op == "SET_VEGETARIAN":
            m["vegetarian"] = True
        elif op == "UNSET_VEGETARIAN":
            m["vegetarian"] = False
        elif op == "ADD_ALLERGEN" and change.get("tag"):
            m["allergens"][change["tag"]] = change.get("label") or change["tag"]
        elif op == "REMOVE_ALLERGEN":
            m["allergens"].pop(change.get("tag"), None)
        elif op == "ADD_PREFERENCE" and change.get("text"):
            m["preferences"].append(change["text"])
    return new, dropped


def open_questions(profile):
    return [q for q in profile.get("questions", []) if q.get("status") == "OPEN"]


def can_confirm(profile):
    """Cho xác nhận khi có thành viên, có quỹ > 0 và không còn câu hỏi mở (BR-10)."""
    return bool(profile.get("members")) and bool(profile.get("budget")) and not open_questions(profile)


# ---------- phiên ----------

def _msg(session, kind, text, role="assistant"):
    session["messages"].append({"role": role, "kind": kind, "text": text, "turn": session.get("turn", 0)})


def _new_turn(session):
    """Mỗi thao tác của người dùng (send/confirm/finalize) là một lượt; render chỉ hiện tin của lượt hiện tại."""
    session["turn"] = session.get("turn", 0) + 1


def get(session_id):
    return SESSIONS[session_id]


def start(chat_text, shipping=None, candidates=None, budget=None):
    """Phase 1 bước 1–2: đọc chat, tạo phiên PROFILE_DRAFT. `budget` (nếu có) ghi đè quỹ đọc từ chat."""
    profile = llm_steps.extract_profile(chat_text)
    if budget:
        profile["budget"] = int(budget)
        for q in profile["questions"]:
            if q.get("member") is None and "quỹ" in q["text"].lower():
                q["status"] = "ANSWERED"
    session = {"id": uuid.uuid4().hex[:8], "status": "PROFILE_DRAFT", "profile": profile, "locked": False,
               "shipping": shipping, "candidates": candidates, "store_id": None, "tried": [],
               "cart": None, "infeasible": None, "messages": []}
    _msg(session, "TEXT", chat_text, role="user")
    for q in open_questions(profile):
        _msg(session, "QUESTION", q["text"])
    SESSIONS[session["id"]] = session
    return session


def confirm(session):
    """Khoá ràng buộc và lập giỏ; chỉ khi can_confirm."""
    _new_turn(session)
    if session["status"] != "PROFILE_DRAFT":
        return session
    if not can_confirm(session["profile"]):
        _msg(session, "QUESTION", "Chưa thể xác nhận: cần trả lời hết câu hỏi và có quỹ chung.")
        return session
    session["locked"] = True
    return _plan_cart(session)


def reopen(session):
    """Mở lại hồ sơ, huỷ giỏ và yêu cầu xác nhận lại (BR-12)."""
    if session["status"] in ("CART_VALID", "CART_INFEASIBLE"):
        session.update(status="PROFILE_DRAFT", locked=False, cart=None, infeasible=None,
                       store_id=None, tried=[])
        _msg(session, "INFO", "Đã mở hồ sơ; giỏ cũ đã huỷ. Vui lòng kiểm tra và xác nhận lại.")
    return session


def edit_profile(session, members):
    """Thay danh sách thành viên khi hồ sơ đang mở; giữ nguyên câu hỏi chưa xử lý."""
    if session["status"] != "PROFILE_DRAFT" or session["locked"]:
        raise ValueError("Hồ sơ chưa mở để sửa")
    session["profile"]["members"] = copy.deepcopy(members)
    _msg(session, "INFO", "Đã cập nhật hồ sơ. Vui lòng kiểm tra các câu hỏi còn mở.")
    return session


def set_budget(session, amount):
    """Cập nhật quỹ rồi lập lại giỏ từ các ràng buộc đã khoá."""
    if session["status"] in ("CART_VALID", "CART_INFEASIBLE") and type(amount) is int and amount > 0:
        session["profile"]["budget"] = amount
        return _plan_cart(session)
    return session


def change_restaurant(session, store_id=None):
    """Chọn quán khác hoặc lập giỏ tại quán được chỉ định."""
    if session["status"] not in ("CART_VALID", "CART_INFEASIBLE"):
        return session
    if store_id is not None and store_id not in {r["id"] for r in tools.list_restaurants()}:
        raise ValueError("Quán không tồn tại")
    if session["store_id"] and session["store_id"] not in session["tried"]:
        session["tried"].append(session["store_id"])
    old = {key: session[key] for key in ("status", "store_id", "cart", "infeasible")}
    session["store_id"] = store_id
    _plan_cart(session)
    if store_id is None and old["status"] == "CART_VALID" and session["status"] != "CART_VALID":
        # Agent tự đổi quán mà không quán nào khác lập được giỏ: không bỏ giỏ hợp lệ đang có.
        session.update(old)
        _msg(session, "INFO", "Không còn quán nào khác lập được giỏ an toàn trong quỹ; giữ giỏ ở %s."
             % _store_name(old["store_id"]))
    return session


def finalize(session):
    _new_turn(session)
    if session["status"] == "CART_VALID":
        session["status"] = "FINALIZED"
    return session


def _ask(profile, member, text):
    """Thêm câu hỏi mở (không trùng câu đang mở)."""
    if any(q["text"] == text and q["status"] == "OPEN" for q in profile["questions"]):
        return
    profile["questions"].append({"id": "q%d" % (len(profile["questions"]) + 1), "member": member,
                                 "text": text, "status": "OPEN"})


def _answer_question(session, text):
    """PROFILE_DRAFT: trả lời câu hỏi mở đầu tiên, hoặc bổ sung/sửa hồ sơ khi không còn câu hỏi."""
    profile = session["profile"]
    questions = open_questions(profile)
    question = questions[0] if questions else {"id": None, "text": "Người đặt bổ sung hoặc sửa hồ sơ."}
    result = llm_steps.apply_answer(profile, question, text)
    new, dropped = apply_changes(profile, result["changes"], locked=False)
    for change in dropped:
        if change.get("op") == "ADD_ALLERGEN":
            _ask(new, change.get("member"), "%s dị ứng chính xác với chất gì?" % (change.get("member") or "Thành viên"))
    if not new.get("budget"):
        _ask(new, None, llm_steps.BUDGET_QUESTION)
    session["profile"] = new
    if result["reply"]:
        _msg(session, "INFO", result["reply"])
    for q in open_questions(new):
        _msg(session, "QUESTION", q["text"])
    return session


def send(session, text):
    """Một lượt người đặt nhắn."""
    _new_turn(session)
    _msg(session, "TEXT", text, role="user")
    if session["status"] == "PROFILE_DRAFT":
        return _answer_question(session, text)
    if session["status"] == "FINALIZED":
        return session
    profile = session["profile"]
    route = llm_steps.route_message(text, profile, session["cart"])
    intent, who = route["intent"], route.get("member")
    if intent == "REMOVE_HARD":
        _msg(session, "REFUSAL", "Không thể bỏ ràng buộc ăn chay/dị ứng đã xác nhận qua chat. "
             "Nếu hồ sơ ghi nhầm, hãy dùng Sửa hồ sơ rồi xác nhận lại.")
        return session
    if intent == "ADD_HARD":
        tag = route.get("tag")
        if _find(profile, who) is None:
            _msg(session, "QUESTION", _who_text(who))
            return session
        if tag == "vegetarian":
            change = {"op": "SET_VEGETARIAN", "member": who}
        elif tag in tools._lookups()[2]:
            change = {"op": "ADD_ALLERGEN", "member": who, "tag": tag, "label": tools._lookups()[2][tag].lower()}
        else:
            _msg(session, "QUESTION", "%s ăn chay hay dị ứng chính xác với chất gì?" % who)
            return session
        session["profile"], _ = apply_changes(profile, [change], locked=True)
        session["store_id"] = None
        return _plan_cart(session)
    if intent == "CHANGE_BUDGET" and route.get("amount"):
        session["profile"]["budget"] = route["amount"]
        return _plan_cart(session)
    if intent == "CHANGE_RESTAURANT":
        return change_restaurant(session)
    if intent == "CHANGE_ITEM":
        target = _find(profile, who)
        if target is None:
            _msg(session, "QUESTION", _who_text(who))
            return session
        if session["store_id"]:
            menu = tools.load_menu(session["store_id"])
            detail = (route["detail"] + " " + text).casefold()
            for key, item in menu.items():
                if key in detail or item["name"].casefold() in detail:
                    reason = tools.dish_exclusion(target, item)
                    if reason:
                        _msg(session, "REFUSAL", "Không thể gán %s cho %s (%s). Ràng buộc đã khoá được giữ nguyên; "
                             "hãy chọn món khác phù hợp." % (item["name"], target["name"], reason))
                        return session
        new, _ = apply_changes(profile, [{"op": "ADD_PREFERENCE", "member": who, "text": route["detail"]}],
                               locked=True)
        old = (session["cart"], session["status"], session["infeasible"])
        session["profile"] = new
        _plan_cart(session)
        if session["status"] != "CART_VALID" and old[1] == "CART_VALID":
            session["cart"], session["status"], session["infeasible"] = old
            _msg(session, "INFO", "Không đổi được mà vẫn giữ an toàn và trong quỹ, giữ giỏ cũ.")
        return session
    _msg(session, "INFO", "Mình chưa hiểu yêu cầu. Bạn có thể đổi món, đổi quỹ, đổi quán hoặc báo thêm dị ứng.")
    return session


def _who_text(who):
    return ("Không tìm thấy thành viên %s trong hồ sơ. Bạn nói về ai?" % who) if who else "Bạn nói về thành viên nào?"


# ---------- lập giỏ ----------

def _shipping(session, store_id):
    return session["shipping"] if session["shipping"] is not None else tools.shipping_fee(store_id)


def _infeasible(session, summary):
    budget = session["profile"]["budget"]
    missing = [name for name, n in summary["safe_counts"].items() if n == 0]
    session.update(status="CART_INFEASIBLE", cart=None, store_id=summary["id"])
    if missing or summary["min_total"] is None:
        session["infeasible"] = {"kind": "NO_SAFE_ITEM", "members": missing, "min_total": None, "shortfall": None}
    else:
        session["infeasible"] = {"kind": "OVER_BUDGET", "members": [], "min_total": summary["min_total"],
                                 "shortfall": summary["min_total"] - budget}
    return session


def _choose_store(session):
    """Trả (store_id, None) nếu có quán khả thi, ngược lại (None, tóm tắt quán gần khả thi nhất)."""
    profile = session["profile"]
    members, budget = profile["members"], profile["budget"]
    ids = session["candidates"] or [s["id"] for s in tools.list_restaurants()]
    ids = [i for i in ids if i not in session["tried"]] or ids
    summaries = [tools.store_summary(i, members, budget, _shipping(session, i)) for i in ids]
    viable = [s for s in summaries if s["min_total"] is not None and s["min_total"] <= budget]
    if not viable:
        best = max(summaries, key=lambda s: (sum(1 for n in s["safe_counts"].values() if n),
                                             -(s["min_total"] or 0)))
        return None, best
    if len(viable) == 1:
        return viable[0]["id"], None
    choice = llm_steps.choose_restaurant(profile, viable, session["tried"])
    if choice["store_id"] in {s["id"] for s in viable}:
        return choice["store_id"], None
    best = max(viable, key=lambda s: (sum(s["safe_counts"].values()), -s["min_total"]))
    return best["id"], None


def _plan_cart(session):
    profile = session["profile"]
    members, budget = profile["members"], profile["budget"]
    store_id = session["store_id"]
    if store_id is None:
        store_id, worst = _choose_store(session)
        if store_id is None:
            return _infeasible(session, worst)
    shipping = _shipping(session, store_id)
    summary = tools.store_summary(store_id, members, budget, shipping)
    if summary["min_total"] is None or summary["min_total"] > budget:
        return _infeasible(session, summary)
    menu = tools.load_menu(store_id)
    safe = [tools.safe_mains(m, menu) for m in members]          # theo thứ tự thành viên, không theo tên
    options = {m["name"]: [{"id": k, "name": menu[k]["name"], "price": menu[k]["price"]} for k in ok]
               for m, (ok, _) in zip(members, safe)}
    errors, selected, reasons, built_by = [], None, [], "AI"
    for _ in range(MAX_REPAIR + 1):
        result = llm_steps.pick_items(members, options, budget, shipping, errors)
        picks = {llm_steps.clean_name(p["member"]).casefold(): p for p in result["picks"]}
        chosen = [picks.get(m["name"].casefold(), {}) for m in members]
        selected = [c.get("item_id") for c in chosen]
        reasons = [c.get("reason", "") for c in chosen]
        errors = ["%s: món %s không nằm trong danh sách an toàn." % (m["name"], k)
                  for m, k, (ok, _) in zip(members, selected, safe) if k not in ok]
        errors += tools.validate_cart(members, selected, menu, budget, shipping)
        if not errors:
            break
    if errors:
        built_by = "FALLBACK"
        selected = [min(ok, key=lambda k: menu[k]["price"]) for ok, _ in safe]
        reasons = ["món an toàn rẻ nhất"] * len(members)
        if tools.validate_cart(members, selected, menu, budget, shipping):
            return _infeasible(session, summary)
    lines = [{"member": m["name"], "item_id": k, "name": menu[k]["name"], "price": menu[k]["price"], "reason": r}
             for m, k, r in zip(members, selected, reasons)]
    subtotal = sum(line["price"] for line in lines)
    excluded = {m["name"]: ex for m, (_, ex) in zip(members, safe) if m["vegetarian"] or m["allergens"]}
    session.update(status="CART_VALID", store_id=store_id, infeasible=None, cart={
        "lines": lines, "subtotal": subtotal, "shipping": shipping, "total": subtotal + shipping,
        "budget": budget, "remaining": budget - subtotal - shipping, "excluded": excluded, "built_by": built_by})
    return session


# ---------- hiển thị ----------

def _vnd(n):
    return format(n, ",") + "đ"


def _store_name(store_id):
    return next((s["name"] for s in tools.list_restaurants() if s["id"] == store_id), store_id)


def _render_draft(profile):
    questions = open_questions(profile)
    if questions:
        return "\n".join(q["text"] for q in questions)
    if not profile.get("budget"):
        return llm_steps.BUDGET_QUESTION
    rows = ["Hồ sơ nháp, quỹ %s:" % _vnd(profile["budget"])]
    for m in profile["members"]:
        tags = (["ăn chay"] if m["vegetarian"] else []) + ["dị ứng " + v for v in m["allergens"].values()]
        rows.append("- %s: %s" % (m["name"], "; ".join(tags + m["preferences"]) or "không có lời dặn riêng"))
    rows.append("Vui lòng xác nhận hồ sơ trước khi lập giỏ.")
    return "\n".join(rows)


def render(session):
    """Chữ hiển thị cho CLI / eval."""
    profile = session["profile"]
    if session["status"] == "PROFILE_DRAFT":
        return _render_draft(profile)
    out = []
    last = session["messages"][-1] if session["messages"] else None
    if (last and last["role"] == "assistant" and last["kind"] in ("REFUSAL", "INFO")
            and last.get("turn", 0) == session.get("turn", 0)):
        out.append(last["text"])
    store = _store_name(session["store_id"])
    if session["status"] == "CART_INFEASIBLE":
        inf = session["infeasible"]
        if inf["kind"] == "NO_SAFE_ITEM":
            out.append("Chưa lập được giỏ ở %s (%s): không có món phù hợp cho %s. Đề xuất đổi sang quán khác."
                       % (store, session["store_id"], ", ".join(inf["members"])))
        else:
            out.append("Chưa lập được giỏ ở %s (%s): tối thiểu %s gồm phí ship, quỹ %s, thiếu %s. "
                       "Đề xuất tăng quỹ lên %s hoặc đổi quán."
                       % (store, session["store_id"], _vnd(inf["min_total"]), _vnd(profile["budget"]),
                          _vnd(inf["shortfall"]), _vnd(inf["min_total"])))
        return "\n".join(out)
    cart = session["cart"]
    menu = tools.load_menu(session["store_id"])
    out.append("Giỏ đề xuất tại %s (%s):" % (store, session["store_id"]))
    for line in cart["lines"]:
        out.append("- %s: %s (%s) · %s" % (line["member"], line["name"], line["item_id"], _vnd(line["price"])))
    out.append("Tạm tính %s · phí ship %s · tổng %s · quỹ %s · còn %s." % (
        _vnd(cart["subtotal"]), _vnd(cart["shipping"]), _vnd(cart["total"]), _vnd(cart["budget"]),
        _vnd(cart["remaining"])))
    for name, items in cart["excluded"].items():
        if items:
            shown = "; ".join("%s: %s" % (menu[k]["name"], r) for k, r in list(items.items())[:3])
            out.append("Món bị loại cho %s: %s" % (name, shown))
    out.append("Đã kiểm theo yêu cầu đã xác nhận và menu quán.")
    allergic = [m for m in profile["members"] if m["allergens"]]
    if allergic:
        out.append("Ghi chú cho quán: " + "; ".join(
            "suất của %s không có %s, kể cả nước dùng và nước chấm" % (m["name"], ", ".join(m["allergens"].values()))
            for m in allergic) + ".")
    out.append("Đã chốt giỏ, copy tin nhắn này gửi lại nhóm." if session["status"] == "FINALIZED"
               else "Vui lòng duyệt giỏ.")
    return "\n".join(out)
