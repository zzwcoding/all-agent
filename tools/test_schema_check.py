#!/usr/bin/env python3
"""schema_check.py 的单测（stdlib unittest + PyYAML，TDD 先行）。

合成两模型（M1/M2）迷你 schema 走端到端，AC1–7 各一条（AC 对应 specs/schema_check.md 断言表）；
票 10 增 GLS 套件（GlossaryModel）；票 11 增 L2 一致性对套件（ConsistencyPairs，
CONS-AC1–3 对应 tickets/11-一致性对核验.md AC 表，基座扩到 M5/M6/M7）；
票 13 增必填闸套件（RequiredFields：L1 required-field 元素级闸）与 AC6 反向套件
（MissingModelFile：L4 missing-model-file + omittedModels 豁免）。
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import schema_check as sc


def quiet_main(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = sc.main(argv)
    return rc


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


REGISTRY = {
    "version": 1,
    "models": {
        "M1": {
            "name": "对象模型", "yamlFile": "m1-object-model.yaml",
            "modelType": "OBJECT", "camp": "business-core",
            "consumers": ["runtime", "build"],
            "profiles": ["full", "mini"],
            "dependsOn": [], "lockedFields": {},
        },
        "M2": {
            "name": "行为模型", "yamlFile": "m2-behavior-model.yaml",
            "modelType": "BEHAVIOR", "camp": "business-core",
            "consumers": ["runtime", "build"],
            "profiles": ["full"],
            "dependsOn": ["M1"], "lockedFields": {},
        },
        "GLS": {
            "name": "术语模型", "yamlFile": "glossary-model.yaml",
            "modelType": "GLOSSARY", "camp": "business-core",
            "consumers": ["runtime", "build"],
            "profiles": ["full"],
            "dependsOn": ["M1"], "lockedFields": {},
        },
    },
}

DEPS = {
    "version": 1,
    "idPrefixes": {"AGG-": "M1", "BH-": "M2", "GLS-": "GLS"},
    "refKeys": ["ownerEntity", "relatedObjectRefs"],
    "edges": [
        {"from": "M2", "field": "ownerEntity", "to": ["M1"]},
        {"from": "GLS", "field": "relatedObjectRefs", "to": ["M1"]},
    ],
}

M1 = """model_type: OBJECT
version: "1.0.0"
domain: demo
aggregates:
  - id: AGG-DEMO-001
    name: 井
    alias: Well
    aggregateType: AGGREGATE_ROOT
    attributes: []
"""

M2 = """model_type: BEHAVIOR
version: "1.0.0"
domain: demo
behaviors:
  - id: BH-DEMO-Record
    name: 录入
    ownerEntity: AGG-DEMO-001
    behaviorType: COMMAND
    triggerType: USER_ACTION
    preconditions: []
    postconditions: []
    appliedRules: []
    requiredPermissions: []
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "onto"
        write(self.root / "schema" / "model-registry.json", json.dumps(REGISTRY))
        write(self.root / "schema" / "model-deps.json", json.dumps(DEPS))
        # 票 13 起 manifest 预置 omittedModels（覆盖注册表全模型）：本基座各测试
        # 只加部分模型文件是常态，AC6 反向闸（missing-model-file）不该改变老测试
        # 语义——反向闸的正负变体由 MissingModelFile 专类用自管 manifest 覆盖。
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "full", "schemaVersion": "1.0.0",
             "omittedModels": [
                 {"model": "M1", "reason": "单测基座：模型文件按需加装"},
                 {"model": "M2", "reason": "单测基座：模型文件按需加装"},
                 {"model": "GLS", "reason": "单测基座：模型文件按需加装"},
             ]}))

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, name, text, domain="demo"):
        write(self.root / domain / name, text)

    def run_check(self, target=None):
        return sc.run(target or self.root)

    def kinds(self, report=None):
        r = report or self.run_check()
        return [v["kind"] for v in r["violations"]]


class Ac1ValidOntologyPasses(Base):
    def test_valid_domain_exits_zero(self):
        self.add("m1-object-model.yaml", M1)
        self.add("m2-behavior-model.yaml", M2)
        report = self.run_check()
        self.assertEqual(report["status"], "pass", report["violations"])
        self.assertEqual(quiet_main(["--json", str(self.root)]), 0)


class Ac2YamlSyntaxError(Base):
    def test_syntax_error_reports_l1_with_filename(self):
        self.add("m2-behavior-model.yaml",
                 "model_type: BEHAVIOR\nbehaviors:\n\t- id: x\n")
        report = self.run_check()
        self.assertEqual(report["status"], "fail")
        kinds = self.kinds(report)
        self.assertIn("yaml-syntax", kinds)
        v = report["violations"][0]
        self.assertEqual(v["level"], "L1")
        self.assertIn("m2-behavior-model.yaml", v["file"])
        self.assertEqual(quiet_main(["--json", str(self.root)]), 1)


class Ac3MissingCommonField(Base):
    def test_missing_version_named(self):
        self.add("m1-object-model.yaml",
                 "\n".join(l for l in M1.splitlines() if not l.startswith("version")))
        report = self.run_check()
        self.assertIn("missing-common-field", self.kinds(report))
        msgs = " ".join(v["message"] for v in report["violations"])
        self.assertIn("version", msgs)

    def test_missing_model_type_named(self):
        self.add("m1-object-model.yaml",
                 "\n".join(l for l in M1.splitlines() if not l.startswith("model_type")))
        msgs = " ".join(v["message"] for v in self.run_check()["violations"])
        self.assertIn("model_type", msgs)


class Ac4DanglingRef(Base):
    def test_dangling_ref_reports_l2_with_location(self):
        self.add("m1-object-model.yaml", M1)
        self.add("m2-behavior-model.yaml",
                 M2.replace("AGG-DEMO-001", "AGG-DEMO-999"))
        report = self.run_check()
        self.assertIn("dangling-ref", self.kinds(report))
        v = next(v for v in report["violations"] if v["kind"] == "dangling-ref")
        self.assertEqual(v["level"], "L2")
        self.assertIn("AGG-DEMO-999", v["message"])
        self.assertIn("m2-behavior-model.yaml", v["file"])
        self.assertGreater(v["line"], 0)


class Ac5DependencyWhitelist(Base):
    def test_cross_model_ref_out_of_whitelist(self):
        # M2 依赖白名单只有 M1：构造 M2 ref 指向本迷你仓不存在的第三类 ID
        # （用锁定外的未登记 ref 字段指向 M1 之外的模型——这里以 M1 引 BH- 反向例证）
        self.add("m1-object-model.yaml", M1 + "\nextraRef: BH-DEMO-Record\n")
        self.add("m2-behavior-model.yaml", M2)
        report = self.run_check()
        self.assertIn("dep-whitelist", self.kinds(report))
        v = next(v for v in report["violations"] if v["kind"] == "dep-whitelist")
        self.assertEqual(v["level"], "L2")
        self.assertIn("M1", v["message"])
        self.assertIn("M2", v["message"])

    def test_registry_deps_conflict_with_edges_is_l1(self):
        deps = json.loads(json.dumps(DEPS))
        deps["edges"].append({"from": "M1", "field": "whatever", "to": ["M2"]})
        write(self.root / "schema" / "model-deps.json", json.dumps(deps))
        self.add("m1-object-model.yaml", M1)
        self.assertIn("deps-registry-conflict", self.kinds())


class Ac6ProfileNotEnabled(Base):
    def test_disabled_model_file_is_l4(self):
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "mini", "schemaVersion": "1.0.0"}))
        self.add("m1-object-model.yaml", M1)
        self.add("m2-behavior-model.yaml", M2)  # M2 不在 mini profile
        report = self.run_check()
        self.assertIn("profile-disabled", self.kinds(report))
        v = next(v for v in report["violations"] if v["kind"] == "profile-disabled")
        self.assertEqual(v["level"], "L4")
        self.assertIn("M2", v["message"])

    def test_unknown_profile_is_violation(self):
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "nope", "schemaVersion": "1.0.0"}))
        self.assertIn("unknown-profile", self.kinds())


class Ac7FieldRedefinition(Base):
    def test_locked_field_is_l4(self):
        registry = json.loads(json.dumps(REGISTRY))
        registry["models"]["M2"]["lockedFields"] = {
            "producedEvents": "v6 事件异步引用；v9 由 syncTriggers 承载"}
        write(self.root / "schema" / "model-registry.json", json.dumps(registry))
        self.add("m1-object-model.yaml", M1)
        self.add("m2-behavior-model.yaml",
                 M2 + "    producedEvents: [EV-DEMO-001]\n")
        report = self.run_check()
        self.assertIn("field-redefinition", self.kinds(report))
        v = next(v for v in report["violations"] if v["kind"] == "field-redefinition")
        self.assertEqual(v["level"], "L4")
        self.assertIn("producedEvents", v["message"])
        self.assertIn("换义", v["message"])


class Misc(Base):
    def test_domain_without_manifest_is_violation(self):
        write(self.root / "wild" / "m1-object-model.yaml", M1)
        self.assertIn("missing-manifest", self.kinds())

    def test_missing_schema_files_is_config_error(self):
        (self.root / "schema" / "model-deps.json").unlink()
        with self.assertRaises(ValueError):
            self.run_check()

    def test_line_numbers_are_one_based_and_accurate(self):
        self.add("m1-object-model.yaml", M1)
        self.add("m2-behavior-model.yaml",
                 M2.replace("AGG-DEMO-001", "AGG-DEMO-999"))
        report = self.run_check()
        v = next(v for v in report["violations"] if v["kind"] == "dangling-ref")
        # ownerEntity 行是 M2 文本的第 7 行
        self.assertEqual(v["line"], 7)


GLOSSARY = """model_type: GLOSSARY
version: "1.0.0"
domain: demo
terms:
  - id: GLS-DEMO-001
    term: 生产井
    aliases: [油井]
    definition: 正在采油的井。
    relatedObjectRefs: [AGG-DEMO-001]
"""


class GlossaryModel(Base):
    """票 10：GLS 术语模型进 schema（元模型演进）——GLS-AC1…AC4 的单测面。"""

    def test_valid_glossary_passes(self):
        # GLS-AC1：合法 glossary + relatedObjectRefs 指向真实 M1 对象 → 全过
        self.add("m1-object-model.yaml", M1)
        self.add("glossary-model.yaml", GLOSSARY)
        report = self.run_check()
        self.assertEqual(report["status"], "pass", report["violations"])

    def test_gls_in_disabled_profile_is_l4(self):
        # GLS-AC2：GLS 不入 mini 组合（对应真仓 v9-core），文件出现 → L4 红
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "mini", "schemaVersion": "1.0.0"}))
        self.add("glossary-model.yaml", GLOSSARY)
        report = self.run_check()
        v = next(v for v in report["violations"] if v["kind"] == "profile-disabled")
        self.assertEqual(v["level"], "L4")
        self.assertIn("GLS", v["message"])

    def test_gls_dangling_object_ref_is_l2(self):
        # GLS-AC3：relatedObjectRefs 指向不存在的 AGG- → L2 悬空引用红
        self.add("m1-object-model.yaml", M1)
        self.add("glossary-model.yaml", GLOSSARY.replace("AGG-DEMO-001", "AGG-DEMO-999"))
        report = self.run_check()
        v = next(v for v in report["violations"] if v["kind"] == "dangling-ref")
        self.assertEqual(v["level"], "L2")
        self.assertIn("AGG-DEMO-999", v["message"])
        self.assertIn("glossary-model.yaml", v["file"])

    def test_gls_dep_whitelist_allows_m1(self):
        # 依赖边 GLS.relatedObjectRefs→[M1] 已登记：指向真实 M1 不触发白名单违规
        self.add("m1-object-model.yaml", M1)
        self.add("glossary-model.yaml", GLOSSARY)
        self.assertNotIn("dep-whitelist", self.kinds())

    def test_filename_model_type_mismatch_is_l1(self):
        # GLS-AC4 甲：glossary 文件 model_type 写错（如 OBJECT）→ L1 filename-mismatch
        self.add("m1-object-model.yaml", M1)
        self.add("glossary-model.yaml", GLOSSARY.replace("GLOSSARY", "OBJECT"))
        report = self.run_check()
        v = next(v for v in report["violations"] if v["kind"] == "filename-mismatch")
        self.assertEqual(v["level"], "L1")
        self.assertIn("glossary-model.yaml", v["file"])
        self.assertIn("m1-object-model.yaml", v["message"])

    def test_gls_content_in_wrong_filename_is_l1(self):
        # GLS-AC4 乙：GLS 内容错挂 m1 文件名 → L1 filename-mismatch
        self.add("m1-object-model.yaml", GLOSSARY)
        report = self.run_check()
        v = next(v for v in report["violations"] if v["kind"] == "filename-mismatch")
        self.assertEqual(v["level"], "L1")
        self.assertIn("glossary-model.yaml", v["message"])

    def test_existing_correct_filenames_still_pass(self):
        # 红线：filename 检查对既有合规文件（m1/m2 按注册表 yamlFile 命名）零扰动
        self.add("m1-object-model.yaml", M1)
        self.add("m2-behavior-model.yaml", M2)
        self.assertNotIn("filename-mismatch", self.kinds())


# ---------- 票 11：L2 一致性对（M7↔M2 / M2↔M5 / M6 roleRef）----------

CONS_REGISTRY = {
    "version": 1,
    "models": {
        "M1": dict(REGISTRY["models"]["M1"], profiles=["full"]),
        "M2": dict(REGISTRY["models"]["M2"], dependsOn=["M1", "M5"]),
        "M5": {
            "name": "主体模型", "yamlFile": "m5-actor-model.yaml",
            "modelType": "ACTOR", "camp": "business-core",
            "consumers": ["runtime", "build"], "profiles": ["full"],
            "dependsOn": ["M1", "M2"], "lockedFields": {},
        },
        "M6": {
            "name": "流程模型", "yamlFile": "m6-flow-model.yaml",
            "modelType": "FLOW", "camp": "business-core",
            "consumers": ["build"], "profiles": ["full"],
            "dependsOn": ["M1", "M2", "M5"], "lockedFields": {},
        },
        "M7": {
            "name": "查询统计与报表模型", "yamlFile": "m7-report-model.yaml",
            "modelType": "REPORT", "camp": "business-core",
            "consumers": ["runtime", "build"], "profiles": ["full"],
            "dependsOn": ["M1", "M2"], "lockedFields": {},
        },
    },
}

CONS_DEPS = {
    "version": 1,
    "idPrefixes": {"AGG-": "M1", "BH-": "M2", "ROLE-": "M5", "PERM-": "M5",
                   "FLOW-": "M6", "QR-": "M7"},
    "refKeys": ["ownerEntity", "requiredPermissions", "roles", "permissions",
                "targetRef", "roleRefs", "businessObjectRefs"],
    "edges": [
        {"from": "M2", "field": "ownerEntity", "to": ["M1"]},
        {"from": "M2", "field": "requiredPermissions", "to": ["M5"]},
        {"from": "M5", "field": "roles", "to": ["M5"]},
        {"from": "M5", "field": "permissions", "to": ["M5"]},
        {"from": "M5", "field": "targetRef", "to": ["M1", "M2"]},
        {"from": "M6", "field": "businessObjectRefs", "to": ["M1"]},
        {"from": "M6", "field": "roleRefs", "to": ["M5"]},
        {"from": "M6", "field": "roleRef", "to": ["M5"]},
        {"from": "M7", "field": "behaviorRef", "to": ["M2"]},
    ],
}

CONS_M1 = """model_type: OBJECT
version: "1.0.0"
domain: demo
aggregates:
  - id: AGG-DEMO-001
    name: 井
    alias: Well
    aggregateType: AGGREGATE_ROOT
    attributes: []
"""

CONS_M2 = """model_type: BEHAVIOR
version: "1.0.0"
domain: demo
behaviors:
  - id: BH-DEMO-Record
    name: 录入
    ownerEntity: AGG-DEMO-001
    behaviorType: COMMAND
    triggerType: USER_ACTION
    preconditions: []
    postconditions: []
    appliedRules: []
    requiredPermissions:
      - PERM-DEMO-Record
  - id: BH-DEMO-Query
    name: 查询
    ownerEntity: AGG-DEMO-001
    behaviorType: QUERY
    triggerType: USER_ACTION
    preconditions: []
    postconditions: []
    appliedRules: []
    requiredPermissions: []
"""

CONS_M5 = """model_type: ACTOR
version: "1.0.0"
domain: demo
roles:
  - roleId: ROLE-DEMO-001
    name: 录入员
    inheritsFrom: []
    permissions:
      - PERM-DEMO-Record
  - roleId: ROLE-DEMO-002
    name: 场外角色
    inheritsFrom: []
    permissions: []
permissions:
  - permissionId: PERM-DEMO-Record
    targetType: BEHAVIOR
    targetRef: BH-DEMO-Record
    dataScope: ALL
"""

CONS_M6 = """model_type: FLOW
version: "1.0.0"
domain: demo
flows:
  - id: FLOW-DEMO-001
    name: 录入流程
    flowType: COLLABORATION
    businessObjectRefs:
      - AGG-DEMO-001
    roleRefs:
      - ROLE-DEMO-001
    trigger:
      triggerType: MANUAL
    startActivity: ACT-DEMO-001
    endActivities:
      - ACT-DEMO-002
    activities:
      - activityId: ACT-DEMO-001
        name: 录入
        activityType: USER_TASK
        roleRef: ROLE-DEMO-001
        nextActivities:
          - ACT-DEMO-002
      - activityId: ACT-DEMO-002
        name: 结束
        activityType: END
"""

CONS_M7 = """model_type: REPORT
version: "1.0.0"
domain: demo
query_reports:
  - id: QR-DEMO-001
    name: 查询报表
    alias: demoQuery
    objectType: DETAIL_QUERY
    behaviorRef: BH-DEMO-Query
"""


class ConsBase(Base):
    """票 11 基座：注册表/依赖表扩到 M5/M6/M7（一致性对所需的模型面）。"""

    def setUp(self):
        super().setUp()
        write(self.root / "schema" / "model-registry.json", json.dumps(CONS_REGISTRY))
        write(self.root / "schema" / "model-deps.json", json.dumps(CONS_DEPS))
        # omittedModels 与本基座注册表对齐（票 13：引用未注册模型 = L1 红）
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "full", "schemaVersion": "1.0.0",
             "omittedModels": [
                 {"model": k, "reason": "单测基座：模型文件按需加装"}
                 for k in ("M1", "M2", "M5", "M6", "M7")
             ]}))

    def add_cons_domain(self):
        self.add("m1-object-model.yaml", CONS_M1)
        self.add("m2-behavior-model.yaml", CONS_M2)
        self.add("m5-actor-model.yaml", CONS_M5)
        self.add("m6-flow-model.yaml", CONS_M6)
        self.add("m7-report-model.yaml", CONS_M7)

    def cons_kinds(self, report=None):
        r = report or self.run_check()
        return [v["kind"] for v in r["violations"] if v["kind"].startswith("consistency-")]


class ConsistencyPairs(ConsBase):
    """票 11 AC 表（CONS-AC1–3）：三对一致性检查的正例与负变体。"""

    def test_consistent_domain_passes(self):
        # 正例：三对全闭合（QR→QUERY 一对一、PERM 回指、活动角色∈流程角色）→ 无 consistency- 行
        self.add_cons_domain()
        report = self.run_check()
        self.assertEqual(report["status"], "pass", report["violations"])
        self.assertEqual(self.cons_kinds(report), [])

    def test_m7_bound_to_non_query_behavior_is_redirection(self):
        # CONS-AC1 甲：behaviorRef 指向 COMMAND 行为 → consistency-redirection（L2）
        self.add_cons_domain()
        self.add("m7-report-model.yaml",
                 CONS_M7.replace("BH-DEMO-Query", "BH-DEMO-Record"))
        report = self.run_check()
        self.assertIn("consistency-redirection", self.cons_kinds(report))
        v = next(v for v in report["violations"]
                 if v["kind"] == "consistency-redirection")
        self.assertEqual(v["level"], "L2")
        for needle in ("QR-DEMO-001", "BH-DEMO-Record", "COMMAND", "behaviorRef"):
            self.assertIn(needle, v["message"])

    def test_shared_query_behavior_is_not_one_to_one(self):
        # CONS-AC1 乙：同一 QUERY 行为被两个 QR 绑定 → consistency-not-one-to-one（L2），
        # 报文含先绑者与再绑者双方 ID
        self.add_cons_domain()
        qr2 = """  - id: QR-DEMO-002
    name: 查询报表二
    alias: demoQueryTwo
    objectType: DETAIL_QUERY
    behaviorRef: BH-DEMO-Query
"""
        self.add("m7-report-model.yaml", CONS_M7 + qr2)
        report = self.run_check()
        self.assertIn("consistency-not-one-to-one", self.cons_kinds(report))
        v = next(v for v in report["violations"]
                 if v["kind"] == "consistency-not-one-to-one")
        self.assertEqual(v["level"], "L2")
        for needle in ("QR-DEMO-001", "QR-DEMO-002", "BH-DEMO-Query"):
            self.assertIn(needle, v["message"])

    def test_perm_target_ref_not_backlinking_is_permission_break(self):
        # CONS-AC2：PERM 存在（dangling 不红）但 targetRef 未回指要求它的行为
        # → consistency-permission（L2）
        self.add_cons_domain()
        self.add("m5-actor-model.yaml",
                 CONS_M5.replace("targetRef: BH-DEMO-Record", "targetRef: BH-DEMO-Query"))
        report = self.run_check()
        self.assertIn("consistency-permission", self.cons_kinds(report))
        v = next(v for v in report["violations"]
                 if v["kind"] == "consistency-permission")
        self.assertEqual(v["level"], "L2")
        for needle in ("BH-DEMO-Record", "PERM-DEMO-Record", "BH-DEMO-Query"):
            self.assertIn(needle, v["message"])

    def test_unknown_perm_stays_dangling_ref_not_consistency(self):
        # P2 存在性向仍归 dangling-ref（requiredPermissions 在 refKeys∪edges），
        # 不重复报 consistency-permission——红因不混
        self.add_cons_domain()
        self.add("m2-behavior-model.yaml",
                 CONS_M2.replace("PERM-DEMO-Record", "PERM-DEMO-999"))
        report = self.run_check()
        self.assertIn("dangling-ref", self.kinds(report))
        self.assertNotIn("consistency-permission", self.cons_kinds(report))

    def test_activity_role_outside_flow_rolerefs_is_flow_role(self):
        # CONS-AC3：活动 roleRef 指向存在但不在流程 roleRefs 内的角色
        # → consistency-flow-role（L2），报文含流程/活动/角色三方 ID
        self.add_cons_domain()
        self.add("m6-flow-model.yaml",
                 CONS_M6.replace("roleRef: ROLE-DEMO-001", "roleRef: ROLE-DEMO-002"))
        report = self.run_check()
        self.assertIn("consistency-flow-role", self.cons_kinds(report))
        v = next(v for v in report["violations"]
                 if v["kind"] == "consistency-flow-role")
        self.assertEqual(v["level"], "L2")
        for needle in ("FLOW-DEMO-001", "ACT-DEMO-001", "ROLE-DEMO-002", "roleRefs"):
            self.assertIn(needle, v["message"])

    def test_json_report_carries_consistency_rows(self):
        # 报告行可机读：--json 输出中每条一致性违规一行（level/kind/file/line/message）
        self.add_cons_domain()
        self.add("m7-report-model.yaml",
                 CONS_M7.replace("BH-DEMO-Query", "BH-DEMO-Record"))
        buf = io.StringIO()
        with redirect_stdout(buf):
            sc.main(["--json", str(self.root)])
        rows = json.loads(buf.getvalue())["violations"]
        cons = [r for r in rows if r["kind"].startswith("consistency-")]
        self.assertTrue(cons)
        for r in cons:
            self.assertEqual(r["level"], "L2")
            self.assertTrue(r["file"].endswith("m7-report-model.yaml"))
            self.assertGreater(r["line"], 0)

    def test_pairs_degenerate_without_models(self):
        # 退化面：注册表只有 M1/M2（Base 迷你表）时一致性对静默跳过，不崩不误报
        # （manifest 同步回 Base 基座形态，票 13：omittedModels 须引用注册模型）
        write(self.root / "schema" / "model-registry.json", json.dumps(REGISTRY))
        write(self.root / "schema" / "model-deps.json", json.dumps(DEPS))
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "full", "schemaVersion": "1.0.0",
             "omittedModels": [
                 {"model": "M1", "reason": "单测基座：模型文件按需加装"},
                 {"model": "M2", "reason": "单测基座：模型文件按需加装"},
                 {"model": "GLS", "reason": "单测基座：模型文件按需加装"},
             ]}))
        self.add("m1-object-model.yaml", M1)
        self.add("m2-behavior-model.yaml", M2)
        self.assertEqual(self.run_check()["status"], "pass")

# ---------- 票 13：L1 元素级必填闸 + L4 AC6 反向（missing-model-file/omittedModels）----------

REQ_REGISTRY = {
    "version": "1.2.0",
    "models": {
        "M1": dict(REGISTRY["models"]["M1"], profiles=["full"]),
        "M2": dict(REGISTRY["models"]["M2"], profiles=["full"],
                   requiredElementFields={
                       "BH-": ["id", "name", "ownerEntity", "behaviorType"]}),
        "M7": {
            "name": "查询统计与报表模型", "yamlFile": "m7-report-model.yaml",
            "modelType": "REPORT", "camp": "business-core",
            "consumers": ["runtime", "build"], "profiles": ["full"],
            "dependsOn": ["M1", "M2"], "lockedFields": {},
            "requiredElementFields": {
                "QR-": ["id", "name", "behaviorRef"]},
        },
    },
}

REQ_DEPS = {
    "version": "1.2.0",
    "idPrefixes": {"AGG-": "M1", "BH-": "M2", "QR-": "M7"},
    "refKeys": ["ownerEntity", "behaviorRef"],
    "edges": [
        {"from": "M2", "field": "ownerEntity", "to": ["M1"]},
        {"from": "M7", "field": "behaviorRef", "to": ["M2"]},
    ],
}


class ReqBase(Base):
    """票 13 基座：M1/M2/M7 迷你注册表，M2/M7 带 requiredElementFields。"""

    def setUp(self):
        super().setUp()
        write(self.root / "schema" / "model-registry.json", json.dumps(REQ_REGISTRY))
        write(self.root / "schema" / "model-deps.json", json.dumps(REQ_DEPS))
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "full", "schemaVersion": "1.2.0",
             "omittedModels": [
                 {"model": "M1", "reason": "单测基座：模型文件按需加装"},
                 {"model": "M2", "reason": "单测基座：模型文件按需加装"},
                 {"model": "M7", "reason": "单测基座：模型文件按需加装"},
             ]}))

    def req_violations(self, report=None, kind="required-field"):
        r = report or self.run_check()
        return [v for v in r["violations"] if v["kind"] == kind]


class RequiredFields(ReqBase):
    """票 13 AC 表 AC1/AC2 的单测面：元素级结构性必填闸。"""

    def test_all_required_fields_present_passes(self):
        self.add("m1-object-model.yaml", M1)
        self.add("m2-behavior-model.yaml", M2 + """  - id: BH-DEMO-Query
    name: 查询
    ownerEntity: AGG-DEMO-001
    behaviorType: QUERY
""")
        self.add("m7-report-model.yaml", CONS_M7)
        self.assertEqual(self.run_check()["status"], "pass",
                         self.run_check()["violations"])

    def test_missing_type_discriminator_is_required_field(self):
        # AC1：M2 行为缺 behaviorType（一致性锚点）→ L1 required-field 红（不再静默跳过）
        self.add("m1-object-model.yaml", M1)
        self.add("m2-behavior-model.yaml",
                 "\n".join(l for l in M2.splitlines()
                           if not l.startswith("    behaviorType")))
        report = self.run_check()
        vs = self.req_violations(report)
        self.assertTrue(vs)
        v = vs[0]
        self.assertEqual(v["level"], "L1")
        self.assertIn("BH-DEMO-Record", v["message"])
        self.assertIn("behaviorType", v["message"])
        self.assertIn("requiredElementFields", v["message"])
        self.assertGreater(v["line"], 0)

    def test_missing_anchor_field_reports_element_and_field(self):
        # AC2 同款：M7 报表缺 behaviorRef → L1 required-field 红
        self.add("m7-report-model.yaml",
                 "\n".join(l for l in CONS_M7.splitlines()
                           if not l.startswith("    behaviorRef")))
        vs = self.req_violations()
        self.assertTrue(vs)
        self.assertIn("QR-DEMO-001", vs[0]["message"])
        self.assertIn("behaviorRef", vs[0]["message"])

    def test_empty_shell_file_is_required_field(self):
        # AC3 同款：behaviors 空列表 = 空壳文件 → L1 required-field 红
        self.add("m2-behavior-model.yaml",
                 "model_type: BEHAVIOR\nversion: \"1.0.0\"\ndomain: demo\nbehaviors: []\n")
        vs = self.req_violations()
        self.assertTrue(vs)
        self.assertIn("空壳", vs[0]["message"])
        self.assertIn("M2", vs[0]["message"])

    def test_filename_mismatch_skips_required_gate(self):
        # 红因纯净：文件名与 model_type 错挂时内容与模型锚已断，必填闸让位给
        # filename-mismatch，不叠加空壳红因（gls-ac4 形态，lessons/13）
        self.add("m1-object-model.yaml",
                 "model_type: BEHAVIOR\nversion: \"1.0.0\"\ndomain: demo\nbehaviors: []\n")
        report = self.run_check()
        self.assertEqual(self.req_violations(report), [])
        self.assertIn("filename-mismatch", self.kinds(report))


class MissingModelFile(ReqBase):
    """票 13 AC 表 AC5/AC6 的单测面：AC6 反向 + omittedModels 豁免机制。"""

    def test_enabled_model_without_file_is_l4(self):
        # AC5：profile 启用 M2 但域内无文件、无豁免 → L4 missing-model-file 红
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "full", "schemaVersion": "1.2.0"}))
        self.add("m1-object-model.yaml", M1)
        report = self.run_check()
        vs = self.req_violations(report, kind="missing-model-file")
        self.assertTrue(vs)
        v = vs[0]
        self.assertEqual(v["level"], "L4")
        self.assertIn("M2", v["message"])
        self.assertIn("omittedModels", v["message"])

    def test_waived_model_with_reason_passes(self):
        # AC6：同上但 omittedModels 带理由豁免 → 不红
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "full", "schemaVersion": "1.2.0",
             "omittedModels": [
                 {"model": "M2", "reason": "无素材证据，有意裁剪"},
                 {"model": "M7", "reason": "无素材证据，有意裁剪"},
             ]}))
        self.add("m1-object-model.yaml", M1)
        report = self.run_check()
        self.assertEqual(report["status"], "pass", report["violations"])

    def test_waiver_without_reason_is_not_exemption(self):
        # 豁免条目缺 reason / reason 空串 = 无效豁免，缺文件照红
        for reason in (None, "", "   "):
            entry = {"model": "M2"}
            if reason is not None:
                entry["reason"] = reason
            write(self.root / "demo" / "manifest.json", json.dumps(
                {"domain": "demo", "profile": "full", "schemaVersion": "1.2.0",
                 "omittedModels": [entry]}))
            self.add("m1-object-model.yaml", M1)
            vs = self.req_violations(self.run_check(), kind="missing-model-file")
            self.assertTrue(vs, f"reason={reason!r} 不应构成有效豁免")
            self.assertIn("M2", vs[0]["message"])

    def test_waiver_referencing_unknown_model_is_l1(self):
        # omittedModels 引用未注册模型 = 配置错误，L1 红（防错别字静默失效）
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "full", "schemaVersion": "1.2.0",
             "omittedModels": [{"model": "MX", "reason": "手滑写错模型键"}]}))
        self.add("m1-object-model.yaml", M1)
        self.assertIn("unknown-omitted-model", self.kinds())

    def test_malformed_waiver_entry_is_l1(self):
        # omittedModels 条目缺 model 键 = 配置错误，L1 红
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "full", "schemaVersion": "1.2.0",
             "omittedModels": [{"reason": "不是合法条目"}]}))
        self.add("m1-object-model.yaml", M1)
        self.assertIn("bad-omitted-model", self.kinds())

    def test_unknown_profile_does_not_trigger_missing_check(self):
        # profile 未知时 enabled 为空，反向闸不触发（unknown-profile 已单独红）
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "nope", "schemaVersion": "1.2.0"}))
        kinds = self.kinds()
        self.assertIn("unknown-profile", kinds)
        self.assertNotIn("missing-model-file", kinds)


# ---------- 票 16：L4 禁用词拦截面（GLS×schema_check 联动闸，BAN-* 出厂断言）----------

BAN_GLS = """model_type: GLOSSARY
version: "1.0.0"
domain: demo
terms:
  - id: GLS-DEMO-001
    term: 老完成率
    aliases: []
    termType: 禁用词
    definition: v1 口径，已废弃；禁用旧称，替代=新完成率。
    status: 禁用（替代：新完成率）
    source: 合成·票 16 出厂集
  - id: GLS-DEMO-002
    term: 剔检产量
    aliases: [净产量]
    termType: 别名
    definition: 剔除检修井口径的产量。
    status: 有效
    source: 合成·票 16 出厂集
"""


class BannedTerm(Base):
    """票 16 AC 表（AC1–4）：禁用词拦截面。真源=域内 GLS 术语 status 含「禁用」
    条目的 term+aliases；匹配面=全文件递归收集键恰为 name/alias 的字符串值
    （description/notes 不扫=文档自由）。防误报对照（AC4/描述提及/GLS 自身 term
    不自匹配）是本套件的灵魂断言——钉死匹配面，防止未来放大。"""

    def test_name_containing_banned_term_is_l4(self):
        # AC1：元素 name 含禁用词（子串）→ L4 banned-term，报文含 GLS 条目 ID 与命中词
        self.add("m1-object-model.yaml", M1.replace("name: 井", "name: 老完成率（v1 口径）"))
        self.add("glossary-model.yaml", BAN_GLS)
        report = self.run_check()
        self.assertIn("banned-term", self.kinds(report))
        v = next(v for v in report["violations"] if v["kind"] == "banned-term")
        self.assertEqual(v["level"], "L4")
        self.assertIn("GLS-DEMO-001", v["message"])
        self.assertIn("老完成率", v["message"])
        self.assertIn("m1-object-model.yaml", v["file"])
        self.assertGreater(v["line"], 0)

    def test_alias_containing_banned_term_is_l4(self):
        # AC2：元素 alias 撞禁用词 → L4 banned-term
        self.add("m1-object-model.yaml", M1.replace("alias: Well", "alias: Well老完成率"))
        self.add("glossary-model.yaml", BAN_GLS)
        report = self.run_check()
        self.assertIn("banned-term", self.kinds(report))
        v = next(v for v in report["violations"] if v["kind"] == "banned-term")
        self.assertEqual(v["level"], "L4")

    def test_alias_of_banned_entry_is_also_banned(self):
        # 禁用条目的 aliases 也是禁用词表成员（设计裁决：term 与 aliases 都算）
        gls = BAN_GLS.replace("    aliases: []", "    aliases: [废弃口径]")
        self.add("m1-object-model.yaml", M1.replace("name: 井", "name: 废弃口径"))
        self.add("glossary-model.yaml", gls)
        report = self.run_check()
        self.assertIn("banned-term", self.kinds(report))
        v = next(v for v in report["violations"] if v["kind"] == "banned-term")
        self.assertIn("废弃口径", v["message"])

    def test_status_substring_wide_gate(self):
        # 宽进严出：status 值含「禁用」子串即入表（不枚举状态值）——
        # 「已禁用待复核」这类非「禁用（替代…）」形态照样拦
        self.add("m1-object-model.yaml", M1.replace("name: 井", "name: 老完成率"))
        self.add("glossary-model.yaml",
                 BAN_GLS.replace("status: 禁用（替代：新完成率）", "status: 已禁用待复核"))
        self.assertIn("banned-term", self.kinds())

    def test_valid_status_term_in_name_passes(self):
        # AC4 防误报对照：status=有效的 GLS 术语出现在 name → 必须绿
        #（只拦禁用 status，不拦全部术语）
        self.add("m1-object-model.yaml", M1.replace("name: 井", "name: 剔检产量"))
        self.add("glossary-model.yaml", BAN_GLS)
        report = self.run_check()
        self.assertNotIn("banned-term", self.kinds(report))
        self.assertEqual(report["status"], "pass", report["violations"])

    def test_description_mention_passes(self):
        # AC3 单域版：description 提及禁用词合法（文档自由）——拦截面只在 name/alias
        self.add("m1-object-model.yaml",
                 M1 + "    description: 禁用旧称「老完成率」——v1 口径，2024 年废弃。\n")
        self.add("glossary-model.yaml", BAN_GLS)
        report = self.run_check()
        self.assertNotIn("banned-term", self.kinds(report))
        self.assertEqual(report["status"], "pass", report["violations"])

    def test_gls_own_terms_do_not_self_match(self):
        # 防自匹配：禁用词表来自 GLS term 值，匹配面是 name/alias 键——
        # GLS 条目以 term/aliases 承载词面，不在匹配面 → 域内仅 GLS 也全绿
        self.add("glossary-model.yaml", BAN_GLS)
        report = self.run_check()
        self.assertNotIn("banned-term", self.kinds(report))
        self.assertEqual(report["status"], "pass", report["violations"])

    def test_matching_face_is_exactly_name_and_alias_keys(self):
        # 匹配面钉死：键恰为 name/alias 的字符串值——label/definition/notes 等
        # 同持禁用词的键不入面（函数级直测，防匹配面悄悄放大成全字段）
        data = sc.load_yaml_from_text(
            "a:\n"
            "  name: 老完成率\n"
            "  alias: 老完成率别名\n"
            "  label: 老完成率标签\n"
            "  definition: 提及老完成率\n"
            "  notes: 老完成率\n"
            "  aliases: [老完成率]\n")
        hits = [v for v, _m, _k in sc.iter_name_alias_values(data)]
        self.assertEqual(hits, ["老完成率", "老完成率别名"])

    def test_nested_name_face_is_matched(self):
        # 通用口径递归收集：M2 behaviors[].name 撞禁用词同红（不逐模型硬列挂点）
        self.add("m1-object-model.yaml", M1)
        self.add("m2-behavior-model.yaml", M2.replace("name: 录入", "name: 录入老完成率"))
        self.add("glossary-model.yaml", BAN_GLS)
        report = self.run_check()
        self.assertIn("banned-term", self.kinds(report))
        v = next(v for v in report["violations"] if v["kind"] == "banned-term")
        self.assertIn("m2-behavior-model.yaml", v["file"])

    def test_filename_mismatch_file_skips_banned_face(self):
        # 红因纯净（沿票 13 先例）：文件名与 model_type 错挂的文件跳过禁用词匹配面，
        # 让位 filename-mismatch，不叠杂音红因
        self.add("m1-object-model.yaml", M1)
        self.add("glossary-model.yaml", BAN_GLS)
        self.add("m2-behavior-model.yaml",
                 M2.replace("model_type: BEHAVIOR", "model_type: OBJECT")
                 .replace("name: 录入", "name: 录入老完成率"))
        report = self.run_check()
        self.assertIn("filename-mismatch", self.kinds(report))
        self.assertNotIn("banned-term", self.kinds(report))


if __name__ == "__main__":
    unittest.main()
