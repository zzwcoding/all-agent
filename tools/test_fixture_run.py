#!/usr/bin/env python3
"""fixture_run.py 的单测（stdlib unittest，TDD）。"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fixture_run


def quiet_main(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = fixture_run.main(argv)
    return rc


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class FixtureRunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fx_root = Path(self.tmp.name) / "fixtures"

    def tearDown(self):
        self.tmp.cleanup()

    def make_fixture(self, name, assertions):
        fx = self.fx_root / name
        fx.mkdir(parents=True)
        write(fx / "assertions.json", json.dumps({"skill": name, "assertions": assertions}))
        return fx

    def test_all_assertion_types_pass(self):
        fx = self.make_fixture("demo", [
            {"type": "file-exists", "path": "out.md"},
            {"type": "file-contains", "path": "out.md", "contains": ["标题", "Status: done"]},
            {"type": "file-matches-regex", "path": "out.md", "pattern": "^Status: \\w+$"},
            {"type": "file-equals-golden", "path": "out.md", "golden": "golden/out.md"},
        ])
        write(fx / "out.md", "# 标题\nStatus: done\n")
        write(fx / "golden" / "out.md", "# 标题\nStatus: done\n")
        report = fixture_run.run(self.fx_root)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(len(report["fixtures"][0]["results"]), 4)

    def test_file_contains_accepts_single_string(self):
        fx = self.make_fixture("demo", [
            {"type": "file-contains", "path": "out.md", "contains": "标题"},
        ])
        write(fx / "out.md", "# 标题\n")
        self.assertEqual(fixture_run.run(self.fx_root)["status"], "pass")

    def test_each_failure_type(self):
        fx = self.make_fixture("demo", [
            {"type": "file-exists", "path": "missing.md"},
            {"type": "file-contains", "path": "out.md", "contains": ["没有的内容"]},
            {"type": "file-matches-regex", "path": "out.md", "pattern": "zzz"},
            {"type": "file-equals-golden", "path": "out.md", "golden": "golden/out.md"},
        ])
        write(fx / "out.md", "actual\n")
        write(fx / "golden" / "out.md", "golden-different\n")
        report = fixture_run.run(self.fx_root)
        self.assertEqual(report["status"], "fail")
        self.assertEqual([r["ok"] for r in report["fixtures"][0]["results"]],
                         [False, False, False, False])

    def test_empty_assertions_is_fail_not_green(self):
        self.make_fixture("demo", [])
        report = fixture_run.run(self.fx_root)
        self.assertEqual(report["status"], "fail")
        self.assertIn("空", report["fixtures"][0]["error"])

    def test_malformed_assertions_json_is_fail(self):
        fx = self.fx_root / "demo"
        fx.mkdir(parents=True)
        write(fx / "assertions.json", "{not json")
        self.assertEqual(fixture_run.run(self.fx_root)["status"], "fail")

    def test_unknown_assertion_type_is_fail(self):
        fx = self.make_fixture("demo", [{"type": "vibe-check", "path": "out.md"}])
        write(fx / "out.md", "x")
        self.assertEqual(fixture_run.run(self.fx_root)["status"], "fail")

    def test_missing_assertions_file_is_fail(self):
        # 本仓实例化：纯空目录=pending 不红；放了输入没断言=红（见 PendingPlaceholderTest）
        (self.fx_root / "demo").mkdir(parents=True)
        (self.fx_root / "demo" / "input.md").write_text("x", encoding="utf-8")
        self.assertEqual(fixture_run.run(self.fx_root)["status"], "fail")

    def test_no_fixtures_warns_but_exit_zero(self):
        report = fixture_run.run(self.fx_root)  # 目录不存在
        self.assertEqual(report["status"], "no-fixtures")
        self.assertIn("warning", report)
        rc = quiet_main(["--fixtures-dir", str(self.fx_root), "--json"])
        self.assertEqual(rc, 0)

    def test_no_fixtures_with_require_is_red(self):
        report = fixture_run.run(self.fx_root, require_fixtures=True)
        self.assertEqual(report["status"], "fail")
        rc = quiet_main(["--fixtures-dir", str(self.fx_root),
                               "--require-fixtures", "--json"])
        self.assertEqual(rc, 1)

    def test_empty_fixtures_dir_is_no_fixtures(self):
        self.fx_root.mkdir(parents=True)
        self.assertEqual(fixture_run.run(self.fx_root)["status"], "no-fixtures")

    def test_main_exit_codes_and_json(self):
        fx = self.make_fixture("demo", [{"type": "file-exists", "path": "out.md"}])
        write(fx / "out.md", "ok")
        self.assertEqual(
            quiet_main(["--fixtures-dir", str(self.fx_root), "--json"]), 0)
        (fx / "out.md").unlink()
        self.assertEqual(
            quiet_main(["--fixtures-dir", str(self.fx_root), "--json"]), 1)


class CmdAssertionTest(unittest.TestCase):
    """本仓实例化新增：cmd-succeeds / cmd-fails（票 03）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fx_root = Path(self.tmp.name) / "fixtures"
        self.fx = self.fx_root / "demo"
        self.fx.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def py(self, code):
        return [sys.executable, "-c", code]

    def test_cmd_succeeds_with_output_needle(self):
        write(self.fx / "assertions.json", json.dumps({"assertions": [
            {"type": "cmd-succeeds", "cmd": f"{sys.executable} -c \"print('语义闸: 全过')\"",
             "outputContains": ["全过"]},
        ]}))
        self.assertEqual(fixture_run.run(self.fx_root)["status"], "pass")

    def test_cmd_fails_requires_nonzero_and_needle(self):
        write(self.fx / "assertions.json", json.dumps({"assertions": [
            {"type": "cmd-fails",
             "cmd": f"{sys.executable} -c \"import sys; print('L1 坏了'); sys.exit(1)\"",
             "outputContains": ["L1"]},
        ]}))
        self.assertEqual(fixture_run.run(self.fx_root)["status"], "pass")

    def test_cmd_fails_zero_exit_is_red(self):
        write(self.fx / "assertions.json", json.dumps({"assertions": [
            {"type": "cmd-fails", "cmd": f"{sys.executable} -c \"print('ok')\""},
        ]}))
        report = fixture_run.run(self.fx_root)
        self.assertEqual(report["status"], "fail")

    def test_missing_needle_is_red_with_output_tail(self):
        write(self.fx / "assertions.json", json.dumps({"assertions": [
            {"type": "cmd-succeeds", "cmd": f"{sys.executable} -c \"print('hello')\"",
             "outputContains": ["全过"]},
        ]}))
        report = fixture_run.run(self.fx_root)
        self.assertEqual(report["status"], "fail")
        self.assertIn("输出末尾", report["fixtures"][0]["results"][0]["detail"])

    def test_fixture_dir_placeholder_and_cwd(self):
        # {fixture_dir} 替换 + cwd=仓根（fixtures/ 上级）：读相对路径文件证明基准
        write(self.fx / "assertions.json", json.dumps({"assertions": [
            {"type": "cmd-succeeds",
             "cmd": f"{sys.executable} -c \"import pathlib; print(pathlib.Path('marker.txt').exists())\"",
             "outputContains": ["True"]},
        ]}))
        (Path(self.tmp.name) / "marker.txt").write_text("x", encoding="utf-8")
        self.assertEqual(fixture_run.run(self.fx_root)["status"], "pass")

    def test_missing_cmd_field_is_red(self):
        write(self.fx / "assertions.json", json.dumps({"assertions": [
            {"type": "cmd-succeeds"},
        ]}))
        self.assertEqual(fixture_run.run(self.fx_root)["status"], "fail")


class PendingPlaceholderTest(unittest.TestCase):
    """本仓实例化新增：空目录=占位 pending 不红；有输入无断言=红。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fx_root = Path(self.tmp.name) / "fixtures"

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_dir_is_pending_not_fail(self):
        (self.fx_root / "later").mkdir(parents=True)
        report = fixture_run.run(self.fx_root)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["fixtures"][0]["status"], "pending")

    def test_input_without_assertions_still_fails(self):
        (self.fx_root / "later").mkdir(parents=True)
        (self.fx_root / "later" / "input.md").write_text("x", encoding="utf-8")
        self.assertEqual(fixture_run.run(self.fx_root)["status"], "fail")


if __name__ == "__main__":
    unittest.main()
