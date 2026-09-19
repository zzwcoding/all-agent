#!/usr/bin/env python3
"""schema_check.py 的单测（stdlib unittest + PyYAML，TDD 先行）。

合成两模型（M1/M2）迷你 schema 走端到端，AC1–7 各一条（AC 对应 specs/schema_check.md 断言表）。
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
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "full", "schemaVersion": "1.0.0"}))

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


if __name__ == "__main__":
    unittest.main()
