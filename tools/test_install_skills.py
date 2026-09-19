#!/usr/bin/env python3
"""install_skills.py 的单测（stdlib unittest，TDD 先行；AC 真源=tickets/12 + tickets/15 AC 表）。

红线：全程 tempfile + 环境变量注入（ALL_AGENT_SKILLS_SRC / ALL_AGENT_SKILLS_HOME /
ALL_AGENT_INSTALL_REGISTRY），绝不读写真实 ~/.agents 与真实 git config；
缺省回落 $HOME / 仓内 tools/ 的解析只有纯计算用例（算路径不落盘）。
合成两个迷你 skill（alpha: SKILL.md+references/guide.md；beta: SKILL.md）走
sync/--check 端到端：票 12 AC1–4（漂移三型）各有着落，另盖幂等/安全删除/单选
范围/JSON 机读面；票 15 三件套——注册表（AC6）、孤儿检测与 --prune（AC3/AC4）、
symlink 拒跑（AC5）、pre-commit 钩子端到端（AC1/AC2，tempfile 内真 git）。
"""

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import install_skills as isk

PROJECT_ROOT = Path(__file__).resolve().parent.parent


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
        self.reg = Path(self.tmp.name) / "repo" / "tools" / "install-registry.json"
        write(self.src / "alpha" / "SKILL.md", ALPHA_SKILL)
        write(self.src / "alpha" / "references" / "guide.md", ALPHA_GUIDE)
        write(self.src / "beta" / "SKILL.md", BETA_SKILL)
        patcher = mock.patch.dict(os.environ, {
            "ALL_AGENT_SKILLS_SRC": str(self.src),
            "ALL_AGENT_SKILLS_HOME": str(self.dst),
            "ALL_AGENT_INSTALL_REGISTRY": str(self.reg),
        })
        patcher.start()
        self.addCleanup(patcher.stop)

    def install_file(self, skill: str, rel: str) -> Path:
        return self.dst / skill / rel

    def snapshot_mtimes(self) -> dict:
        return {str(p.relative_to(self.dst)): p.stat().st_mtime_ns
                for p in sorted(self.dst.rglob("*")) if p.is_file()}

    def registry_skills(self) -> list:
        """读注册表 skills 名单（测试断言用）。"""
        return json.loads(self.reg.read_text(encoding="utf-8"))["skills"]

    def make_orphan(self) -> None:
        """孤儿三要素入位：sync 登记全量 → 仓内删 alpha 正本（安装位残留）。"""
        self.assertEqual(run_main(["sync"])[0], 0)
        shutil.rmtree(self.src / "alpha")


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

    def test_registry_path_env_injectable_default_is_repo_tools(self):
        # 缺省注册表 = <仓根>/tools/install-registry.json（与被治理脚本同域）
        with mock.patch.dict(os.environ):
            os.environ.pop("ALL_AGENT_INSTALL_REGISTRY", None)
            self.assertEqual(isk.registry_path(),
                             Path(isk.__file__).resolve().parent
                             / "install-registry.json")
        self.assertEqual(isk.registry_path(), self.reg.resolve())


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


# ==================== 票 15：注册表 / 孤儿 / prune / symlink / 钩子 ====================


class RegistryMaintenance(Base):
    """票 15 AC6：注册表是 sync 的原子副产物——全量清单入表、新 skill 入表、
    内容不变不重写、拷贝半途失败不留脏表。"""

    def test_sync_writes_full_inventory(self):
        rc, _out, err = run_main(["sync"])
        self.assertEqual(rc, 0, err)
        data = json.loads(self.reg.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], 1)
        self.assertEqual(data["skills"], ["alpha", "beta"])
        # 原子写不留临时文件残骸
        self.assertEqual([p.name for p in self.reg.parent.iterdir()],
                         ["install-registry.json"])

    def test_sync_selected_names_still_writes_full_inventory(self):
        """注册表语义=本仓管理的 skill 全集，与单次 sync 的所选范围无关。"""
        rc, _out, err = run_main(["sync", "beta"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.registry_skills(), ["alpha", "beta"])

    def test_new_skill_enters_registry_on_sync(self):
        run_main(["sync"])
        write(self.src / "gamma" / "SKILL.md", "# gamma\n\n新增 skill。\n")
        rc, _out, err = run_main(["sync"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.registry_skills(), ["alpha", "beta", "gamma"])

    def test_second_sync_leaves_registry_bytes_unchanged(self):
        run_main(["sync"])
        before = self.reg.read_bytes()
        rc, _out, err = run_main(["sync"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.reg.read_bytes(), before, "注册表内容不变时不得重写")

    def test_midway_failure_leaves_registry_intact(self):
        """拷贝半途失败 → 注册表一字不动、无临时文件残骸（半途失败不留脏表）。"""
        run_main(["sync"])
        before = self.reg.read_bytes()
        write(self.src / "gamma" / "SKILL.md", "# gamma\n")
        real_sync_one = isk.sync_one

        def boom(src, dst):
            if src.name == "gamma":
                raise OSError("模拟拷贝中途失败")
            return real_sync_one(src, dst)

        with mock.patch.object(isk, "sync_one", boom):
            rc, _out, err = run_main(["sync"])
        self.assertEqual(rc, 2)
        self.assertIn("配置错误", err)
        self.assertEqual(self.reg.read_bytes(), before)
        self.assertEqual([p.name for p in self.reg.parent.iterdir()],
                         ["install-registry.json"])

    def test_corrupt_registry_is_config_error(self):
        run_main(["sync"])
        self.reg.write_text("{not json", encoding="utf-8")
        rc, _out, err = run_main(["--check"])
        self.assertEqual(rc, 2)
        self.assertIn("配置错误", err)


class OrphanDetection(Base):
    """票 15 AC3：孤儿 = 注册表登记过 + 安装位还在 + 仓内正本已删。
    --check 报 orphan（类型+路径），退出非零；别人的 skill 与未登记残留绝不是孤儿。"""

    def test_check_reports_orphan_with_type_and_path(self):
        self.make_orphan()
        rc, out, _err = run_main(["--check"])
        self.assertEqual(rc, 1)
        self.assertIn("orphan\talpha", out)
        self.assertIn(str(self.dst / "alpha"), out)
        self.assertIn("--prune", out)

    def test_check_json_orphans_carry_path(self):
        self.make_orphan()
        rc, out, _err = run_main(["--check", "--json"])
        self.assertEqual(rc, 1)
        report = json.loads(out)
        self.assertEqual(report["orphans"],
                         [{"skill": "alpha",
                           "path": str(self.dst.resolve() / "alpha")}])

    def test_other_peoples_skills_never_orphans(self):
        """安装位里 29 个非本仓 skill（不在注册表）绝不能被判孤儿。"""
        write(self.dst / "archify" / "SKILL.md", "# archify（用户自装）\n")
        self.make_orphan()
        rc, out, _err = run_main(["--check"])
        self.assertEqual(rc, 1)
        self.assertIn("orphan\talpha", out)
        self.assertNotIn("archify", out)

    def test_never_registered_leftover_is_not_orphan(self):
        """没登记过的残留不判孤儿（三要素缺登记不可）。"""
        shutil.rmtree(self.src / "beta")
        self.assertEqual(run_main(["sync"])[0], 0)      # 注册表只会登记 alpha
        write(self.dst / "beta" / "SKILL.md", BETA_SKILL)  # 手工放个未登记残留
        rc, out, _err = run_main(["--check"])
        self.assertEqual(rc, 0)
        self.assertNotIn("orphan", out)

    def test_sync_retains_orphan_in_registry_until_prune(self):
        """sync 不得把未清场的孤儿洗出注册表（防「删正本+sync」把孤儿遗忘）。"""
        self.make_orphan()
        rc, _out, err = run_main(["sync"])
        self.assertEqual(rc, 0, err)
        self.assertIn("alpha", self.registry_skills())
        self.assertIn("退役候选", err)
        rc, _out, _err = run_main(["--check"])
        self.assertEqual(rc, 1, "孤儿仍在册，--check 必须继续报")


class Prune(Base):
    """票 15 AC4：--prune 清孤儿残留并同步注册表；默认 dry-run 只列清单，
    --yes 才真删（破坏性操作加确认闸）。"""

    def setUp(self):
        super().setUp()
        write(self.dst / "archify" / "SKILL.md", "# archify（用户自装）\n")

    def test_dry_run_lists_but_touches_nothing(self):
        self.make_orphan()
        rc, out, err = run_main(["--prune"])
        self.assertEqual(rc, 0, err)
        self.assertIn("alpha", out)
        self.assertIn(str(self.dst / "alpha"), out)
        self.assertTrue((self.dst / "alpha" / "SKILL.md").is_file(), "dry-run 不得真删")
        self.assertEqual(self.registry_skills(), ["alpha", "beta"], "dry-run 不得改注册表")

    def test_yes_removes_residue_and_syncs_registry(self):
        self.make_orphan()
        rc, out, err = run_main(["--prune", "--yes"])
        self.assertEqual(rc, 0, err)
        self.assertFalse((self.dst / "alpha").exists(), "残留应被清除")
        self.assertTrue((self.dst / "archify" / "SKILL.md").is_file(),
                        "非注册表兄弟目录绝不动")
        self.assertEqual(self.registry_skills(), ["beta"], "注册表应同步除名")
        rc, out, _err = run_main(["--check"])
        self.assertEqual(rc, 0, "--check 归零")

    def test_without_orphans_is_noop(self):
        self.assertEqual(run_main(["sync"])[0], 0)
        rc, out, err = run_main(["--prune", "--yes"])
        self.assertEqual(rc, 0, err)
        self.assertIn("无孤儿", out)

    def test_orphan_symlink_blocks_prune(self):
        self.make_orphan()
        shutil.rmtree(self.dst / "alpha")
        os.symlink(self.src.parent / "elsewhere", self.dst / "alpha")
        rc, _out, err = run_main(["--prune", "--yes"])
        self.assertEqual(rc, 2)
        self.assertIn("符号链接", err)
        self.assertTrue((self.dst / "alpha").is_symlink(), "拒处理时不得误删")

    def test_refuses_install_root_equal_to_src_root(self):
        self.assertEqual(run_main(["sync"])[0], 0)
        with mock.patch.dict(os.environ, {"ALL_AGENT_SKILLS_HOME": str(self.src)}):
            rc, _out, err = run_main(["--prune", "--yes"])
            self.assertEqual(rc, 2)
            self.assertIn("正本根", err)
        self.assertTrue((self.src / "alpha" / "SKILL.md").is_file(), "正本必须完好")

    def test_flag_misuse_is_usage_error(self):
        cases = [
            (["sync", "--prune"], "互斥"),
            (["--prune", "--check"], "互斥"),
            (["--prune", "alpha"], "不接 skill 名"),
            (["sync", "--yes"], "--prune"),
        ]
        for argv, hint in cases:
            rc, _out, err = run_main(argv)
            self.assertEqual(rc, 2, f"{argv} 应判用法错误")
            self.assertIn(hint, err)


class SymlinkGuard(Base):
    """票 15 AC5：正本/安装位任一侧 skill 目录为 symlink → sync/--check/prune
    一律拒处理，退出 2，报 config-error 并列出路径。"""

    def test_install_side_symlink_rejected(self):
        self.assertEqual(run_main(["sync"])[0], 0)
        shutil.rmtree(self.dst / "alpha")
        os.symlink(self.src / "alpha", self.dst / "alpha")
        rc, _out, err = run_main(["--check"])
        self.assertEqual(rc, 2)
        self.assertIn("符号链接", err)
        self.assertIn(str(self.dst / "alpha"), err)
        rc, _out, err = run_main(["sync"])
        self.assertEqual(rc, 2, "sync 同样拒处理")

    def test_src_side_symlink_rejected(self):
        real = Path(self.tmp.name) / "elsewhere" / "real-beta"
        write(real / "SKILL.md", "# beta 真身在外部\n")
        shutil.rmtree(self.src / "beta")
        os.symlink(real, self.src / "beta")
        rc, _out, err = run_main(["sync"])
        self.assertEqual(rc, 2)
        self.assertIn("符号链接", err)
        self.assertIn(str(self.src / "beta"), err)


class HookGate(unittest.TestCase):
    """票 15 AC1/AC2：pre-commit 钩子端到端——tempfile 里真 git init +
    core.hooksPath（仓内局部配置，绝不碰真实 git config / 真实 ~/.agents），
    拷贝本仓真实钩子脚本与 install_skills.py 跑通拦截与放行两条链路。"""

    def setUp(self):
        if not shutil.which("git"):
            self.skipTest("git 不可用")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        repo = Path(self.tmp.name) / "repo"
        self.repo = repo
        (repo / "tools" / "hooks").mkdir(parents=True)
        (repo / "skills").mkdir()
        shutil.copy2(PROJECT_ROOT / "tools" / "install_skills.py",
                     repo / "tools" / "install_skills.py")
        hook_src = PROJECT_ROOT / "tools" / "hooks" / "pre-commit"
        self.assertTrue(hook_src.is_file(), "本仓钩子脚本必须已落盘（票 15 产物）")
        shutil.copy2(hook_src, repo / "tools" / "hooks" / "pre-commit")
        (repo / "tools" / "hooks" / "pre-commit").chmod(0o755)
        write(repo / "skills" / "alpha" / "SKILL.md", ALPHA_SKILL)
        write(repo / "skills" / "beta" / "SKILL.md", BETA_SKILL)
        self.home = Path(self.tmp.name) / "home"
        self.env = {**os.environ,
                    "ALL_AGENT_SKILLS_SRC": str(repo / "skills"),
                    "ALL_AGENT_SKILLS_HOME": str(self.home / ".agents" / "skills"),
                    "ALL_AGENT_INSTALL_REGISTRY":
                        str(repo / "tools" / "install-registry.json")}
        for args in (("init", "-q"), ("config", "user.email", "t@example.com"),
                     ("config", "user.name", "t"),
                     ("config", "core.hooksPath", "tools/hooks")):
            self.git(*args)
        self.assertEqual(self.spawn(sys.executable,
                                    str(repo / "tools" / "install_skills.py"),
                                    "sync")[0], 0, "基线 sync 必须成功")
        self.git("add", "-A")
        r = self.git("commit", "-q", "-m", "init")
        self.assertEqual(r[0], 0, f"基线提交（钩子放行）失败: {r[1]}{r[2]}")
        self.head0 = self.git("rev-parse", "HEAD")[1].strip()

    def git(self, *args):
        r = subprocess.run(["git", "-C", str(self.repo), *args],
                           capture_output=True, text=True, env=self.env)
        return r.returncode, r.stdout, r.stderr

    def spawn(self, *args):
        r = subprocess.run(list(args), capture_output=True, text=True,
                           env=self.env)
        return r.returncode, r.stdout, r.stderr

    def test_hook_blocks_drifted_commit(self):
        """AC1：安装位漂移 + 已配 hooksPath → commit 被拒，stderr 指引 sync。"""
        install_md = self.home / ".agents" / "skills" / "alpha" / "SKILL.md"
        install_md.write_text(install_md.read_text(encoding="utf-8") + "\n漂移行\n",
                              encoding="utf-8")
        rc, out, err = self.git("commit", "--allow-empty", "-m", "drift")
        self.assertNotEqual(rc, 0, "漂移提交必须被钩子拦截")
        combined = out + err
        self.assertIn("install_skills", combined, "拦截输出必须指向 check 报告")
        self.assertIn("sync", combined, "拦截输出必须给 sync 指引")
        self.assertEqual(self.git("rev-parse", "HEAD")[1].strip(), self.head0,
                         "被拦截的提交不得产生新 commit")

    def test_hook_passes_clean_commit(self):
        """AC2：安装位零漂移 → 钩子放行，commit 正常产生。"""
        rc, _out, _err = self.spawn(sys.executable,
                                    str(self.repo / "tools" / "install_skills.py"),
                                    "sync")
        self.assertEqual(rc, 0, "恢复 sync 必须成功")
        r = self.git("commit", "--allow-empty", "-m", "clean")
        self.assertEqual(r[0], 0, f"干净提交应放行: {r[1]}{r[2]}")
        self.assertNotEqual(self.git("rev-parse", "HEAD")[1].strip(), self.head0)


if __name__ == "__main__":
    unittest.main()
