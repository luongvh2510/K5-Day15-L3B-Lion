import tempfile
import unittest
from pathlib import Path
from unittest import mock
import _path
import store


class TestStore(unittest.TestCase):
    def test_roundtrip_and_update(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(store, 'DB_PATH', Path(directory) / 'test.sqlite3'):
            self.assertIsNone(store.load('missing'))
            session = {'id': 'abc', 'text': 'ăn chay'}
            store.save(session)
            self.assertEqual(store.load('abc'), session)
            session['text'] = 'đã đổi'
            store.save(session)
            self.assertEqual(store.load('abc'), session)
