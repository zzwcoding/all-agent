#!/usr/bin/env python3
"""skill_pack_gen.py 的单测（stdlib unittest，TDD 先行；票 36）。

被测面：
  1. 切片声明纪律——--models 显式子集：未知模型/含 build-contract 阵营模型
     （MU，检索面纪律生成器侧延伸）/域缺声明模型文件/model_type 不符 → exit 2
     不产残包（AC3 的单测面，modules.md 边界规则 5 同款）；
  2. 口径卡装配纪律——M7 在切片而 M1/M2/M3 缺伴 → exit 2（口径卡命中集须与
     CORE 同源，不产残卡）；M7 未声明 → 如实注记无口径卡（L0 示例切片可出包）；
  3. 三件套内容契约——frontmatter（name/slice-models/citation-prefixes/人审状态）、
     工序路由四步静态化（票 39 件二起自 core WATERFALL_STEPS 真源常量渲染：
     import 同一性+渲染含常量全部步骤名+常量自身契约四步钉死）、口径问答卡
     hitIds 装配（behaviorRef+objectRef+appliedRules+承载对象关联规则，同票 35
     口径节装配来源）、引用纪律（camp 面外/切片外/禁用词/可拒答声明）、GLS 术语面；
     口径装配必备键缺失（QR 缺 behaviorRef 键）→ exit 2 不裸崩（票 39 件一同款）；
  4. 确定性核心——零时间戳、两次生成字节一致（AC2 的单测面）；
  5. CLI 三模式——stdout 缺省 / --out 双文件 / --check 逐字节比对（AC2 载体）；
  6. 渤海真域回归——三件套齐 + 口径卡与 CORE-01 冻结命中集同源（AC1 单测面）
     + 入库副本 --check 一致 + fixtures 负变体（剃 m3）exit 2 + 真域 camp 负变体
     （M1,MU）exit 2。

红相记录（TDD）：本文件先行落盘，skill_pack_gen 未实现时收集即红。
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

import skill_pack_gen as spg

REPO = Path(__file__).resolve().parent.parent
BOHAI = REPO / "ontology" / "bohai"
SCHEMA_DIR = REPO / "ontology" / "schema"
EXPORTS_SKILLPKG = REPO / "exports" / "skillpkg" / "bohai"
NEGATIVE_NO_M3 = (REPO / "fixtures" / "skill-pack-gen"
                  / "negative-variants" / "bohai-no-m3")

# 金包切片声明：M1/M2/M3/M7 + GLS——恰=语义服务检索引用面（CITATION_MODEL_TYPES：
# OBJECT/BEHAVIOR/RULE/REPORT/GLOSSARY 五型）。口径问答卡装配来源同票 35 口径节
# （M7×M2×M3×M1），CORE 命中含 QR/BH，故正例切片必须含 M7/M2（AC 表期望列）。
GOLDEN_MODELS = ["M1", "M2", "M3", "M7", "GLS"]

# CORE-01 冻结期望集（fixtures/semantic-service 探针同源）：
# core 对 bohai「日产量口径是什么？」的命中 ID。
CORE01_HITS = ["AGG-BOHAI-002", "BH-BOHAI-QueryWellDailyOutput", "QR-BOHAI-001",
               "RULE-BOHAI-003", "RULE-BOHAI-004"]

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

SECTION_HEADS = ("## 一、工序路由（问答四步·静态化）",
                 "## 二、口径问答卡（M7 逐口径·与语义服务 CORE 同源）",
                 "## 三、引用纪律与拒答边界")

# ---------- 合成演示域（tempfile 注入；域词 demo，schema 用仓内真注册表） ----------

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

GLS = """\
model_type: GLOSSARY
version: "1.0.0"
domain: demo
terms:
  - id: GLS-DEMO-001
    term: 旧产量
    aliases: [老产量]
    termType: 禁用词
    definition: 旧口径已废弃，替代口径=日计量产量。
    relatedObjectRefs: [AGG-DEMO-002]
    status: 禁用（替代：日计量产量）
  - id: GLS-DEMO-002
    term: 计量
    aliases: []
    termType: 简称
    definition: 日计量的简称。
    relatedObjectRefs: [AGG-DEMO-002]
    status: 有效
"""

MODEL_FILES = {"M1": ("m1-object-model.yaml", M1),
               "M2": ("m2-behavior-model.yaml", M2),
               "M3": ("m3-rule-model.yaml", M3),
               "M7": ("m7-report-model.yaml", M7),
               "GLS": ("glossary-model.yaml", GLS)}


def run_main(argv):
    """跑生成器 main，捕获 stdout+stderr（argparse 用法错 SystemExit 也接住）。"""
    out, err = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(out), redirect_stderr(err):
            rc = spg.main(argv)
    except SystemExit as exc:  # argparse 用法错误（如缺 --models）退出码 2
        rc = exc.code
    return rc, out.getvalue(), err.getvalue()


def make_domain(tmp: Path, *, with_models=("M1", "M2", "M3", "M7", "GLS"),
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


class SliceDeclarationTest(unittest.TestCase):
    """切片声明纪律：未知模型/camp 面外/缺文件/model_type 不符 → exit 2（AC3）。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _argv(self, dom, models):
        return [str(dom), "--models", models, "--schema-dir", str(SCHEMA_DIR)]

    def test_build_contract_model_exit_2(self):
        """--models M1,MU：camp=build-contract → 面外报错（检索面纪律生成器侧）。"""
        dom = make_domain(self.tmp / "a")
        rc, _out, err = run_main(self._argv(dom, "M1,MU"))
        self.assertEqual(rc, 2)
        self.assertIn("非 business-core 阵营", err)
        self.assertIn("MU", err)
        self.assertIn("build-contract", err)

    def test_unknown_model_exit_2(self):
        dom = make_domain(self.tmp / "b")
        rc, _out, err = run_main(self._argv(dom, "M1,M9"))
        self.assertEqual(rc, 2)
        self.assertIn("未知声明模型", err)
        self.assertIn("M9", err)

    def test_missing_declared_file_exit_2(self):
        dom = make_domain(self.tmp / "c", with_models=("M1", "M2", "M7", "GLS"))
        rc, _out, err = run_main(self._argv(dom, "M1,M2,M3,M7,GLS"))
        self.assertEqual(rc, 2)
        self.assertIn("缺声明模型", err)
        self.assertIn("M3", err)

    def test_model_type_mismatch_exit_2(self):
        dom = make_domain(self.tmp / "d",
                          model_type_override={"GLS": "OBJECT"})
        rc, _out, err = run_main(self._argv(dom, "M1,M2,M3,M7,GLS"))
        self.assertEqual(rc, 2)
        self.assertIn("model_type", err)

    def test_missing_models_arg_exit_2(self):
        dom = make_domain(self.tmp / "e")
        rc, _out, err = run_main([str(dom), "--schema-dir", str(SCHEMA_DIR)])
        self.assertEqual(rc, 2)

    def test_empty_models_arg_exit_2(self):
        dom = make_domain(self.tmp / "f")
        rc, _out, err = run_main(self._argv(dom, " , "))
        self.assertEqual(rc, 2)
        self.assertIn("切片声明", err)

    def test_duplicate_models_deduped(self):
        dom = make_domain(self.tmp / "g")
        rc, _out, _err = run_main(self._argv(dom, "M1,M3,GLS,M1"))
        self.assertEqual(rc, 0)

    def test_camp_check_precedes_file_check(self):
        """camp 判定在先（先阵营后存在性，同 core 瀑布）：无 MU 文件也报阵营。"""
        dom = make_domain(self.tmp / "h")
        rc, _out, err = run_main(self._argv(dom, "MU"))
        self.assertEqual(rc, 2)
        self.assertIn("非 business-core 阵营", err)
        self.assertNotIn("缺声明模型", err)


class CaliberQuartetTest(unittest.TestCase):
    """口径卡装配纪律：M7 在场须四模型齐备；M7 缺席如实注记（L0 示例可出包）。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _argv(self, dom, models):
        return [str(dom), "--models", models, "--schema-dir", str(SCHEMA_DIR)]

    def test_m7_without_partners_exit_2(self):
        dom = make_domain(self.tmp / "a", with_models=("M1", "M7"))
        rc, _out, err = run_main(self._argv(dom, "M1,M7"))
        self.assertEqual(rc, 2)
        self.assertIn("口径问答卡装配缺声明模型", err)
        self.assertIn("M2", err)

    def test_l0_example_slice_without_m7_exits_0_with_note(self):
        """L0 设计裁决示例切片 M1,M3,GLS：可出包，口径卡节如实注记无卡。"""
        dom = make_domain(self.tmp / "b")
        rc, out, _err = run_main(self._argv(dom, "M1,M3,GLS"))
        self.assertEqual(rc, 0)
        for head in SECTION_HEADS:
            self.assertIn(head, out)
        self.assertIn("未声明 M7", out)
        self.assertNotIn("### 口径", out)

    def test_missing_behavior_ref_key_exit_2(self):
        """票 39 件一（同款装配链）：M7 口径缺 behaviorRef 键 → 结构化 exit 2
        （不 KeyError 裸崩），stderr 定位元素 id + behaviorRef 字样。"""
        dom = make_domain(self.tmp / "c2")
        (dom / "m7-report-model.yaml").write_text(
            M7.replace("    behaviorRef: BH-DEMO-Query\n", ""), encoding="utf-8")
        rc, _out, err = run_main(self._argv(dom, ",".join(GOLDEN_MODELS)))
        self.assertEqual(rc, 2)
        self.assertIn("QR-DEMO-001", err)
        self.assertIn("behaviorRef", err)
        self.assertIn("schema_check", err)
        self.assertNotIn("Traceback", err)


class DeterminismTest(unittest.TestCase):
    """确定性核心：幂等 + 零时间戳（AC2 单测面）。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.dom = make_domain(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def _argv(self, *extra):
        return [str(self.dom), "--models", ",".join(GOLDEN_MODELS),
                "--schema-dir", str(SCHEMA_DIR), *extra]

    def test_two_runs_stdout_identical(self):
        rc1, out1, _ = run_main(self._argv())
        rc2, out2, _ = run_main(self._argv())
        self.assertEqual((rc1, rc2), (0, 0))
        self.assertEqual(out1, out2)

    def test_two_out_files_byte_identical(self):
        a = self.tmp / "a"
        b = self.tmp / "b"
        run_main(self._argv("--out", str(a)))
        run_main(self._argv("--out", str(b)))
        self.assertEqual((a / "SKILL.md").read_bytes(),
                         (b / "SKILL.md").read_bytes())
        self.assertEqual((a / "skillpack.json").read_bytes(),
                         (b / "skillpack.json").read_bytes())

    def test_zero_timestamp_no_time_like_tokens(self):
        _rc, md, _ = run_main(self._argv())
        js = json.dumps(spg.build_package(
            self.dom, GOLDEN_MODELS, schema_dir=SCHEMA_DIR), ensure_ascii=False)
        for text, label in ((md, "MD"), (js, "JSON")):
            self.assertIsNone(DATE_RE.search(text),
                              f"{label} 不得含日期形态 token（零时间戳）")
            for forbidden in ("timestamp", "generatedAt", "generated_at",
                              "generated_on", "createdAt"):
                self.assertNotIn(forbidden, text)


class ContentContractTest(unittest.TestCase):
    """三件套内容契约：frontmatter/路由四步/口径卡/引用纪律/GLS 术语面。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.dom = make_domain(self.tmp)
        self.pkg = spg.build_package(self.dom, GOLDEN_MODELS,
                                     schema_dir=SCHEMA_DIR)
        self.md = spg.render_md(self.pkg)

    def tearDown(self):
        self._tmp.cleanup()

    def test_review_status_header(self):
        self.assertEqual(self.pkg["status"],
                         "待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）")
        self.assertIn("status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）", self.md)

    def test_md_three_sections_and_frontmatter(self):
        self.assertTrue(self.md.startswith("---\n"), "SKILL.md 须以 frontmatter 开头")
        for head in SECTION_HEADS:
            self.assertIn(head, self.md)

    def test_frontmatter_fields(self):
        self.assertIn("name: demo-semantic", self.md)
        self.assertIn("slice-models: " + json.dumps(GOLDEN_MODELS), self.md)
        prefixes = self.pkg["slice"]["citationPrefixes"]
        self.assertEqual(prefixes, ["AGG-", "ASSOC-", "DICT-", "BH-", "RULE-",
                                    "QR-", "RPT-", "GLS-"])
        self.assertIn("citation-prefixes: " + json.dumps(prefixes), self.md)

    def test_routing_four_steps(self):
        steps = self.pkg["routing"]["steps"]
        self.assertEqual([s["name"] for s in steps],
                         ["显式锚定", "名称解析", "闭包装配", "可拒答"])
        self.assertIn("① 显式锚定", self.md)
        self.assertIn("④ 可拒答", self.md)

    def test_routing_steps_single_source_with_core_constant(self):
        """票 39 件二：工序路由四步 = core WATERFALL_STEPS 单一真源——
        渲染输出包含常量全部步骤名与纪律句；改常量→本测试与黄金包 --check
        抓工序/发布物同步。"""
        import semantic_service_core as ssc
        self.assertIs(spg.WATERFALL_STEPS, ssc.WATERFALL_STEPS,
                      "skill_pack_gen 须 import core WATERFALL_STEPS 消费，"
                      "不得自有静态副本")
        self.assertFalse(hasattr(spg, "ROUTING_STEPS"),
                         "自有静态四步文本须删除（票 39 件二）")
        # 常量自身契约：四步 (编号,名称,一句话)，与 core answer() 工序一一对应
        steps_const = ssc.WATERFALL_STEPS
        self.assertEqual(len(steps_const), 4, "四步瀑布：常量须恰四步")
        self.assertEqual([num for num, _n, _t in steps_const],
                         ["①", "②", "③", "④"])
        self.assertTrue(all(text.strip() for _num, _n, text in steps_const),
                        "每步须带一句话纪律")
        steps = self.pkg["routing"]["steps"]
        self.assertEqual([(s["step"], s["name"], s["discipline"])
                          for s in steps],
                         [(num, name, text) for num, name, text
                          in steps_const])
        for num, name, text in steps_const:
            self.assertIn(f"{num} {name}:", self.md)
            self.assertIn(text, spg.render_json(self.pkg))

    def test_caliber_card_hit_ids_assembly(self):
        """口径卡同票 35 装配来源：hitIds=QR+behaviorRef+objectRefs+关联规则。"""
        cards = {c["id"]: c for c in self.pkg["calibers"]}
        self.assertEqual(set(cards), {"QR-DEMO-001"})
        card = cards["QR-DEMO-001"]
        self.assertEqual(card["questionSample"], "日计量明细查询")
        self.assertEqual(card["behavior"]["id"], "BH-DEMO-Query")
        self.assertEqual([s["objectRef"] for s in card["sourceObjects"]],
                         ["AGG-DEMO-002", "AGG-DEMO-001"])
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
        self.assertIn("命中 ID 集: " + " ".join(card["hitIds"]), self.md)

    def test_citation_discipline_out_of_surface_and_outside_slice(self):
        cd = self.pkg["citationDiscipline"]
        self.assertEqual(cd["outOfSurface"],
                         [{"prefixes": ["SCR-"], "model": "MU",
                           "name": "UI 模型", "camp": "build-contract"}])
        self.assertEqual([x["model"] for x in cd["outsideSlice"]], ["M5", "M6"])
        self.assertIn("SCR-（MU UI 模型，camp=build-contract）", self.md)
        self.assertIn("切片外", self.md)
        self.assertIn("ACTOR-/ROLE-/PERM-（M5 主体模型", self.md)

    def test_glossary_terms_and_banned(self):
        self.assertTrue(self.pkg["glossary"]["declared"])
        banned = self.pkg["glossary"]["bannedTerms"]
        self.assertEqual([t["id"] for t in banned], ["GLS-DEMO-001"])
        self.assertEqual(banned[0]["term"], "旧产量")
        self.assertIn("禁用词: 旧产量（GLS-DEMO-001", self.md)
        self.assertEqual(len(self.pkg["glossary"]["terms"]), 2)

    def test_refusal_declaration_in_md(self):
        self.assertIn("可拒答声明", self.md)
        self.assertIn("提案流程", self.md)

    def test_dangling_gls_related_ref_exit_2(self):
        dom = make_domain(self.tmp / "glsbad")
        gls = dom / "glossary-model.yaml"
        gls.write_text(GLS.replace("relatedObjectRefs: [AGG-DEMO-002]\n    status: 禁用",
                                   "relatedObjectRefs: [AGG-DEMO-999]\n    status: 禁用"),
                       encoding="utf-8")
        with self.assertRaises(spg.ConfigError) as ctx:
            spg.build_package(dom, GOLDEN_MODELS, schema_dir=SCHEMA_DIR)
        self.assertIn("AGG-DEMO-999", str(ctx.exception))


class CliModesTest(unittest.TestCase):
    """CLI 三模式：stdout / --out 双文件 / --check 逐字节比对（AC2 载体）。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.dom = make_domain(self.tmp)
        self.base = [str(self.dom), "--models", ",".join(GOLDEN_MODELS),
                     "--schema-dir", str(SCHEMA_DIR)]

    def tearDown(self):
        self._tmp.cleanup()

    def test_stdout_default_is_md(self):
        rc, out, _ = run_main(self.base)
        self.assertEqual(rc, 0)
        self.assertIn("## 一、工序路由（问答四步·静态化）", out)

    def test_out_writes_both_files_and_stdout_quiet(self):
        outdir = self.tmp / "pkg"
        rc, out, _ = run_main(self.base + ["--out", str(outdir)])
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")
        self.assertTrue((outdir / "SKILL.md").is_file())
        self.assertTrue((outdir / "skillpack.json").is_file())

    def test_check_mode_match_exit_0(self):
        outdir = self.tmp / "pkg"
        run_main(self.base + ["--out", str(outdir)])
        rc, out, _ = run_main(self.base + ["--check", str(outdir / "SKILL.md")])
        self.assertEqual(rc, 0)
        self.assertIn("再制一致", out)

    def test_check_mode_stale_exit_1(self):
        outdir = self.tmp / "pkg"
        run_main(self.base + ["--out", str(outdir)])
        stale = json.loads((outdir / "skillpack.json").read_text(encoding="utf-8"))
        stale["calibers"] = []
        (outdir / "skillpack.json").write_text(
            json.dumps(stale, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        rc, out, _ = run_main(self.base + ["--check", str(outdir)])
        self.assertEqual(rc, 1)
        self.assertIn("不一致", out)

    def test_check_mode_missing_copy_exit_1(self):
        rc, out, _ = run_main(
            self.base + ["--check", str(self.tmp / "nope" / "SKILL.md")])
        self.assertEqual(rc, 1)
        self.assertIn("不存在", out)

    def test_non_domain_target_exit_2(self):
        rc, _out, err = run_main([str(self.tmp / "void"), "--models",
                                  ",".join(GOLDEN_MODELS),
                                  "--schema-dir", str(SCHEMA_DIR)])
        self.assertEqual(rc, 2)
        self.assertIn("域目录", err)

    def test_missing_schema_dir_exit_2(self):
        rc, _out, err = run_main([str(self.dom), "--models",
                                  ",".join(GOLDEN_MODELS)])
        self.assertEqual(rc, 2)
        self.assertIn("schema", err)


@unittest.skipUnless(BOHAI.is_dir(), "真域缺失（跳过真域回归）")
class BohaiRealDomainTest(unittest.TestCase):
    """渤海真域回归：三件套齐 + 口径卡与 CORE-01 同源 + 入库副本 --check +
    fixtures 剃 m3 负变体 + camp 负变体（AC1/AC3/AC4 的真域实证）。"""

    def test_three_sections_and_status_header(self):
        rc, md, _ = run_main(["ontology/bohai", "--models",
                              ",".join(GOLDEN_MODELS)])
        self.assertEqual(rc, 0)
        self.assertIn("status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）", md)
        for head in SECTION_HEADS:
            self.assertIn(head, md)

    def test_caliber_section_same_source_with_core01(self):
        """AC1：CORE-01 冻结命中集 ⊆ 口径卡（QR-BOHAI-001）hitIds。"""
        pkg = spg.build_package(BOHAI, GOLDEN_MODELS)
        card = next(c for c in pkg["calibers"] if c["id"] == "QR-BOHAI-001")
        missing = [i for i in CORE01_HITS if i not in card["hitIds"]]
        self.assertEqual(missing, [],
                         f"口径卡缺 CORE-01 命中 ID: {missing}")

    def test_bohai_banned_term_surface(self):
        pkg = spg.build_package(BOHAI, GOLDEN_MODELS)
        banned = {t["id"]: t for t in pkg["glossary"]["bannedTerms"]}
        self.assertIn("GLS-BOHAI-001", banned)
        self.assertEqual(banned["GLS-BOHAI-001"]["term"], "老完成率")

    def test_exports_copy_regenerates_identical(self):
        self.assertTrue((EXPORTS_SKILLPKG / "SKILL.md").is_file(),
                        "exports/skillpkg/bohai/SKILL.md 未落盘")
        self.assertTrue((EXPORTS_SKILLPKG / "skillpack.json").is_file())
        rc, out, err = run_main(
            ["ontology/bohai", "--models", ",".join(GOLDEN_MODELS),
             "--check", str(EXPORTS_SKILLPKG / "SKILL.md")])
        self.assertEqual(rc, 0, f"入库副本陈旧: {out}{err}")

    def test_negative_variant_missing_m3_exit_2(self):
        self.assertTrue(NEGATIVE_NO_M3.is_dir(),
                        "fixtures 负变体（剃 m3 域副本）未落盘")
        rc, _out, err = run_main([str(NEGATIVE_NO_M3), "--models",
                                  ",".join(GOLDEN_MODELS),
                                  "--schema-dir", str(SCHEMA_DIR)])
        self.assertEqual(rc, 2)
        self.assertIn("缺声明模型", err)
        self.assertIn("M3", err)

    def test_camp_negative_variant_on_real_domain_exit_2(self):
        rc, _out, err = run_main(["ontology/bohai", "--models", "M1,MU"])
        self.assertEqual(rc, 2)
        self.assertIn("非 business-core 阵营", err)
        self.assertIn("MU", err)


if __name__ == "__main__":
    unittest.main()
