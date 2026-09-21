#!/usr/bin/env python3
"""test_proposal_check.py —— proposal_check 单测（All-agent 票 18）。

红线：单测不打真实仓——每个用例在 tempfile 里自建最小本体仓
（ontology/schema/model-deps.json + 一个域 yaml）与提案目录，
经 --root 注入，绝不读写本仓 ontology/ 与 docs/proposals/。
真实仓的端到端红绿由出厂集 fixtures/proposal-pool 承载（AC1–6）。

覆盖面（对应票 18 AC 表 + 工具契约）：
  Schema   AC4 两半（必备字段缺失/枚举非法）+ id 格式/YAML 头形态/重复 id/
           schema 红不进后续检查（红因纯净）
  Target   AC2/AC3 + add 未占用放行 + 未登记前缀按不存在判（口径=图索引）
  Conflict AC5 + 同值不矛盾/draft 与已裁决不参战
  Evidence AC6 + 仓根相对/提案目录相对/#锚点容许/绝对路径拒
  Cli      退出码 0/1/2 对齐 + --json 机读面 + 非 PROP 文件跳过
"""

import io
import json
import contextlib
import tempfile
import unittest
from pathlib import Path

from proposal_check import main


def run_main(argv):
    """跑 main 并捕获两流，返回 (退出码, stdout, stderr)；argparse 的 SystemExit(2) 折算为退出码。"""
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
    except SystemExit as exc:  # argparse 缺参等以 SystemExit(2) 退出
        code = exc.code if isinstance(exc.code, int) else 1
    return code, out.getvalue(), err.getvalue()


DEPS = {
    "version": "1.0.0",
    "description": "单测最小依赖白名单",
    "idPrefixes": {"AGG-": "M1", "RULE-": "M3"},
    "refKeys": ["ownerEntity", "targetAggregate"],
}

DOMAIN_YAML = """\
model_type: OBJECT
version: "1.0.0"
domain: demo
aggregates:
  - id: AGG-DEMO-001
    name: 样例对象
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: code, label: 编码, type: String }
rules:
  - id: RULE-DEMO-001
    name: 样例规则
    ruleType: VALIDATION
    ownerEntity: AGG-DEMO-001
"""


class Base(unittest.TestCase):
    """tempfile 最小仓 + 提案目录脚手架。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        schema = self.root / "ontology" / "schema"
        schema.mkdir(parents=True)
        (schema / "model-deps.json").write_text(
            json.dumps(DEPS, ensure_ascii=False), encoding="utf-8")
        (self.root / "ontology" / "demo").mkdir()
        (self.root / "ontology" / "demo" / "m1.yaml").write_text(
            DOMAIN_YAML, encoding="utf-8")
        self.pool = self.root / "proposals"
        self.pool.mkdir()

    def tearDown(self):
        pass

    # -- 提案文件工厂：默认全部合法（add 一个不存在的规则），逐参覆盖 --

    def write_proposal(self, name="PROP-DEMO-001.md", *, pool=None,
                       pid="PROP-DEMO-001", title="t", status="open",
                       kind="拒答", ref="evidence/note.md", model="M3",
                       element="RULE-DEMO-099", change="add",
                       rationale="r", body="正文。", omit=(), extra="",
                       raw=None):
        """omit=省略字段名（构造字段缺失）；raw=整文件原文直写。"""
        lines = ["---"]
        fields = [("id", pid), ("title", title), ("status", status)]
        lines += [f"{k}: {v}" for k, v in fields]
        if "source-signal" not in omit:
            if kind is not None and ref is not None:
                lines += ["source-signal:",
                          f"  kind: {kind}",
                          f"  ref: {ref}"]
            elif kind is not None:
                lines += ["source-signal:", f"  kind: {kind}"]
        lines += ["target:", f"  model: {model}", f"  element: {element}",
                  f"change: {change}", f"rationale: {rationale}"]
        lines = [ln for ln in lines
                 if not any(ln.startswith(f"{f}:") or ln == f for f in omit)]
        lines += ["---", "", body, extra]
        text = raw if raw is not None else "\n".join(lines) + "\n"
        target_dir = pool or self.pool
        p = target_dir / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def write_evidence(self, rel="evidence/note.md", text="证据。"):
        p = self.pool / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def check(self, *extra):
        return run_main([str(self.pool), "--root", str(self.root), *extra])


class SchemaTests(Base):
    """proposal-schema：必备字段与枚举自检（AC4）。"""

    def test_valid_pool_passes(self):
        """正例基线：add 未占用 ID + 证据在档 → exit 0 全过。"""
        self.write_evidence()
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("结论: 全过", out)
        self.assertNotIn("proposal-", out.replace("proposal_check", ""))

    def test_missing_required_field_red(self):
        self.write_proposal(omit=("status",))
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)
        self.assertIn("status", out)
        self.assertIn("缺必备字段", out)

    def test_missing_whole_source_signal_red(self):
        self.write_proposal(omit=("source-signal",))
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)
        self.assertIn("source-signal", out)

    def test_illegal_status_enum_red(self):
        self.write_proposal(status="published")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)
        self.assertIn("published", out)
        self.assertIn("非法", out)

    def test_illegal_kind_enum_red(self):
        self.write_proposal(kind="道听途说")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)
        self.assertIn("道听途说", out)

    def test_illegal_change_enum_red(self):
        self.write_proposal(change="upsert")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)
        self.assertIn("upsert", out)

    def test_bad_id_format_red(self):
        self.write_proposal(pid="PROP-DEMO-1")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)
        self.assertIn("PROP-DEMO-1", out)

    def test_duplicate_id_red(self):
        self.write_evidence()
        self.write_proposal()
        self.write_proposal(name="PROP-DEMO-002.md", title="另一份")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)
        self.assertIn("重复", out)

    def test_no_front_matter_red(self):
        self.write_proposal(raw="没有 YAML 头的纯 markdown。\n")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)

    def test_unclosed_front_matter_red(self):
        self.write_proposal(raw="---\nid: PROP-DEMO-001\n")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)

    def test_broken_yaml_red(self):
        self.write_proposal(raw="---\nid: [PROP-DEMO-001\n---\n正文\n")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)

    def test_schema_red_excludes_later_checks(self):
        """schema 红的文件不进 target/conflict/evidence（红因纯净，不连环报）。"""
        self.write_proposal(omit=("status",))  # 其余字段故意也是坏靶+坏证据
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-schema", out)
        self.assertNotIn("proposal-target", out)
        self.assertNotIn("proposal-evidence", out)
        self.assertNotIn("proposal-conflict", out)


class TargetTests(Base):
    """proposal-target：存在性判定（AC2/AC3），口径照票 04 图索引。"""

    def test_modify_not_exist_red(self):
        self.write_evidence()
        self.write_proposal(change="modify", element="AGG-DEMO-999",
                            model="M1")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-target", out)
        self.assertIn("AGG-DEMO-999", out)
        self.assertIn("不存在", out)

    def test_deprecate_not_exist_red(self):
        self.write_evidence()
        self.write_proposal(change="deprecate", element="AGG-DEMO-999",
                            model="M1")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-target", out)
        self.assertIn("不存在", out)

    def test_add_already_exist_red(self):
        self.write_evidence()
        self.write_proposal(change="add", element="AGG-DEMO-001", model="M1")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-target", out)
        self.assertIn("AGG-DEMO-001", out)
        self.assertIn("已存在", out)

    def test_accepted_add_already_exist_ok(self):
        """票 56 AC1：accepted add 的靶在场=实施完成预期态，不判（A 线 PROP-006 实弹盲区）。"""
        self.write_evidence()
        self.write_proposal(change="add", element="AGG-DEMO-001", model="M1",
                            status="accepted")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)
        self.assertNotIn("proposal-target", out)

    def test_rejected_modify_not_exist_ok(self):
        """票 56：rejected 提案靶在不在都合法（modify+不存在也不判）。"""
        self.write_evidence()
        self.write_proposal(change="modify", element="AGG-DEMO-999", model="M1",
                            status="rejected")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)
        self.assertNotIn("proposal-target", out)

    def test_modify_exist_ok(self):
        self.write_evidence()
        self.write_proposal(change="modify", element="AGG-DEMO-001",
                            model="M1")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)

    def test_definition_key_with_Id_suffix_counts(self):
        """定义键口径：actorId 等 *Id 键同样算定义（M5 先例），存在即可 modify。"""
        (self.root / "ontology" / "demo" / "m5.yaml").write_text(
            "model_type: ACTOR\nversion: \"1.0.0\"\ndomain: demo\n"
            "actors:\n  - actorId: AGG-DEMO-042\n    name: 主体\n",
            encoding="utf-8")
        self.write_evidence()
        self.write_proposal(change="modify", element="AGG-DEMO-042",
                            model="M1")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)

    def test_ref_key_does_not_define_element(self):
        """ref 键（refKeys 登记/Ref 后缀）不产生定义——引用 AGG-DEMO-001 之外的
        悬空 ID 不能被 modify。"""
        dangling = DOMAIN_YAML.replace(
            "ownerEntity: AGG-DEMO-001", "ownerEntity: AGG-DEMO-777")
        (self.root / "ontology" / "demo" / "m1.yaml").write_text(
            dangling, encoding="utf-8")
        self.write_evidence()
        self.write_proposal(change="modify", element="AGG-DEMO-777",
                            model="M1")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-target", out)

    def test_unregistered_prefix_judged_nonexistent(self):
        """前缀即类型标签：未登记前缀的 ID 不入元素集——add 放行（前缀登记属
        schema 演进面），modify 红不存在。"""
        self.write_evidence()
        self.write_proposal(element="FOO-BAR-001", model="M3")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)
        self.write_proposal(name="PROP-DEMO-002.md", pid="PROP-DEMO-002",
                            change="modify", element="FOO-BAR-001",
                            model="M3")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-target", out)


class ConflictTests(Base):
    """proposal-conflict：同靶 open 提案 change 矛盾（AC5）。"""

    def test_conflicting_pair_red(self):
        self.write_evidence()
        self.write_proposal(change="modify", element="AGG-DEMO-001",
                            model="M1")
        self.write_proposal(name="PROP-DEMO-002.md", pid="PROP-DEMO-002",
                            change="deprecate", element="AGG-DEMO-001",
                            model="M1", title="乙")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-conflict", out)
        self.assertIn("AGG-DEMO-001", out)
        self.assertIn("modify", out)
        self.assertIn("deprecate", out)
        self.assertIn("矛盾", out)

    def test_add_vs_modify_also_conflict(self):
        self.write_evidence()
        self.write_proposal(change="add", element="RULE-DEMO-099")
        self.write_proposal(name="PROP-DEMO-002.md", pid="PROP-DEMO-002",
                            change="modify", element="RULE-DEMO-099",
                            title="乙")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-conflict", out)

    def test_same_change_not_conflict(self):
        """同值重复提案不判矛盾（重复提案属人裁决面，闸只报方向矛盾）。"""
        self.write_evidence()
        self.write_proposal(change="modify", element="AGG-DEMO-001",
                            model="M1")
        self.write_proposal(name="PROP-DEMO-002.md", pid="PROP-DEMO-002",
                            change="modify", element="AGG-DEMO-001",
                            model="M1", title="乙")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)

    def test_draft_not_counted(self):
        self.write_evidence()
        self.write_proposal(status="draft", change="modify",
                            element="AGG-DEMO-001", model="M1")
        self.write_proposal(name="PROP-DEMO-002.md", pid="PROP-DEMO-002",
                            change="deprecate", element="AGG-DEMO-001",
                            model="M1", title="乙")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)

    def test_decided_not_counted(self):
        self.write_evidence()
        self.write_proposal(status="accepted", change="modify",
                            element="AGG-DEMO-001", model="M1")
        self.write_proposal(name="PROP-DEMO-002.md", pid="PROP-DEMO-002",
                            change="deprecate", element="AGG-DEMO-001",
                            model="M1", title="乙")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)

    def test_different_targets_not_conflict(self):
        self.write_evidence()
        self.write_proposal(change="modify", element="AGG-DEMO-001",
                            model="M1")
        self.write_proposal(name="PROP-DEMO-002.md", pid="PROP-DEMO-002",
                            change="deprecate", element="RULE-DEMO-001",
                            model="M3", title="乙")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)


class EvidenceTests(Base):
    """proposal-evidence：证据文件存在性（AC6）。"""

    def test_missing_evidence_red(self):
        self.write_proposal(ref="evidence/ghost.md")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-evidence", out)
        self.assertIn("ghost.md", out)
        self.assertIn("不存在", out)

    def test_anchor_tolerated(self):
        self.write_evidence()
        self.write_proposal(ref="evidence/note.md#第二节")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)

    def test_proposal_dir_relative_ok(self):
        self.write_evidence("att/材料.md")
        self.write_proposal(ref="att/材料.md")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)

    def test_absolute_ref_red(self):
        self.write_evidence()
        self.write_proposal(ref="/etc/hosts")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-evidence", out)

    def test_anchor_only_ref_red(self):
        # YAML 里 # 起注释，需引号包裹才能让 ref 真的只剩锚点
        self.write_proposal(ref='"#只有锚点"')
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("proposal-evidence", out)


class CliTests(Base):
    """退出码 0/1/2 对齐 + --json 机读 + 非 PROP 文件跳过。"""

    def test_exit2_when_dir_missing(self):
        code, _, err = run_main([str(self.root / "nope"), "--root",
                                 str(self.root)])
        self.assertEqual(code, 2)
        self.assertIn("用法错误", err)

    def test_exit2_when_dir_is_file(self):
        f = self.root / "afile.md"
        f.write_text("x", encoding="utf-8")
        code, _, err = run_main([str(f), "--root", str(self.root)])
        self.assertEqual(code, 2)
        self.assertIn("用法错误", err)

    def test_exit2_when_no_args(self):
        code, _, err = run_main([])
        self.assertEqual(code, 2)

    def test_exit2_when_ontology_missing(self):
        pool = self.root / "proposals"
        (pool / "PROP-DEMO-001.md").write_text("---\n---\n", encoding="utf-8")
        import shutil
        shutil.rmtree(self.root / "ontology")
        code, _, err = run_main([str(pool), "--root", str(self.root)])
        self.assertEqual(code, 2)
        self.assertIn("配置错误", err)

    def test_exit2_when_model_deps_missing(self):
        pool = self.root / "proposals"
        (pool / "PROP-DEMO-001.md").write_text("---\n---\n", encoding="utf-8")
        (self.root / "ontology" / "schema" / "model-deps.json").unlink()
        code, _, err = run_main([str(pool), "--root", str(self.root)])
        self.assertEqual(code, 2)
        self.assertIn("配置错误", err)

    def test_exit2_when_ontology_yaml_unparseable(self):
        pool = self.root / "proposals"
        (pool / "PROP-DEMO-001.md").write_text("---\n---\n", encoding="utf-8")
        (self.root / "ontology" / "demo" / "m1.yaml").write_text(
            "a: [b\n", encoding="utf-8")
        code, _, err = run_main([str(pool), "--root", str(self.root)])
        self.assertEqual(code, 2)
        self.assertIn("配置错误", err)

    def test_non_prop_files_skipped(self):
        self.write_evidence()
        self.write_proposal()
        (self.pool / "README.md").write_text("对账 README", encoding="utf-8")
        (self.pool / "att.md").write_text("附件", encoding="utf-8")
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("解析提案 1 份", out)
        self.assertIn("跳过非提案 md 文件 3 个", out)  # README + att + evidence/note

    def test_json_report_shape(self):
        self.write_proposal(ref="evidence/ghost.md")
        code, out, _ = self.check("--json")
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["proposals"], 1)
        codes = {v["code"] for v in report["violations"]}
        self.assertEqual(codes, {"proposal-evidence"})
        for v in report["violations"]:
            self.assertIn("file", v)
            self.assertIn("message", v)

    def test_json_pass_shape(self):
        self.write_evidence()
        code, out, _ = self.check("--json")
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["violations"], [])


if __name__ == "__main__":
    unittest.main()
