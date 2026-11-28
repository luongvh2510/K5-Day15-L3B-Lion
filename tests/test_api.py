import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import _path
from server import api
from test_core import first_pick, member, profile


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = mock.patch.object(api.store, 'DB_PATH', Path(cls.temp.name) / 'test.sqlite3')
        cls.db.start()
        cls.server = api.ThreadingHTTPServer(('127.0.0.1', 0), api.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:%s/api' % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()
        cls.db.stop(); cls.temp.cleanup()

    def request(self, method, path, data=None):
        req = Request(self.base + path, data=json.dumps(data).encode() if data is not None else None, method=method, headers={'Content-Type': 'application/json'})
        try:
            with urlopen(req) as res:
                return res.status, json.load(res)
        except HTTPError as exc:
            return exc.code, json.load(exc)

    def test_lifecycle_and_errors(self):
        profile = {'budget': 300000, 'members': [{'name': 'An', 'vegetarian': False, 'allergens': {}, 'preferences': [], 'quotes': []}], 'questions': []}
        with mock.patch.object(api.core.llm_steps, 'extract_profile', return_value=profile):
            status, draft = self.request('POST', '/sessions', {'chat_text': 'An: ăn trưa 300k'})
        self.assertEqual(status, 200)
        sid = draft['session_id']
        self.assertTrue(draft['can_confirm'])
        self.assertEqual(self.request('GET', '/sessions/' + sid)[1], draft)
        self.assertEqual(self.request('POST', '/sessions/' + sid + '/finalize')[0], 409)
        with mock.patch.object(api.core.llm_steps, 'choose_restaurant', return_value={'store_id': 'store_01'}), mock.patch.object(api.core.llm_steps, 'pick_items', return_value={'picks': [{'member': 'An', 'item_id': 'dish_009', 'reason': 'test'}]}):
            status, cart = self.request('POST', '/sessions/' + sid + '/confirm')
        self.assertEqual(status, 200)
        self.assertEqual(cart['status'], 'CART_VALID')
        self.assertTrue(cart['validation']['ok'])
        status, final = self.request('POST', '/sessions/' + sid + '/finalize')
        self.assertEqual(final['status'], 'FINALIZED')
        self.assertTrue(final['final_message'])
        self.assertEqual(self.request('POST', '/sessions/' + sid + '/messages', {'text': 'hello'})[0], 409)
        self.assertEqual(self.request('POST', '/sessions', {'chat_text': ' '})[0], 400)
        self.assertEqual(self.request('GET', '/sessions/missing')[0], 404)
        self.assertEqual(self.request('GET', '/restaurants/missing/menu')[0], 404)

    def test_finalize_deducts_budget_and_persists_remaining(self):
        initial_budget = 300000
        profile = {'budget': initial_budget, 'members': [
            {'name': 'An', 'vegetarian': False, 'allergens': {}, 'preferences': [], 'quotes': []}
        ], 'questions': []}
        steps = api.core.llm_steps
        with mock.patch.object(steps, 'extract_profile', return_value=profile):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An: quỹ chung 300k'})
        path = '/sessions/' + draft['session_id']
        picks = {'picks': [{'member': 'An', 'item_id': 'dish_009', 'reason': 'test'}]}
        with mock.patch.object(steps, 'choose_restaurant', return_value={'store_id': 'store_01'}), \
                mock.patch.object(steps, 'pick_items', return_value=picks):
            _, proposed = self.request('POST', path + '/confirm')
        self.assertEqual(proposed['budget'], initial_budget)
        self.assertEqual(proposed['status'], 'CART_VALID')

        status, finalized = self.request('POST', path + '/finalize')
        self.assertEqual((status, finalized['status']), (200, 'FINALIZED'))
        self.assertEqual(finalized['budget'], max(0, initial_budget - proposed['cart']['total']))
        self.assertEqual(finalized['budget'], proposed['cart']['remaining'])
        self.assertEqual(finalized['cart'], proposed['cart'])
        self.assertIn(f"quỹ {initial_budget:,}đ", finalized['final_message'])
        self.assertIn(f"còn {finalized['budget']:,}đ", finalized['final_message'])
        self.assertEqual(self.request('GET', path)[1], finalized)
        self.assertEqual(self.request('POST', path + '/finalize')[0], 409)
        self.assertEqual(self.request('GET', path)[1]['budget'], finalized['budget'])

    def test_reopen_discards_cart_and_unlocks(self):
        profile = {'budget': 300000, 'members': [{'name': 'An', 'vegetarian': True, 'allergens': {}, 'preferences': [], 'quotes': []}], 'questions': []}
        with mock.patch.object(api.core.llm_steps, 'extract_profile', return_value=profile):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An: chay 300k'})
        path = '/sessions/' + draft['session_id']
        self.assertEqual(self.request('POST', path + '/reopen')[0], 409)
        with mock.patch.object(api.core.llm_steps, 'choose_restaurant', return_value={'store_id': 'store_08'}), mock.patch.object(api.core.llm_steps, 'pick_items', return_value={'picks': [{'member': 'An', 'item_id': 'dish_077', 'reason': 'test'}]}):
            _, cart = self.request('POST', path + '/confirm')
        self.assertEqual(cart['status'], 'CART_VALID')
        self.assertTrue(cart['members'][0]['hard_constraints'][0]['locked'])
        _, reopened = self.request('POST', path + '/reopen')
        self.assertEqual(reopened['status'], 'PROFILE_DRAFT')
        self.assertIsNone(reopened['cart'])
        self.assertFalse(reopened['members'][0]['hard_constraints'][0]['locked'])
        self.assertEqual(self.request('GET', path)[1], reopened)

    def test_select_restaurant_rebuilds_with_locked_profile(self):
        profile = {'budget': 100000, 'members': [{'name': 'An', 'vegetarian': True, 'allergens': {},
                                                 'preferences': [], 'quotes': []}], 'questions': []}
        steps = api.core.llm_steps
        with mock.patch.object(steps, 'extract_profile', return_value=profile):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An: ăn chay, quỹ 100k'})
        path = '/sessions/' + draft['session_id']

        def select(restaurant_id):
            action = {'type': 'SELECT_RESTAURANT', 'restaurant_id': restaurant_id}
            return self.request('POST', path + '/actions', {'action': action})

        with mock.patch.object(steps, 'choose_restaurant', return_value={'store_id': 'store_08'}), \
                mock.patch.object(steps, 'pick_items', return_value={'picks': [{'member': 'An', 'item_id': 'dish_077'}]}):
            _, cart = self.request('POST', path + '/confirm')
        self.assertEqual(cart['restaurant']['id'], 'store_08')
        self.assertEqual(select('')[0], 400)
        self.assertEqual(select('missing')[0], 404)
        self.assertEqual(self.request('GET', path)[1], cart)

        status, infeasible = select('store_01')
        self.assertEqual((status, infeasible['status'], infeasible['restaurant']['id']),
                         (200, 'CART_INFEASIBLE', 'store_01'))
        self.assertIsNone(infeasible['cart'])
        with mock.patch.object(steps, 'pick_items', return_value={'picks': [{'member': 'An', 'item_id': 'dish_077'}]}):
            status, restored = select('store_08')
        self.assertEqual((status, restored['status'], restored['restaurant']['id']), (200, 'CART_VALID', 'store_08'))
        self.assertTrue(restored['validation']['ok'])
        self.assertEqual(restored['members'], cart['members'])
        self.assertEqual(restored['budget'], 100000)

    def test_change_restaurant_cycles_between_feasible_stores(self):
        steps = api.core.llm_steps
        with mock.patch.object(steps, 'extract_profile', return_value=profile([member('An', vegetarian=True)])):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An ăn chay, quỹ 300k'})
        path = '/sessions/' + draft['session_id']
        change = {'action': {'type': 'CHANGE_RESTAURANT'}}

        with mock.patch.object(steps, 'choose_restaurant', return_value={'store_id': 'store_08'}), \
                mock.patch.object(steps, 'pick_items', side_effect=first_pick):
            _, confirmed = self.request('POST', path + '/confirm')
            self.assertEqual(confirmed['restaurant']['id'], 'store_08')
            for expected in ('store_09', 'store_08', 'store_09', 'store_08'):
                status, switched = self.request('POST', path + '/actions', change)
                self.assertEqual((status, switched['status'], switched['restaurant']['id']),
                                 (200, 'CART_VALID', expected))
                self.assertTrue(switched['validation']['ok'])
                self.assertEqual(switched['members'], confirmed['members'])
                self.assertEqual(switched['messages'], confirmed['messages'])

    def test_chat_budget_keeps_valid_cart_and_rechecks_restaurants(self):
        steps = api.core.llm_steps
        with mock.patch.object(steps, 'extract_profile', return_value=profile([member('An', vegetarian=True)])):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An ăn chay, quỹ 300k'})
        sid = draft['session_id']
        path = '/sessions/' + sid
        change = {'action': {'type': 'CHANGE_RESTAURANT'}}
        with mock.patch.object(steps, 'choose_restaurant', return_value={'store_id': 'store_08'}), \
                mock.patch.object(steps, 'pick_items', side_effect=first_pick):
            self.request('POST', path + '/confirm')
            self.request('POST', path + '/actions', change)
            self.request('POST', path + '/actions', change)
        lower = {'action': {'type': 'SET_BUDGET', 'budget': 50000}}
        self.assertEqual(self.request('POST', path + '/actions', lower)[0], 200)
        _, before = self.request('POST', path + '/actions', change)
        self.assertEqual(before['restaurant']['id'], 'store_08')
        min_total = api.tools.load_menu('store_09')['dish_090']['price'] + api.tools.shipping_fee('store_09')
        self.assertIn(f'{min_total:,}đ', before['messages'][-1]['text'])
        self.assertIn('giữ giỏ', before['messages'][-1]['text'])
        self.assertIn('store_09', api.store.load(sid)['tried'])

        for text, amount in [('đổi quỹ lên 1 triệu', 1000000), ('Đổi quỹ thành 3 triệu', 3000000)]:
            with self.subTest(text=text), \
                    mock.patch.object(steps, 'call_json', return_value={'intent': 'CHANGE_BUDGET', 'amount': amount}), \
                    mock.patch.object(steps, 'pick_items', side_effect=AssertionError('Giỏ vẫn trong quỹ')):
                status, updated = self.request('POST', path + '/messages', {'text': text})
                self.assertEqual((status, updated['status'], updated['budget']), (200, 'CART_VALID', amount))
                self.assertEqual(updated['restaurant'], before['restaurant'])
                self.assertEqual(updated['members'], before['members'])
                cart = updated['cart']
                self.assertEqual(cart, {**before['cart'], 'budget': amount,
                                        'remaining': amount - before['cart']['total']})
                last = updated['messages'][-1]
                self.assertEqual((last['role'], last['kind'], last['text']),
                                 ('assistant', 'INFO', f'Đã cập nhật quỹ chung thành {amount:,}đ.'))
                self.assertEqual(last['turn'], updated['messages'][-2]['turn'])
                self.assertEqual(api.store.load(sid)['tried'], [])
                self.assertEqual(self.request('GET', path)[1], updated)

        with mock.patch.object(steps, 'pick_items', side_effect=first_pick):
            _, switched = self.request('POST', path + '/actions', change)
        self.assertEqual((switched['status'], switched['restaurant']['id']), ('CART_VALID', 'store_09'))

    def test_chat_budget_recovers_infeasible_cart_from_another_store(self):
        steps = api.core.llm_steps
        with mock.patch.object(steps, 'extract_profile', return_value=profile([member('An', vegetarian=True)], budget=10000)):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An ăn chay, quỹ 10k'})
        path = '/sessions/' + draft['session_id']
        self.request('POST', path + '/confirm')
        select = {'action': {'type': 'SELECT_RESTAURANT', 'restaurant_id': 'store_01'}}
        _, before = self.request('POST', path + '/actions', select)
        self.assertEqual((before['status'], before['restaurant']['id']), ('CART_INFEASIBLE', 'store_01'))
        route = {'intent': 'CHANGE_BUDGET', 'amount': 50000}
        with mock.patch.object(steps, 'call_json', return_value=route), \
                mock.patch.object(steps, 'pick_items', side_effect=first_pick):
            status, updated = self.request('POST', path + '/messages', {'text': 'Đổi quỹ lên 50k'})
        self.assertEqual((status, updated['status'], updated['restaurant']['id']), (200, 'CART_VALID', 'store_08'))
        self.assertEqual(updated['cart']['remaining'], 50000 - updated['cart']['total'])
        self.assertEqual(updated['members'], before['members'])
        self.assertEqual(updated['messages'][-1]['text'], 'Đã cập nhật quỹ chung thành 50,000đ.')

    def test_menu_only_returns_available_items(self):
        menu = {
            'in-stock': {'name': 'Xôi gà', 'available': True},
            'sold-out': {'name': 'Xôi bắp', 'available': False},
        }
        with mock.patch.object(api.tools, 'load_menu', return_value=menu):
            status, response = self.request('GET', '/restaurants/store_08/menu')
        self.assertEqual(status, 200)
        self.assertEqual(response['restaurant']['id'], 'store_08')
        self.assertEqual([item['id'] for item in response['items']], ['in-stock'])

    def test_chat_swaps_one_dish_and_preserves_cart_on_rejection(self):
        members = [
            {'name': 'An', 'vegetarian': True, 'allergens': {}, 'preferences': [], 'quotes': []},
            {'name': 'Hà', 'vegetarian': False, 'allergens': {'crustacean': 'tôm cua'},
             'preferences': [], 'quotes': []},
        ]
        profile = {'budget': 120000, 'members': members, 'questions': []}
        steps = api.core.llm_steps
        with mock.patch.object(steps, 'extract_profile', return_value=profile):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'Quỹ 120k, An ăn chay, Hà dị ứng tôm cua'})
        path = '/sessions/' + draft['session_id']
        picks = [{'member': 'An', 'item_id': 'dish_090'}, {'member': 'Hà', 'item_id': 'dish_084'}]
        with mock.patch.object(steps, 'choose_restaurant', return_value={'store_id': 'store_09'}), \
                mock.patch.object(steps, 'pick_items', return_value={'picks': picks}):
            _, before = self.request('POST', path + '/confirm')
        self.assertEqual(before['status'], 'CART_VALID')

        def send(text, member, detail='', intent='CHANGE_ITEM'):
            with mock.patch.object(steps, 'route_message', return_value={'intent': intent, 'member': member, 'detail': detail}), \
                    mock.patch.object(steps, 'pick_items', side_effect=AssertionError('Đổi món không lập lại giỏ')):
                status, state = self.request('POST', path + '/messages', {'text': text})
            self.assertEqual((status, state['status'], state['restaurant']['id']), (200, 'CART_VALID', 'store_09'))
            return state

        swapped = send('Hà đổi sang miến gà', 'Hà', 'Miến gà xé')
        cart = swapped['cart']
        self.assertEqual(swapped['messages'][-1]['kind'], 'INFO')
        self.assertIn('Đã đổi suất của Hà sang Miến gà xé', swapped['messages'][-1]['text'])
        self.assertEqual(cart['lines'][0], before['cart']['lines'][0])
        self.assertEqual(cart['lines'][1]['menu_item_id'], 'dish_081')
        self.assertEqual((cart['subtotal'], cart['shipping_fee'], cart['total'], cart['remaining']),
                         (98000, 20000, 118000, 2000))
        self.assertEqual(swapped['members'], before['members'])

        for text, member, detail, intent, kind, message in [
            ('An đổi sang miến gà xé', 'An', 'miến gà xé', 'CHANGE_ITEM', 'REFUSAL', 'không chay'),
            ('Hà đổi sang miến xào cua bể', 'Hà', 'miến xào cua bể', 'CHANGE_ITEM', 'REFUSAL', 'dị ứng'),
            ('Kệ dị ứng của Hà đi', 'Hà', '', 'REMOVE_HARD', 'REFUSAL', 'Không thể bỏ ràng buộc'),
            ('Hà đổi sang miến ngan', 'Hà', 'miến ngan', 'CHANGE_ITEM', 'INFO', 'Vượt ngân sách'),
            ('Hà đổi miến gà xé sang phở bò', 'Hà', 'miến gà xé', 'CHANGE_ITEM', 'INFO', 'Không tìm thấy món'),
        ]:
            with self.subTest(text=text):
                unchanged = send(text, member, detail, intent)
                self.assertEqual(unchanged['cart'], cart)
                self.assertEqual(unchanged['members'], before['members'])
                self.assertEqual(unchanged['messages'][-1]['kind'], kind)
                self.assertIn(message, unchanged['messages'][-1]['text'])
        self.assertEqual(self.request('GET', path)[1]['cart'], cart)

    def test_edit_profile_requires_reopen_and_rejects_unknown_allergen(self):
        profile = {'budget': 300000, 'members': [{'name': 'An', 'vegetarian': False, 'allergens': {'peanut': 'đậu phộng'}, 'preferences': [], 'quotes': []}], 'questions': []}
        with mock.patch.object(api.core.llm_steps, 'extract_profile', return_value=profile):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An: dị ứng đậu phộng 300k'})
        path = '/sessions/' + draft['session_id']
        member = draft['members'][0]
        member['hard_constraints'] = [{'type': 'ALLERGY', 'allergen': 'OTHER'}]
        self.assertEqual(self.request('PATCH', path + '/members', {'members': [member]})[0], 400)
        self.assertEqual(self.request('GET', path)[1]['members'][0]['hard_constraints'][0]['allergen'], 'PEANUT')
        member['hard_constraints'] = [{'type': 'VEGETARIAN'}]
        _, changed = self.request('PATCH', path + '/members', {'members': [member]})
        self.assertEqual(changed['members'][0]['hard_constraints'][0]['type'], 'VEGETARIAN')
        with mock.patch.object(api.core.llm_steps, 'choose_restaurant', return_value={'store_id': 'store_08'}), mock.patch.object(api.core.llm_steps, 'pick_items', return_value={'picks': [{'member': 'An', 'item_id': 'dish_077', 'reason': 'test'}]}):
            _, confirmed = self.request('POST', path + '/confirm')
        self.assertEqual(self.request('PATCH', path + '/members', {'members': []})[0], 409)
        self.assertTrue(self.request('GET', path)[1]['members'][0]['hard_constraints'][0]['locked'])
        self.request('POST', path + '/reopen')
        member['hard_constraints'] = []
        _, changed = self.request('PATCH', path + '/members', {'members': [member]})
        self.assertEqual(changed['members'][0]['hard_constraints'], [])

    def test_actions_recalculate_and_keep_constraints(self):
        profile = {'budget': 10000, 'members': [{'name': 'An', 'vegetarian': True, 'allergens': {}, 'preferences': [], 'quotes': []}], 'questions': []}
        with mock.patch.object(api.core.llm_steps, 'extract_profile', return_value=profile):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An: chay 10k'})
        path = '/sessions/' + draft['session_id']
        self.assertEqual(self.request('POST', path + '/actions', {'action': {'type': 'SET_BUDGET', 'budget': 300000}})[0], 409)
        _, result = self.request('POST', path + '/confirm')
        self.assertEqual(result['status'], 'CART_INFEASIBLE')
        self.assertEqual(self.request('POST', path + '/actions', {'action': {'type': 'SET_BUDGET', 'budget': -1}})[0], 400)
        self.assertEqual(self.request('POST', path + '/actions', {'action': {'type': 'CHANGE_RESTAURANT', 'restaurant_id': 'missing'}})[0], 404)
        with mock.patch.object(api.core.llm_steps, 'pick_items', return_value={'picks': [{'member': 'An', 'item_id': 'dish_077', 'reason': 'test'}]}):
            _, result = self.request('POST', path + '/actions', {'action': {'type': 'SET_BUDGET', 'budget': 300000}})
        self.assertEqual(result['status'], 'CART_VALID')
        self.assertTrue(result['members'][0]['hard_constraints'][0]['locked'])
        _, result = self.request('POST', path + '/actions', {'action': {'type': 'CHANGE_RESTAURANT', 'restaurant_id': 'store_01'}})
        self.assertEqual(result['status'], 'CART_INFEASIBLE')
        self.assertTrue(result['members'][0]['hard_constraints'][0]['locked'])

    def test_ai_failure_does_not_save_partial_mutations(self):
        profile = {'budget': 300000, 'members': [{'name': 'An', 'vegetarian': False, 'allergens': {}, 'preferences': [], 'quotes': []}], 'questions': []}
        with mock.patch.object(api.core.llm_steps, 'extract_profile', return_value=profile):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An: 300k'})
        path = '/sessions/' + draft['session_id']
        with mock.patch.object(api.core.llm_steps, 'apply_answer', side_effect=api.AIUnavailable('failed')):
            status, error = self.request('POST', path + '/messages', {'text': 'thêm món'})
        self.assertEqual((status, error['error']['code']), (502, 'AI_UNAVAILABLE'))
        self.assertEqual(self.request('GET', path)[1], draft)

    def test_unconfigured_model_returns_502(self):
        with mock.patch.object(api.core.llm_steps, 'extract_profile', side_effect=NotImplementedError()):
            status, result = self.request('POST', '/sessions', {'chat_text': 'An: 300k'})
        self.assertEqual((status, result['error']['code']), (502, 'AI_UNAVAILABLE'))

    def test_confirm_with_open_question_returns_409_and_keeps_state(self):
        profile = {'budget': 300000, 'members': [{'name': 'An', 'vegetarian': True, 'allergens': {}, 'preferences': [], 'quotes': []}],
                   'questions': [{'id': 'q1', 'member': 'An', 'text': 'An ăn chay mà xin cơm gà?', 'status': 'OPEN'}]}
        with mock.patch.object(api.core.llm_steps, 'extract_profile', return_value=profile):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An: chay, cơm gà 300k'})
        path = '/sessions/' + draft['session_id']
        self.assertFalse(draft['can_confirm'])
        status, error = self.request('POST', path + '/confirm')
        self.assertEqual((status, error['error']['code']), (409, 'INVALID_STATE'))
        self.assertEqual(self.request('GET', path)[1], draft)

    def test_draft_answer_moves_dish_preferences_to_recipients(self):
        an = member('An', vegetarian=True)
        an['preferences'] = ['cơm gà', 'ít cay']
        an['quotes'] = ['An: lấy thêm cơm gà']
        question = {'id': 'q1', 'member': 'An', 'text': 'An ăn chay. Cơm gà là cho ai?', 'status': 'OPEN'}
        draft_profile = profile([an, member('Dũng'), member('Chi')], questions=[question])
        steps = api.core.llm_steps

        for answer, recipients, expected in [
            ('Cơm gà dành cho Dũng', ['Dũng'], [['ít cay'], ['cơm gà'], []]),
            ('Cơm gà cho cả nhóm, trừ An', ['Dũng', 'Chi'], [['ít cay'], ['cơm gà'], ['cơm gà']]),
            ('Cơm gà cho Dũng và Tuấn', ['Dũng', 'Tuấn'], [['cơm gà', 'ít cay'], [], []]),
        ]:
            with self.subTest(answer=answer):
                with mock.patch.object(steps, 'extract_profile', return_value=draft_profile):
                    _, draft = self.request('POST', '/sessions', {'chat_text': an['quotes'][0]})
                path = '/sessions/' + draft['session_id']
                result = {
                    'changes': [
                        {'op': 'RESOLVE_QUESTION', 'question_id': 'q1'},
                        {'op': 'MOVE_PREFERENCE', 'member': 'An', 'text': 'cơm gà', 'recipients': recipients},
                    ],
                    'reply': 'Đã chuyển món.',
                }
                with mock.patch.object(steps, 'call_model', return_value={'text': json.dumps(result)}):
                    status, updated = self.request('POST', path + '/messages', {'text': answer})
                self.assertEqual((status, updated['status']), (200, 'PROFILE_DRAFT'))
                self.assertEqual([[p['text'] for p in m['preferences']] for m in updated['members']], expected)
                self.assertEqual(updated['members'][0]['hard_constraints'], draft['members'][0]['hard_constraints'])
                self.assertEqual(updated['members'][0]['quotes'], an['quotes'])
                moved = 'cơm gà' not in expected[0]
                self.assertEqual(updated['questions'][0]['status'], 'ANSWERED' if moved else 'OPEN')
                self.assertEqual(updated['can_confirm'], moved)
                self.assertEqual(self.request('GET', path)[1], updated)

    def test_unexpected_error_returns_json_500(self):
        with mock.patch.object(api.core.llm_steps, 'extract_profile', side_effect=KeyError('boom')):
            status, result = self.request('POST', '/sessions', {'chat_text': 'An: 300k'})
        self.assertEqual((status, result['error']['code']), (500, 'INTERNAL'))

    def test_get_not_blocked_while_session_busy(self):
        profile = {'budget': 300000, 'members': [{'name': 'An', 'vegetarian': False, 'allergens': {}, 'preferences': [], 'quotes': []}], 'questions': []}
        with mock.patch.object(api.core.llm_steps, 'extract_profile', return_value=profile):
            _, draft = self.request('POST', '/sessions', {'chat_text': 'An: 300k'})
        sid = draft['session_id']
        done = []
        with api.store.session_lock(sid):
            t = threading.Thread(target=lambda: done.append(self.request('GET', '/sessions/' + sid)[0]))
            t.start(); t.join(2)
            self.assertEqual(done, [200])

    def test_restaurants_and_debug(self):
        status, restaurants = self.request('GET', '/restaurants')
        self.assertEqual(status, 200)
        status, menu = self.request('GET', '/restaurants/' + restaurants[0]['id'] + '/menu')
        self.assertTrue(menu['items'])
        status, errors = self.request('POST', '/debug/validate-cart', {'store_id': restaurants[0]['id'], 'members': [{'name': 'An'}], 'selected': ['missing'], 'budget': 100000, 'shipping': 15000})
        self.assertEqual(status, 200)
        self.assertTrue(errors)
