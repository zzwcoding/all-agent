#!/usr/bin/env python3
"""meta_probe.py 的单测（票 28 建：元循环探针；票 29 增第 10 项与豁免复核并入）。

TDD 面全部注入式（票面红线：collectors 用 tempfile 造 root + 假 runner 注入），
对真仓一条集成冒烟（skipUnless 真仓在位——本仓开发即真仓，实跑）。
覆盖：十项全绿 exit 0 / 硬闸红灯路径（出厂集 fail、语义闸 L1、安装位漂移、
skill 无卡、路由表坏表/坏 JSON/缺类/坏 commit/坏 PROP）→ exit 1 /
工具缺席与坏输出 → SKIPPED 降级不崩（AC4）/ 信息项红不判死（CORE 期望漂移、
提案冲突、豁免行缺理由）/ 豁免复核结论并入（--review 与缺省
docs/meta/exemption-reviews.json 两条路，无结论=留空栏，坏结论文件=注记不判死）/
--out 双落盘 / 用法错误 exit 2 / 真仓冒烟（硬闸 5/5 全绿 + CORE 八问分布钉死）。
"""

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import meta_probe as mp

REAL_ROOT = Path(__file__).resolve().parent.parent


# ---------- 注入基座：假仓 + 假 runner ----------

class FakeRepo:
    """tempfile 假仓：文件面四项（豁免×2、卡同步、提案池）的注入基座。"""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "specs").mkdir()
        (self.root / "skills").mkdir()
        (self.root / "docs" / "proposals").mkdir(parents=True)
        (self.root / "ontology" / "bohai").mkdir(parents=True)
        self.add_routing_table()  # 缺省绿路由表（票 29 第 10 项；坏表场景各自覆写）

    def cleanup(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def add_cards(self, names):
        self.write("specs/modules.md", "".join(
            f"# modules.md\n\n## skill: {n}\n\n- 职责: {n}的职责\n" for n in names))

    def add_skill(self, name):
        (self.root / "skills" / name).mkdir()
        (self.root / "skills" / name / "SKILL.md").write_text("# s\n", encoding="utf-8")

    def add_prop(self, name, status):
        self.write(f"docs/proposals/PROP-X-{name}.md",
                   f"---\nid: PROP-X-{name}\ntitle: t\nstatus: {status}\n"
                   f"source-signal:\n  kind: k\n  ref: r\ntarget:\n  model: M\n"
                   f"  element: E\nchange: add\nrationale: r\n---\n\n正文\n")

    def add_routing_table(self, table=None):
        """合法路由表 + 表内引用的 PROP 文件（默认绿表；坏表场景传 table 覆写）。"""
        self.write("policies/signal-routing.json",
                   json.dumps(table or TEST_ROUTING, ensure_ascii=False,
                              indent=2))
        for pid in ("PROP-BOHAI-005", "PROP-BOHAI-006", "PROP-BOHAI-031"):
            self.write(f"docs/proposals/{pid}.md",
                       f"---\nid: {pid}\ntitle: t\nstatus: open\n---\n\n正文\n")

    def drop_routing_table(self):
        (self.root / "policies" / "signal-routing.json").unlink()


# 测试用绿路由表：三类齐、每类 2 条实例（commit 由假 git 一律验存；PROP 文件由
# add_routing_table 落盘）——只测探针的判定逻辑，不测真表内容（真表由真仓冒烟管）。
TEST_ROUTING = {
    "version": 1,
    "routes": [
        {"kind": "业务错", "destination": "本体 MR（人审）", "mechanism": "提案池→人 merge",
         "instances": [
             {"desc": "落池", "ticket": "19", "commit": "aaaa111",
              "props": ["PROP-BOHAI-006", "PROP-BOHAI-031"]},
             {"desc": "回填", "ticket": "17", "commit": "bbbb222",
              "props": ["PROP-BOHAI-005"]}]},
        {"kind": "工程错", "destination": "tickets/ 票", "mechanism": "一票一提交",
         "instances": [
             {"desc": "图索引", "ticket": "04", "commit": "cccc333"},
             {"desc": "camp 裁剪", "ticket": "25", "commit": "dddd444"}]},
        {"kind": "元模型错", "destination": "schema 演进票", "mechanism": "CHANGELOG+版本号",
         "instances": [
             {"desc": "GLS", "ticket": "10", "commit": "eeee555"},
             {"desc": "缺 id", "ticket": "27", "commit": "ffff666"}]},
    ],
}


def fx_json(status="pass", suites=(("alpha", "pass"), ("beta", "pass"))):
    return json.dumps({"status": status, "fixturesDir": "fixtures",
                       "fixtures": [{"name": n, "status": s, "results": [],
                                     "error": None} for n, s in suites]})


SC_GREEN = json.dumps({"status": "pass", "levels": {"L1": 0, "L2": 0, "L4": 0},
                       "violations": []})
SC_RED = json.dumps({"status": "fail", "levels": {"L1": 2, "L2": 0, "L4": 1},
                     "violations": [{"level": "L1", "kind": "x", "file": "f",
                                     "line": 1, "message": "m"}]})
IS_GREEN = json.dumps({"mode": "check", "src": "s", "dst": "d",
                       "skills": ["a-skill", "b-skill"],
                       "diffs": [], "consistent": ["a-skill", "b-skill"],
                       "orphans": []})
IS_RED = json.dumps({"mode": "check", "src": "s", "dst": "d",
                     "skills": ["a-skill", "b-skill"],
                     "diffs": [{"skill": "a-skill", "path": "SKILL.md",
                                "type": "modified"}],
                     "consistent": ["b-skill"],
                     "orphans": [{"skill": "ghost", "path": "d/ghost"}]})
PC_GREEN = json.dumps({"status": "pass", "proposals": 3, "violations": []})
PC_RED = json.dumps({"status": "fail", "proposals": 3,
                     "violations": [{"kind": "proposal-conflict"}]})
GI_FOUND = json.dumps({"target": "ontology/bohai", "query": "AGG-BOHAI-001",
                       "found": True, "stats": {"nodes": 10, "edges": 12}})
GI_NOT_FOUND = json.dumps({"target": "ontology/x", "query": "NOPE-1",
                           "found": False, "stats": {"nodes": 7, "edges": 3}})


def core_status_runner(status_by_ask):
    """CORE 探针假 runner：按 --ask 文本回罐头 verdict（期望全对即绿）。"""
    def run(cmd):
        ask = cmd[cmd.index("--ask") + 1]
        status = status_by_ask[ask]
        rc = 0 if status == "answered" else 1
        verdict = {"question": ask, "status": status, "hits": [], "citations": []}
        return rc, json.dumps(verdict), ""
    return run


def green_routes(extra=None):
    """十项探针的「全绿」假 runner 路由（None 槽位交给 core runner）。"""
    routes = {
        "fixture_run": (0, fx_json(), ""),
        "schema_check": (0, SC_GREEN, ""),
        "semantic_service_core": None,
        "install_skills": (0, IS_GREEN, ""),
        "proposal_check": (0, PC_GREEN, ""),
        "graph_index": (0, GI_FOUND, ""),
        "git": (0, "0474bc8\n", ""),  # 路由表 commit 核实（一律验存）
    }
    if extra:
        routes.update(extra)
    return routes


def make_runner(routes, core_runner=None):
    def run(cmd):
        joined = " ".join(cmd)
        if core_runner is not None and "semantic_service_core" in joined:
            return core_runner(cmd)
        for key, resp in routes.items():
            if resp is not None and key in joined:
                if callable(resp):
                    return resp(cmd)  # 按命令细分的假响应（如坏 commit 只红特定哈希）
                if resp == "MISSING":
                    return 127, "", f"工具缺席: {key}"
                if resp == "GARBAGE":
                    return 0, "这不是 JSON", ""
                return resp
        raise AssertionError(f"未预期的命令: {joined}")
    return run


ALL_EXPECT = {q["ask"]: q["expect"] for q in mp.CORE_QUESTIONS}


def run_probe(root, runner, target="ontology/bohai"):
    return mp.collect_all(Path(root), Path(target), runner)


def run_main(argv, runner=None):
    out = io.StringIO()
    with redirect_stdout(out):
        rc = mp.main(argv, runner=runner)
    return rc, out.getvalue()


# ---------- 注入式单测 ----------

class MetaProbeAllGreen(unittest.TestCase):
    def setUp(self):
        self.repo = FakeRepo()
        self.root = self.repo.root

    def tearDown(self):
        self.repo.cleanup()

    def test_ten_items_all_green_exit_zero(self):
        self.repo.add_cards(["a-skill", "b-skill", "placeholder"])
        self.repo.add_skill("a-skill")
        self.repo.add_skill("b-skill")
        self.repo.add_prop("001", "open")
        self.repo.add_prop("002", "open")
        self.repo.add_prop("003", "accepted")
        items = run_probe(self.root, make_runner(green_routes(),
                                                 core_status_runner(ALL_EXPECT)))
        self.assertEqual([i["id"] for i in items],
                         ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        conclusion, exit_code = mp.evaluate(items)
        self.assertEqual((conclusion, exit_code), ("PASS", 0))
        hard = [i for i in items if i["kind"] == "hard"]
        self.assertEqual({i["id"] for i in hard}, {"1", "2", "6", "7", "10"})
        self.assertTrue(all(i["status"] == "green" for i in hard))

    def test_routing_table_green_checks_all_pointers(self):
        items = run_probe(self.root, make_runner(green_routes(),
                                                 core_status_runner(ALL_EXPECT)))
        rt = items[9]
        self.assertEqual(rt["status"], "green")
        self.assertEqual(rt["data"]["kindsFound"],
                         ["业务错", "工程错", "元模型错"])
        self.assertEqual(len(rt["data"]["commitChecks"]), 6)
        self.assertTrue(all(c["exists"] for c in rt["data"]["commitChecks"]))
        self.assertEqual({p["prop"] for p in rt["data"]["propChecks"]
                          if p["exists"]},
                         {"PROP-BOHAI-005", "PROP-BOHAI-006", "PROP-BOHAI-031"})

    def test_md_has_ten_sections_and_conclusion(self):
        self.repo.add_cards(["a-skill", "b-skill"])
        self.repo.add_skill("a-skill")
        self.repo.add_skill("b-skill")
        items = run_probe(self.root, make_runner(green_routes(),
                                                 core_status_runner(ALL_EXPECT)))
        md = mp.render_md(items, "PASS", Path("ontology/bohai"), self.root,
                          "2026-09-19 00:00:00")
        for n in range(1, 11):
            self.assertIn(f"## {n}. ", md)
        self.assertIn("结论: PASS", md)
        self.assertIn("生成时间: 2026-09-19 00:00:00", md)


class MetaProbeHardRedPaths(unittest.TestCase):
    """AC2：硬闸红灯可造——注入坏场景 → 对应探针红、退出 1。"""

    def setUp(self):
        self.repo = FakeRepo()
        self.root = self.repo.root
        self.repo.add_cards(["a-skill", "b-skill"])
        self.repo.add_skill("a-skill")
        self.repo.add_skill("b-skill")

    def tearDown(self):
        self.repo.cleanup()

    def _probe(self, routes):
        return run_probe(self.root, make_runner(routes,
                                                core_status_runner(ALL_EXPECT)))

    @staticmethod
    def _red_ids(items):
        return sorted(i["id"] for i in items if i["status"] == "red")

    def test_fixture_fail_red_exit1(self):
        items = self._probe(green_routes({"fixture_run": (
            1, fx_json(suites=(("alpha", "pass"), ("beta", "fail"))), "")}))
        self.assertEqual(self._red_ids(items), ["1"])
        self.assertEqual(items[0]["data"]["counts"], {"pass": 1, "fail": 1})
        self.assertEqual(mp.evaluate(items), ("FAIL", 1))

    def test_schema_red_exit1(self):
        items = self._probe(green_routes({"schema_check": (1, SC_RED, "")}))
        self.assertEqual(self._red_ids(items), ["2"])
        self.assertEqual(items[1]["data"]["levels"], {"L1": 2, "L2": 0, "L4": 1})
        self.assertEqual(mp.evaluate(items), ("FAIL", 1))

    def test_install_drift_red_exit1(self):
        items = self._probe(green_routes({"install_skills": (1, IS_RED, "")}))
        self.assertEqual(self._red_ids(items), ["6"])
        self.assertEqual(items[5]["data"]["driftCount"], 1)
        self.assertEqual(items[5]["data"]["orphanCount"], 1)
        self.assertEqual(mp.evaluate(items), ("FAIL", 1))

    def test_install_tool_missing_skipped_exit0(self):
        items = self._probe(green_routes({"install_skills": "MISSING"}))
        self.assertEqual(items[5]["status"], "skipped")
        self.assertEqual(mp.evaluate(items), ("DEGRADED", 0))

    def test_skill_without_card_hard_red_exit1(self):
        self.repo.add_skill("ghost-skill")  # 有 skill 无卡 = 违规
        items = self._probe(green_routes())
        self.assertEqual(self._red_ids(items), ["7"])
        self.assertEqual(items[6]["data"]["skillNoCard"], ["ghost-skill"])
        self.assertEqual(mp.evaluate(items), ("FAIL", 1))

    def test_fixture_tool_missing_skipped_degraded_exit0(self):
        items = self._probe(green_routes({"fixture_run": "MISSING"}))
        self.assertEqual(items[0]["status"], "skipped")
        self.assertEqual(mp.evaluate(items), ("DEGRADED", 0))

    def test_fixture_garbage_output_skipped(self):
        items = self._probe(green_routes({"fixture_run": "GARBAGE"}))
        self.assertEqual(items[0]["status"], "skipped")
        self.assertEqual(mp.evaluate(items), ("DEGRADED", 0))

    def test_schema_tool_missing_skipped_exit0(self):
        items = self._probe(green_routes({"schema_check": "MISSING"}))
        self.assertEqual(items[1]["status"], "skipped")


# ---------- 票 34 P2-A 扩根：第 2 项「目标域 + 溯源仓根」两跑，任一红即红 ----------

XP_REGISTRY = {"version": 1, "models": {
    "M1": {"name": "对象模型", "yamlFile": "m1-object-model.yaml",
           "modelType": "OBJECT", "camp": "business-core",
           "consumers": ["runtime"], "profiles": ["full"],
           "dependsOn": [], "lockedFields": {}}}}
XP_DEPS = {"version": 1, "idPrefixes": {"AGG-": "M1"},
           "refKeys": ["ownerEntity"], "edges": []}
XP_M1 = """model_type: OBJECT
version: "1.0.0"
domain: bohai
aggregates:
  - id: AGG-XP-001
    name: 扩根单测对象
    aggregateType: AGGREGATE_ROOT
    attributes: []
"""


class MetaProbeSchemaRootExpansion(unittest.TestCase):
    """票 34 扩根（AC2）：probe 第 2 项对「目标域 + 溯源 ontology 根」各跑一次
    schema_check（目标即根时去重），任一红即红——裸仓根绿挂硬闸。溯源规则：
    从目标目录起向上找含 schema/ 子目录的祖先（最多 3 级）。注入场景照主窗口
    防踩坑 #2 修正：patterns 素材目录排除后其坏 YAML 不再红，「根下真域坏 YAML」
    才是仓根闸要抓的（patterns 复现场景的修前红已由 L0/施工窗实跑留痕）。"""

    def _fake_repo(self, *, patterns_bad_yaml=False, root_bad_domain=False):
        """tempfile 假仓：ontology/schema + ontology/bohai（合法域）。"""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        onto = root / "ontology"
        (onto / "schema").mkdir(parents=True)
        (onto / "schema" / "model-registry.json").write_text(
            json.dumps(XP_REGISTRY), encoding="utf-8")
        (onto / "schema" / "model-deps.json").write_text(
            json.dumps(XP_DEPS), encoding="utf-8")
        bohai = onto / "bohai"
        bohai.mkdir()
        (bohai / "manifest.json").write_text(json.dumps(
            {"domain": "bohai", "profile": "full", "schemaVersion": "1.0.0"}),
            encoding="utf-8")
        (bohai / "m1-object-model.yaml").write_text(XP_M1, encoding="utf-8")
        if patterns_bad_yaml:
            (onto / "patterns").mkdir()
            (onto / "patterns" / "broken-pattern.yaml").write_text(
                "model_type: [破括号\n", encoding="utf-8")
        if root_bad_domain:
            bad = onto / "wildjunk"
            bad.mkdir()
            (bad / "m1-object-model.yaml").write_text(XP_M1, encoding="utf-8")
        return root, bohai, onto

    def _probe_real(self, target):
        """真 subprocess runner（cwd=真仓跑真 schema_check）打 tempfile 假仓。"""
        return mp.probe_schema(REAL_ROOT, target, mp.subprocess_runner(REAL_ROOT))

    def test_target_and_root_both_run_green_with_patterns_bad_yaml(self):
        # 修后绿态：patterns/ 坏 YAML 被素材排除——目标域与仓根两跑全过
        _root, bohai, onto = self._fake_repo(patterns_bad_yaml=True)
        item = self._probe_real(bohai)
        self.assertEqual(item["status"], "green")
        self.assertTrue(item["data"]["rootChecked"])
        self.assertEqual(item["data"]["ontologyRoot"], str(onto))
        self.assertEqual([r["role"] for r in item["data"]["runs"]],
                         ["目标域", "仓根"])
        self.assertTrue(all(r["status"] == "pass"
                            for r in item["data"]["runs"]))
        self.assertEqual(mp.evaluate([item]), ("PASS", 0))

    def test_target_is_root_dedup_single_run(self):
        # 目标即根（溯源返回自身）→ 去重只跑一次，不再注记 rootChecked
        _root, _bohai, onto = self._fake_repo()
        item = self._probe_real(onto)
        self.assertEqual(item["status"], "green")
        self.assertFalse(item["data"]["rootChecked"])
        self.assertEqual([r["role"] for r in item["data"]["runs"]], ["目标域"])

    def test_bad_real_domain_at_root_is_red_even_when_target_green(self):
        # 注入红态（仓根闸的本职）：目标域 bohai 合法，根下 wildjunk 真域坏
        # （有模型 YAML 无 manifest）——修前 probe 只跑目标域会放行，扩根后红
        _root, bohai, _onto = self._fake_repo(root_bad_domain=True)
        item = self._probe_real(bohai)
        self.assertEqual(item["status"], "red")
        self.assertEqual(mp.evaluate([item]), ("FAIL", 1))
        self.assertIn("仓根", item["summary"])
        roles = {r["role"]: r["status"] for r in item["data"]["runs"]}
        self.assertEqual(roles, {"目标域": "pass", "仓根": "fail"})

    def test_injected_runner_two_calls_root_red_decides(self):
        # 注入式假 runner：按目标路径分流——目标域绿、仓根红 → 项红且取红方计数
        _root, bohai, onto = self._fake_repo()
        green = json.dumps({"status": "pass",
                            "levels": {"L1": 0, "L2": 0, "L4": 0},
                            "violations": [], "files": 1})
        red = json.dumps({"status": "fail",
                          "levels": {"L1": 2, "L2": 0, "L4": 0},
                          "violations": [{"level": "L1", "kind": "x",
                                          "file": "f", "line": 1,
                                          "message": "m"}], "files": 3})
        calls: list[list[str]] = []

        def split_runner(cmd):
            calls.append(cmd)
            return (0, green, "") if cmd[2] == str(bohai) else (1, red, "")

        item = mp.probe_schema(Path("/any"), bohai, split_runner)
        self.assertEqual(len(calls), 2)  # 目标域 + 仓根各一次
        self.assertEqual(item["status"], "red")
        self.assertEqual(item["data"]["levels"], {"L1": 2, "L2": 0, "L4": 0})
        self.assertEqual(item["data"]["fileCount"], 3)  # 取决定方（红）的快照
        self.assertEqual([r["role"] for r in item["data"]["runs"]],
                         ["目标域", "仓根"])


class MetaProbeSignalRoutingRed(unittest.TestCase):
    """票 29 AC2：路由表自检（第 10 项）红灯可注入——坏表各形态 → 红 + exit 1。"""

    def setUp(self):
        self.repo = FakeRepo()

    def tearDown(self):
        self.repo.cleanup()

    def _table(self):
        return json.loads(json.dumps(TEST_ROUTING))

    def _probe(self, table="KEEP", routes=None, drop=False):
        if drop:
            self.repo.drop_routing_table()
        elif table != "KEEP":
            self.repo.add_routing_table(table)
        items = run_probe(self.repo.root,
                          make_runner(routes or green_routes(),
                                      core_status_runner(ALL_EXPECT)))
        return items

    def test_missing_table_red_exit1(self):
        items = self._probe(drop=True)
        self.assertEqual(items[9]["status"], "red")
        self.assertIn("不存在", items[9]["summary"])
        self.assertEqual(mp.evaluate(items), ("FAIL", 1))

    def test_bad_json_red_exit1(self):
        self.repo.write("policies/signal-routing.json", "{这不是 JSON")
        items = self._probe()
        self.assertEqual(items[9]["status"], "red")
        self.assertIn("合法 JSON", items[9]["summary"])
        self.assertEqual(mp.evaluate(items), ("FAIL", 1))

    def test_routes_not_list_red(self):
        self.repo.add_routing_table({"version": 1})
        items = self._probe()
        self.assertEqual(items[9]["status"], "red")
        self.assertTrue(any("routes 不是数组" in e
                            for e in items[9]["data"]["errors"]))

    def test_missing_kind_red_exit1(self):
        table = self._table()
        table["routes"] = table["routes"][:2]  # 少了元模型错
        items = self._probe(table=table)
        self.assertEqual(items[9]["status"], "red")
        self.assertTrue(any("缺路由类「元模型错」" in e
                            for e in items[9]["data"]["errors"]))
        self.assertEqual(mp.evaluate(items), ("FAIL", 1))

    def test_unknown_kind_red(self):
        table = self._table()
        table["routes"].append({"kind": "文档错", "destination": "x",
                                "mechanism": "y",
                                "instances": [{"commit": "cccc333"},
                                              {"commit": "dddd444"}]})
        items = self._probe(table=table)
        self.assertEqual(items[9]["status"], "red")
        self.assertTrue(any("未知路由类" in e for e in items[9]["data"]["errors"]))

    def test_bad_commit_pointer_red_exit1(self):
        def git_split(cmd):
            return (1, "", "fatal: 无效对象") if "dddd444" in " ".join(cmd) \
                else (0, "ok\n", "")
        table = self._table()
        table["routes"][1]["instances"][1]["commit"] = "dddd444"
        items = self._probe(table=table,
                            routes=green_routes({"git": git_split}))
        self.assertEqual(items[9]["status"], "red")
        self.assertTrue(any("commit dddd444" in e
                            for e in items[9]["data"]["errors"]))
        ok = [c for c in items[9]["data"]["commitChecks"] if c["exists"]]
        bad = [c for c in items[9]["data"]["commitChecks"] if not c["exists"]]
        self.assertEqual([c["commit"] for c in bad], ["dddd444"])
        self.assertEqual(len(ok), 5)
        self.assertEqual(mp.evaluate(items), ("FAIL", 1))

    def test_bad_prop_pointer_red(self):
        table = self._table()
        table["routes"][0]["instances"][0]["props"] = ["PROP-NOPE-999"]
        items = self._probe(table=table)
        self.assertEqual(items[9]["status"], "red")
        self.assertTrue(any("PROP-NOPE-999 不在 docs/proposals/" in e
                            for e in items[9]["data"]["errors"]))
        self.assertEqual(mp.evaluate(items), ("FAIL", 1))

    def test_too_few_instances_red(self):
        table = self._table()
        table["routes"][2]["instances"] = table["routes"][2]["instances"][:1]
        items = self._probe(table=table)
        self.assertEqual(items[9]["status"], "red")
        self.assertTrue(any("实例指针不足 2 条" in e
                            for e in items[9]["data"]["errors"]))

    def test_instance_without_pointer_red(self):
        table = self._table()
        table["routes"][2]["instances"][1] = {"desc": "空指针"}
        items = self._probe(table=table)
        self.assertEqual(items[9]["status"], "red")
        self.assertTrue(any("缺 commit/props 指针" in e
                            for e in items[9]["data"]["errors"]))

    def test_route_missing_destination_mechanism_red(self):
        table = self._table()
        del table["routes"][1]["mechanism"]
        items = self._probe(table=table)
        self.assertEqual(items[9]["status"], "red")
        self.assertTrue(any("缺 destination/mechanism" in e
                            for e in items[9]["data"]["errors"]))

    def test_git_missing_skipped_degraded_exit0(self):
        items = self._probe(routes=green_routes({"git": "MISSING"}))
        self.assertEqual(items[9]["status"], "skipped")
        self.assertEqual(mp.evaluate(items), ("DEGRADED", 0))
        self.assertEqual(mp.evaluate(items), ("DEGRADED", 0))


class MetaProbeInfoItems(unittest.TestCase):
    """信息项（3/4/5/8/9）红不判死：红时退出码仍 0；占位卡不判违规。"""

    def setUp(self):
        self.repo = FakeRepo()
        self.root = self.repo.root
        self.repo.add_cards(["a-skill", "b-skill"])
        self.repo.add_skill("a-skill")
        self.repo.add_skill("b-skill")

    def tearDown(self):
        self.repo.cleanup()

    def _probe(self, routes=None, core=None):
        return run_probe(self.root, make_runner(routes or green_routes(),
                                                core or core_status_runner(ALL_EXPECT)))

    def test_core_distribution_counts(self):
        items = self._probe()
        data = items[2]["data"]
        self.assertEqual(data["dist"], {"answered": 5, "refused_missing": 1,
                                        "refused_banned": 1,
                                        "refused_out_of_surface": 1})
        self.assertEqual(items[2]["status"], "green")

    def test_core_expect_drift_red_but_exit0(self):
        answers = dict(ALL_EXPECT)
        answers[mp.CORE_QUESTIONS[0]["ask"]] = "refused_banned"  # 期望漂移
        items = self._probe(core=core_status_runner(answers))
        self.assertEqual(items[2]["status"], "red")
        self.assertEqual(mp.evaluate(items), ("PASS", 0))

    def test_core_tool_missing_skipped(self):
        def absent(cmd):
            return 127, "", "工具缺席"
        items = self._probe(core=absent)
        self.assertEqual(items[2]["status"], "skipped")

    def test_boundary_allow_listing_with_slots(self):
        self.repo.write(".skill-deps-allow",
                        "fixtures/onto/**  # 出厂集 Seam（票 05）\n"
                        "fixtures/db/**  # 出厂集 Seam（票 06）\n")
        items = self._probe()
        data = items[3]["data"]
        self.assertEqual([e["pattern"] for e in data["entries"]],
                         ["fixtures/onto/**", "fixtures/db/**"])
        self.assertEqual(data["entries"][0]["reason"], "出厂集 Seam（票 05）")
        self.assertEqual(data["reviewSlots"], 2)
        self.assertEqual(items[3]["status"], "green")

    def test_boundary_allow_bad_line_red_but_exit0(self):
        self.repo.write(".skill-deps-allow", "no-reason-pattern\n")
        items = self._probe()
        self.assertEqual(items[3]["status"], "red")
        self.assertEqual(mp.evaluate(items), ("PASS", 0))

    def test_archive_allow_absent_zero_entries(self):
        items = self._probe()
        self.assertEqual(items[4]["status"], "green")
        self.assertEqual(items[4]["data"]["entries"], [])

    def test_archive_allow_entries_listed(self):
        self.repo.write(".archive-allow", "exports/**  # 派生物（票 23）\n")
        items = self._probe()
        self.assertEqual(items[4]["data"]["entries"],
                         [{"pattern": "exports/**", "reason": "派生物（票 23）"}])

    def test_proposal_status_counts(self):
        self.repo.add_prop("001", "open")
        self.repo.add_prop("002", "open")
        self.repo.add_prop("003", "accepted")
        items = self._probe()
        data = items[7]["data"]
        # FakeRepo 缺省路由表自带 3 份 PROP-BOHAI-*（open），一并计入
        self.assertEqual(data["statusCounts"], {"open": 5, "accepted": 1})
        self.assertEqual(data["files"], 6)
        self.assertEqual(items[7]["status"], "green")

    def test_proposal_conflict_red_but_exit0(self):
        self.repo.add_prop("001", "open")
        items = self._probe(routes=green_routes(
            {"proposal_check": (1, PC_RED, "")}))
        self.assertEqual(items[7]["status"], "red")
        self.assertEqual(items[7]["data"]["proposalCheck"]["exitCode"], 1)
        self.assertEqual(mp.evaluate(items), ("PASS", 0))

    def test_proposal_check_missing_skipped(self):
        self.repo.add_prop("001", "open")
        items = self._probe(routes=green_routes({"proposal_check": "MISSING"}))
        self.assertEqual(items[7]["status"], "skipped")

    def test_graph_baseline_snapshot(self):
        items = self._probe()
        data = items[8]["data"]
        self.assertEqual((data["found"], data["nodes"], data["edges"]),
                         (True, 10, 12))
        self.assertEqual(items[8]["status"], "green")

    def test_graph_not_found_still_records_stats(self):
        items = self._probe(routes=green_routes(
            {"graph_index": (1, GI_NOT_FOUND, "")}))
        self.assertEqual(items[8]["data"]["found"], False)
        self.assertEqual(items[8]["data"]["nodes"], 7)
        self.assertEqual(items[8]["status"], "green")

    def test_card_without_skill_placeholder_not_violation(self):
        self.repo.add_cards(["a-skill", "b-skill", "future-card"])
        items = self._probe()
        self.assertEqual(items[6]["status"], "green")
        self.assertEqual(items[6]["data"]["cardNoSkill"], ["future-card"])


class MetaProbeReviewMerge(unittest.TestCase):
    """票 29：豁免复核结论并入——--review 显式 / 缺省 docs/meta/exemption-reviews.json
    两条路；无结论=留空栏；坏结论文件=注记不判死；未匹配模式=注记防漂移。"""

    def setUp(self):
        self.repo = FakeRepo()
        self.repo.add_cards(["a-skill", "b-skill"])
        self.repo.add_skill("a-skill")
        self.repo.add_skill("b-skill")
        self.repo.write(".skill-deps-allow",
                        "fixtures/onto/**  # 出厂集 Seam（票 05）\n"
                        "fixtures/db/**  # 出厂集 Seam（票 06）\n")

    def tearDown(self):
        self.repo.cleanup()

    def _run(self, extra_argv, review_file=None, entries=None):
        review = {"reviewedBy": "L0", "reviewedAt": "2026-09-19",
                  "entries": entries or [
                      {"file": "fixtures/onto/**", "verdict": "保留",
                       "reason": "Seam 声明面闸不解析，机制性豁免"},
                      {"file": "fixtures/db/**", "verdict": "保留",
                       "reason": "同 Seam 机制性豁免"}]}
        if review_file:
            self.repo.write(review_file, json.dumps(review, ensure_ascii=False))
        argv = ([str(self.repo.root / "ontology" / "bohai"),
                 "--root", str(self.repo.root)] + extra_argv)
        return run_main(argv, runner=make_runner(green_routes(),
                                                 core_status_runner(ALL_EXPECT)))

    def test_explicit_review_flag_merges_into_md(self):
        rc, out = self._run(["--review", str(self.repo.root / "reviews.json")],
                            review_file="reviews.json")
        self.assertEqual(rc, 0)
        self.assertIn("豁免复核: 本次留痕并入 2 条复核结论"
                      "（复核人 L0，复核日期 2026-09-19", out)
        self.assertIn("- [x] 保留（L0 2026-09-19）: "
                      "Seam 声明面闸不解析，机制性豁免", out)
        self.assertIn("人工复核结论（复核人 / 日期）", out)

    def test_default_review_path_autoload(self):
        rc, out = self._run([], review_file="docs/meta/exemption-reviews.json")
        self.assertEqual(rc, 0)
        self.assertIn("豁免复核: 本次留痕并入 2 条复核结论", out)

    def test_summary_table_row_updated_not_blank(self):
        rc, out = self._run([], review_file="docs/meta/exemption-reviews.json")
        self.assertIn("| 边界闸豁免 | 信息 | GREEN | 2 条豁免"
                      "（复核结论已并入 2 条，复核人 L0，复核日期 2026-09-19） |",
                      out)

    def test_list_form_accepted(self):
        self.repo.write("docs/meta/exemption-reviews.json", json.dumps(
            [{"file": "fixtures/onto/**", "verdict": "保留", "reason": "机制性"}],
            ensure_ascii=False))
        rc, out = self._run([])
        self.assertIn("- [x] 保留（— —）: 机制性", out)

    def test_no_review_file_leaves_blank_slots(self):
        rc, out = self._run([])
        self.assertEqual(rc, 0)
        self.assertIn("人工复核（值留空，批收官填）", out)
        self.assertIn("- [ ] 保留 / 可收敛: ____", out)

    def test_bad_review_file_noted_not_fatal(self):
        self.repo.write("docs/meta/exemption-reviews.json", "{坏 JSON")
        rc, out = self._run([])
        self.assertEqual(rc, 0)
        self.assertIn("复核结论文件注记", out)
        self.assertIn("- [ ] 保留 / 可收敛: ____", out)

    def test_unmatched_pattern_noted(self):
        self.repo.write("docs/meta/exemption-reviews.json", json.dumps(
            {"reviewedBy": "L0", "reviewedAt": "2026-09-19",
             "entries": [{"file": "fixtures/ghost/**", "verdict": "可收敛",
                          "reason": "r"}]}, ensure_ascii=False))
        rc, out = self._run([])
        self.assertIn("1 条结论模式未匹配豁免清单（fixtures/ghost/**）", out)

    # ---- 票 54（第八轮 P2-B）：豁免复核双向检查 ----

    def test_unmatched_review_pattern_red(self):
        """注入「复核有、豁免无」→ 第 4 项信息红（信息项语义，rc 仍 0）。"""
        rc, out = self._run([],
                            review_file="docs/meta/exemption-reviews.json",
                            entries=[
                                {"file": "fixtures/onto/**", "verdict": "保留",
                                 "reason": "机制性"},
                                {"file": "fixtures/db/**", "verdict": "保留",
                                 "reason": "机制性"},
                                {"file": "fixtures/ghost/**", "verdict": "可收敛",
                                 "reason": "r"}])
        self.assertEqual(rc, 0)
        self.assertIn("1 条结论模式未匹配豁免清单（fixtures/ghost/**）", out)
        self.assertIn("| 边界闸豁免 | 信息 | RED |", out)
        self.assertIn("（信息红）", out)

    def test_unreviewed_allow_pattern_red(self):
        """注入「豁免有、复核无」→ 第 4 项信息红（P2-B：防新增豁免漏复核被绿灯掩盖）。"""
        rc, out = self._run([],
                            review_file="docs/meta/exemption-reviews.json",
                            entries=[{"file": "fixtures/onto/**",
                                      "verdict": "保留", "reason": "机制性"}])
        self.assertEqual(rc, 0)
        self.assertIn("1 条豁免无复核结论（fixtures/db/**）", out)
        self.assertIn("| 边界闸豁免 | 信息 | RED |", out)
        self.assertIn("（信息红）", out)

    def test_bidirectional_zero_diff_green(self):
        """双向零差（2 豁免 2 复核）→ 第 4 项保持 GREEN、无红注记。"""
        rc, out = self._run([], review_file="docs/meta/exemption-reviews.json")
        self.assertEqual(rc, 0)
        self.assertIn("| 边界闸豁免 | 信息 | GREEN | 2 条豁免"
                      "（复核结论已并入 2 条，复核人 L0，复核日期 2026-09-19） |",
                      out)
        self.assertNotIn("条豁免无复核结论", out)
        self.assertNotIn("条结论模式未匹配豁免清单", out)


class MetaProbeCli(unittest.TestCase):
    def setUp(self):
        self.repo = FakeRepo()
        self.repo.add_cards(["a-skill", "b-skill"])
        self.repo.add_skill("a-skill")
        self.repo.add_skill("b-skill")

    def tearDown(self):
        self.repo.cleanup()

    def _argv(self, extra):
        return [str(self.repo.root / "ontology" / "bohai"),
                "--root", str(self.repo.root)] + extra

    def test_usage_error_nonexistent_target_exit2(self):
        rc, _ = run_main([str(self.repo.root / "no-such-dir"),
                          "--root", str(self.repo.root)])
        self.assertEqual(rc, 2)

    def test_stdout_default(self):
        rc, out = run_main(self._argv([]),
                           runner=make_runner(green_routes(),
                                              core_status_runner(ALL_EXPECT)))
        self.assertEqual(rc, 0)
        self.assertIn("## 10. ", out)
        self.assertIn("结论: PASS", out)

    def test_out_writes_md_and_json_pair(self):
        out_dir = Path(self.repo.tmp.name) / "docs" / "meta"
        rc, _ = run_main(self._argv(["--out", str(out_dir / "体检.md")]),
                         runner=make_runner(green_routes(),
                                            core_status_runner(ALL_EXPECT)))
        self.assertEqual(rc, 0)
        md = (out_dir / "体检.md").read_text(encoding="utf-8")
        data = json.loads((out_dir / "体检.json").read_text(encoding="utf-8"))
        self.assertIn("结论: PASS", md)
        self.assertEqual(data["conclusion"], "PASS")
        self.assertEqual(data["exitCode"], 0)
        self.assertEqual(len(data["probes"]), 10)
        self.assertIn("generatedAt", data)

    def test_out_hard_red_exit1_files_still_written(self):
        self.repo.add_skill("ghost-skill")
        out_dir = Path(self.repo.tmp.name) / "docs" / "meta"
        rc, _ = run_main(self._argv(["--out", str(out_dir / "体检.md")]),
                         runner=make_runner(green_routes(),
                                            core_status_runner(ALL_EXPECT)))
        self.assertEqual(rc, 1)
        data = json.loads((out_dir / "体检.json").read_text(encoding="utf-8"))
        self.assertEqual(data["conclusion"], "FAIL")


# ---------- 真仓集成冒烟（实跑，不注入） ----------

@unittest.skipUnless(
    (REAL_ROOT / "tools" / "meta_probe.py").is_file()
    and (REAL_ROOT / "ontology" / "bohai").is_dir(),
    "真仓不在位（tools/meta_probe.py 或 ontology/bohai 缺）")
class MetaProbeRealRepoSmoke(unittest.TestCase):
    """AC1 机读面：真仓实跑硬闸 5/5 全绿 + CORE 八问分布钉死 + 图基线在场
    + 路由表三类齐且指针全核实（票 29）。"""

    def test_real_repo_all_hard_green_and_core_dist(self):
        runner = mp.subprocess_runner(REAL_ROOT)
        items = mp.collect_all(REAL_ROOT, REAL_ROOT / "ontology" / "bohai", runner)
        conclusion, exit_code = mp.evaluate(items)
        self.assertEqual(conclusion, "PASS")
        self.assertEqual(exit_code, 0)
        core = next(i for i in items if i["id"] == "3")
        self.assertEqual(core["data"]["dist"],
                         {"answered": 5, "refused_missing": 1,
                          "refused_banned": 1, "refused_out_of_surface": 1})
        graph = next(i for i in items if i["id"] == "9")
        self.assertGreater(graph["data"]["nodes"], 0)
        self.assertGreater(graph["data"]["edges"], 0)
        sync = next(i for i in items if i["id"] == "7")
        self.assertEqual(sync["data"]["skillNoCard"], [])
        self.assertTrue(sync["data"]["cardNoSkill"])  # 占位卡在列（不判违规）
        rt = next(i for i in items if i["id"] == "10")
        self.assertEqual(rt["status"], "green")
        self.assertEqual(rt["data"]["kindsFound"], list(mp.ROUTING_KINDS))
        self.assertTrue(all(c["exists"] for c in rt["data"]["commitChecks"]))
        self.assertTrue(all(p["exists"] for p in rt["data"]["propChecks"]))
        self.assertEqual(rt["data"]["errors"], [])


class MetaProbeMultiDomain(unittest.TestCase):
    """票 64 多域适配：CORE/图基线按域登记——无冻结集域=豁免注记不假红；
    图锚按目标域解析，显式 graph_query 优先。"""

    def setUp(self):
        self.repo = FakeRepo()
        self.root = self.repo.root
        self.repo.add_cards(["a-skill", "b-skill"])
        self.repo.add_skill("a-skill")
        self.repo.add_skill("b-skill")
        # pkb 域目录（无 manifest 时目录名即域名；pkb 无冻结 CORE 集）
        (self.root / "ontology" / "pkb").mkdir()

    def tearDown(self):
        self.repo.cleanup()

    def test_core_exempt_for_domain_without_frozen_set(self):
        asks = []

        def spy_core(cmd):
            asks.append(cmd[cmd.index("--ask") + 1])
            return 0, json.dumps({"status": "answered"}), ""

        items = run_probe(self.root, make_runner(green_routes(), spy_core),
                          target="ontology/pkb")
        core = next(i for i in items if i["id"] == "3")
        self.assertEqual(core["status"], "green")
        self.assertTrue(core["data"]["exempt"])
        self.assertEqual(core["data"]["domain"], "pkb")
        self.assertEqual(asks, [])  # 豁免域不跑他域问句（跑了必假红，P2-1）

    def test_core_bohai_still_runs_frozen_eight(self):
        asks = []

        def spy_core(cmd):
            asks.append(cmd[cmd.index("--ask") + 1])
            return 0, json.dumps({"status": "answered"}), ""

        run_probe(self.root, make_runner(green_routes(), spy_core),
                  target="ontology/bohai")
        self.assertEqual(len(asks), len(mp.CORE_QUESTIONS))

    def test_graph_anchor_resolved_per_domain(self):
        seen = []

        def spy_graph(cmd):
            seen.append(cmd[cmd.index("--query") + 1])
            return 0, GI_FOUND, ""

        routes = green_routes(extra={"graph_index": spy_graph})
        run_probe(self.root,
                  make_runner(routes, core_status_runner(ALL_EXPECT)),
                  target="ontology/pkb")
        self.assertEqual(seen, ["AGG-PKB-001"])
        seen.clear()
        run_probe(self.root,
                  make_runner(routes, core_status_runner(ALL_EXPECT)),
                  target="ontology/bohai")
        self.assertEqual(seen, ["AGG-BOHAI-001"])

    def test_graph_explicit_query_overrides_domain_anchor(self):
        seen = []

        def spy_graph(cmd):
            seen.append(cmd[cmd.index("--query") + 1])
            return 0, GI_FOUND, ""

        mp.collect_all(Path(self.root), Path("ontology/pkb"),
                       make_runner(green_routes(extra={"graph_index": spy_graph}),
                                   core_status_runner(ALL_EXPECT)),
                       graph_query="CUSTOM-1")
        self.assertEqual(seen, ["CUSTOM-1"])


class ListDomainsMode(unittest.TestCase):
    """票 77：--list-domains 域清单枚举（AGENTS 协议①去手抄域名单的承载）。"""

    def _call(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            try:
                rc = mp.main(argv)
            except SystemExit as exc:  # argparse 用法错按退出码收
                rc = exc.code if isinstance(exc.code, int) else 2
        return rc, buf.getvalue()

    def test_real_repo_lists_three_domains(self):
        proc = subprocess.run(
            [sys.executable, str(REAL_ROOT / "tools" / "meta_probe.py"),
             "--list-domains"],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.splitlines(), ["bohai", "his", "pkb"])

    def test_tmp_root_sorted_enumeration(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for d in ("a2", "a1"):
                (root / "ontology" / d).mkdir(parents=True)
                (root / "ontology" / d / "manifest.json").write_text(
                    json.dumps({"domain": d}), encoding="utf-8")
            (root / "ontology" / "notadomain.txt").write_text(
                "x", encoding="utf-8")  # 非目录项不进清单
            rc, out = self._call(["--list-domains", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertEqual(out.splitlines(), ["a1", "a2"])

    def test_tmp_root_without_ontology_is_empty_not_crash(self):
        with tempfile.TemporaryDirectory() as td:
            rc, out = self._call(["--list-domains", "--root", td])
            self.assertEqual(rc, 0)
            self.assertEqual(out, "")

    def test_target_optional_but_required_without_flag(self):
        rc, _out = self._call([])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
