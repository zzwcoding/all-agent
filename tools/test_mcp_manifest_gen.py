#!/usr/bin/env python3
"""mcp_manifest_gen.py 的单测（stdlib unittest，TDD 先行；票 23）。

被测面：
  1. 确定性核心——零时间戳、两次生成字节一致（票 23 AC1，幂等）；
  2. 内容契约——四工具齐（name/description/inputSchema）、domains 含被扫域、
     profile 圈定模型面 + omittedModels 剔除（AC3 的单测面）；
  3. CLI 三模式——stdout 缺省 / --out 写文件 / --check 再生一致（AC2 的
     防陈旧载体：与入库副本逐字节比对）；
  4. 渤海真域回归——对 ontology/ 现场重生成与 exports/mcp/ 入库副本
     --check 一致（真域存在时）。

红相记录（TDD）：本文件先行落盘，mcp_manifest_gen 未实现时收集即红。
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

import mcp_manifest_gen as mmg

REPO = Path(__file__).resolve().parent.parent
BOHAI = REPO / "ontology" / "bohai"
EXPORTS_MANIFEST = REPO / "exports" / "mcp" / "capability-manifest.json"

EXPECTED_TOOLS = ["semantic_ask", "semantic_query", "semantic_closure",
                  "semantic_impact"]

# 合成迷你注册表：profiles 圈定 + camp 两阵营（MU=build-contract 供剔除实测）
REGISTRY = {
    "version": "9.9.9-test",
    "models": {
        "M1": {"name": "对象模型", "modelType": "OBJECT",
               "camp": "business-core", "profiles": ["v9-core", "v9-full"]},
        "M7": {"name": "查询统计与报表模型", "modelType": "REPORT",
               "camp": "business-core", "profiles": ["v9-full"]},
        "MU": {"name": "UI 模型", "modelType": "UI",
               "camp": "build-contract", "profiles": ["v9-full"]},
        "GLS": {"name": "术语模型", "modelType": "GLOSSARY",
                "camp": "business-core", "profiles": ["v9-full", "headless"]},
    },
}

MANIFEST_A = {"domain": "dom-a", "label": "演示域甲", "profile": "v9-full",
              "schemaVersion": "1.0.0",
              "omittedModels": [{"model": "MU", "reason": "无素材证据"}]}
MANIFEST_B = {"domain": "dom-b", "label": "演示域乙", "profile": "v9-core"}


def run_main(argv):
    """跑生成器 main，捕获 stdout+stderr，返回 (退出码, stdout, stderr)。"""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = mmg.main(argv)
    return rc, out.getvalue(), err.getvalue()


def make_root(tmp: Path, registry=None, manifests=None) -> Path:
    """搭合成本体根：schema/model-registry.json + 两个域 manifest。"""
    root = tmp / "onto"
    (root / "schema").mkdir(parents=True)
    (root / "schema" / "model-registry.json").write_text(
        json.dumps(registry or REGISTRY, ensure_ascii=False, indent=2),
        encoding="utf-8")
    for name, manifest in (manifests or
                           {"dom-a": MANIFEST_A, "dom-b": MANIFEST_B}).items():
        dom = root / name
        dom.mkdir(parents=True)
        (dom / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8")
    return root


class DeterminismTest(unittest.TestCase):
    """确定性核心：幂等 + 零时间戳（AC1）。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_root(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_ac1_two_runs_byte_identical(self):
        rc1, out1, _ = run_main([str(self.root)])
        rc2, out2, _ = run_main([str(self.root)])
        self.assertEqual((rc1, rc2), (0, 0))
        self.assertEqual(out1, out2)

    def test_ac1_two_out_files_byte_identical(self):
        a, b = Path(self._tmp.name) / "a.json", Path(self._tmp.name) / "b.json"
        run_main([str(self.root), "--out", str(a)])
        run_main([str(self.root), "--out", str(b)])
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_zero_timestamp_no_time_like_tokens(self):
        _rc, out, _ = run_main([str(self.root)])
        for forbidden in ("timestamp", "generatedAt", "generated_at",
                          "generated_on", "createdAt"):
            self.assertNotIn(forbidden, out)
        self.assertIsNone(re.search(r"\d{4}-\d{2}-\d{2}", out),
                          "manifest 不得含日期形态 token（零时间戳）")

    def test_domains_and_tools_sorted_deterministic(self):
        manifest = json.loads(run_main([str(self.root)])[1])
        self.assertEqual([d["domain"] for d in manifest["domains"]],
                         sorted(d["domain"] for d in manifest["domains"]))
        self.assertEqual([t["name"] for t in manifest["tools"]], EXPECTED_TOOLS)


class ContentContractTest(unittest.TestCase):
    """内容契约：四工具 + 域概览（AC3 的单测面）。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_root(Path(self._tmp.name))
        self.manifest = json.loads(run_main([str(self.root)])[1])

    def tearDown(self):
        self._tmp.cleanup()

    def test_manifest_json_parseable_top_keys(self):
        for key in ("status", "server", "domains", "tools", "generatedFrom"):
            self.assertIn(key, self.manifest)

    def test_four_tools_with_description_and_schema(self):
        tools = self.manifest["tools"]
        self.assertEqual([t["name"] for t in tools], EXPECTED_TOOLS)
        for tool in tools:
            self.assertTrue(tool["description"].strip(),
                            f"{tool['name']} 缺 description")
            schema = tool["inputSchema"]
            self.assertIsInstance(schema, dict)
            self.assertEqual(schema.get("type"), "object")
            self.assertIsInstance(schema.get("properties"), dict)
            self.assertIsInstance(schema.get("required"), list)

    def test_ask_schema_question_required(self):
        ask = next(t for t in self.manifest["tools"]
                   if t["name"] == "semantic_ask")
        self.assertIn("question", ask["inputSchema"]["required"])
        self.assertEqual(ask["inputSchema"]["properties"]["question"]["type"],
                         "string")

    def test_closure_schema_hops_optional_default(self):
        closure = next(t for t in self.manifest["tools"]
                       if t["name"] == "semantic_closure")
        props = closure["inputSchema"]["properties"]
        self.assertEqual(props["hops"]["default"], 3)
        self.assertNotIn("hops", closure["inputSchema"]["required"])

    def test_domains_profile_scope_and_omitted(self):
        doms = {d["domain"]: d for d in self.manifest["domains"]}
        self.assertEqual(set(doms), {"dom-a", "dom-b"})
        models_a = {m["model"] for m in doms["dom-a"]["models"]}
        self.assertEqual(models_a, {"M1", "M7", "GLS"})  # MU 被 omittedModels 剔除
        self.assertEqual(doms["dom-a"]["omittedModels"],
                         [{"model": "MU", "reason": "无素材证据"}])
        models_b = {m["model"] for m in doms["dom-b"]["models"]}
        self.assertEqual(models_b, {"M1"})  # v9-core 只圈 M1
        camps = {m["model"]: m["camp"] for m in doms["dom-a"]["models"]}
        self.assertEqual(camps["GLS"], "business-core")

    def test_server_block_and_generated_from(self):
        self.assertEqual(self.manifest["server"]["name"], mmg.SERVER_NAME)
        self.assertEqual(self.manifest["server"]["transport"], "stdio")
        gen = self.manifest["generatedFrom"]
        self.assertEqual(gen["generator"], "tools/mcp_manifest_gen.py")
        self.assertEqual(gen["registryVersion"], "9.9.9-test")


class CliModesTest(unittest.TestCase):
    """CLI 三模式：stdout / --out / --check（AC2 载体）+ 配置错误退出码。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_root(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_out_file_equals_stdout_and_stdout_quiet(self):
        _rc, out_std, _ = run_main([str(self.root)])
        target = Path(self._tmp.name) / "manifest.json"
        rc, out_file_mode, _ = run_main([str(self.root), "--out", str(target)])
        self.assertEqual(rc, 0)
        self.assertEqual(out_file_mode, "")  # --out 模式 stdout 安静
        self.assertEqual(target.read_text(encoding="utf-8"), out_std)

    def test_check_mode_match_exit_0(self):
        target = Path(self._tmp.name) / "manifest.json"
        run_main([str(self.root), "--out", str(target)])
        rc, out, err = run_main([str(self.root), "--check", str(target)])
        self.assertEqual(rc, 0)
        self.assertIn("一致", out + err)

    def test_check_mode_stale_exit_1(self):
        target = Path(self._tmp.name) / "manifest.json"
        run_main([str(self.root), "--out", str(target)])
        stale = json.loads(target.read_text(encoding="utf-8"))
        stale["tools"] = stale["tools"][:2]  # 模拟入库副本陈旧（少两工具）
        target.write_text(json.dumps(stale, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        rc, out, err = run_main([str(self.root), "--check", str(target)])
        self.assertEqual(rc, 1)
        self.assertIn("不一致", out + err)

    def test_check_mode_missing_copy_exit_1(self):
        rc, out, err = run_main(
            [str(self.root), "--check", str(Path(self._tmp.name) / "nope.json")])
        self.assertEqual(rc, 1)
        self.assertIn("不存在", out + err)

    def test_config_error_no_target_exit_2(self):
        rc, _out, err = run_main([str(Path(self._tmp.name) / "void")])
        self.assertEqual(rc, 2)
        self.assertIn("配置错误", err)

    def test_config_error_no_domains_exit_2(self):
        root = Path(self._tmp.name) / "empty"
        (root / "schema").mkdir(parents=True)
        (root / "schema" / "model-registry.json").write_text(
            json.dumps(REGISTRY, ensure_ascii=False), encoding="utf-8")
        rc, _out, err = run_main([str(root)])
        self.assertEqual(rc, 2)
        self.assertIn("域", err)

    def test_config_error_registry_missing_exit_2(self):
        root = Path(self._tmp.name) / "noref"
        (root / "schema").mkdir(parents=True)  # 有 schema/ 但缺 model-registry.json
        (root / "dom-x").mkdir()
        (root / "dom-x" / "manifest.json").write_text(
            json.dumps(MANIFEST_B, ensure_ascii=False), encoding="utf-8")
        rc, _out, err = run_main([str(root)])
        self.assertEqual(rc, 2)
        self.assertIn("model-registry", err)

    def test_config_error_domain_without_profile_exit_2(self):
        root = make_root(Path(self._tmp.name) / "second",  # 避开 setUp 已建的根
                         manifests={"dom-bad": {"domain": "dom-bad"}})
        rc, _out, err = run_main([str(root)])
        self.assertEqual(rc, 2)
        self.assertIn("profile", err)


@unittest.skipUnless(BOHAI.is_dir(), "真域缺失（跳过真域回归）")
class BohaiRealDomainTest(unittest.TestCase):
    """渤海真域回归：内容断言 + 入库副本再生一致（AC2/AC3 的真域实证）。"""

    def test_domains_contain_bohai_with_profile_scope(self):
        manifest = json.loads(run_main(["ontology"])[1])
        doms = {d["domain"]: d for d in manifest["domains"]}
        self.assertIn("bohai", doms)
        bohai = doms["bohai"]
        self.assertEqual(bohai["profile"], "v9-full")
        models = {m["model"] for m in bohai["models"]}
        self.assertIn("GLS", models)
        self.assertNotIn("MU", models)  # 真域 omittedModels 剔除
        camps = {m["model"]: m["camp"] for m in bohai["models"]}
        self.assertNotIn("build-contract", set(camps.values()))

    def test_exports_copy_regenerates_identical(self):
        self.assertTrue(EXPORTS_MANIFEST.is_file(),
                        "exports/mcp/capability-manifest.json 未落盘")
        rc, out, err = run_main(["ontology", "--check", str(EXPORTS_MANIFEST)])
        self.assertEqual(rc, 0, f"入库副本陈旧: {out}{err}")

    def test_check_reports_mismatch_when_copy_tampered(self):
        # 篡改副本的临时探针（写到 /tmp，不动入库文件）
        with tempfile.TemporaryDirectory() as td:
            tampered = Path(td) / "t.json"
            data = json.loads(EXPORTS_MANIFEST.read_text(encoding="utf-8"))
            data["server"]["name"] = "tampered"
            tampered.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                encoding="utf-8")
            rc, _out, _err = run_main(["ontology", "--check", str(tampered)])
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
