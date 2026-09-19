#!/usr/bin/env python3
"""guard_corpus_check.py 的单测（票 20：守卫单源化，L3 例集回归检具）。

覆盖六路径（票面 TDD 要求，全部 tempfile 造root）：全过（含 ../ 出 root 引用）/
好例失配（预期 nomatch 却命中）/ 坏例失配（预期 match 却未命中）/ 文件缺失 /
坏正则（退出 2）/ 空 manifest（违规）；外加 manifest 行格式非法与缺参类退出 2。
"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from contextlib import redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import guard_corpus_check as gcc

PATTERN = r"老完成率[^。\n]{0,4}(?:有效|可用)口径"


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = gcc.main(argv)
    return rc, out.getvalue(), err.getvalue()


class GuardCorpusCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "guard-corpus"
        (self.root / "good").mkdir(parents=True)
        (self.root / "bad").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def write_regex(self, pattern=PATTERN):
        self.write("regex.txt", pattern + "\n")

    def write_manifest(self, lines):
        self.write("manifest.txt", "".join(line + "\n" for line in lines))

    # ── 路径一：全过（含 ../ 出 root 引用与 # 注释行） ──
    def test_all_pass_with_out_of_root_ref(self):
        self.write_regex()
        self.write("good/clean.md", "「老完成率」已禁用，请以产量完成率作答。")
        self.write("bad/banned.md", "老完成率是有效口径。")
        outside = Path(self.tmp.name) / "real-answer.md"
        outside.write_text("口径见产量完成率。", encoding="utf-8")
        self.write_manifest([
            "# 好例：必须不命中",
            "nomatch\tgood/clean.md",
            "match\tbad/banned.md",
            "nomatch\t../real-answer.md",
        ])
        rc, out, _ = run_main([str(self.root)])
        self.assertEqual(rc, 0)
        self.assertIn("全过", out)

    # ── 路径二：好例失配（预期 nomatch 却命中 → 违规行） ──
    def test_unexpected_hit_is_violation(self):
        self.write_regex()
        self.write("good/leak.md", "其实老完成率是有效口径。")
        self.write_manifest(["nomatch\tgood/leak.md"])
        rc, out, _ = run_main([str(self.root)])
        self.assertEqual(rc, 1)
        self.assertIn("违规", out)
        self.assertIn("good/leak.md", out)

    # ── 路径三：坏例失配（预期 match 却未命中 → 违规行） ──
    def test_expected_hit_missing_is_violation(self):
        self.write_regex()
        self.write("bad/clean.md", "请以产量完成率作答。")
        self.write_manifest(["match\tbad/clean.md"])
        rc, out, _ = run_main([str(self.root)])
        self.assertEqual(rc, 1)
        self.assertIn("违规", out)
        self.assertIn("bad/clean.md", out)

    # ── 路径四：文件缺失 = 违规行 ──
    def test_missing_file_is_violation(self):
        self.write_regex()
        self.write_manifest(["match\tbad/gone.md"])
        rc, out, _ = run_main([str(self.root)])
        self.assertEqual(rc, 1)
        self.assertIn("文件缺失", out)
        self.assertIn("bad/gone.md", out)

    # ── 路径五：坏正则 → 退出 2 ──
    def test_bad_regex_exits_2(self):
        self.write_regex("(?P<未闭合")
        self.write_manifest(["nomatch\tgood/x.md"])
        rc, out, err = run_main([str(self.root)])
        self.assertEqual(rc, 2)
        self.assertIn("正则", err + out)

    # ── 路径六：空 manifest = 违规（空套件不许亮绿灯） ──
    def test_empty_manifest_is_violation(self):
        self.write_regex()
        self.write_manifest(["# 只有注释，无条目"])
        rc, out, _ = run_main([str(self.root)])
        self.assertEqual(rc, 1)
        self.assertIn("空", out)

    # ── 附加：manifest 行格式非法 → 退出 2 ──
    def test_malformed_manifest_line_exits_2(self):
        self.write_regex()
        self.write_manifest(["matchme\tgood/x.md"])
        self.assertEqual(run_main([str(self.root)])[0], 2)
        self.write_manifest(["match good/x.md"])  # 空格分隔、无 TAB
        self.assertEqual(run_main([str(self.root)])[0], 2)

    # ── 附加：缺参 / root 不存在 / regex.txt 缺失 / manifest.txt 缺失 → 退出 2 ──
    def test_usage_errors_exit_2(self):
        self.assertEqual(run_main([])[0], 2)
        self.assertEqual(run_main([str(self.root / "nope")])[0], 2)
        self.write_manifest(["nomatch\tgood/x.md"])
        self.assertEqual(run_main([str(self.root)])[0], 2)  # 缺 regex.txt
        self.write_regex()
        (self.root / "manifest.txt").unlink()
        self.assertEqual(run_main([str(self.root)])[0], 2)  # 缺 manifest.txt

    # ── 附加：regex.txt 多行（违背一行契约）→ 退出 2 ──
    def test_multi_line_regex_exits_2(self):
        self.write("regex.txt", PATTERN + "\n另一行\n")
        self.write_manifest(["nomatch\tgood/x.md"])
        rc, out, err = run_main([str(self.root)])
        self.assertEqual(rc, 2)
        self.assertIn("一行", err + out)


if __name__ == "__main__":
    unittest.main()
