#!/usr/bin/env python3
"""app_pack_gen.py 的单测（stdlib unittest，TDD 先行；票 35）。

被测面：
  1. 确定性核心——零时间戳、两次生成字节一致（AC2 的单测面）；
  2. 内容契约——四节齐（数据字典/口径四件套/行为与规则清单/开放疑点）、
     人审状态头部、固定输入原样装配、口径卡 hitIds 装配
     （behaviorRef+objectRef+appliedRules+承载对象关联规则）、
     开放提案过滤（status=open 且 target.element 含本域前缀）；
  3. 声明模型集——缺 M1/M2/M3/M7 任一 → exit 2 不产残包（AC3 的单测面，
     modules.md 边界规则 5 生成器侧）；引用失效（behaviorRef 指空）→ exit 2；
     口径装配必备键缺失（QR 缺 behaviorRef 键）→ exit 2 干净报错不裸崩不产残包
     （票 39 件一）；
  4. CLI 三模式——stdout 缺省 / --out 双文件 / --check 逐字节比对（AC2 载体）；
  5. 渤海真域回归——四节齐 + 口径节与 CORE-01 冻结命中集同源（AC1 单测面）
     + 入库副本 --check 一致 + fixtures 负变体（剃 m3）exit 2
     + fixtures 负变体（剃 behaviorRef）exit 2 干净报错（票 39 件一 AC1）。

红相记录（TDD）：本文件先行落盘，app_pack_gen 未实现时收集即红。
"""

import io
import json
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import app_pack_gen as apg

REPO = Path(__file__).resolve().parent.parent
BOHAI = REPO / "ontology" / "bohai"
EXPORTS_DEVKIT = REPO / "exports" / "devkit" / "bohai"
NEGATIVE_VARIANT = REPO / "fixtures" / "app-pack-gen" / "negative-variants" / "bohai-no-m3"
NEGATIVE_NO_BEHAVIORREF = (REPO / "fixtures" / "app-pack-gen"
                           / "negative-variants" / "bohai-no-behaviorref")

# CORE-01 冻结期望集（fixtures/semantic-service 票 25 探针同源）：
# core 对 bohai「日产量口径是什么？」的命中 ID。
CORE01_HITS = ["AGG-BOHAI-002", "BH-BOHAI-QueryWellDailyOutput", "QR-BOHAI-001",
               "RULE-BOHAI-003", "RULE-BOHAI-004"]

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# ---------- 合成演示域（tempfile 注入；域词 demo，源标签 R9 仿注源纪律） ----------

M1 = """\
model_type: OBJECT
version: "1.0.0"
domain: demo
aggregates:
  # [R9·A.1 演示井档案] 井
  - id: AGG-DEMO-001
    name: 井
    alias: Well
    description: "演示井档案，一井一行。"
    aggregateType: AGGREGATE_ROOT
    lifecycle: [在产, 停产]
    attributes:
      - { name: wellId, label: 井号, type: String, unique: true }
      - { name: wellType, label: 井别, type: Enum, enumValues: [EW, IW] }
  # [R9·A.2 演示日计量] 计量
  - id: AGG-DEMO-002
    name: 日计量
    alias: DailyMetering
    description: "演示日计量，一井一日。"
    aggregateType: AGGREGATE_ROOT
    attributes:
      - name: wellRef
        label: 所属井
        type: AggregateRootRef
        targetAggregate: AGG-DEMO-001
      - name: output
        label: 产量
        type: Decimal
        refRules:
          - name: 产量值域
            expression: value >= 0
            violationMessage: 产量非负
            enforcedAt: ALWAYS
"""

M2 = """\
model_type: BEHAVIOR
version: "1.0.0"
domain: demo
behaviors:
  # [R9·§2 录入链路] 手工录入
  - id: BH-DEMO-Record
    name: 录入日计量
    ownerEntity: AGG-DEMO-002
    behaviorType: COMMAND
    triggerType: USER_ACTION
    appliedRules:
      - RULE-DEMO-002
      - RULE-DEMO-003
  # [R9·§3 查询出口] 查询行为
  - id: BH-DEMO-Query
    name: 查询日计量
    ownerEntity: AGG-DEMO-001
    behaviorType: QUERY
    triggerType: USER_ACTION
    appliedRules: []
"""

M3 = """\
model_type: RULE
version: "1.0.0"
domain: demo
rules:
  # [R9·§4 规则 1] 产量口径
  - id: RULE-DEMO-002
    name: 产量口径
    ruleType: CALCULATION
    description: "R9·§4 规则 1，产量口径定义。"
    outputType: Decimal
    expression: output * 100
    reusedBy:
      - BH-DEMO-Query
  # [R9·§4 规则 2] 值域校验
  - id: RULE-DEMO-003
    name: 产量非负校验
    ruleType: VALIDATION
    description: "R9·§4 规则 2，产量值域。"
    narrative: 产量须非负
"""

M7 = """\
model_type: REPORT
version: "1.0.0"
domain: demo
query_reports:
  # [R9·§3 指标 1] 日计量查询
  - id: QR-DEMO-001
    name: 日计量明细查询
    alias: dailyMeteringQuery
    description: "按井号查日计量明细。"
    objectType: DETAIL_QUERY
    behaviorRef: BH-DEMO-Query
    sourceObjects:
      - objectRef: AGG-DEMO-002
        alias: d
        primary: true
      - objectRef: AGG-DEMO-001
        alias: w
        primary: false
    parameters:
      - name: wellId
        label: 井号
        dataType: String
        required: true
        allowedOperators: [EQ]
    resultColumns:
      - name: wellId
        label: 井号
        dataType: String
        sourceExpression: w.wellId
"""

MODEL_FILES = {"M1": ("m1-object-model.yaml", M1),
               "M2": ("m2-behavior-model.yaml", M2),
               "M3": ("m3-rule-model.yaml", M3),
               "M7": ("m7-report-model.yaml", M7)}

TECH_CONSTRAINTS = "出厂集固定输入（合成）\n架构约束：服务端 Python/关系库/三层。\n"
DEV_GUIDE = "出厂集固定输入（合成）\n开发指导书：先数据字典后接口、口径以规则为准。\n"


def run_main(argv):
    """跑生成器 main，捕获 stdout+stderr，返回 (退出码, stdout, stderr)。"""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = apg.main(argv)
    return rc, out.getvalue(), err.getvalue()


def make_inputs(tmp: Path) -> Path:
    d = tmp / "inputs"
    d.mkdir(parents=True)
    (d / "tech-constraints.md").write_text(TECH_CONSTRAINTS, encoding="utf-8")
    (d / "dev-guide.md").write_text(DEV_GUIDE, encoding="utf-8")
    return d


def make_domain(tmp: Path, *, with_models=("M1", "M2", "M3", "M7"),
                domain="demo", label="演示域", model_type_override=None) -> Path:
    """搭合成域目录：manifest + 指定声明模型文件（with_models 之外不落盘）。"""
    dom = tmp / "onto" / domain
    dom.mkdir(parents=True)
    (dom / "manifest.json").write_text(
        json.dumps({"domain": domain, "label": label, "profile": "v9-core"},
                   ensure_ascii=False), encoding="utf-8")
    for mid in with_models:
        fname, text = MODEL_FILES[mid]
        if model_type_override and mid in model_type_override:
            text = text.replace(
                text.splitlines()[0], f"model_type: {model_type_override[mid]}", 1)
        (dom / fname).write_text(text, encoding="utf-8")
    return dom


def make_proposals(tmp: Path) -> Path:
    """合成提案池：open(本域)×2 / accepted(本域) / open(他域) 各 1。"""
    d = tmp / "proposals"
    d.mkdir(parents=True)
    (d / "PROP-DEMO-001.md").write_text(
        "---\nid: PROP-DEMO-001\ntitle: 新增演示规则\nstatus: open\n"
        "target:\n  model: M3\n  element: RULE-DEMO-099\nchange: add\n"
        'rationale: "演示。"\n---\n\n正文。\n', encoding="utf-8")
    (d / "PROP-DEMO-002.md").write_text(
        "---\nid: PROP-DEMO-002\ntitle: 已裁决提案\nstatus: accepted\n"
        "target:\n  model: M3\n  element: RULE-DEMO-002\nchange: modify\n"
        'rationale: "已裁决。"\n---\n\n正文。\n', encoding="utf-8")
    (d / "PROP-OTHER-003.md").write_text(
        "---\nid: PROP-OTHER-003\ntitle: 他域提案\nstatus: open\n"
        "target:\n  model: M3\n  element: RULE-OTHER-001\nchange: add\n"
        'rationale: "他域。"\n---\n\n正文。\n', encoding="utf-8")
    (d / "PROP-DEMO-004.md").write_text(
        "---\nid: PROP-DEMO-004\ntitle: 修改演示对象\nstatus: open\n"
        "target:\n  model: M1\n  element: AGG-DEMO-002\nchange: modify\n"
        'rationale: "演示。"\n---\n\n正文。\n', encoding="utf-8")
    return d


class DeterminismTest(unittest.TestCase):
    """确定性核心：幂等 + 零时间戳（AC2 单测面）。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.dom = make_domain(self.tmp)
        self.inputs = make_inputs(self.tmp)
        self.props = make_proposals(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def _argv(self, *extra):
        return [str(self.dom), "--inputs-dir", str(self.inputs),
                "--proposals-dir", str(self.props), *extra]

    def test_two_runs_stdout_identical(self):
        rc1, out1, _ = run_main(self._argv())
        rc2, out2, _ = run_main(self._argv())
        self.assertEqual((rc1, rc2), (0, 0))
        self.assertEqual(out1, out2)

    def test_two_out_files_byte_identical(self):
        a = self.tmp / "a" / "devkit.md"
        b = self.tmp / "b" / "devkit.md"
        run_main(self._argv("--out", str(a.parent)))
        run_main(self._argv("--out", str(b.parent)))
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual((a.parent / "devkit.json").read_bytes(),
                         (b.parent / "devkit.json").read_bytes())

    def test_zero_timestamp_no_time_like_tokens(self):
        _rc, md, _ = run_main(self._argv())
        js = json.dumps(apg.build_package(
            self.dom, inputs_dir=self.inputs, proposals_dir=self.props),
            ensure_ascii=False)
        for text, label in ((md, "MD"), (js, "JSON")):
            self.assertIsNone(DATE_RE.search(text),
                              f"{label} 不得含日期形态 token（零时间戳）")
            for forbidden in ("timestamp", "generatedAt", "generated_at",
                              "generated_on", "createdAt"):
                self.assertNotIn(forbidden, text)


class ContentContractTest(unittest.TestCase):
    """内容契约：四节齐 + 人审头部 + 固定输入 + 口径卡装配 + 提案过滤。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.dom = make_domain(self.tmp)
        self.inputs = make_inputs(self.tmp)
        self.props = make_proposals(self.tmp)
        self.pkg = apg.build_package(self.dom, inputs_dir=self.inputs,
                                     proposals_dir=self.props)
        self.md = apg.render_md(self.pkg)

    def tearDown(self):
        self._tmp.cleanup()

    def test_review_status_header(self):
        self.assertEqual(self.pkg["status"],
                         "待Owner人审（生成物禁手改，可再生）")
        self.assertIn("status: 待Owner人审（生成物禁手改，可再生）", self.md)

    def test_md_four_sections(self):
        for head in ("## 一、数据字典", "## 二、口径四件套", "## 三、行为与规则清单",
                     "## 四、开放疑点"):
            self.assertIn(head, self.md)

    def test_fixed_inputs_embedded_verbatim(self):
        self.assertEqual(self.pkg["fixedInputs"]["techConstraints"]["text"],
                         TECH_CONSTRAINTS)
        self.assertIn("架构约束：服务端 Python/关系库/三层。", self.md)
        self.assertIn("开发指导书：先数据字典后接口、口径以规则为准。", self.md)
        self.assertIn("出厂集固定输入（合成）", self.md)

    def test_data_dictionary_attributes_and_constraints(self):
        aggs = {a["id"]: a for a in self.pkg["dataDictionary"]["aggregates"]}
        self.assertEqual(set(aggs), {"AGG-DEMO-001", "AGG-DEMO-002"})
        attrs = {x["name"]: x for x in aggs["AGG-DEMO-001"]["attributes"]}
        self.assertEqual(attrs["wellId"]["constraints"], {"unique": True})
        self.assertEqual(attrs["wellType"]["constraints"],
                         {"enumValues": ["EW", "IW"]})
        ref = {x["name"]: x for x in aggs["AGG-DEMO-002"]["attributes"]}
        self.assertEqual(ref["wellRef"]["constraints"],
                         {"targetAggregate": "AGG-DEMO-001"})
        self.assertEqual(ref["output"]["constraints"]["refRules"][0]["expression"],
                         "value >= 0")
        self.assertEqual(aggs["AGG-DEMO-001"]["sourceNote"], "R9·A.1 演示井档案")
        self.assertEqual(len(self.pkg["dataDictionary"]["associations"]), 0)

    def test_caliber_card_hit_ids_assembly(self):
        cards = {c["id"]: c for c in self.pkg["calibers"]}
        self.assertEqual(set(cards), {"QR-DEMO-001"})
        card = cards["QR-DEMO-001"]
        self.assertEqual(card["questionSample"], "日计量明细查询")
        self.assertEqual(card["behavior"]["id"], "BH-DEMO-Query")
        self.assertEqual([s["objectRef"] for s in card["sourceObjects"]],
                         ["AGG-DEMO-002", "AGG-DEMO-001"])
        # 命中 ID = QR + behaviorRef + objectRefs + 关联规则（appliedRules /
        # reusedBy / 承载对象关联规则；去重保序）
        self.assertEqual(card["hitIds"],
                         ["QR-DEMO-001", "BH-DEMO-Query", "AGG-DEMO-002",
                          "AGG-DEMO-001", "RULE-DEMO-002", "RULE-DEMO-003"])
        rules = {r["id"]: r for r in card["rules"]}
        self.assertEqual(rules["RULE-DEMO-002"]["via"],
                         "reusedBy(BH-DEMO-Query)")
        self.assertEqual(rules["RULE-DEMO-003"]["via"],
                         "ownerObjectBehaviors(AGG-DEMO-002)")
        self.assertEqual(rules["RULE-DEMO-002"]["point"],
                         {"expression": "output * 100"})
        self.assertEqual(rules["RULE-DEMO-003"]["point"],
                         {"narrative": "产量须非负"})

    def test_behavior_rule_inventory_with_source_notes(self):
        inv = self.pkg["behaviorRuleInventory"]
        self.assertEqual([b["id"] for b in inv["behaviors"]],
                         ["BH-DEMO-Record", "BH-DEMO-Query"])
        self.assertEqual(inv["behaviors"][0]["sourceNote"], "R9·§2 录入链路")
        self.assertEqual([r["id"] for r in inv["rules"]],
                         ["RULE-DEMO-002", "RULE-DEMO-003"])
        self.assertEqual(inv["rules"][0]["sourceNote"], "R9·§4 规则 1")

    def test_open_proposals_filtered_by_status_and_domain_prefix(self):
        items = self.pkg["openProposals"]["items"]
        self.assertEqual([i["id"] for i in items],
                         ["PROP-DEMO-001", "PROP-DEMO-004"])

    def test_no_open_proposals_message(self):
        empty = self.tmp / "empty-pool"
        empty.mkdir()
        pkg = apg.build_package(self.dom, inputs_dir=self.inputs,
                                proposals_dir=empty)
        self.assertEqual(pkg["openProposals"]["items"], [])
        self.assertIn("无开放提案", apg.render_md(pkg))

    def test_no_proposals_switch_disables_section(self):
        pkg = apg.build_package(self.dom, inputs_dir=self.inputs,
                                include_proposals=False)
        self.assertFalse(pkg["openProposals"]["enabled"])
        md = apg.render_md(pkg)
        self.assertIn("未启用", md)


class DeclaredModelsTest(unittest.TestCase):
    """声明模型集：缺任一声明模型报错退出不硬编（AC3 单测面，边界规则 5）。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.inputs = make_inputs(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_m3_exit_2(self):
        dom = make_domain(self.tmp / "a", with_models=("M1", "M2", "M7"))
        rc, _out, err = run_main([str(dom), "--inputs-dir", str(self.inputs)])
        self.assertEqual(rc, 2)
        self.assertIn("缺声明模型", err)
        self.assertIn("M3", err)

    def test_missing_m1_exit_2(self):
        dom = make_domain(self.tmp / "b", with_models=("M2", "M3", "M7"))
        rc, _out, err = run_main([str(dom), "--inputs-dir", str(self.inputs)])
        self.assertEqual(rc, 2)
        self.assertIn("缺声明模型", err)
        self.assertIn("M1", err)

    def test_model_type_mismatch_exit_2(self):
        dom = make_domain(self.tmp / "c",
                          model_type_override={"M3": "BEHAVIOR"})
        rc, _out, err = run_main([str(dom), "--inputs-dir", str(self.inputs)])
        self.assertEqual(rc, 2)
        self.assertIn("model_type", err)

    def test_dangling_behavior_ref_exit_2(self):
        dom = make_domain(self.tmp / "d")
        m7 = dom / "m7-report-model.yaml"
        m7.write_text(M7.replace("behaviorRef: BH-DEMO-Query",
                                 "behaviorRef: BH-DEMO-Ghost"),
                      encoding="utf-8")
        rc, _out, err = run_main([str(dom), "--inputs-dir", str(self.inputs)])
        self.assertEqual(rc, 2)
        self.assertIn("BH-DEMO-Ghost", err)

    def test_missing_behavior_ref_key_exit_2_no_partial_output(self):
        """票 39 件一：M7 口径缺 behaviorRef 键 → 结构化 exit 2（不 KeyError 裸崩），
        stderr 定位元素 id + behaviorRef 字样 + schema_check 指路，--out 不产残包。"""
        dom = make_domain(self.tmp / "d2")
        m7 = dom / "m7-report-model.yaml"
        m7.write_text(M7.replace("    behaviorRef: BH-DEMO-Query\n", ""),
                      encoding="utf-8")
        outdir = self.tmp / "pkg-no-bref"
        rc, _out, err = run_main([str(dom), "--inputs-dir", str(self.inputs),
                                  "--out", str(outdir)])
        self.assertEqual(rc, 2)
        self.assertIn("QR-DEMO-001", err)
        self.assertIn("behaviorRef", err)
        self.assertIn("schema_check", err)
        self.assertNotIn("Traceback", err)
        self.assertFalse(outdir.exists() and any(outdir.iterdir()),
                         "配置错误不得产出残包文件")

    def test_missing_fixed_inputs_exit_2(self):
        dom = make_domain(self.tmp / "e")
        rc, _out, err = run_main(
            [str(dom), "--inputs-dir", str(self.tmp / "void")])
        self.assertEqual(rc, 2)
        self.assertIn("固定输入", err)


class CliModesTest(unittest.TestCase):
    """CLI 三模式：stdout / --out 双文件 / --check 逐字节比对（AC2 载体）。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.dom = make_domain(self.tmp)
        self.inputs = make_inputs(self.tmp)
        self.props = make_proposals(self.tmp)
        self.base = [str(self.dom), "--inputs-dir", str(self.inputs),
                     "--proposals-dir", str(self.props)]

    def tearDown(self):
        self._tmp.cleanup()

    def test_stdout_default_is_md(self):
        rc, out, _ = run_main(self.base)
        self.assertEqual(rc, 0)
        self.assertIn("## 一、数据字典", out)

    def test_out_writes_both_files_and_stdout_quiet(self):
        outdir = self.tmp / "pkg"
        rc, out, _ = run_main(self.base + ["--out", str(outdir)])
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")
        self.assertTrue((outdir / "devkit.md").is_file())
        self.assertTrue((outdir / "devkit.json").is_file())

    def test_check_mode_match_exit_0(self):
        outdir = self.tmp / "pkg"
        run_main(self.base + ["--out", str(outdir)])
        rc, out, _ = run_main(self.base + ["--check", str(outdir / "devkit.md")])
        self.assertEqual(rc, 0)
        self.assertIn("再制一致", out)

    def test_check_mode_stale_exit_1(self):
        outdir = self.tmp / "pkg"
        run_main(self.base + ["--out", str(outdir)])
        stale = json.loads((outdir / "devkit.json").read_text(encoding="utf-8"))
        stale["calibers"] = []
        (outdir / "devkit.json").write_text(
            json.dumps(stale, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        rc, out, _ = run_main(self.base + ["--check", str(outdir)])
        self.assertEqual(rc, 1)
        self.assertIn("不一致", out)

    def test_check_mode_missing_copy_exit_1(self):
        rc, out, _ = run_main(
            self.base + ["--check", str(self.tmp / "nope" / "devkit.md")])
        self.assertEqual(rc, 1)
        self.assertIn("不存在", out)

    def test_non_domain_target_exit_2(self):
        rc, _out, err = run_main([str(self.tmp / "void"),
                                  "--inputs-dir", str(self.inputs)])
        self.assertEqual(rc, 2)
        self.assertIn("域目录", err)


@unittest.skipUnless(BOHAI.is_dir(), "真域缺失（跳过真域回归）")
class BohaiRealDomainTest(unittest.TestCase):
    """渤海真域回归：四节齐 + 口径节与 CORE-01 同源 + 入库副本 --check +
    fixtures 剃 m3 负变体（AC1/AC3/AC4 的真域实证）。"""

    def test_four_sections_and_status_header(self):
        rc, md, _ = run_main(["ontology/bohai"])
        self.assertEqual(rc, 0)
        self.assertIn("status: 待Owner人审（生成物禁手改，可再生）", md)
        for head in ("## 一、数据字典", "## 二、口径四件套", "## 三、行为与规则清单",
                     "## 四、开放疑点"):
            self.assertIn(head, md)

    def test_caliber_section_same_source_with_core01(self):
        """AC1：CORE-01 冻结命中集 ⊆ 口径节对应卡片（QR-BOHAI-001）hitIds。"""
        pkg = apg.build_package(REPO / "ontology" / "bohai")
        card = next(c for c in pkg["calibers"] if c["id"] == "QR-BOHAI-001")
        missing = [i for i in CORE01_HITS if i not in card["hitIds"]]
        self.assertEqual(missing, [],
                         f"口径卡缺 CORE-01 命中 ID: {missing}")

    def test_exports_copy_regenerates_identical(self):
        self.assertTrue((EXPORTS_DEVKIT / "devkit.md").is_file(),
                        "exports/devkit/bohai/devkit.md 未落盘")
        self.assertTrue((EXPORTS_DEVKIT / "devkit.json").is_file())
        rc, out, err = run_main(
            ["ontology/bohai", "--check", str(EXPORTS_DEVKIT / "devkit.md")])
        self.assertEqual(rc, 0, f"入库副本陈旧: {out}{err}")

    def test_negative_variant_missing_m3_exit_2(self):
        self.assertTrue(NEGATIVE_VARIANT.is_dir(),
                        "fixtures 负变体（剃 m3 域副本）未落盘")
        rc, _out, err = run_main([str(NEGATIVE_VARIANT)])
        self.assertEqual(rc, 2)
        self.assertIn("缺声明模型", err)
        self.assertIn("M3", err)

    def test_negative_variant_missing_behavior_ref_exit_2(self):
        """票 39 件一 AC1：剃 behaviorRef 域副本 → exit 2 干净报错：
        stderr 定位元素 id + behaviorRef 字样，无 traceback，不产残包文件。"""
        self.assertTrue(NEGATIVE_NO_BEHAVIORREF.is_dir(),
                        "fixtures 负变体（剃 behaviorRef 域副本）未落盘")
        with tempfile.TemporaryDirectory() as td:
            outdir = Path(td) / "out"
            rc, _out, err = run_main([str(NEGATIVE_NO_BEHAVIORREF),
                                      "--out", str(outdir)])
        self.assertEqual(rc, 2)
        self.assertIn("QR-BOHAI-001", err)
        self.assertIn("behaviorRef", err)
        self.assertNotIn("Traceback", err)
        self.assertFalse(outdir.exists() and any(outdir.iterdir()),
                         "配置错误不得产出残包文件")


if __name__ == "__main__":
    unittest.main()
