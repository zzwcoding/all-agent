#!/usr/bin/env python3
"""report_numbers.py 的单测（票 77 AC5）。

临时夹具面：单测计数（discover 数用例不执行）/域行（模型文件数与豁免数）/
审记状态（approve 后 pass）/git 缺席降级「未知」/--out 落 md+json 双件；
实跑面：真仓计数非零、三域、exports 面齐全。
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_numbers as rn

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            rc = rn.main(argv)
        except SystemExit as exc:
            rc = exc.code if isinstance(exc.code, int) else 2
    return rc, out.getvalue(), err.getvalue()


def seed_fixture(root: Path, module: str = "test_dummy") -> Path:
    """module 名须逐测试唯一——unittest discover 对同名模块二次发现会撞车。"""
    tools = root / "tools"
    tools.mkdir(parents=True)
    (tools / f"{module}.py").write_text(
        "import unittest\n\n\nclass TD(unittest.TestCase):\n"
        "    def test_ok(self):\n        self.assertTrue(True)\n",
        encoding="utf-8")
    dom = root / "ontology" / "demo"
    dom.mkdir(parents=True)
    (dom / "manifest.json").write_text(json.dumps({
        "domain": "demo", "profile": "full", "schemaVersion": "1.0.0",
        "omittedModels": [{"model": "M7", "reason": "单测"}],
    }), encoding="utf-8")
    (dom / "m1-object-model.yaml").write_text("model_type: M1\n",
                                              encoding="utf-8")
    target = root / "exports" / "devkit" / "demo" / "devkit.md"
    target.parent.mkdir(parents=True)
    target.write_text("# devkit demo\n", encoding="utf-8")
    rpath = root / "exports" / "reviews" / "devkit-review.json"
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = __import__("review_gate").cmd_approve(target, rpath, [], "票 77 测试")
    assert rc == 0, err.getvalue()
    return target


class ReportNumbersTmp(unittest.TestCase):
    """AC5：机取计数正确、降级路径、落盘双件。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_counts_review_status_and_git_degrade(self):
        seed_fixture(self.root)
        rep = rn.collect(self.root)
        self.assertEqual(rep["unitTests"], 1)  # discover 计数不执行
        self.assertEqual(rep["gitHead"], "未知")  # 非 git 目录降级
        self.assertEqual(rep["domains"],
                         [{"domain": "demo", "profile": "full",
                           "modelFiles": 1, "omitted": 1}])
        self.assertEqual(rep["exports"],
                         [{"target": "exports/devkit/demo/devkit.md",
                           "review": "pass"}])
        md = rn.render_md(rep)
        self.assertIn("| demo | full | 1 | 1 |", md)
        self.assertIn("exports/devkit/demo/devkit.md", md)
        self.assertIn("| 生成物 | 审记 |", md)

    def test_out_writes_md_and_json_pair(self):
        seed_fixture(self.root, module="test_dummy_out")
        out_path = self.root / "docs" / "meta" / "指标快照-测试.md"
        rc, out, _err = run_main(
            ["--out", str(out_path), "--root", str(self.root)])
        self.assertEqual(rc, 0)
        self.assertTrue(out_path.is_file())
        json_path = out_path.with_suffix(".json")
        self.assertTrue(json_path.is_file())
        data = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(data["unitTests"], 1)
        self.assertIn("已落盘", out)

    def test_empty_root_counts_zero(self):
        rep = rn.collect(self.root)
        self.assertEqual(rep["unitTests"], 0)
        self.assertEqual(rep["domains"], [])
        self.assertEqual(rep["exports"], [])
        self.assertEqual(rep["checkupNotes"], 0)


class ReportNumbersRealRepo(unittest.TestCase):
    """实跑面：真仓计数非零、域面与 exports 面动态对齐文件系统
    （不钉死域数——票 79 第四域入仓打红三域字面量，动态化根治）。"""

    def test_real_repo_snapshot_shape(self):
        rep = rn.collect(REPO_ROOT)
        self.assertGreater(rep["unitTests"], 50)
        self.assertNotEqual(rep["gitHead"], "未知")
        expected_domains = sorted(p.parent.name for p in
                                  (REPO_ROOT / "ontology").glob("*/manifest.json"))
        self.assertEqual([r["domain"] for r in rep["domains"]],
                         expected_domains)
        expected_exports = sorted(
            str(t.relative_to(REPO_ROOT))
            for pat in rn.review_gate.VERIFY_ALL_GLOBS
            for t in REPO_ROOT.glob(pat))
        self.assertEqual([r["target"] for r in rep["exports"]],
                         expected_exports)
        self.assertGreater(rep["checkupNotes"], 0)


if __name__ == "__main__":
    unittest.main()
