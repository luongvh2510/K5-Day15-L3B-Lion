import unittest

import _path  # noqa: F401
import app


class TestCli(unittest.TestCase):
    def test_cli_joins_lines_until_blank(self):
        lines = iter(["An", "mình ăn chay", "Bình", "dị ứng đậu phộng", ""])
        self.assertEqual(app.read_message(lines), "An\nmình ăn chay\nBình\ndị ứng đậu phộng")

    def test_cli_end_of_input(self):
        self.assertIsNone(app.read_message(iter([])))

    def test_cli_skips_leading_blank(self):
        self.assertEqual(app.read_message(iter(["", "xin chào", ""])), "xin chào")


if __name__ == "__main__":
    unittest.main()
