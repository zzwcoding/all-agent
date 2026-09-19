#!/usr/bin/env python3
"""semantic_mcp_server.py 的单测（stdlib unittest，TDD 先行；票 23）。

可测面（票 23 L0 设计裁决：协议面留票 24 实弹）：
  1. CI 免疫引导路径——无 mcp SDK 时起服退出 2、stderr 含 `pip install mcp`
     指引（AC4；强制 _HAS_MCP=False 实测，不依赖环境是否装了 SDK）；
  2. manifest 装载——load_manifest 对入库副本的结构/契约一致性校验、
     缺失/坏 JSON/契约漂移的报错面（描述真源=生成器模板，防两处漂移）；
  3. 回答骨架组装（纯函数）——answered/refused 两态文本必含 ID token 与
     「本回答引用的元素 ID」清单（票 24 AC3 grep 的载体）；
  4. 子进程链路（真域集成）——core/graph_index 包装的真实回答文本；
  5. 协议面——skipUnless(_HAS_MCP) 占位骨架（票 24 venv 实弹）。

红相记录（TDD）：本文件先行落盘，semantic_mcp_server 未实现时收集即红。
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import semantic_mcp_server as sms
from mcp_manifest_gen import TOOL_CONTRACTS

REPO = Path(__file__).resolve().parent.parent
BOHAI = REPO / "ontology" / "bohai"
EXPORTS_MANIFEST = REPO / "exports" / "mcp" / "capability-manifest.json"

CITATION_HEADER = "本回答引用的元素 ID"


def run_main(argv):
    """跑 server main（重定向 stderr），返回 (退出码, stderr)。"""
    err = io.StringIO()
    saved = sms._HAS_MCP
    try:
        sms._HAS_MCP = False  # 强制免疫路径：不依赖环境是否装了 mcp
        with redirect_stderr(err):
            rc = sms.main(argv)
    finally:
        sms._HAS_MCP = saved
    return rc, err.getvalue()


class BootstrapTest(unittest.TestCase):
    """CI 免疫红线（AC4）：无 mcp 起服 = 退出 2 + 安装指引。"""

    def test_no_mcp_exit_2_with_pip_hint(self):
        rc, err = run_main(["ontology/bohai"])
        self.assertEqual(rc, 2)
        self.assertIn("pip install mcp", err)

    def test_no_mcp_hint_mentions_venv_and_docs(self):
        _rc, err = run_main(["ontology/bohai"])
        self.assertIn("venv", err)
        self.assertIn("docs/mcp-server.md", err)

    def test_no_mcp_before_arg_validation(self):
        # 引导路径先于参数校验：裸起（无参数）也是同一免疫出口
        rc, err = run_main([])
        self.assertEqual(rc, 2)
        self.assertIn("pip install mcp", err)

    @unittest.skipIf(sms._HAS_MCP, "本机已装 mcp：真实免疫路径不可观测")
    def test_real_environment_bootstrap(self):
        proc_rc = sms.main(["ontology/bohai"])
        self.assertEqual(proc_rc, 2)


class ManifestLoadTest(unittest.TestCase):
    """manifest 装载：结构校验 + 与生成器模板契约一致性（防漂移哨兵）。"""

    def test_load_exports_copy_and_descriptions_match_contracts(self):
        manifest = sms.load_manifest(EXPORTS_MANIFEST)
        for key in ("server", "domains", "tools", "generatedFrom"):
            self.assertIn(key, manifest)
        descriptions = sms.tool_descriptions(manifest)
        self.assertEqual(sorted(descriptions),
                         sorted(c["name"] for c in TOOL_CONTRACTS))
        for contract in TOOL_CONTRACTS:
            self.assertEqual(descriptions[contract["name"]],
                             contract["description"],
                             f"{contract['name']} 描述与模板漂移")

    def test_load_missing_raises(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(sms.ManifestError):
                sms.load_manifest(Path(td) / "nope.json")

    def test_load_bad_json_raises(self):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            with self.assertRaises(sms.ManifestError):
                sms.load_manifest(bad)

    def test_load_drifted_tools_raises(self):
        with tempfile.TemporaryDirectory() as td:
            drifted = Path(td) / "d.json"
            data = {"server": {}, "domains": [],
                    "tools": [{"name": "legacy_tool", "description": "x",
                               "inputSchema": {}}]}
            drifted.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(sms.ManifestError):
                sms.load_manifest(drifted)

    def test_fallback_descriptions_equal_contracts(self):
        fallback = sms.contract_descriptions()
        self.assertEqual(fallback,
                         {c["name"]: c["description"] for c in TOOL_CONTRACTS})


class AskSkeletonTest(unittest.TestCase):
    """回答骨架组装（纯函数）：两态必含 ID token（票 24 AC3 的载体）。"""

    ANSWERED = {
        "status": "answered", "waterfall_level": "一级·显式锚定",
        "anchor": "AGG-X-001",
        "hits": [{"id": "AGG-X-001", "model": "M1", "name": "对象甲",
                  "via": "显式锚定直达"},
                 {"id": "BH-X-Do", "model": "M2", "name": "处理对象甲",
                  "via": "--impact 反向 ownerEntity hops=1"}],
        "citations": ["AGG-X-001", "BH-X-Do", "RULE-X-001"],
        "scaffold_commands": ["python3 tools/graph_index.py ontology "
                              "--query AGG-X-001 --impact --json"],
        "note": "名下行为见 hits。", "ambiguous": False,
    }

    REFUSED = {
        "status": "refused_banned",
        "waterfall_level": "二级·ID/名称解析（GLS 禁用词处置）",
        "anchor": None,
        "hits": [{"id": "GLS-X-001", "model": "GLS", "name": "老口径",
                  "via": "GLS 禁用词命中"}],
        "citations": ["GLS-X-001", "RULE-X-009", "QR-X-002"],
        "scaffold_commands": [],
        "banned": {"id": "GLS-X-001", "term": "老口径", "status": "禁用",
                   "termType": "禁用词", "replacement_query": "替代口径=新口径"},
        "reason": "禁用词不得作为可用口径作答；替代口径指路 RULE-X-009/QR-X-002。",
        "ambiguous": False, "note": "",
    }

    def test_answered_has_citation_list_and_ids(self):
        text = sms.assemble_ask_text(self.ANSWERED)
        self.assertIn(CITATION_HEADER, text)
        for token in ("answered", "AGG-X-001", "BH-X-Do", "RULE-X-001"):
            self.assertIn(token, text)
        self.assertIn("graph_index.py", text)  # 装配指令可复现

    def test_refused_carries_verdict_and_pointer_ids(self):
        text = sms.assemble_ask_text(self.REFUSED)
        self.assertIn("refused_banned", text)
        self.assertIn(CITATION_HEADER, text)
        self.assertIn("GLS-X-001", text)   # 拒答也带 ID（禁用词条目+替代指路）
        self.assertIn("RULE-X-009", text)

    def test_missing_citations_line_present(self):
        verdict = {"status": "refused_out_of_surface", "waterfall_level": "x",
                   "anchor": "SCR-X-01", "hits": [], "citations": [],
                   "scaffold_commands": []}
        text = sms.assemble_ask_text(verdict)
        self.assertIn(CITATION_HEADER, text)      # 清单节固定在场
        self.assertIn("SCR-X-01", text)           # 锚定 ID token 可 grep
        self.assertIn("refused_out_of_surface", text)


class GraphSkeletonTest(unittest.TestCase):
    """graph_index 包装的骨架组装（纯函数）。"""

    REPORT = {
        "found": True, "query": "AGG-X-001",
        "node": {"id": "AGG-X-001", "model": "M1", "domain": "demo",
                 "file": "/repo/ontology/demo/m1.yaml", "line": 5,
                 "element": {"id": "AGG-X-001", "name": "对象甲"}},
        "closure": [{"id": "RULE-X-001", "model": "M3", "hops": 1,
                     "via": "appliedRules", "path": ["AGG-X-001", "RULE-X-001"]}],
        "impact": [{"id": "BH-X-Do", "model": "M2", "hops": 1,
                    "via": "ownerEntity", "path": ["BH-X-Do", "AGG-X-001"]}],
        "stats": {"nodes": 3, "edges": 2},
    }

    def test_found_report_contains_node_and_rows(self):
        text = sms.assemble_graph_text(self.REPORT)
        for token in ("AGG-X-001", "RULE-X-001", "BH-X-Do", "hops=1",
                      "m1.yaml:5"):
            self.assertIn(token, text)

    def test_not_found_report_explicit(self):
        text = sms.assemble_graph_text(
            {"found": False, "query": "AGG-X-999", "error": "未找到: AGG-X-999"})
        self.assertIn("未找到", text)
        self.assertIn("AGG-X-999", text)


@unittest.skipUnless(BOHAI.is_dir(), "真域缺失（跳过集成链路）")
class SubprocessIntegrationTest(unittest.TestCase):
    """子进程链路（真域，无 SDK 依赖）：core/graph_index 包装的真实回答。"""

    def test_ask_answered_contains_citations(self):
        text = sms._ask_text("ontology/bohai", "日产量口径是什么？")
        self.assertIn(CITATION_HEADER, text)
        self.assertIn("AGG-BOHAI-002", text)  # 出厂集 CORE-01 同源基准

    def test_ask_refused_banned_contains_pointers(self):
        text = sms._ask_text("ontology/bohai", "老完成率还能用吗？")
        self.assertIn("refused_banned", text)
        self.assertIn("GLS-BOHAI-001", text)
        self.assertIn("RULE-BOHAI-009", text)

    def test_ask_config_error_text(self):
        text = sms._ask_text("ontology/void-domain", "问题")
        self.assertIn("配置错误", text)

    def test_query_found_and_not_found(self):
        found = sms._graph_text("ontology/bohai", "AGG-BOHAI-001")
        self.assertIn("AGG-BOHAI-001", found)
        missing = sms._graph_text("ontology/bohai", "AGG-BOHAI-999")
        self.assertIn("未找到", missing)
        self.assertIn("AGG-BOHAI-999", missing)

    def test_impact_lists_dependents(self):
        text = sms._graph_text("ontology/bohai", "AGG-BOHAI-001", ("--impact",))
        self.assertIn("BH-BOHAI-", text)  # 名下行为反向可达（出厂集 AC2 同源）

    def test_closure_bad_hops_usage(self):
        text = sms._closure_text("ontology/bohai", "AGG-BOHAI-001", 0)
        self.assertIn("用法错误", text)


@unittest.skipUnless(sms._HAS_MCP, "需要 mcp SDK（票 24 venv 实弹，CI 无 SDK 跳过）")
class ProtocolFaceTest(unittest.TestCase):
    """协议面占位骨架（票 24 实弹）：SDK 在场时才实跑。"""

    def test_sdk_server_buildable(self):
        self.assertIn(sms._MCP_API or "", ("v2 mcp.server.MCPServer",
                                           "v1 mcp.server.fastmcp.FastMCP"))
        mcp = sms.build_server("ontology/bohai")
        self.assertIsNotNone(mcp)


if __name__ == "__main__":
    unittest.main()
