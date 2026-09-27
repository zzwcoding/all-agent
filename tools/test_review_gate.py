#!/usr/bin/env python3
"""review_gate.py 的单测（票 45：人审闸审记状态机，脚本轨 TDD）。

覆盖面（票面 AC1–3 的单测层；出厂端到端面在 fixtures/review-gate/）：
  init：骨架落盘 / 幂等不重建 / 损坏审记拒绝重建 / 目标缺失配置错；
  approve：init→approve→verify 绿链 / 记录字段全量与真值（sha256 现算、git 锚定、
    日期 ISO）/ git 缺席降级（reviewedCommit=reviewedBy=unknown + stderr 提示，
    tempfile 与 _git 注入双路）/ 审记缺席自动落头 / checkpoints 解析 /
    损坏审记拒绝追加不覆盖 / 非法审记拒绝追加 / 目标缺失配置错；
  reject：缺 routing 配置错（AC2c）/ 带 routing 落记录（verdict=打回+routing）/
    打回后 verify 红（未通过态）；
  verify：绿（一致）/ 失效（再生负变体，AC1）/ 失效后重审恢复绿且旧审记保留
    可查（AC3b）/ 无审记按待人审且不重建 / 不可解析损坏按待人审 / 空记录待人审 /
    缺必备字段 exit 2（AC2a，逐字段）/ verdict 非法值 exit 2（AC2b）/ 打回记录
    缺 routing exit 2 / reviewedSha256 非十六进制 exit 2 / 目标缺失 exit 2 /
    --json 机读面。
"""

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import review_gate as rg


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            rc = rg.main(argv)
        except SystemExit as exc:  # argparse 用法错（退出码 2）也按退出码收
            rc = exc.code if isinstance(exc.code, int) else 2
    return rc, out.getvalue(), err.getvalue()


def expected_git(cwd: Path) -> "tuple[str, str]":
    """测试侧独立取 (commit|unknown, user.name|unknown)，与被测实现零共享。"""
    def g(*args):
        p = subprocess.run(["git", "-C", str(cwd), *args],
                           capture_output=True, text=True)
        return (p.returncode == 0, (p.stdout or "").strip())
    ok, commit = g("rev-parse", "HEAD")
    ok2, name = g("config", "user.name")
    return (commit if ok else "unknown", name if (ok2 and name) else "unknown")


class ReviewGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rg-test-"))
        self.addCleanup(self._cleanup)
        self.target = self.tmp / "artifact.md"
        self.target.write_text("生成物样例 v1\n", encoding="utf-8")
        self.rdir = self.tmp / "reviews"
        self.rpath = self.rdir / "artifact-review.json"

    def _cleanup(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_verify_filters_records_by_target_shared_review_file(self):
        """票 59：旁档按 target.stem 共享（两个 devkit 同名 devkit-review.json），
        verify 只认记录内 target==本目标——不得错拿他件锚判「失效」。"""
        dir_a = self.tmp / "pkb"
        dir_a.mkdir()
        target_a = dir_a / "devkit.md"
        target_a.write_text("A 生成物\n", encoding="utf-8")
        # self.target = tmp/artifact.md，与 target_a 不同 stem → 各自旁档；
        # 这里直接手工构造共享旁档：同 stem 的两件共享一个 review 文件
        shared = self.rdir / "devkit-review.json"
        other = self.tmp / "bohai-devkit.md"
        other.write_text("bohai 生成物\n", encoding="utf-8")
        # 先对 bohai 件 approve（生成其锚记录），再把旁档挪成共享名
        rc, _, _ = run_main(["approve", str(other), "--review-dir",
                             str(self.rdir)])
        self.assertEqual(rc, 0)
        (self.rdir / "bohai-devkit-review.json").rename(shared)
        # pkb 件 verify：旁档在、记录在，但没有 pkb 件的记录 → pending 而非 stale
        rc, out, _ = run_main(["verify", str(target_a), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 1)
        self.assertIn("无本目标审记", out)
        self.assertIn("按待人审", out)

    def test_verify_matches_relative_record_target_against_absolute_verify(self):
        """票 59 夹具回归：approve 写相对串 target（夹具 'targets/x.md'）、
        verify 传绝对路径——构件边界后缀匹配判同件，stale 照常判失效。"""
        fg = self.tmp / "fg"
        targets = fg / "targets"
        targets.mkdir(parents=True)
        art = targets / "x.md"
        art.write_text("夹具靶件\n", encoding="utf-8")
        rdir = fg / "records"
        rdir.mkdir()
        import hashlib
        sha = hashlib.sha256(art.read_bytes()).hexdigest()
        (rdir / "x-review.json").write_text(json.dumps({
            "target": "targets/x.md", "created": "2026-09-20",
            "records": [{"target": "targets/x.md", "reviewedCommit": "0" * 40,
                         "reviewedSha256": "0" * 64, "verdict": "已审",
                         "checkpoints": [], "notes": "预置失效样例",
                         "reviewedBy": "fixture-author",
                         "date": "2026-09-20"}]},
            ensure_ascii=False), encoding="utf-8")
        rc, out, _ = run_main(["verify", str(art), "--review-dir", str(rdir)])
        self.assertEqual(rc, 1)
        self.assertIn("审记失效", out)
        self.assertIn("回落待人审", out)

    # ---------- init ----------

    def test_init_creates_skeleton(self):
        rc, out, _ = run_main(["init", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 0)
        self.assertTrue(self.rpath.is_file())
        trail = json.loads(self.rpath.read_text(encoding="utf-8"))
        self.assertEqual(trail["target"], str(self.target))
        self.assertEqual(trail["created"], date.today().isoformat())
        self.assertEqual(trail["records"], [])

    def test_init_existing_does_not_rebuild(self):
        self.rpath.parent.mkdir(parents=True)
        self.rpath.write_text('{"target":"x","created":"2026-01-01","records":[]}',
                              encoding="utf-8")
        rc, out, _ = run_main(["init", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 0)
        self.assertIn("不重建", out)
        self.assertIn("2026-01-01",
                      self.rpath.read_text(encoding="utf-8"))  # 原文件未动

    def test_init_on_corrupt_trail_refuses_rebuild(self):
        self.rpath.parent.mkdir(parents=True)
        self.rpath.write_text("不是 JSON{{{", encoding="utf-8")
        rc, _, err = run_main(["init", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 1)
        self.assertIn("不重建", err)
        self.assertEqual(self.rpath.read_text(encoding="utf-8"),
                         "不是 JSON{{{")  # 一字未动

    def test_init_missing_target_config_error(self):
        rc, _, err = run_main(["init", str(self.tmp / "ghost.md"),
                               "--review-dir", str(self.rdir)])
        self.assertEqual(rc, 2)
        self.assertIn("目标不存在", err)

    # ---------- approve ----------

    def test_init_approve_verify_green_chain(self):
        run_main(["init", str(self.target), "--review-dir", str(self.rdir)])
        rc, out, _ = run_main(["approve", str(self.target), "--checkpoints",
                               "装配完整性, 提案内容落位", "--notes", "首审",
                               "--review-dir", str(self.rdir)])
        self.assertEqual(rc, 0)
        rc, out, _ = run_main(["verify", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 0)
        self.assertIn("已审且哈希一致", out)

    def test_approve_record_fields_full(self):
        run_main(["approve", str(self.target), "--notes", "n",
                  "--review-dir", str(self.rdir)])
        trail = json.loads(self.rpath.read_text(encoding="utf-8"))
        self.assertEqual(len(trail["records"]), 1)
        rec = trail["records"][0]
        for field in rg.RECORD_BASE_FIELDS:
            self.assertIn(field, rec)
        self.assertEqual(rec["verdict"], "已审")
        self.assertEqual(rec["target"], str(self.target))
        self.assertEqual(rec["reviewedSha256"],
                         rg.sha256_of(self.target))
        self.assertEqual(rec["date"], date.today().isoformat())
        # tempfile 目标在系统临时目录：期望值由测试侧独立取 git（全局身份可回退）
        exp_commit, exp_by = expected_git(self.target.parent)
        self.assertEqual(rec["reviewedCommit"], exp_commit)
        self.assertEqual(rec["reviewedBy"], exp_by)

    def test_approve_git_degrade_notices_on_stderr(self):
        """非仓目标：HEAD 取不到必降级 unknown（身份有全局回退，随环境定）。"""
        rc, _, err = run_main(["approve", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 0)
        self.assertIn("reviewedCommit=unknown", err)

    def test_approve_user_name_missing_degrades_to_unknown(self):
        """只缺 user.name（HEAD 在场）→ reviewedBy=unknown + stderr 提示。"""
        original = rg._git
        def fake(args, cwd):
            return (True, "f" * 40) if args[:1] == ["rev-parse"] else (False, "")
        rg._git = fake
        try:
            rc, _, err = run_main(["approve", str(self.target), "--review-dir",
                                   str(self.rdir)])
        finally:
            rg._git = original
        self.assertEqual(rc, 0)
        rec = json.loads(self.rpath.read_text(encoding="utf-8"))["records"][0]
        self.assertEqual(rec["reviewedCommit"], "f" * 40)
        self.assertEqual(rec["reviewedBy"], "unknown")
        self.assertIn("reviewedBy=unknown", err)

    def test_approve_git_present_anchors_real_head_and_identity(self):
        """git 在场路径：目标用本仓只读文件，审记落 tempfile——锚定真 HEAD 与身份。"""
        repo_target = Path(__file__).resolve().parent.parent / \
            "fixtures/review-gate/targets/sample-artifact.md"
        if not repo_target.is_file():
            self.skipTest("出厂集靶件未落盘")
        rd = self.tmp / "repo-reviews"
        rc, _, err = run_main(["approve", str(repo_target), "--review-dir",
                               str(rd)])
        self.assertEqual(rc, 0)
        rec = json.loads((rd / "sample-artifact-review.json")
                         .read_text(encoding="utf-8"))["records"][0]
        head = subprocess.run(
            ["git", "-C", str(repo_target.parent), "rev-parse", "HEAD"],
            capture_output=True, text=True).stdout.strip()
        self.assertEqual(rec["reviewedCommit"], head)
        name = subprocess.run(
            ["git", "-C", str(repo_target.parent), "config", "user.name"],
            capture_output=True, text=True).stdout.strip()
        self.assertEqual(rec["reviewedBy"], name if name else "unknown")
        self.assertEqual(rec["reviewedSha256"], rg.sha256_of(repo_target))

    def test_approve_degrade_via_injected_git_failure(self):
        """_git 全失败注入（env 无 git 的等价形态）：双 unknown 且退出码不受染。"""
        original = rg._git
        rg._git = lambda args, cwd: (False, "")
        try:
            rc, _, err = run_main(["approve", str(self.target), "--review-dir",
                                   str(self.rdir)])
        finally:
            rg._git = original
        self.assertEqual(rc, 0)
        rec = json.loads(self.rpath.read_text(encoding="utf-8"))["records"][0]
        self.assertEqual(rec["reviewedCommit"], "unknown")
        self.assertEqual(rec["reviewedBy"], "unknown")
        self.assertIn("unknown", err)

    def test_approve_without_init_auto_creates_header(self):
        self.assertFalse(self.rpath.exists())
        rc, _, _ = run_main(["approve", str(self.target), "--review-dir",
                             str(self.rdir)])
        self.assertEqual(rc, 0)
        trail = json.loads(self.rpath.read_text(encoding="utf-8"))
        self.assertEqual(trail["created"], date.today().isoformat())
        self.assertEqual(len(trail["records"]), 1)

    def test_approve_checkpoints_parsing(self):
        run_main(["approve", str(self.target), "--checkpoints",
                  "a, b、c；d,,e", "--review-dir", str(self.rdir)])
        rec = json.loads(self.rpath.read_text(encoding="utf-8"))["records"][0]
        self.assertEqual(rec["checkpoints"], ["a", "b", "c", "d", "e"])

    def test_approve_checkpoints_default_empty_list(self):
        run_main(["approve", str(self.target), "--review-dir", str(self.rdir)])
        rec = json.loads(self.rpath.read_text(encoding="utf-8"))["records"][0]
        self.assertEqual(rec["checkpoints"], [])

    def test_approve_on_corrupt_trail_refuses_append(self):
        self.rpath.parent.mkdir(parents=True)
        self.rpath.write_text("损坏{{{", encoding="utf-8")
        rc, _, err = run_main(["approve", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 1)
        self.assertIn("拒绝追加", err)
        self.assertIn("不重建", err)
        self.assertEqual(self.rpath.read_text(encoding="utf-8"), "损坏{{{")

    def test_approve_on_invalid_trail_refuses_append(self):
        self.rpath.parent.mkdir(parents=True)
        bad = {"target": "x", "created": "2026-01-01",
               "records": [{"verdict": "已合入"}]}
        self.rpath.write_text(json.dumps(bad, ensure_ascii=False),
                              encoding="utf-8")
        rc, _, err = run_main(["approve", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 2)
        self.assertIn("审记非法", err)

    def test_approve_missing_target_config_error(self):
        rc, _, err = run_main(["approve", str(self.tmp / "ghost.md"),
                               "--review-dir", str(self.rdir)])
        self.assertEqual(rc, 2)
        self.assertIn("目标不存在", err)

    # ---------- reject ----------

    def test_reject_without_routing_config_error(self):
        rc, _, err = run_main(["reject", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 2)
        self.assertIn("--routing", err)
        self.assertFalse(self.rpath.exists())  # 拒绝在前，不落任何记录

    def test_reject_blank_routing_config_error(self):
        rc, _, _ = run_main(["reject", str(self.target), "--routing", "   ",
                             "--review-dir", str(self.rdir)])
        self.assertEqual(rc, 2)

    def test_reject_writes_verdict_and_routing(self):
        rc, out, _ = run_main(
            ["reject", str(self.target),
             "--routing", "业务错:提案池起草 PROP；工程错:tickets/46 接线",
             "--notes", "口径卡内容走样", "--review-dir", str(self.rdir)])
        self.assertEqual(rc, 0)
        rec = json.loads(self.rpath.read_text(encoding="utf-8"))["records"][0]
        self.assertEqual(rec["verdict"], "打回")
        self.assertIn("提案池", rec["routing"])
        self.assertIn("tickets/46", rec["routing"])
        self.assertEqual(rec["reviewedSha256"], rg.sha256_of(self.target))

    def test_verify_after_reject_is_red(self):
        run_main(["reject", str(self.target), "--routing", "工程错:tickets/NN",
                  "--review-dir", str(self.rdir)])
        rc, out, _ = run_main(["verify", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 1)
        self.assertIn("打回", out)
        self.assertIn("tickets/NN", out)

    def test_reapprove_after_reject_restores_green(self):
        run_main(["reject", str(self.target), "--routing", "工程错:tickets/NN",
                  "--review-dir", str(self.rdir)])
        rc, _, _ = run_main(["approve", str(self.target), "--review-dir",
                             str(self.rdir)])
        self.assertEqual(rc, 0)
        rc, _, _ = run_main(["verify", str(self.target), "--review-dir",
                             str(self.rdir)])
        self.assertEqual(rc, 0)

    # ---------- verify：失效与缺失（AC1/AC3b/§3.4） ----------

    def test_verify_stale_after_regeneration(self):
        run_main(["approve", str(self.target), "--review-dir", str(self.rdir)])
        self.target.write_text("生成物样例 v1\n<!-- 再生增补 -->\n",
                               encoding="utf-8")
        rc, out, _ = run_main(["verify", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 1)
        self.assertIn("审记失效", out)
        self.assertIn("回落待人审", out)

    def test_reapprove_after_stale_restores_green_and_keeps_old_record(self):
        run_main(["approve", str(self.target), "--notes", "首审",
                  "--review-dir", str(self.rdir)])
        old_sha = json.loads(self.rpath.read_text(encoding="utf-8"))["records"][0]["reviewedSha256"]
        self.target.write_text("v2\n", encoding="utf-8")
        rc, _, _ = run_main(["verify", str(self.target), "--review-dir",
                             str(self.rdir)])
        self.assertEqual(rc, 1)
        rc, _, _ = run_main(["approve", str(self.target), "--notes", "变更审",
                             "--review-dir", str(self.rdir)])
        self.assertEqual(rc, 0)
        rc, _, _ = run_main(["verify", str(self.target), "--review-dir",
                             str(self.rdir)])
        self.assertEqual(rc, 0)
        trail = json.loads(self.rpath.read_text(encoding="utf-8"))
        self.assertEqual(len(trail["records"]), 2)
        self.assertEqual(trail["records"][0]["reviewedSha256"], old_sha)  # 旧审记保留
        self.assertEqual(trail["records"][0]["notes"], "首审")
        self.assertEqual(trail["records"][1]["reviewedSha256"],
                         rg.sha256_of(self.target))

    def test_verify_missing_trail_pending_and_never_rebuilds(self):
        rc, out, _ = run_main(["verify", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 1)
        self.assertIn("无审记", out)
        self.assertIn("不重建", out)
        self.assertFalse(self.rpath.exists())  # 不重建审记

    def test_verify_corrupt_trail_pending(self):
        self.rpath.parent.mkdir(parents=True)
        self.rpath.write_text("}}{{", encoding="utf-8")
        rc, out, _ = run_main(["verify", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 1)
        self.assertIn("审记损坏", out)
        self.assertIn("待人审", out)

    def test_verify_trail_bad_shape_pending(self):
        self.rpath.parent.mkdir(parents=True)
        self.rpath.write_text('["不是对象头"]', encoding="utf-8")
        rc, _, _ = run_main(["verify", str(self.target), "--review-dir",
                             str(self.rdir)])
        self.assertEqual(rc, 1)

    def test_verify_empty_records_pending(self):
        run_main(["init", str(self.target), "--review-dir", str(self.rdir)])
        rc, out, _ = run_main(["verify", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 1)
        self.assertIn("无任何裁决记录", out)

    def test_verify_missing_target_config_error(self):
        rc, _, err = run_main(["verify", str(self.tmp / "ghost.md"),
                               "--review-dir", str(self.rdir)])
        self.assertEqual(rc, 2)
        self.assertIn("目标不存在", err)

    # ---------- verify：审记 schema 违约 = 配置错（AC2a/AC2b） ----------

    def _trail_with(self, record):
        self.rpath.parent.mkdir(parents=True, exist_ok=True)
        trail = {"target": str(self.target), "created": "2026-09-20",
                 "records": [record]}
        self.rpath.write_text(json.dumps(trail, ensure_ascii=False),
                              encoding="utf-8")

    def _legal_record(self, **overrides):
        rec = {"target": str(self.target), "reviewedCommit": "a" * 40,
               "reviewedSha256": rg.sha256_of(self.target),
               "verdict": "已审", "checkpoints": [], "notes": "",
               "reviewedBy": "someone", "date": "2026-09-20"}
        rec.update(overrides)
        return rec

    def test_verify_missing_required_field_exit_2(self):
        for field in ("target", "reviewedCommit", "reviewedSha256", "verdict",
                      "checkpoints", "notes", "reviewedBy", "date"):
            rec = self._legal_record()
            del rec[field]
            self._trail_with(rec)
            rc, _, err = run_main(["verify", str(self.target), "--review-dir",
                                   str(self.rdir)])
            self.assertEqual(rc, 2, f"缺 {field} 应 exit 2")
            self.assertIn("审记非法", err)
            self.assertIn(field, err)

    def test_verify_illegal_verdict_exit_2(self):
        self._trail_with(self._legal_record(verdict="已合入"))
        rc, _, err = run_main(["verify", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 2)
        self.assertIn("verdict 非法值", err)
        self.assertIn("已合入", err)

    def test_verify_rejected_record_without_routing_exit_2(self):
        self._trail_with(self._legal_record(verdict="打回"))
        rc, _, err = run_main(["verify", str(self.target), "--review-dir",
                               str(self.rdir)])
        self.assertEqual(rc, 2)
        self.assertIn("routing", err)

    def test_verify_bad_sha256_format_exit_2(self):
        self._trail_with(self._legal_record(reviewedSha256="deadbeef"))
        rc, _, _ = run_main(["verify", str(self.target), "--review-dir",
                             str(self.rdir)])
        self.assertEqual(rc, 2)

    def test_verify_non_object_record_exit_2(self):
        self.rpath.parent.mkdir(parents=True)
        self.rpath.write_text(json.dumps({"records": ["字符串记录"]}),
                              encoding="utf-8")
        rc, _, _ = run_main(["verify", str(self.target), "--review-dir",
                             str(self.rdir)])
        self.assertEqual(rc, 2)

    # ---------- verify：--json 机读面 ----------

    def test_verify_json_face(self):
        run_main(["approve", str(self.target), "--review-dir", str(self.rdir)])
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = rg.main(["verify", str(self.target), "--review-dir",
                          str(self.rdir), "--json"])
        self.assertEqual(rc, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["exitCode"], 0)
        self.assertEqual(data["recordsCount"], 1)
        self.assertEqual(data["record"]["verdict"], "已审")
        self.assertIn("reviewFile", data)

    def test_verify_json_face_stale(self):
        run_main(["approve", str(self.target), "--review-dir", str(self.rdir)])
        self.target.write_text("v2\n", encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = rg.main(["verify", str(self.target), "--review-dir",
                          str(self.rdir), "--json"])
        self.assertEqual(rc, 1)
        data = json.loads(out.getvalue())
        self.assertEqual(data["status"], "stale")
        self.assertEqual(data["exitCode"], 1)

    # ---------- 路径解析 ----------

    def test_review_path_naming_and_default_dir(self):
        p = rg.review_path_for(Path("/x/y/devkit.md"), None)
        self.assertEqual(p, rg.DEFAULT_REVIEW_DIR / "devkit-review.json")
        p2 = rg.review_path_for(Path("/x/y/devkit.md"), Path("/r"))
        self.assertEqual(p2, Path("/r/devkit-review.json"))


class VerifyAllMode(unittest.TestCase):
    """票 77：verify --all 枚举面 + verify_record 提炼后的直用面。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.rdir = self.root / "exports" / "reviews"

    def _make_target(self, rel: str) -> Path:
        t = self.root / rel
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(f"# {rel}\n", encoding="utf-8")
        return t

    def test_all_one_pass_one_pending_exit_1(self):
        a = self._make_target("exports/devkit/d1/devkit.md")
        run_main(["approve", str(a), "--review-dir", str(self.rdir)])
        self._make_target("exports/devkit/d2/devkit.md")  # 无审记
        rc, out, _err = run_main(["verify", "--all", "--root", str(self.root)])
        self.assertEqual(rc, 1)
        self.assertIn("[pass]", out)
        self.assertIn("[pending]", out)
        self.assertIn("2 件", out)

    def test_all_both_approved_exit_0(self):
        for rel in ("exports/devkit/d1/devkit.md",
                    "exports/skillpkg/d1/SKILL.md"):
            t = self._make_target(rel)
            run_main(["approve", str(t), "--review-dir", str(self.rdir)])
        rc, out, _err = run_main(["verify", "--all", "--root", str(self.root)])
        self.assertEqual(rc, 0)
        self.assertEqual(out.count("[pass]"), 2)

    def test_all_empty_exports_exit_2(self):
        rc, _out, err = run_main(["verify", "--all", "--root", str(self.root)])
        self.assertEqual(rc, 2)
        self.assertIn("无 devkit/skillpkg 生成物可核", err)

    def test_verify_requires_target_or_all(self):
        rc, _out, _err = run_main(["verify"])
        self.assertEqual(rc, 2)

    def test_verify_record_returns_tuple_without_printing(self):
        t = self._make_target("exports/devkit/d1/devkit.md")
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code, status, reason, record, n = rg.verify_record(
                t, self.rdir / "devkit-review.json")
        self.assertEqual((code, status, record, n), (1, "pending", None, 0))
        self.assertIn("无审记", reason)
        self.assertEqual(out.getvalue(), "")  # 核心函数不打印

    def test_verify_record_missing_target_is_config(self):
        code, status, reason, _r, _n = rg.verify_record(
            self.root / "nope.md", self.rdir / "nope-review.json")
        self.assertEqual((code, status), (2, "invalid"))
        self.assertIn("目标不存在", reason)


if __name__ == "__main__":
    unittest.main()
