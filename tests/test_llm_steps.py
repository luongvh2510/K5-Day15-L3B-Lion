import unittest
from unittest import mock

import _path  # noqa: F401
import llm_steps


def reply(text):
    return {"text": text, "model": "test", "tokens_in": 1, "tokens_out": 1}


class TestJson(unittest.TestCase):
    def test_parse_json_fenced(self):
        self.assertEqual(llm_steps.parse_json('Đây:\n```json\n{"a": 1}\n```'), {"a": 1})

    def test_parse_json_rejects_garbage(self):
        with self.assertRaises(ValueError):
            llm_steps.parse_json("không có json")

    def test_call_json_retries_once(self):
        with mock.patch("llm_steps.call_model", side_effect=[reply("rác"), reply('{"x": 1}')]) as cm:
            self.assertEqual(llm_steps.call_json("s", "u", ["x"]), {"x": 1})
        self.assertEqual(cm.call_count, 2)

    def test_call_json_gives_up_after_retry(self):
        with mock.patch("llm_steps.call_model", side_effect=[reply("rác"), reply("rác")]):
            with self.assertRaises(llm_steps.AIUnavailable):
                llm_steps.call_json("s", "u", ["x"])

    def test_call_json_missing_key_retries(self):
        with mock.patch("llm_steps.call_model", side_effect=[reply('{"y": 1}'), reply('{"x": 2}')]):
            self.assertEqual(llm_steps.call_json("s", "u", ["x"]), {"x": 2})


if __name__ == "__main__":
    unittest.main()


PROFILE_JSON = '''{"budget": 300000, "members": [
 {"name": "An", "vegetarian": true, "allergens": [], "preferences": [], "quotes": ["mình ăn chay"]},
 {"name": "Bình", "vegetarian": false, "allergens": [{"tag": "peanut", "label": "đậu phộng"}], "preferences": [], "quotes": ["dị ứng đậu phộng"]}
], "questions": []}'''


class TestPhase1(unittest.TestCase):
    def test_extract_profile_returns_members(self):
        with mock.patch("llm_steps.call_model", return_value=reply(PROFILE_JSON)):
            profile = llm_steps.extract_profile("Chi\nquỹ 300k\nAn\nmình ăn chay\nBình\ndị ứng đậu phộng")
        self.assertEqual(profile["budget"], 300000)
        self.assertEqual([m["name"] for m in profile["members"]], ["An", "Bình"])
        self.assertIs(profile["members"][0]["vegetarian"], True)
        self.assertEqual(profile["members"][1]["allergens"], {"peanut": "đậu phộng"})
        self.assertEqual(profile["questions"], [])

    def test_extract_profile_drops_unknown_tag(self):
        bad = PROFILE_JSON.replace('"peanut"', '"seafood"')
        with mock.patch("llm_steps.call_model", return_value=reply(bad)):
            profile = llm_steps.extract_profile("chat")
        self.assertEqual(profile["members"][1]["allergens"], {})
        self.assertEqual([q["member"] for q in profile["questions"]], ["Bình"])
        self.assertEqual(profile["questions"][0]["status"], "OPEN")

    def test_apply_answer_keeps_known_ops(self):
        out = '{"changes": [{"op": "ADD_PREFERENCE", "member": "Dũng", "text": "cơm gà"}, {"op": "HACK"}], "reply": "ok"}'
        with mock.patch("llm_steps.call_model", return_value=reply(out)):
            result = llm_steps.apply_answer({"members": []}, {"id": "q1", "text": "?"}, "cho Dũng")
        self.assertEqual([c["op"] for c in result["changes"]], ["ADD_PREFERENCE"])
        self.assertEqual(result["reply"], "ok")
