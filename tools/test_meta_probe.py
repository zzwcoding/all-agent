#!/usr/bin/env python3
"""meta_probe.py 的单测（票 28：元循环探针）。

TDD 面全部注入式（票面红线：collectors 用 tempfile 造 root + 假 runner 注入），
对真仓一条集成冒烟（skipUnless 真仓在位——本仓开发即真仓，实跑）。
覆盖：九项全绿 exit 0 / 硬闸红灯路径（出厂集 fail、语义闸 L1、安装位漂移、
skill 无卡）→ exit 1 / 工具缺席与坏输出 → SKIPPED 降级不崩（AC4）/
信息项红不判死（CORE 期望漂移、提案冲突、豁免行缺理由）/ --out 双落盘 /
用法错误 exit 2 / 真仓冒烟（硬闸全绿 + CORE 八问分布钉死）。
"""

import io
import json
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
    """九项探针的「全绿」假 runner 路由（None 槽位交给 core runner）。"""
    routes = {
        "fixture_run": (0, fx_json(), ""),
        "schema_check": (0, SC_GREEN, ""),
        "semantic_service_core": None,
        "install_skills": (0, IS_GREEN, ""),
        "proposal_check": (0, PC_GREEN, ""),
        "graph_index": (0, GI_FOUND, ""),
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

    def test_nine_items_all_green_exit_zero(self):
        self.repo.add_cards(["a-skill", "b-skill", "placeholder"])
        self.repo.add_skill("a-skill")
        self.repo.add_skill("b-skill")
        self.repo.add_prop("001", "open")
        self.repo.add_prop("002", "open")
        self.repo.add_prop("003", "accepted")
        items = run_probe(self.root, make_runner(green_routes(),
                                                 core_status_runner(ALL_EXPECT)))
        self.assertEqual([i["id"] for i in items],
                         ["1", "2", "3", "4", "5", "6", "7", "8", "9"])
        conclusion, exit_code = mp.evaluate(items)
        self.assertEqual((conclusion, exit_code), ("PASS", 0))
        hard = [i for i in items if i["kind"] == "hard"]
        self.assertEqual({i["id"] for i in hard}, {"1", "2", "6", "7"})
        self.assertTrue(all(i["status"] == "green" for i in hard))

    def test_md_has_nine_sections_and_conclusion(self):
        self.repo.add_cards(["a-skill", "b-skill"])
        self.repo.add_skill("a-skill")
        self.repo.add_skill("b-skill")
        items = run_probe(self.root, make_runner(green_routes(),
                                                 core_status_runner(ALL_EXPECT)))
        md = mp.render_md(items, "PASS", Path("ontology/bohai"), self.root,
                          "2026-09-19 00:00:00")
        for n in range(1, 10):
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
        self.assertEqual(data["statusCounts"], {"open": 2, "accepted": 1})
        self.assertEqual(data["files"], 3)
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
        self.assertIn("## 9. ", out)
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
        self.assertEqual(len(data["probes"]), 9)
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
    """AC1 机读面：真仓实跑硬闸全绿 + CORE 八问分布钉死 + 图基线在场。"""

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


if __name__ == "__main__":
    unittest.main()
