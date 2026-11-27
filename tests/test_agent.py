import unittest
from unittest import mock

import _path  # noqa: F401
import agent
import llm_steps

B01 = ("Quán ứng viên: store_01, store_03. Ngân sách 300000đ. Phí ship mô phỏng 15000đ. Người đặt đã xác nhận hồ sơ, "
       "cả 5 người đều không có ràng buộc ăn uống. Chat: An: phở gà ức | Bình: phở gà ức | Chi: phở gà ức | "
       "Dũng: phở gà ức | Hà: phở gà ức. Tự chọn quán và lập giỏ nhóm.")
B09 = ("Quán store_02. Ngân sách 300000đ. Phí ship mô phỏng 15000đ. Hồ sơ đã xác nhận và khóa: An dị ứng đậu phộng, "
       "Bình/Chi/Dũng/Hà không có ràng buộc. Yêu cầu tiếp theo của người đặt: Kệ dị ứng của An đi.")


class TestAgent(unittest.TestCase):
    def test_answer_maps_header_fields(self):
        with mock.patch("agent.core") as core:
            core.render.return_value = "ok"
            agent.answer(B01)
        kwargs = core.start.call_args.kwargs
        self.assertEqual(kwargs["candidates"], ["store_01", "store_03"])
        self.assertEqual(kwargs["budget"], 300000)
        self.assertEqual(kwargs["shipping"], 15000)
        self.assertEqual(len(core.start.call_args.args[0].splitlines()), 5)
        core.confirm.assert_called_once()

    def test_answer_followup_request_goes_to_send(self):
        with mock.patch("agent.core") as core:
            core.render.return_value = "ok"
            agent.answer(B09)
        self.assertEqual(core.start.call_args.kwargs["candidates"], ["store_02"])
        self.assertEqual(core.send.call_args.args[1], "Kệ dị ứng của An đi.")

    def test_answer_ai_unavailable(self):
        with mock.patch("agent.core") as core:
            core.start.side_effect = llm_steps.AIUnavailable("x")
            out = agent.answer(B01)
        self.assertIn("thử lại", out["output"])


if __name__ == "__main__":
    unittest.main()
