#!/usr/bin/env python3
"""semantic_service_core.py 的单测（stdlib unittest + PyYAML，TDD 先行）。

两类被测域：
  1. /tmp 合成迷你域（每测自建，含 MU 屏/禁用术语/有效术语，camp 面外与
     禁用词/缺件/锚定四类裁决在受控域逐条实测）；
  2. 渤海域真域回归（tickets/22 AC 表 + docs/walkthrough/step3-golden-qa.md
     八问基准）：Q1–Q6 走查六问 + 票 17 术语两问（Q7/Q8），对 ontology/bohai
     逐问断言 status 与关键 ID（真域缺失时 skip，不误红）。

红相记录（TDD）：本文件先行落盘，semantic_service_core 未实现时收集即红。
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import semantic_service_core as ssc

REPO = Path(__file__).resolve().parent.parent
BOHAI = REPO / "ontology" / "bohai"


def run_main(argv):
    """跑 CLI main，捕获 stdout+stderr，返回 (退出码, stdout, stderr)。"""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = ssc.main(argv)
    return rc, out.getvalue(), err.getvalue()


def ask_json(root: Path, question: str) -> tuple[int, dict]:
    """对给定仓根 --json 提问，返回 (退出码, 裁决 dict)。"""
    rc, out, _ = run_main([str(root), "--ask", question, "--json"])
    return rc, json.loads(out)


# ---------- 合成迷你域（camp 面外原样场景 + 禁用词 + 术语指路） ----------

DEPS = {
    "version": "1",
    "idPrefixes": {"AGG-": "M1", "DICT-": "M1", "BH-": "M2", "RULE-": "M3",
                   "SCR-": "MU", "GLS-": "GLS"},
    "refKeys": ["ownerEntity", "appliedRules", "targetAggregate",
                "relatedObjectRefs"],
    "edges": [{"from": "M3", "field": "reusedBy", "to": ["M2"]}],
}

REGISTRY = {
    "version": "1",
    "models": {
        "M1": {"name": "对象模型", "modelType": "OBJECT", "camp": "business-core"},
        "M2": {"name": "行为模型", "modelType": "BEHAVIOR", "camp": "business-core"},
        "M3": {"name": "规则模型", "modelType": "RULE", "camp": "business-core"},
        "MU": {"name": "UI 模型", "modelType": "UI", "camp": "build-contract"},
        "GLS": {"name": "术语模型", "modelType": "GLOSSARY", "camp": "business-core"},
    },
}

M1 = """model_type: OBJECT
version: "1.0.0"
domain: demo
aggregates:
  - id: AGG-DEMO-001
    name: 对象甲
    alias: ObjAlpha
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: alphaOutput, label: 甲产量（吨）, type: Decimal }
  - id: AGG-DEMO-002
    name: 对象乙
    aggregateType: AGGREGATE_ROOT
"""

M2 = """model_type: BEHAVIOR
version: "1.0.0"
domain: demo
behaviors:
  - id: BH-DEMO-Do
    name: 处理对象甲
    ownerEntity: AGG-DEMO-001
    behaviorType: COMMAND
    appliedRules: [RULE-DEMO-001]
  - id: BH-DEMO-Do2
    name: 处理对象乙
    ownerEntity: AGG-DEMO-002
    behaviorType: QUERY
"""

M3 = """model_type: RULE
version: "1.0.0"
domain: demo
rules:
  - id: RULE-DEMO-001
    name: 对象甲值域校验
    ruleType: VALIDATION
    reusedBy: [BH-DEMO-Do]   # 镜像真域形态：规则登记复用方（依赖方向 appliedRules 反向可达）
  - id: RULE-DEMO-009
    name: 新口径
    ruleType: CALCULATION
    reusedBy: [BH-DEMO-Do2]
"""

MU = """model_type: UI
version: "1.0.0"
domain: demo
screens:
  - screenId: SCR-DEMO-01
    name: 对象甲管理屏
    screenType: LIST
    elements: []
    actions: []
"""

GLS = """model_type: GLOSSARY
version: "1.0.0"
domain: demo
terms:
  - id: GLS-DEMO-001
    term: 老口径
    aliases: []
    termType: 禁用词
    definition: v1 口径已废弃，替代口径=新口径。界面侧替代口径=对象甲管理屏。
    relatedObjectRefs: []
    status: 禁用（替代：新口径）
  - id: GLS-DEMO-002
    term: 术语丙
    aliases: [丙别称]
    termType: 术语
    definition: 对象乙的业务别名口径。
    relatedObjectRefs: [AGG-DEMO-002]
    status: 有效
"""


def make_domain(root: Path) -> Path:
    """建 <root>/schema + <root>/demo 迷你域，返回域目录。"""
    (root / "schema").mkdir(parents=True)
    (root / "schema" / "model-deps.json").write_text(
        json.dumps(DEPS, ensure_ascii=False), encoding="utf-8")
    (root / "schema" / "model-registry.json").write_text(
        json.dumps(REGISTRY, ensure_ascii=False), encoding="utf-8")
    demo = root / "demo"
    demo.mkdir()
    (demo / "manifest.json").write_text('{"domain": "demo"}', encoding="utf-8")
    for name, text in (("m1-object-model.yaml", M1), ("m2-behavior-model.yaml", M2),
                       ("m3-rule-model.yaml", M3), ("mu-ui-model.yaml", MU),
                       ("glossary-model.yaml", GLS)):
        (demo / name).write_text(text, encoding="utf-8")
    return demo


class DemoDomainCase(unittest.TestCase):
    """迷你域上的瀑布四步与三分支拒答。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.demo = make_domain(self.root)

    def verdict(self, question: str) -> tuple[int, dict]:
        return ask_json(self.root, question)

    # -- 一级显式锚定 --

    def test_anchor_in_surface_answered_with_behaviors(self):
        rc, v = self.verdict("@AGG-DEMO-001 有哪些行为")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        self.assertIn("显式锚定", v["waterfall_level"])
        self.assertEqual("AGG-DEMO-001", v["anchor"])
        hit_ids = [h["id"] for h in v["hits"]]
        self.assertIn("AGG-DEMO-001", hit_ids)
        self.assertIn("BH-DEMO-Do", hit_ids)          # 经 --impact 反向收集
        self.assertIn("BH-DEMO-Do", v["citations"])
        self.assertIn("RULE-DEMO-001", v["citations"])  # appliedRules 反向可达

    def test_anchor_out_of_surface_node_exists(self):
        """R1 原样场景：SCR 节点在图内真实存在，camp 裁剪拒答。"""
        rc, v = self.verdict("@SCR-DEMO-01 的界面细节")
        self.assertEqual(1, rc)
        self.assertEqual("refused_out_of_surface", v["status"])
        self.assertEqual("SCR-DEMO-01", v["anchor"])
        self.assertEqual("build-contract", v["camp"]["camp"])
        self.assertTrue(v["camp"]["anchor_exists"])
        self.assertEqual([], v["hits"])               # 不返回任何元素细节

    def test_anchor_out_of_surface_prefix_first(self):
        """面外判定先按前缀→模型→camp，节点不存在同样拒面外（票 22 顺序裁决）。"""
        rc, v = self.verdict("@SCR-DEMO-99 的页面长什么样")
        self.assertEqual(1, rc)
        self.assertEqual("refused_out_of_surface", v["status"])
        self.assertFalse(v["camp"]["anchor_exists"])

    def test_anchor_not_found_in_surface(self):
        """面内锚定失败 → R3 并入 R2 拒答（不猜拼写）。"""
        rc, v = self.verdict("@AGG-DEMO-999 的口径是什么")
        self.assertEqual(1, rc)
        self.assertEqual("refused_missing", v["status"])
        self.assertIn("未找到", v["reason"])

    # -- 禁用词（禁用词表自实现：读域内 GLS status 含「禁用」）--

    def test_banned_term_refused_with_replacement(self):
        rc, v = self.verdict("老口径还能用吗")
        self.assertEqual(1, rc)
        self.assertEqual("refused_banned", v["status"])
        self.assertEqual("GLS-DEMO-001", v["banned"]["id"])
        self.assertIn("RULE-DEMO-009", v["citations"])  # 替代口径真实 ID 指路
        self.assertIn("提案流程", v["reason"])

    # -- 四级 R2 仓内没有 --

    def test_missing_concept_refused_with_layers(self):
        rc, v = self.verdict("量子扰动成本的口径是什么")
        self.assertEqual(1, rc)
        self.assertEqual("refused_missing", v["status"])
        self.assertEqual([], v["hits"])
        blob = json.dumps(v, ensure_ascii=False)
        self.assertIn("未建", blob)
        self.assertIn("待 Owner", blob)
        self.assertIn("提案流程", blob)

    # -- 二级名称解析 + 三级闭包装配 --

    def test_name_resolution_unique_answered(self):
        rc, v = self.verdict("对象甲的口径是什么")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        # 承载（t1 全等）排候选首位；行为名「处理对象甲」是合法 t3 词面候选，
        # 多候选=ambiguous（列候选请锚定，core 不擅自合并——瀑布 §2 多义纪律）。
        self.assertEqual("AGG-DEMO-001", v["hits"][0]["id"])
        self.assertIn("AGG-DEMO-001", [h["id"] for h in v["hits"]])
        self.assertTrue(v["ambiguous"])
        self.assertIn("BH-DEMO-Do", v["citations"])
        self.assertTrue(any(c.startswith("python3 tools/graph_index.py")
                            for c in v["scaffold_commands"]))

    def test_gls_term_answered_with_related_pointers(self):
        rc, v = self.verdict("术语丙是什么口径")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        self.assertIn("GLS-DEMO-002", v["citations"])
        self.assertIn("AGG-DEMO-002", v["citations"])  # relatedObjectRefs 指路

    def test_gls_alias_resolution(self):
        rc, v = self.verdict("丙别称的口径是什么")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        self.assertIn("GLS-DEMO-002", [h["id"] for h in v["hits"]])

    # -- 票 25 R1：名称解析候选集 camp 裁剪（面外不进 hits/citations/装配指令） --

    def test_name_resolution_trims_out_of_surface_candidates(self):
        """R1（票 25）：MU 屏名即使 t1 全等也必须被裁——面外 ID 不进
        hits/citations/scaffold_commands，business-core 命中照常保留。"""
        rc, v = self.verdict("对象甲管理屏")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        ids = [h["id"] for h in v["hits"]]
        self.assertNotIn("SCR-DEMO-01", ids)
        self.assertNotIn("SCR-DEMO-01", v["citations"])
        self.assertNotIn("SCR-DEMO-01", " ".join(v["scaffold_commands"]))
        self.assertIn("AGG-DEMO-001", ids)   # 面内承载照常命中（t2）

    def test_banned_replacement_pointers_trim_out_of_surface(self):
        """R1（票 25）：禁用词替代指路的候选 ID 同样过 camp 裁剪——替代名
        恰为 MU 屏名时，指路集不得带出面外 ID，面内替代照常指路。"""
        rc, v = self.verdict("老口径还能用吗")
        self.assertEqual(1, rc)
        self.assertEqual("refused_banned", v["status"])
        self.assertNotIn("SCR-DEMO-01", v["citations"])
        self.assertIn("RULE-DEMO-009", v["citations"])   # 面内替代照常指路

    def test_anchor_path_unaffected_by_candidate_trimming(self):
        """票 25 回归：@锚定路径与候选裁剪共用同一 in_surface 判定后行为
        不变——面外拒答带阵营说明，面内锚定照常直达。"""
        rc, v = self.verdict("@SCR-DEMO-01 的界面细节")
        self.assertEqual(1, rc)
        self.assertEqual("refused_out_of_surface", v["status"])
        self.assertEqual("build-contract", v["camp"]["camp"])
        rc, v = self.verdict("@AGG-DEMO-001 有哪些行为")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        self.assertIn("显式锚定", v["waterfall_level"])

    # -- CLI/配置 --

    def test_config_error_without_schema(self):
        other = self.root / "noschema"
        other.mkdir()
        rc, _out, err = run_main([str(other), "--ask", "对象甲", "--json"])
        self.assertEqual(2, rc)
        self.assertIn("配置错误", err)

    def test_verdict_contract_fields(self):
        _rc, v = self.verdict("对象甲的口径是什么")
        for key in ("status", "waterfall_level", "anchor", "hits",
                    "citations", "scaffold_commands"):
            self.assertIn(key, v)
        for hit in v["hits"]:
            for key in ("id", "model", "name"):
                self.assertIn(key, hit)

    def test_human_output_is_brief(self):
        rc, out, _err = run_main([str(self.demo), "--ask", "对象甲的口径是什么"])
        self.assertEqual(0, rc)
        self.assertIn("answered", out)
        self.assertIn("AGG-DEMO-001", out)


@unittest.skipUnless(BOHAI.is_dir(), "真域 ontology/bohai 不在（仓外检具场景）")
class BohaiGoldenEight(unittest.TestCase):
    """八问真域回归（tickets/22 AC 表；Q1–Q6 基准=step3 走查，Q7/Q8=票 17）。"""

    def verdict(self, question: str) -> tuple[int, dict]:
        return ask_json(BOHAI, question)

    def assertCitations(self, v, *ids):
        for i in ids:
            self.assertIn(i, v["citations"], f"citations 缺 {i}")

    # Q1（AC1）
    def test_q1_daily_output_caliber(self):
        rc, v = self.verdict("日产量口径是什么？")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        self.assertCitations(v, "AGG-BOHAI-002", "RULE-BOHAI-002")

    # Q2（走查 Q2：月度结算）
    def test_q2_monthly_settlement(self):
        rc, v = self.verdict("月度结算的口径是什么？")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        self.assertIn("AGG-BOHAI-008", [h["id"] for h in v["hits"]])
        self.assertCitations(v, "BH-BOHAI-QueryMonthlySettlement", "QR-BOHAI-003")

    # Q3（AC2，走查 Q3）
    def test_q3_anchor_behaviors(self):
        rc, v = self.verdict("@AGG-BOHAI-001 有哪些行为？")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        self.assertIn("显式锚定", v["waterfall_level"])
        hit_ids = [h["id"] for h in v["hits"]]
        self.assertIn("AGG-BOHAI-001", hit_ids)
        self.assertTrue(any(h.startswith("BH-BOHAI-") for h in hit_ids),
                        f"hits 缺 BH-BOHAI-*: {hit_ids}")

    # Q4（AC3，走查 Q4）
    def test_q4_refused_missing(self):
        rc, v = self.verdict("桶油增产成本的口径是什么？")
        self.assertEqual(1, rc)
        self.assertEqual("refused_missing", v["status"])
        self.assertEqual([], v["hits"])
        blob = json.dumps(v, ensure_ascii=False)
        self.assertIn("未建", blob)
        self.assertIn("待 Owner", blob)

    # Q5（AC4，走查 Q5 替代形态；L0 期望 status=refused_out_of_surface）
    def test_q5_refused_out_of_surface(self):
        rc, v = self.verdict("@SCR-BOHAI-01 的界面细节")
        self.assertEqual(1, rc)
        self.assertEqual("refused_out_of_surface", v["status"])
        self.assertEqual("SCR-BOHAI-01", v["anchor"])
        self.assertEqual("build-contract", v["camp"]["camp"])

    # Q6（走查 Q6：有效产量两支并列）
    def test_q6_effective_output_candidates(self):
        rc, v = self.verdict("有效产量的口径是什么？")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        hit_ids = [h["id"] for h in v["hits"]]
        self.assertIn("GLS-BOHAI-003", hit_ids)
        self.assertIn("RULE-BOHAI-019", hit_ids)
        self.assertCitations(v, "QR-BOHAI-002")

    # Q7（票 17 AC1）
    def test_q7_term_caliber(self):
        rc, v = self.verdict("剔检产量是什么口径？")
        self.assertEqual(0, rc)
        self.assertEqual("answered", v["status"])
        self.assertIn("GLS-BOHAI-002", [h["id"] for h in v["hits"]])
        self.assertCitations(v, "AGG-BOHAI-001", "AGG-BOHAI-002", "RULE-BOHAI-019")

    # Q8（AC5，票 17 AC2）
    def test_q8_banned_term(self):
        rc, v = self.verdict("老完成率还能用吗？")
        self.assertEqual(1, rc)
        self.assertEqual("refused_banned", v["status"])
        self.assertEqual("GLS-BOHAI-001", v["banned"]["id"])
        self.assertCitations(v, "RULE-BOHAI-009", "QR-BOHAI-002")


if __name__ == "__main__":
    unittest.main()
