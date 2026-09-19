#!/usr/bin/env python3
"""check_citations.py 的单测（票 13：ID 引用清单双向比对检具，审查一 P2）。

覆盖：一致/两类不一致/清单节缺失/token 正则边界（两段形、T-3 样粘连、驼峰段、
中文紧邻）/退出码三态。
"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from contextlib import redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_citations as cc


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = cc.main(argv)
    return rc, out.getvalue(), err.getvalue()


class SplitAnswer(unittest.TestCase):
    def test_split_at_marker(self):
        body, listing = cc.split_answer(
            "正文 `AGG-X-001`。\n## 本回答引用的元素 ID\n- AGG-X-001（载体）\n")
        self.assertEqual(body, "正文 `AGG-X-001`。\n")
        self.assertTrue(listing.startswith("## 本回答引用的元素 ID"))

    def test_missing_marker_puts_all_in_body(self):
        body, listing = cc.split_answer("全文无清单节 `BH-X-001`")
        self.assertIn("BH-X-001", body)
        self.assertEqual(listing, "")


class TokenRegex(unittest.TestCase):
    def test_registered_style_tokens_match(self):
        toks = cc.extract_tokens(
            "`AGG-BOHAI-001` 与 BH-BOHAI-RecordDailyOutput、GLS-X-001、SCR-BOHAI-01")
        self.assertEqual(toks, {"AGG-BOHAI-001", "BH-BOHAI-RecordDailyOutput",
                                "GLS-X-001", "SCR-BOHAI-01"})

    def test_two_segment_forms_do_not_match(self):
        # MENU-01 / T-3 / R5 不是元素 ID 形态
        self.assertEqual(cc.extract_tokens("MENU-01、样本 20260911-T3、R5·§6"), set())

    def test_camel_segment_and_digits(self):
        toks = cc.extract_tokens("BH-X-QueryWell Output? RULE-X-009, QR-X-001x AGG-X-001-")
        # 尾部粘字母（001x）与连字尾（001-）不误收；数字段+驼峰段正常命中
        self.assertEqual(toks, {"BH-X-QueryWell", "RULE-X-009"})

    def test_adjacent_chinese_still_matches(self):
        # 中文紧邻不算 ASCII 边界字符，照常命中（规则RULE-X-001 形态）
        self.assertEqual(cc.extract_tokens("规则RULE-X-001承载"),
                         {"RULE-X-001"})


class Compare(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        p = self.root / name
        p.write_text(text, encoding="utf-8")
        return p

    def test_consistent_answer_is_ok(self):
        p = self.write("a.md",
                       "口径见 `RULE-X-001`，量在 AGG-X-002。\n"
                       "## 本回答引用的元素 ID\n\n"
                       "- RULE-X-001（校验规则）\n"
                       "- AGG-X-002（量的载体）\n"
                       "- AGG-X-002（重复登记不算差）\n")
        ok, report = cc.compare(p)
        self.assertTrue(ok)
        self.assertIn("结论: 一致", report)

    def test_body_token_missing_from_list_is_reported(self):
        p = self.write("b.md",
                       "见 `RULE-X-001`。\n## 本回答引用的元素 ID\n- AGG-X-002（x）\n")
        ok, report = cc.compare(p)
        self.assertFalse(ok)
        self.assertIn("正文有清单无", report)
        self.assertIn("RULE-X-001", report)
        self.assertIn("清单有正文无", report)
        self.assertIn("AGG-X-002", report)

    def test_list_token_missing_from_body_is_reported(self):
        p = self.write("c.md",
                       "见 `AGG-X-002`。\n## 本回答引用的元素 ID\n"
                       "- AGG-X-002（x）\n- QR-X-999（清单注水）\n")
        ok, report = cc.compare(p)
        self.assertFalse(ok)
        self.assertIn("QR-X-999", report)

    def test_no_marker_no_tokens_is_consistent(self):
        p = self.write("d.md", "拒答话术，无任何 ID。")
        ok, report = cc.compare(p)
        self.assertTrue(ok)

    def test_no_marker_with_body_tokens_is_inconsistent(self):
        p = self.write("e.md", "正文引了 `AGG-X-002` 但忘写清单节。")
        ok, report = cc.compare(p)
        self.assertFalse(ok)
        self.assertIn("AGG-X-002", report)


class ExitCodes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_exit_0_consistent(self):
        p = self.root / "ok.md"
        p.write_text("x `AGG-X-001`\n## 本回答引用的元素 ID\n- AGG-X-001（x）\n",
                     encoding="utf-8")
        rc, _, _ = run_main([str(p)])
        self.assertEqual(rc, 0)

    def test_exit_1_inconsistent(self):
        p = self.root / "bad.md"
        p.write_text("x `AGG-X-001`\n## 本回答引用的元素 ID\n- AGG-X-002（x）\n",
                     encoding="utf-8")
        rc, out, _ = run_main([str(p)])
        self.assertEqual(rc, 1)
        self.assertIn("不一致", out)

    def test_exit_2_usage(self):
        self.assertEqual(run_main([])[0], 2)
        self.assertEqual(run_main([str(self.root / "nope.md")])[0], 2)
        self.assertEqual(run_main(["-h"])[0], 2)


if __name__ == "__main__":
    unittest.main()
