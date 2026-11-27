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

    def test_restaurants_and_debug(self):
        status, restaurants = self.request('GET', '/restaurants')
        self.assertEqual(status, 200)
        status, menu = self.request('GET', '/restaurants/' + restaurants[0]['id'] + '/menu')
        self.assertTrue(menu['items'])
        status, errors = self.request('POST', '/debug/validate-cart', {'store_id': restaurants[0]['id'], 'members': [{'name': 'An'}], 'selected': ['missing'], 'budget': 100000, 'shipping': 15000})
        self.assertEqual(status, 200)
        self.assertTrue(errors)
