#!/usr/bin/env python3
"""graph_index.py 的单测（stdlib unittest + PyYAML，TDD 先行）。

合成三模型（M1/M2/M3）迷你域走端到端，AC1–6 各有着落
（AC 对应 specs/graph_index.md 断言表；出厂集 cmd 断言在 fixtures/graph_index/）。
迷你域引用链：BH-DEMO-Do →(ownerEntity) AGG-DEMO-001 →(targetAggregate) AGG-DEMO-002、
AGG-DEMO-001 →(dictionaryId) DICT-DEMO-01、BH-DEMO-Do ↔ RULE-DEMO-001（appliedRules/reusedBy 成环，
验证环安全）；AGG-DEMO-003 孤立（验证空影响集）。
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import graph_index as gi


def run_main(argv):
    """跑 main，捕获 stdout+stderr，返回 (退出码, stdout, stderr)。"""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = gi.main(argv)
    return rc, out.getvalue(), err.getvalue()


def json_main(*argv):
    """--json 模式跑 main，返回 (退出码, 解析后的报告)。"""
    rc, out, _err = run_main(["--json", *argv])
    return rc, json.loads(out)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


DEPS = {
    "version": 1,
    "idPrefixes": {"AGG-": "M1", "DICT-": "M1", "BH-": "M2", "RULE-": "M3"},
    # 镜像真实 model-deps.json 形态：reusedBy 只在 edges 登记（不在 refKeys），
    # 覆盖「ref 扫描键 = refKeys ∪ *Ref/*Refs ∪ edges 登记字段」的并集路径。
    "refKeys": ["ownerEntity", "appliedRules", "targetAggregate", "dictionaryId"],
    "edges": [{"from": "M3", "field": "reusedBy", "to": ["M2"]}],
}

M1 = """model_type: OBJECT
version: "1.0.0"
domain: demo
aggregates:
  - id: AGG-DEMO-001
    name: 对象甲
    aggregateType: AGGREGATE_ROOT
    attributes:
      - name: peer
        label: 对端
        type: AggregateRootRef
        targetAggregate: AGG-DEMO-002
      - name: status
        label: 状态
        type: DictionaryRef
        dictionaryRef:
          dictionaryId: DICT-DEMO-01
          typeCode: T
  - id: AGG-DEMO-002
    name: 对象乙
    aggregateType: AGGREGATE_ROOT
    attributes: []
  - id: AGG-DEMO-003
    name: 孤立对象
    aggregateType: AGGREGATE_ROOT
    attributes: []
data_dictionaries:
  - id: DICT-DEMO-01
    name: 字典甲
    types: []
"""

M2 = """model_type: BEHAVIOR
version: "1.0.0"
domain: demo
behaviors:
  - id: BH-DEMO-Do
    name: 干活
    ownerEntity: AGG-DEMO-001
    behaviorType: COMMAND
    triggerType: USER_ACTION
    preconditions: []
    postconditions: []
    appliedRules: [RULE-DEMO-001]
    requiredPermissions: []
"""

M3 = """model_type: RULE
version: "1.0.0"
domain: demo
rules:
  - id: RULE-DEMO-001
    name: 规则甲
    ruleType: VALIDATION
    outputType: Boolean
    expression: value >= 0
    reusedBy: [BH-DEMO-Do]
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "onto"
        write(self.root / "schema" / "model-deps.json", json.dumps(DEPS))
        write(self.root / "demo" / "manifest.json", json.dumps(
            {"domain": "demo", "profile": "full", "schemaVersion": "1.0.0"}))
        write(self.root / "demo" / "m1-object-model.yaml", M1)
        write(self.root / "demo" / "m2-behavior-model.yaml", M2)
        write(self.root / "demo" / "m3-rule-model.yaml", M3)

    def tearDown(self):
        self.tmp.cleanup()

    def build(self):
        return gi.build_graph(self.root)


class Ac1BuildStats(Base):
    def test_nodes_and_edges_counts_nonzero(self):
        graph = self.build()
        self.assertEqual(set(graph.nodes),
                         {"AGG-DEMO-001", "AGG-DEMO-002", "AGG-DEMO-003",
                          "DICT-DEMO-01", "BH-DEMO-Do", "RULE-DEMO-001"})
        self.assertEqual(len(graph.edges), 5)
        stats = graph.stats()
        self.assertGreater(stats["nodes"], 0)
        self.assertGreater(stats["edges"], 0)

    def test_edges_carry_ref_field_labels(self):
        graph = self.build()
        triples = {(e["src"], e["field"], e["dst"]) for e in graph.edges}
        self.assertIn(("AGG-DEMO-001", "targetAggregate", "AGG-DEMO-002"), triples)
        self.assertIn(("AGG-DEMO-001", "dictionaryId", "DICT-DEMO-01"), triples)
        self.assertIn(("BH-DEMO-Do", "ownerEntity", "AGG-DEMO-001"), triples)
        self.assertIn(("BH-DEMO-Do", "appliedRules", "RULE-DEMO-001"), triples)
        self.assertIn(("RULE-DEMO-001", "reusedBy", "BH-DEMO-Do"), triples)

    def test_human_output_has_stats_line(self):
        rc, out, _err = run_main([str(self.root), "--query", "AGG-DEMO-001"])
        self.assertEqual(rc, 0)
        self.assertIn("图统计: 节点=6 边=5", out)


class Ac2QueryHit(Base):
    def test_human_hit_returns_node_and_attributes(self):
        rc, out, _err = run_main([str(self.root), "--query", "AGG-DEMO-001"])
        self.assertEqual(rc, 0)
        self.assertIn("命中: AGG-DEMO-001", out)
        self.assertIn("对象甲", out)          # 属性：name
        self.assertIn("AggregateRootRef", out)  # 属性：attributes[].type
        self.assertIn("m1-object-model.yaml", out)  # 溯源：文件

    def test_json_hit_with_node_record(self):
        rc, report = json_main(str(self.root), "--query", "AGG-DEMO-001")
        self.assertEqual(rc, 0)
        self.assertTrue(report["found"])
        node = report["node"]
        self.assertEqual(node["id"], "AGG-DEMO-001")
        self.assertEqual(node["model"], "M1")
        self.assertEqual(node["domain"], "demo")
        self.assertTrue(node["file"].endswith("m1-object-model.yaml"))
        self.assertGreater(node["line"], 0)
        self.assertEqual(node["element"]["name"], "对象甲")


class Ac3Closure(Base):
    def test_two_hop_closure_includes_downstream(self):
        rc, report = json_main(str(self.root), "--query", "BH-DEMO-Do",
                               "--closure", "2")
        self.assertEqual(rc, 0)
        rows = report["closure"]
        ids = {row["id"] for row in rows}
        self.assertEqual(ids, {"AGG-DEMO-001", "RULE-DEMO-001",
                               "AGG-DEMO-002", "DICT-DEMO-01"})
        hops = {row["id"]: row["hops"] for row in rows}
        self.assertEqual(hops["AGG-DEMO-001"], 1)
        self.assertEqual(hops["RULE-DEMO-001"], 1)
        self.assertEqual(hops["AGG-DEMO-002"], 2)  # 经 AGG-DEMO-001 连出
        self.assertEqual(hops["DICT-DEMO-01"], 2)

    def test_one_hop_excludes_second_hop(self):
        _rc, report = json_main(str(self.root), "--query", "BH-DEMO-Do",
                                "--closure", "1")
        ids = {row["id"] for row in report["closure"]}
        self.assertEqual(ids, {"AGG-DEMO-001", "RULE-DEMO-001"})
        self.assertNotIn("AGG-DEMO-002", ids)
        self.assertNotIn("DICT-DEMO-01", ids)

    def test_closure_cycle_safe_and_start_excluded(self):
        _rc, report = json_main(str(self.root), "--query", "BH-DEMO-Do",
                                "--closure", "10")
        ids = {row["id"] for row in report["closure"]}
        self.assertNotIn("BH-DEMO-Do", ids)  # 环（reusedBy/appliedRules）不回吞起点
        self.assertEqual(len(ids), 4)

    def test_closure_of_isolated_node_is_empty(self):
        _rc, report = json_main(str(self.root), "--query", "AGG-DEMO-003",
                                "--closure", "2")
        self.assertEqual(report["closure"], [])

    def test_closure_paths_end_at_reached_node(self):
        _rc, report = json_main(str(self.root), "--query", "BH-DEMO-Do",
                                "--closure", "2")
        row = next(r for r in report["closure"] if r["id"] == "DICT-DEMO-01")
        self.assertEqual(row["path"],
                         ["BH-DEMO-Do", "AGG-DEMO-001", "DICT-DEMO-01"])
        self.assertEqual(row["via"], "dictionaryId")


class Ac4Impact(Base):
    def test_impact_reverse_walk_set_and_hops(self):
        rc, report = json_main(str(self.root), "--query", "DICT-DEMO-01",
                               "--impact")
        self.assertEqual(rc, 0)
        rows = report["impact"]
        ids = {row["id"] for row in rows}
        self.assertEqual(ids, {"AGG-DEMO-001", "BH-DEMO-Do", "RULE-DEMO-001"})
        hops = {row["id"]: row["hops"] for row in rows}
        self.assertEqual(hops["AGG-DEMO-001"], 1)
        self.assertEqual(hops["BH-DEMO-Do"], 2)
        self.assertEqual(hops["RULE-DEMO-001"], 3)
        self.assertNotIn("AGG-DEMO-002", ids)  # 无路径可达者不入影响集

    def test_impact_paths_start_at_dependent(self):
        _rc, report = json_main(str(self.root), "--query", "DICT-DEMO-01",
                                "--impact")
        row = next(r for r in report["impact"] if r["id"] == "RULE-DEMO-001")
        self.assertEqual(row["path"],
                         ["RULE-DEMO-001", "BH-DEMO-Do",
                          "AGG-DEMO-001", "DICT-DEMO-01"])

    def test_impact_empty_reports_zero(self):
        rc, out, _err = run_main([str(self.root), "--query", "AGG-DEMO-003",
                                  "--impact"])
        self.assertEqual(rc, 0)
        self.assertIn("0 个受影响节点", out)

    def test_impact_human_lists_dependents(self):
        rc, out, _err = run_main([str(self.root), "--query", "DICT-DEMO-01",
                                  "--impact"])
        self.assertEqual(rc, 0)
        self.assertIn("影响集", out)
        self.assertIn("BH-DEMO-Do", out)


class Ac5NotFound(Base):
    def test_human_miss_is_explicit_nonzero(self):
        rc, out, err = run_main([str(self.root), "--query", "AGG-DEMO-999"])
        self.assertEqual(rc, 1)
        combined = out + err
        self.assertIn("未找到", combined)
        self.assertIn("AGG-DEMO-999", combined)
        self.assertNotIn("命中", combined)  # 不猜：绝不返回近似节点

    def test_json_miss_found_false(self):
        rc, report = json_main(str(self.root), "--query", "AGG-DEMO-999")
        self.assertEqual(rc, 1)
        self.assertFalse(report["found"])
        self.assertIn("未找到", report["error"])
        self.assertEqual(report["stats"]["nodes"], 6)


class Ac6RebuildReflectsNewTruth(Base):
    def test_rebuild_after_edit_reflects_new_content(self):
        rc1, out1, _err1 = run_main([str(self.root), "--query", "AGG-DEMO-002"])
        self.assertEqual(rc1, 0)
        self.assertIn("对象乙", out1)
        # 改仓内容（旧名 → 无重叠的新名），同进程内重建必须反映新真源
        write(self.root / "demo" / "m1-object-model.yaml",
              M1.replace("对象乙", "台账乙"))
        rc2, out2, _err2 = run_main([str(self.root), "--query", "AGG-DEMO-002"])
        self.assertEqual(rc2, 0)
        self.assertIn("台账乙", out2)
        self.assertNotIn("对象乙", out2)  # 无陈旧缓存

    def test_no_cache_files_created(self):
        before = sorted(p.name for p in (self.root / "demo").iterdir())
        for _ in range(3):
            rc, _out, _err = run_main([str(self.root), "--query", "AGG-DEMO-001"])
            self.assertEqual(rc, 0)
        after = sorted(p.name for p in (self.root / "demo").iterdir())
        self.assertEqual(before, after)  # 工具只读，不落任何缓存文件


class Robustness(Base):
    def test_unknown_prefix_ref_ignored(self):
        variant = M1.replace(
            "      - name: peer",
            "      - name: note\n        type: String\n        noteRef: XX-DEMO-9\n"
            "      - name: peer")
        write(self.root / "demo" / "m1-object-model.yaml", variant)
        graph = self.build()
        self.assertEqual(len(graph.edges), 5)  # 未登记前缀不构成边
        self.assertFalse(any("XX-DEMO-9" in e["dst"] for e in graph.edges))

    def test_dangling_ref_edge_kept_and_traversable(self):
        write(self.root / "demo" / "m2-behavior-model.yaml",
              M2.replace("ownerEntity: AGG-DEMO-001",
                         "ownerEntity: AGG-DEMO-999"))
        graph = self.build()  # 图反映声明；悬空判定归语义闸
        self.assertIn(("BH-DEMO-Do", "ownerEntity", "AGG-DEMO-999"),
                      {(e["src"], e["field"], e["dst"]) for e in graph.edges})
        _rc, report = json_main(str(self.root), "--query", "BH-DEMO-Do",
                                "--closure", "1")
        self.assertIn("AGG-DEMO-999", {row["id"] for row in report["closure"]})

    def test_multi_domain_build_over_root(self):
        write(self.root / "demo2" / "manifest.json", json.dumps(
            {"domain": "demo2", "profile": "full", "schemaVersion": "1.0.0"}))
        write(self.root / "demo2" / "m2-behavior-model.yaml",
              M2.replace("BH-DEMO-Do", "BH-DEMO2-Check"))
        graph = self.build()
        self.assertEqual(graph.stats()["nodes"], 7)
        self.assertIn("BH-DEMO2-Check", graph.nodes)
        self.assertEqual(graph.nodes["BH-DEMO2-Check"]["domain"], "demo2")
        # 跨域边照常挂接
        self.assertIn(("BH-DEMO2-Check", "ownerEntity", "AGG-DEMO-001"),
                      {(e["src"], e["field"], e["dst"]) for e in graph.edges})

    def test_json_output_deterministic(self):
        _rc1, out1, _e1 = run_main([str(self.root), "--query", "BH-DEMO-Do",
                                    "--closure", "2", "--impact", "--json"])
        _rc2, out2, _e2 = run_main([str(self.root), "--query", "BH-DEMO-Do",
                                    "--closure", "2", "--impact", "--json"])
        self.assertEqual(out1, out2)


class UsageAndConfigErrors(Base):
    def test_missing_query_is_usage_error(self):
        with self.assertRaises(SystemExit) as cm:
            run_main([str(self.root)])
        self.assertEqual(cm.exception.code, 2)

    def test_closure_zero_is_usage_error(self):
        rc, _out, err = run_main([str(self.root), "--query", "AGG-DEMO-001",
                                  "--closure", "0"])
        self.assertEqual(rc, 2)
        self.assertIn("用法错误", err)

    def test_missing_target_dir_is_config_error(self):
        rc, _out, err = run_main([str(self.root / "nope"), "--query", "X"])
        self.assertEqual(rc, 2)
        self.assertIn("配置错误", err)

    def test_missing_model_deps_is_config_error(self):
        (self.root / "schema" / "model-deps.json").unlink()
        rc, _out, err = run_main([str(self.root), "--query", "AGG-DEMO-001"])
        self.assertEqual(rc, 2)
        self.assertIn("配置错误", err)

    def test_dir_without_any_domain_is_config_error(self):
        empty = self.root / "nowhere"
        empty.mkdir()
        rc, _out, err = run_main([str(empty), "--query", "AGG-DEMO-001"])
        self.assertEqual(rc, 2)
        self.assertIn("配置错误", err)

    def test_broken_yaml_refuses_to_build(self):
        write(self.root / "demo" / "m2-behavior-model.yaml",
              "model_type: BEHAVIOR\nbehaviors:\n\t- id: x\n")
        rc, _out, err = run_main([str(self.root), "--query", "AGG-DEMO-001"])
        self.assertEqual(rc, 2)  # 部分图=说谎的图：拒绝建图，不做部分索引
        self.assertIn("配置错误", err)


if __name__ == "__main__":
    unittest.main()
