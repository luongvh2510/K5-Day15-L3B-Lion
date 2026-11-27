"""API HTTP dùng thư viện chuẩn, mọi quyết định phiên do core xử lý."""
import json
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'codebase'))
import core
import store
import tools
from llm_steps import AIUnavailable


class ApiError(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message


def fail(status, code, message):
    raise ApiError(status, code, message)


def restaurant(store_id):
    found = next((x for x in tools.list_restaurants() if x['id'] == store_id), None)
    if found is None:
        fail(404, 'NOT_FOUND', 'Không tìm thấy quán.')
    return {**found, 'shipping_fee': tools.shipping_fee(store_id)}


def stamp_messages(session):
    for index, msg in enumerate(session['messages'], 1):
        msg.setdefault('id', f'msg{index}')
        msg.setdefault('created_at', datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))


def state(s):
    profile = s['profile']
    ids = {m['name']: f'm{i}' for i, m in enumerate(profile['members'], 1)}
    members = []
    for m in profile['members']:
        mid = ids[m['name']]
        # Core chỉ lưu danh sách câu trích theo người, không gán chính xác từng câu cho từng ràng buộc.
        source = {'kind': 'CHAT', 'line': None, 'quote': None}
        constraints = []
        if m.get('vegetarian'):
            constraints.append({'id': f'{mid}-vegetarian', 'type': 'VEGETARIAN', 'allergen': None, 'note': None, 'source': source.copy(), 'locked': s['locked']})
        for tag in m.get('allergens', {}):
            constraints.append({'id': f'{mid}-{tag}', 'type': 'ALLERGY', 'allergen': tag.upper(), 'note': None, 'source': source.copy(), 'locked': s['locked']})
        members.append({'id': mid, 'name': m['name'], 'origin': 'CHAT', 'hard_constraints': constraints,
                        'preferences': [{'id': f'{mid}-p{i}', 'text': p, 'source': source.copy()} for i, p in enumerate(m.get('preferences', []), 1)], 'flags': [], 'quotes': m.get('quotes', [])})
    questions = [{'id': q['id'], 'member_id': ids.get(q.get('member')), 'text': q['text'], 'options': [], 'status': q['status']} for q in profile.get('questions', [])]
    cart = None
    if s['cart'] is not None:
        c = s['cart']
        menu = tools.load_menu(s['store_id'])
        lines = [{'member_id': ids.get(line['member']), 'menu_item_id': line['item_id'], 'name': line['name'], 'type': 'MAIN', 'unit_price': line['price'], 'qty': 1, 'line_total': line['price'], 'reason': line.get('reason'), 'note': None} for line in c['lines']]
        excluded = []
        for name, items in c['excluded'].items():
            for item_id, reason in items.items():
                rule = 'BR-04' if reason == 'không rõ thành phần' else 'BR-02' if reason.startswith('không chay') else 'BR-03' if reason.startswith('dị ứng') else 'BR-05'
                excluded.append({'member_id': ids.get(name), 'menu_item_id': item_id, 'name': menu[item_id]['name'], 'reasons': [{'rule': rule, 'text': reason}]})
        cart = {'lines': lines, 'subtotal': c['subtotal'], 'shipping_fee': c['shipping'], 'total': c['total'], 'budget': c['budget'], 'remaining': c['remaining'], 'excluded': excluded, 'built_by': c['built_by']}
    infeasible = None
    if s['infeasible']:
        item = s['infeasible']
        options = []
        if item['kind'] == 'OVER_BUDGET':
            options.append({'id': 'budget', 'label': f"Tăng quỹ lên {item['min_total']:,}đ", 'action': {'type': 'SET_BUDGET', 'budget': item['min_total']}})
        options.append({'id': 'restaurant', 'label': 'Đổi quán', 'action': {'type': 'CHANGE_RESTAURANT'}})
        infeasible = {'kind': item['kind'], 'members_without_option': [ids.get(n) for n in item['members']], 'min_total': item['min_total'], 'shortfall': item['shortfall'], 'message': core.render(s), 'options': options}
    return {'session_id': s['id'], 'status': s['status'], 'restaurant': restaurant(s['store_id']) if s['store_id'] else None,
            'budget': profile.get('budget'), 'chat_lines': [], 'members': members, 'questions': questions,
            'can_confirm': s['status'] == 'PROFILE_DRAFT' and core.can_confirm(profile),
            'messages': [{**m, 'question_id': None} for m in s['messages']], 'cart': cart,
            'validation': {'ok': True, 'violations': []} if cart else None,
            'infeasible': infeasible, 'final_message': core.render(s) if s['status'] == 'FINALIZED' else None}


def text_field(body, name):
    value = body.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > 4000:
        fail(400, 'INVALID_INPUT', 'Nội dung phải có từ 1 đến 4.000 ký tự.')
    return value


def dispatch(method, path, body):
    parts = path.strip('/').split('/')
    if parts[:1] != ['api']:
        fail(404, 'NOT_FOUND', 'Không tìm thấy đường dẫn.')
    parts = parts[1:]
    if method == 'GET' and parts == ['restaurants']:
        return [restaurant(x['id']) for x in tools.list_restaurants()]
    if method == 'GET' and len(parts) == 3 and parts[0] == 'restaurants' and parts[2] == 'menu':
        return {'restaurant': restaurant(parts[1]), 'items': [{'id': k, **v} for k, v in tools.load_menu(parts[1]).items()]}
    if method == 'POST' and parts == ['debug', 'validate-cart']:
        try:
            rid = body['store_id']; restaurant(rid)
            members, selected, budget, shipping = (body[k] for k in ('members', 'selected', 'budget', 'shipping'))
            if not isinstance(members, list) or not all(isinstance(m, dict) and isinstance(m.get('name'), str) and isinstance(m.get('allergens', {}), dict) for m in members) or not isinstance(selected, list) or not all(isinstance(x, str) for x in selected) or type(budget) is not int or budget <= 0 or type(shipping) is not int or shipping < 0:
                raise ValueError()
            return tools.validate_cart(members, selected, tools.load_menu(rid), budget, shipping)
        except (KeyError, TypeError, ValueError):
            fail(400, 'INVALID_INPUT', 'Dữ liệu kiểm giỏ không hợp lệ.')
    if method == 'POST' and parts == ['sessions']:
        session = core.start(text_field(body, 'chat_text'))
        stamp_messages(session)
        store.save(session)
        core.SESSIONS.pop(session['id'], None)
        return state(session)
    if len(parts) >= 2 and parts[0] == 'sessions':
        sid = parts[1]
        with store.session_lock(sid):
            session = store.load(sid)
            if session is None:
                fail(404, 'NOT_FOUND', 'Không tìm thấy phiên.')
            if method == 'GET' and len(parts) == 2:
                return state(session)
            if method == 'POST' and len(parts) == 3:
                action = parts[2]
                allowed = {'messages': ('PROFILE_DRAFT', 'CART_VALID', 'CART_INFEASIBLE'), 'confirm': ('PROFILE_DRAFT',), 'finalize': ('CART_VALID',)}
                if action not in allowed:
                    fail(404, 'NOT_FOUND', 'Không tìm thấy đường dẫn.')
                if session['status'] not in allowed[action]:
                    fail(409, 'INVALID_STATE', 'Thao tác không phù hợp trạng thái phiên.')
                if action == 'messages':
                    core.send(session, text_field(body, 'text'))
                elif action == 'confirm':
                    core.confirm(session)
                else:
                    core.finalize(session)
                stamp_messages(session)
                store.save(session)
                return state(session)
    fail(404, 'NOT_FOUND', 'Không tìm thấy đường dẫn.')


class Handler(BaseHTTPRequestHandler):
    def _handle(self):
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size < 0 or size > 65536:
                fail(400, 'INVALID_INPUT', 'Dữ liệu gửi lên không hợp lệ.')
            raw = self.rfile.read(size)
            body = json.loads(raw) if raw else {}
            if not isinstance(body, dict):
                fail(400, 'INVALID_INPUT', 'Nội dung phải là JSON object.')
            result = dispatch(self.command, urlsplit(self.path).path, body)
            status = 200
        except (ValueError, UnicodeDecodeError):
            status, result = 400, {'error': {'code': 'INVALID_INPUT', 'message': 'JSON không hợp lệ.'}}
        except AIUnavailable:
            status, result = 502, {'error': {'code': 'AI_UNAVAILABLE', 'message': 'Hệ thống AI tạm thời không phản hồi, vui lòng thử lại.'}}
        except ApiError as exc:
            status, result = exc.status, {'error': {'code': exc.code, 'message': exc.message}}
        data = json.dumps(result, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    do_GET = _handle
    do_POST = _handle
    do_PATCH = _handle


def serve(host='127.0.0.1', port=8000):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f'API đang chạy tại http://{host}:{port}/api', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
