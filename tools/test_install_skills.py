#!/usr/bin/env python3
"""install_skills.py 的单测（stdlib unittest，TDD 先行；AC 真源=tickets/12 AC 表）。

红线：全程 tempfile + 环境变量注入（ALL_AGENT_SKILLS_SRC / ALL_AGENT_SKILLS_HOME），
绝不读写真实 ~/.agents；缺省回落 $HOME 的解析只有一条纯计算用例（算路径不落盘）。
合成两个迷你 skill（alpha: SKILL.md+references/guide.md；beta: SKILL.md）走
sync/--check 端到端，AC1–4 各有着落，另盖幂等/安全删除/单选范围/JSON 机读面。
"""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import install_skills as isk


def run_main(argv):
    """跑 main，捕获 stdout+stderr，返回 (退出码, stdout, stderr)。"""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = isk.main(argv)
    return rc, out.getvalue(), err.getvalue()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


ALPHA_SKILL = """---
name: alpha
description: 测试 skill 甲
---

# alpha 工序
四步：一查、二建、三核、四交。
"""
ALPHA_GUIDE = "# 细则甲\n\n下沉到 references 的内容。\n"
BETA_SKILL = "# beta\n\n最简 skill，单文件。\n"


class Base(unittest.TestCase):
    """tmp 仓 + tmp HOME，环境变量注入两个根；落盘只发生在 tmp 内。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = Path(self.tmp.name) / "repo" / "skills"
        self.dst = Path(self.tmp.name) / "home" / ".agents" / "skills"
        write(self.src / "alpha" / "SKILL.md", ALPHA_SKILL)
        write(self.src / "alpha" / "references" / "guide.md", ALPHA_GUIDE)
        write(self.src / "beta" / "SKILL.md", BETA_SKILL)
        patcher = mock.patch.dict(os.environ, {
            "ALL_AGENT_SKILLS_SRC": str(self.src),
            "ALL_AGENT_SKILLS_HOME": str(self.dst),
        })
        patcher.start()
        self.addCleanup(patcher.stop)

    def install_file(self, skill: str, rel: str) -> Path:
        return self.dst / skill / rel

    def snapshot_mtimes(self) -> dict:
        return {str(p.relative_to(self.dst)): p.stat().st_mtime_ns
                for p in sorted(self.dst.rglob("*")) if p.is_file()}


class Ac1CleanSync(Base):
    """AC1：干净 tmp HOME，sync 后逐文件 diff 与正本零差异，退出 0。"""

    def test_sync_into_clean_home_zero_diff_exit0(self):
        self.assertFalse(self.dst.exists(), "前置：安装位还没建")
        rc, out, err = run_main(["sync"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(sorted(p.name for p in self.dst.iterdir()),
                         ["alpha", "beta"])
        # 逐文件字节级对照（文件集合 + 内容）
        for skill in ("alpha", "beta"):
            src_files = isk.list_files(self.src / skill)
            dst_files = isk.list_files(self.dst / skill)
            self.assertEqual(set(src_files), set(dst_files))
            for rel, spath in src_files.items():
                self.assertEqual(spath.read_bytes(),
                                 (self.dst / skill / rel).read_bytes(),
                                 f"{skill}/{rel} 内容不一致")
        # sync 自报复检零漂移；随后 --check 也零漂移
        self.assertIn("零漂移", out)
        rc, out, _ = run_main(["--check"])
        self.assertEqual(rc, 0)

    def test_sync_creates_missing_install_root(self):
        rc, _out, err = run_main(["sync", "beta"])
        self.assertEqual(rc, 0, err)
        self.assertTrue(self.install_file("beta", "SKILL.md").is_file())


class Ac2DriftDetection(Base):
    """AC2：安装位文件被篡改/删除，--check 非零退出并报差异文件路径。"""

    def test_tamper_and_delete_reported_with_paths(self):
        self.assertEqual(run_main(["sync"])[0], 0)
        write(self.install_file("alpha", "SKILL.md"), "# 被篡改\n")   # modified
        self.install_file("beta", "SKILL.md").unlink()               # missing
        rc, out, _err = run_main(["--check"])
        self.assertEqual(rc, 1)
        self.assertIn("modified\talpha/SKILL.md", out)
        self.assertIn("missing\tbeta/SKILL.md", out)
        # 机读行后随人读汇总（含分型计数）
        self.assertIn("missing 1 / modified 1 / extra 0", out)

    def test_single_skill_selection_scopes_the_check(self):
        """单选 alpha 时 beta 的漂移不入报告也不影响退出码（范围由参数定）。"""
        self.assertEqual(run_main(["sync"])[0], 0)
        write(self.install_file("beta", "SKILL.md"), "# beta 被改\n")
        rc, out, _err = run_main(["--check", "alpha"])
        self.assertEqual(rc, 0)
        self.assertNotIn("beta", out)


class Ac3ExtraCleared(Base):
    """AC3：安装位多出正本没有的文件，sync 清除并恢复零差异。"""

    def test_extra_file_removed_and_zero_diff_restored(self):
        self.assertEqual(run_main(["sync"])[0], 0)
        write(self.install_file("alpha", "references/stray.tmp"), "多余")
        rc, out, _err = run_main(["--check"])
        self.assertEqual(rc, 1)
        self.assertIn("extra\talpha/references/stray.tmp", out)
        rc, out, err = run_main(["sync"])
        self.assertEqual(rc, 0, err)
        self.assertFalse(self.install_file("alpha", "references/stray.tmp").exists(),
                         "多余文件应被先清后拷清除")
        rc, out, _err = run_main(["--check"])
        self.assertEqual(rc, 0)


class Ac4ZeroDrift(Base):
    """AC4：零漂移时 --check 退出 0 并输出一致清单。"""

    def test_check_zero_drift_exit0_with_consistent_list(self):
        self.assertEqual(run_main(["sync"])[0], 0)
        rc, out, _err = run_main(["--check"])
        self.assertEqual(rc, 0)
        self.assertIn("零漂移", out)
        self.assertIn("alpha", out)
        self.assertIn("beta", out)
        self.assertIn("一致清单", out)


class Idempotency(Base):
    """sync 连跑两次，第二次必须是 no-op（全跳过、文件 mtime 不变）。"""

    def test_second_sync_is_noop(self):
        self.assertEqual(run_main(["sync"])[0], 0)
        before = self.snapshot_mtimes()
        rc, out, err = run_main(["sync"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.snapshot_mtimes(), before,
                         "第二次 sync 重写了文件，破坏 no-op 幂等")
        self.assertIn("skip\talpha", out)
        self.assertIn("skip\tbeta", out)


class DeletionSafety(Base):
    """删除语义安全：只清 <安装位>/<skill名>/ 本身，兄弟目录（用户其他 skill）绝不动。"""

    def test_sibling_skill_survives_sync(self):
        sibling = self.dst / "archify" / "SKILL.md"
        write(sibling, "# archify（非本仓 skill，用户自装）\n")
        self.assertEqual(run_main(["sync"])[0], 0)
        self.assertTrue(sibling.is_file())
        self.assertEqual(sibling.read_text(encoding="utf-8"),
                         "# archify（非本仓 skill，用户自装）\n")

    def test_path_escape_names_rejected(self):
        for bad in ("../evil", "a/b", "..", "."):
            rc, _out, err = run_main(["sync", bad])
            self.assertEqual(rc, 2, f"非法名 {bad!r} 应判用法错误")
            self.assertIn("非法", err)
        self.assertFalse((self.src.parent / "evil").exists(), "不得逃逸出正本根")
        self.assertFalse((self.dst.parent / "evil").exists(), "不得逃逸出安装位根")

    def test_sync_refuses_install_root_equal_to_src_root(self):
        """安装位根=正本根时拒绝跑 sync（防先清后拷自删正本）。"""
        with mock.patch.dict(os.environ, {"ALL_AGENT_SKILLS_HOME": str(self.src)}):
            rc, _out, err = run_main(["sync"])
            self.assertEqual(rc, 2)
            self.assertIn("正本根", err)
        self.assertTrue((self.src / "alpha" / "SKILL.md").is_file(), "正本必须完好")


class CliUsage(Base):
    """用法面：互斥/缺命令/未知名 = 退出码 2；路径解析可注入、缺省回落 HOME。"""

    def test_sync_and_check_mutually_exclusive(self):
        rc, _out, err = run_main(["sync", "--check"])
        self.assertEqual(rc, 2)
        self.assertIn("互斥", err)

    def test_no_command_is_usage_error(self):
        rc, _out, err = run_main([])
        self.assertEqual(rc, 2)
        self.assertIn("用法错误", err)

    def test_unknown_skill_name_lists_available(self):
        rc, _out, err = run_main(["sync", "nope"])
        self.assertEqual(rc, 2)
        self.assertIn("未知 skill", err)
        self.assertIn("alpha", err)
        self.assertIn("beta", err)

    def test_roots_are_env_injectable_and_default_falls_back_to_home(self):
        # 缺省回落：unset 两个专用变量后，安装位根 = $HOME/.agents/skills（只算不写）
        with mock.patch.dict(os.environ):
            os.environ.pop("ALL_AGENT_SKILLS_SRC", None)
            os.environ.pop("ALL_AGENT_SKILLS_HOME", None)
            os.environ["HOME"] = str(Path(self.tmp.name) / "home")
            self.assertEqual(isk.install_skills_root(),
                             (Path(self.tmp.name) / "home" / ".agents"
                              / "skills").resolve())
            self.assertEqual(isk.repo_skills_root(),
                             (Path(isk.__file__).resolve().parent.parent
                              / "skills").resolve())
        self.assertFalse(self.dst.exists(), "解析用例不得落盘")


class MachineReadable(Base):
    """--json 机读面（给未来 pre-commit 钩子/CI 消费）。"""

    def test_check_json_reports_typed_diffs(self):
        self.assertEqual(run_main(["sync"])[0], 0)
        write(self.install_file("alpha", "SKILL.md"), "# 被篡改\n")
        write(self.install_file("beta", "extra.tmp"), "多余")
        rc, out, _err = run_main(["--check", "--json"])
        self.assertEqual(rc, 1)
        report = json.loads(out)
        self.assertEqual(report["mode"], "check")
        self.assertEqual(
            sorted((d["skill"], d["path"], d["type"]) for d in report["diffs"]),
            [("alpha", "SKILL.md", "modified"), ("beta", "extra.tmp", "extra")])
        self.assertEqual(report["consistent"], [])

    def test_check_json_zero_drift(self):
        self.assertEqual(run_main(["sync"])[0], 0)
        rc, out, _err = run_main(["--check", "alpha", "--json"])
        self.assertEqual(rc, 0)
        report = json.loads(out)
        self.assertEqual(report["diffs"], [])
        self.assertEqual(report["consistent"], ["alpha"])

    def test_sync_json_reports_actions(self):
        rc, out, _err = run_main(["sync", "--json"])
        self.assertEqual(rc, 0)
        report = json.loads(out)
        self.assertEqual(report["mode"], "sync")
        self.assertEqual([a["skill"] for a in report["actions"]], ["alpha", "beta"])
        self.assertTrue(all(a["action"] == "rewrite" for a in report["actions"]))
        self.assertEqual(report["post_diffs"], [])


if __name__ == "__main__":
    unittest.main()
