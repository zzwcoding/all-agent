#!/usr/bin/env python3
"""onboard_check.py 的单测（票 77 AC1/AC2/AC3）。

临时夹具面：manifest 缺失/域值不一致/devkit 缺席=硬缺口 exit 1，skillpkg
缺席只警告（豁免域不误伤）；实跑面：bohai/his 硬项全绿、pkb 豁免注记、
域枚举与 meta_probe --list-domains 同源一致。
"""

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import onboard_check as oc

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            rc = oc.main(argv)
        except SystemExit as exc:  # argparse 用法错也按退出码收
            rc = exc.code if isinstance(exc.code, int) else 2
    return rc, out.getvalue(), err.getvalue()


def seed_manifest(root: Path, dname: str, domain_value=None):
    d = root / "ontology" / dname
    d.mkdir(parents=True)
    (d / "manifest.json").write_text(json.dumps({
        "domain": domain_value or dname,
        "profile": "full", "schemaVersion": "1.0.0",
    }), encoding="utf-8")
    return d


class OnboardTmpFixture(unittest.TestCase):
    """AC2：硬缺口当场报，软项只警不拦。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_missing_manifest_is_hard_fail_exit_1(self):
        rc, out, _err = run_main(["ghost", "--root", str(self.root)])
        self.assertEqual(rc, 1)
        self.assertIn("✘ [hard] manifest 在场", out)
        self.assertIn("缺 ontology/ghost/manifest.json", out)

    def test_manifest_domain_mismatch_is_hard_fail(self):
        seed_manifest(self.root, "other", domain_value="elsewhere")
        rep = oc.run(self.root, ["other"])
        kinds = {(i["item"], i["status"]) for i in rep["domains"]["other"]}
        self.assertIn(("manifest 在场", "fail"), kinds)
        self.assertGreaterEqual(rep["hardFails"], 1)

    def test_missing_devkit_hard_and_skillpkg_warn_only(self):
        seed_manifest(self.root, "demo")
        rc, out, _err = run_main(["demo", "--root", str(self.root)])
        self.assertEqual(rc, 1)  # devkit 缺席=硬
        self.assertIn("✘ [hard] devkit 导出", out)
        self.assertIn("⚠ [soft] skillpkg 导出", out)  # 软项不误伤
        self.assertIn("⚠ [soft] 体检留痕", out)

    def test_all_domains_default_enumeration_empty_root(self):
        rc, out, _err = run_main(["--root", str(self.root)])
        self.assertEqual(rc, 0)  # 无域可查不算硬缺口
        self.assertIn("无域可查", out)

    def test_json_flag_machine_readable(self):
        seed_manifest(self.root, "demo")
        rc, out, _err = run_main(["demo", "--root", str(self.root), "--json"])
        self.assertEqual(rc, 1)
        data = json.loads(out)
        self.assertEqual(data["hardFails"], 2)  # devkit 缺席 + 空域 schema 红
        self.assertIn("demo", data["domains"])


class OnboardRealRepo(unittest.TestCase):
    """AC1/AC3：依赖仓内已提交状态（三域 schema 绿、devkit 在场、锚定一致）。"""

    def test_bohai_hard_green(self):
        rep = oc.run(REPO_ROOT, ["bohai"])
        self.assertEqual(rep["hardFails"], 0)
        schema = next(i for i in rep["domains"]["bohai"]
                      if i["item"].startswith("语义闸"))
        self.assertEqual(schema["status"], "pass")

    def test_his_hard_green(self):
        rep = oc.run(REPO_ROOT, ["his"])
        self.assertEqual(rep["hardFails"], 0)

    def test_pkb_skillpkg_absent_warn_not_fail(self):
        rep = oc.run(REPO_ROOT, ["pkb"])
        self.assertEqual(rep["hardFails"], 0)
        kinds = {(i["item"], i["status"]) for i in rep["domains"]["pkb"]}
        self.assertIn(("skillpkg 导出", "warn"), kinds)

    def test_enumeration_same_source_as_meta_probe(self):
        # 期望值动态取自文件系统（不钉死域数——票 79 第四域打红三域字面量）
        expected = sorted(p.parent.name for p in
                          (REPO_ROOT / "ontology").glob("*/manifest.json"))
        self.assertGreaterEqual(len(expected), 4)
        self.assertEqual(oc.list_domains(REPO_ROOT), expected)
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "meta_probe.py"),
             "--list-domains"],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.splitlines(),
                         oc.list_domains(REPO_ROOT))


if __name__ == "__main__":
    unittest.main()
