#!/usr/bin/env python3
"""mcp_smoke_client.py 的单测（stdlib unittest；票 24）。

可测面（票 24 L0 设计裁决：可测面=用例表装载与期望结构，协议面 skipUnless）：
  1. 用例表结构——CASES 的 ID 集/工具名/入参形态/期望字段齐备且与四工具契约
     对得上（U1–U9：U1–U8=fixtures/mcp-publisher/cases 对照单 + U9=交接包
     指定的 closure(AGG-BOHAI-001, hops=2)）；
  2. 断言评估纯函数——evaluate_case 对命中/缺失/禁词/引用清单节/ID token
     的判定面（无 SDK 也可跑，AC3 grep 面的载体）；
  3. CI 免疫引导路径——无 mcp SDK 时 run_all/main 退出 2、stderr 含 venv
     安装指引（强制 _HAS_MCP=False 实测，不依赖环境是否装了 SDK）；
  4. 协议面——skipUnless(_HAS_MCP)：真起 server 实调全部用例（CI 裸环境
     天然跳过；实跑用 .venv-mcp/bin/python -m unittest 见 lessons/24）。
"""

import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mcp_smoke_client as msc

REPO = Path(__file__).resolve().parent.parent
BOHAI = REPO / "ontology" / "bohai"

EXPECTED_TOOLS = {"semantic_ask", "semantic_query", "semantic_closure",
                  "semantic_impact"}


class CaseTableTest(unittest.TestCase):
    """用例表装载与期望结构（票 24 指定的可测面）。"""

    def setUp(self):
        self.cases = msc.CASES

    def test_nine_cases_u1_to_u9(self):
        self.assertEqual([c["id"] for c in self.cases],
                         [f"U{i}" for i in range(1, 10)])

    def test_ids_unique(self):
        ids = [c["id"] for c in self.cases]
        self.assertEqual(len(ids), len(set(ids)))

    def test_tools_within_contract(self):
        for case in self.cases:
            self.assertIn(case["tool"], EXPECTED_TOOLS,
                          f"{case['id']} 工具名越出四工具契约")

    def test_four_tools_each_covered(self):
        self.assertEqual({c["tool"] for c in self.cases}, EXPECTED_TOOLS)

    def test_args_match_tool_schema(self):
        for case in self.cases:
            args = case["args"]
            if case["tool"] == "semantic_ask":
                self.assertIsInstance(args.get("question"), str,
                                      f"{case['id']} 缺 question")
                self.assertTrue(args["question"].strip())
            elif case["tool"] in ("semantic_query", "semantic_impact"):
                self.assertCountEqual(args.keys(), {"element_id"},
                                      f"{case['id']} 入参应为 element_id 单键")
            elif case["tool"] == "semantic_closure":
                self.assertCountEqual(args.keys(), {"element_id", "hops"},
                                      f"{case['id']} 入参应为 element_id+hops")
                self.assertGreaterEqual(args["hops"], 1,
                                        f"{case['id']} hops 需要 >=1")

    def test_expectations_present(self):
        for case in self.cases:
            self.assertTrue(case["expect_contains"],
                            f"{case['id']} 缺 expect_contains")
            for token in case["expect_contains"]:
                self.assertIsInstance(token, str)
                self.assertTrue(token.strip())
            self.assertIsInstance(case["expect_not_contains"], list)
            self.assertTrue(case["note"].strip(), f"{case['id']} 缺真源注")

    def test_ask_cases_demand_citation_header(self):
        """AC3：每个 ask 用例都断言「本回答引用的元素 ID」清单节在场。"""
        for case in self.cases:
            if case["tool"] == "semantic_ask":
                self.assertTrue(case["expect_citation_header"],
                                f"{case['id']} 未断言引用清单节")

    def test_u2_missing_state_no_id_token(self):
        """U2（refused_missing 无近邻）不硬凑 ID——AC3 由引用清单节承载。"""
        u2 = next(c for c in self.cases if c["id"] == "U2")
        self.assertFalse(u2["expect_id_token"])

    def test_u8_impact_asserts_shape_not_count(self):
        """U8 断形态不断量级快照（票 66）：影响集规模随本体演进是活数
        （票 24 基线 56 → 2026-09-24 demo 实点 64，钉快照必陈旧）——
        形态 token 与非空守卫必须在位，量级快照 token 不得入期望。"""
        u8 = next(c for c in self.cases if c["id"] == "U8")
        contains = "；".join(u8["expect_contains"])
        self.assertIn("【影响 --impact】", contains)
        self.assertIn("个受影响节点（依赖方）", contains)
        self.assertIn("BH-BOHAI-QueryWellDailyOutput", contains)
        self.assertIn("0 个受影响节点", "；".join(u8["expect_not_contains"]))
        for token in u8["expect_contains"]:
            self.assertNotRegex(
                token, r"\d+ 个受影响节点",
                f"U8 期望钉了量级快照（随本体演进必陈旧）: {token}")

    def test_u9_is_handover_closure_call(self):
        """U9=票 24 交接包指定：closure(AGG-BOHAI-001, hops=2)，钉空闭包诚实报告。"""
        u9 = next(c for c in self.cases if c["id"] == "U9")
        self.assertEqual(u9["tool"], "semantic_closure")
        self.assertEqual(u9["args"], {"element_id": "AGG-BOHAI-001", "hops": 2})
        self.assertIn("0 个下游节点", "；".join(u9["expect_contains"]))


class EvaluateCaseTest(unittest.TestCase):
    """断言评估纯函数（无 SDK 也可跑；AC3 grep 面的载体）。"""

    U1 = next(c for c in msc.CASES if c["id"] == "U1")
    U2 = next(c for c in msc.CASES if c["id"] == "U2")
    U4 = next(c for c in msc.CASES if c["id"] == "U4")

    def test_passing_text_all_green(self):
        text = ("【裁决】answered（二级·ID/名称解析）\n"
                "- AGG-BOHAI-002 (M1) 日产计量\n"
                "【理由】……RULE-BOHAI-002……命中多个候选……\n"
                "【本回答引用的元素 ID】\nAGG-BOHAI-002 RULE-BOHAI-002\n")
        checks = msc.evaluate_case(self.U1, text, is_error=False)
        self.assertTrue(all(ok for _, ok, _ in checks),
                        f"应全过，实得: {[(n, ok) for n, ok, _ in checks if not ok]}")

    def test_missing_token_detected(self):
        checks = dict((n, ok) for n, ok, _ in
                      msc.evaluate_case(self.U1, "【裁决】refused_missing\n",
                                        is_error=False))
        self.assertFalse(checks["contains[AGG-BOHAI-002]"])
        self.assertFalse(checks["citation_header"])
        self.assertFalse(checks["id_token"])

    def test_protocol_error_flagged(self):
        checks = dict((n, ok) for n, ok, _ in
                      msc.evaluate_case(self.U1, "任何文本", is_error=True))
        self.assertFalse(checks["is_error"])

    def test_banned_token_detected(self):
        """U4 的 MU 细节非泄清单：出现即红（fixture AC4 正则的 token 面镜像）。"""
        text = ("【裁决】refused_out_of_surface\n【锚定】@SCR-BOHAI-01\n"
                "camp=build-contract\n【本回答引用的元素 ID】\n（无可引用）\n"
                "gridDaily 字段是……\n")
        checks = dict((n, ok) for n, ok, _ in msc.evaluate_case(self.U4, text, False))
        self.assertFalse(checks["not_contains[gridDaily]"])

    def test_id_token_regex_shapes(self):
        hits = msc.ID_TOKEN_RE.findall(
            "AGG-BOHAI-001 GLS-BOHAI-002 BH-BOHAI-QueryWellDailyOutput "
            "QR-BOHAI-01 SCR-BOHAI-01 RULE-BOHAI-019 xBOHAI-1 -BOHAI-9")
        self.assertIn("AGG-BOHAI-001", hits)
        self.assertIn("BH-BOHAI-QueryWellDailyOutput", hits)
        self.assertIn("SCR-BOHAI-01", hits)
        self.assertNotIn("xBOHAI-1", hits)
        self.assertNotIn("-BOHAI-9", hits)

    def test_summarize_text(self):
        self.assertEqual(msc.summarize_text(""), "（空回答）")
        one_line = msc.summarize_text("第一行\n第二行\n第三行\n第四行\n第五行")
        self.assertIn("…（共 5 行）", one_line)
        self.assertTrue(one_line.startswith("第一行"))


class BootstrapTest(unittest.TestCase):
    """CI 免疫引导路径：无 SDK → exit 2 + stderr 安装指引（强制标志实测）。"""

    def setUp(self):
        self._saved = msc._HAS_MCP
        msc._HAS_MCP = False

    def tearDown(self):
        msc._HAS_MCP = self._saved

    def test_run_all_exit_2_with_hint(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code, records = msc.run_all()
        self.assertEqual(code, 2)
        self.assertEqual(records, [])
        self.assertIn("pip install mcp", err.getvalue())
        self.assertIn(".venv-mcp", err.getvalue())

    def test_main_exit_2_with_hint(self):
        err, out = io.StringIO(), io.StringIO()
        with redirect_stderr(err), redirect_stdout(out):
            code = msc.main([])
        self.assertEqual(code, 2)
        self.assertIn("venv", err.getvalue())

    def test_list_mode_works_without_sdk(self):
        """--list 只读用例表（纯 stdlib）：无 SDK 也 exit 0。"""
        out = io.StringIO()
        with redirect_stdout(out):
            code = msc.main(["--list"])
        self.assertEqual(code, 0)
        self.assertIn("U9", out.getvalue())


@unittest.skipUnless(msc._HAS_MCP, "需要 mcp SDK（.venv-mcp/bin/python 实跑；CI 裸环境跳过）")
@unittest.skipUnless(BOHAI.is_dir(), "真域缺失（跳过集成链路）")
class ProtocolSmokeTest(unittest.TestCase):
    """协议面实弹：真起 server、经 MCP stdio 实调全部用例（票 24 AC1/AC2/AC3）。"""

    def test_full_run_all_pass_exit_0(self):
        out = io.StringIO()
        code, records = None, []
        with redirect_stdout(out):
            code, records = msc.run_all()  # 缺省 ontology/bohai
        self.assertEqual(code, 0, f"smoke 未全过，输出：\n{out.getvalue()}")
        self.assertEqual(len(records), 9)
        self.assertTrue(all(r["pass"] for r in records),
                        f"失败用例: {[r['id'] for r in records if not r['pass']]}")

    def test_answers_carry_id_references(self):
        """AC3：全部回答带 ID 引用（ask=引用清单节在场；graph=BOHAI ID token）。"""
        out = io.StringIO()
        with redirect_stdout(out):
            _, records = msc.run_all()
        for r in records:
            if r["tool"] == "semantic_ask":
                self.assertIn(msc.CITATION_HEADER, r["text"], f"{r['id']} 缺引用清单节")
            self.assertTrue(msc.ID_TOKEN_RE.search(r["text"]) or r["id"] == "U2",
                            f"{r['id']} 无 ID token（U2 缺件态除外）")


if __name__ == "__main__":
    unittest.main()
