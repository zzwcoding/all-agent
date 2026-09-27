#!/usr/bin/env python3
"""mcp_smoke_client.py —— MCP 端到端实弹 smoke 客户端（票 24，PRD F11）。

以官方 mcp SDK 客户端 API（stdio 子进程）拉起 tools/semantic_mcp_server.py，
顺序实调四工具（用例表 CASES = fixtures/mcp-publisher/cases/mcp-tool-contract-usecases.md
U1–U8 对照单 + 票 24 交接包指定的 closure(AGG-BOHAI-001, hops=2) 一发），逐调用
打印请求/响应摘要（走查证据），并内置出厂集同源断言（期望值抄自
fixtures/semantic-service/assertions.json CORE-01/03/04/05 与 cases/ 对照单，
直连 CLI 基线定准）——经 MCP 协议实调的结果必须与出厂集行为一致（票 24 AC2）。

AC3 grep 面（内置为断言，不靠人眼）：每个 ask 回答必带「本回答引用的元素 ID」
清单节；每个回答（除 refused_missing 无近邻可指路的缺件态）必含至少一个
*-BOHAI-* ID token。refused_missing 态按 core 纪律不硬凑近邻 ID——引用清单节
在场并明示「无可引用元素」即其 AC3 形态。

CLI: .venv-mcp/bin/python tools/mcp_smoke_client.py [ontology目录] [--full] [--list]
  ontology目录  传给 server 的本体目录（相对仓根解释；缺省 ontology/bohai）
  --full        额外打印每个回答全文（走查记录留证用）
  --list        只列用例表不实调（无 SDK 也可用——用例表与断言结构是纯 stdlib）

退出码：0 全部用例过；1 有失败（含协议/异常）；2 无 mcp SDK（stderr 打印
安装指引——与 server 同一免疫纪律，指引建 .venv-mcp）。

依赖：stdlib；mcp 仅客户端协议面 import（try/except 收敛 _HAS_MCP）。
环境（票 24 实测）：mcp 2.2.0 + Python 3.11（.venv-mcp；venv 内同时装有
PyYAML——server 的 core/graph_index 子进程要用）。
"""

import argparse
import asyncio
import importlib.metadata
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVER_SCRIPT = Path(__file__).resolve().parent / "semantic_mcp_server.py"
DEFAULT_ONTOLOGY = "ontology/bohai"
# 多域示例（票 72）：实跑域=ontology/bohai、ontology/his；豁免注记域=ontology/pkb
# （smoke 的 ID 断言正则为 bohai 词面——跨域跑请先核对用例面，见 --help）
CITATION_HEADER = "本回答引用的元素 ID"
SERVER_NAME_EXPECTED = "all-agent-semantic"  # 契约钉死（真源=exports/mcp/capability-manifest.json）
CALL_TIMEOUT_SECONDS = 120

ID_TOKEN_RE = re.compile(r"\b[A-Z]{2,}[A-Z0-9]*-BOHAI-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b")

INSTALL_HINT = (
    "未安装 mcp SDK，无法运行 MCP smoke 客户端（票 24 实弹）。\n"
    "  本客户端是发布侧组件：本体仓构建/CI 链路不安装 mcp（CI 照常全绿）。\n"
    "  安装（建议 venv 隔离）：python3 -m venv .venv-mcp && .venv-mcp/bin/pip install mcp\n"
    "  之后用 .venv-mcp/bin/python 跑本客户端与 tools/semantic_mcp_server.py。\n"
    "  详见 docs/mcp-server.md 与 docs/walkthrough/step7-mcp-e2e.md。")

# ---------- 用例表（真源=fixtures/mcp-publisher/cases U1–U8 + 票 24 交接包） ----------
#
# expect_contains / expect_not_contains 的值抄自出厂集断言（CORE-01/03/04/05、
# cases/ 对照单 U1–U8）与直连 CLI 基线实测（2026-09-19，ontology/bohai 真域）。
# expect_citation_header：ask 回答必带引用清单节（AC3）。
# expect_id_token：回答必含 *-BOHAI-* ID token（AC3 grep 面；U2 缺件态无近邻
# 可指路、core 纪律不硬凑 ID——False，AC3 由引用清单节承载）。


def _cases():
    return [
        {
            "id": "U1",
            "tool": "semantic_ask",
            "args": {"question": "日产量口径是什么？"},
            "expect_contains": ["answered", "AGG-BOHAI-002", "RULE-BOHAI-002",
                                "命中多个候选"],
            "expect_not_contains": [],
            "expect_citation_header": True,
            "expect_id_token": True,
            "note": "answered（ambiguous 列候选是合法形态）；真源=CORE-01/U1",
        },
        {
            "id": "U2",
            "tool": "semantic_ask",
            "args": {"question": "桶油增产成本的口径是什么？"},
            "expect_contains": ["refused_missing", "未建", "待 Owner", "提案流程"],
            "expect_not_contains": [],
            "expect_citation_header": True,
            "expect_id_token": False,  # 缺件态无近邻不硬凑：引用清单节在场即 AC3
            "note": "refused_missing：缺件三层未建+待 Owner+提案流程；真源=CORE-03/U2",
        },
        {
            "id": "U3",
            "tool": "semantic_ask",
            "args": {"question": "老完成率还能用吗？"},
            "expect_contains": ["refused_banned", "GLS-BOHAI-001",
                                "RULE-BOHAI-009", "QR-BOHAI-002", "产量完成率"],
            "expect_not_contains": [],
            "expect_citation_header": True,
            "expect_id_token": True,
            "note": "refused_banned：GLS 禁用词命中+替代口径真实 ID 指路；真源=CORE-05/U3",
        },
        {
            "id": "U4",
            "tool": "semantic_ask",
            "args": {"question": "@SCR-BOHAI-01 的界面细节"},
            "expect_contains": ["refused_out_of_surface", "camp=build-contract",
                                "SCR-BOHAI-01"],
            "expect_not_contains": [
                "MENU-", "gridDaily", "screenType", "GRID",
                "日产量列表", "单井日产量录入", "产量管理",
            ],
            "expect_citation_header": True,
            "expect_id_token": True,
            "note": "面外拒答不泄 MU 细节（非泄清单抄 fixtures AC4 正则 token）；真源=CORE-04/U4",
        },
        {
            "id": "U5",
            "tool": "semantic_query",
            "args": {"element_id": "AGG-BOHAI-001"},
            "expect_contains": ["【节点】AGG-BOHAI-001", "(M1)", "域=bohai",
                                "位置=m1-object-model.yaml", "【图统计】"],
            "expect_not_contains": [],
            "expect_citation_header": False,
            "expect_id_token": True,
            "note": "节点简报：ID/model/域/文件位置；真源=cases U5",
        },
        {
            "id": "U6",
            "tool": "semantic_query",
            "args": {"element_id": "AGG-BOHAI-999"},
            "expect_contains": ["AGG-BOHAI-999", "未找到", "不做名称猜测"],
            "expect_not_contains": [],
            "expect_citation_header": False,
            "expect_id_token": True,  # 未找到也回带所查 ID（不猜不编）
            "note": "未找到明确报错不猜；真源=cases U6 + 出厂集「机读佐证（未找到不猜）」",
        },
        {
            "id": "U7",
            "tool": "semantic_closure",
            "args": {"element_id": "GLS-BOHAI-002", "hops": 1},
            "expect_contains": ["【闭包 --closure】", "AGG-BOHAI-001",
                                "AGG-BOHAI-002", "relatedObjectRefs", "hops=1"],
            "expect_not_contains": [],
            "expect_citation_header": False,
            "expect_id_token": True,
            "note": "GLS 术语闭包沿 relatedObjectRefs 正向 1 跳；真源=cases U7 + 票 17 机读佐证",
        },
        {
            "id": "U8",
            "tool": "semantic_impact",
            "args": {"element_id": "AGG-BOHAI-001"},
            "expect_contains": ["【影响 --impact】", "个受影响节点（依赖方）",
                                "BH-BOHAI-QueryWellDailyOutput", "hops=1"],
            "expect_not_contains": ["0 个受影响节点"],
            "expect_citation_header": False,
            "expect_id_token": True,
            "note": "影响集非空且含 BH-BOHAI-* 名下行为（反向依赖）；量级随本体演进是"
                    "活数不钉快照（票 66：票 24 基线 56 已陈旧至 64）——契约断形态不断数",
        },
        {
            "id": "U9",
            "tool": "semantic_closure",
            "args": {"element_id": "AGG-BOHAI-001", "hops": 2},
            "expect_contains": ["【节点】AGG-BOHAI-001", "【闭包 --closure】0 个下游节点"],
            "expect_not_contains": [],
            "expect_citation_header": False,
            "expect_id_token": True,
            "note": "票 24 交接包指定一发；AGG-BOHAI-001 无正向引用（只被引用），"
                    "空闭包=真实图形态，断言钉「0 个下游节点」的诚实报告（不硬凑）",
        },
    ]


CASES = _cases()

# ---------- SDK 引导（与 server 同纪律：缺席可 import，运行指路退出 2） ----------

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    _HAS_MCP = True
except ImportError:
    _HAS_MCP = False


def sdk_version() -> str:
    if not _HAS_MCP:
        return "（未安装）"
    try:
        return importlib.metadata.version("mcp")
    except importlib.metadata.PackageNotFoundError:  # pragma: no cover
        return "（已 import 但元数据缺失）"


# ---------- 断言评估（纯函数，无 SDK 也可单测） ----------


def evaluate_case(case: dict, text: str, is_error: bool) -> list[tuple]:
    """对单条回答评估内置断言，返回 (检查名, 是否过, 明细) 列表。"""
    checks = []
    for token in case["expect_contains"]:
        checks.append((f"contains[{token}]", token in text, "命中" if token in text else "缺失"))
    for token in case["expect_not_contains"]:
        checks.append((f"not_contains[{token}]", token not in text,
                       "未出现" if token not in text else "出现（禁）"))
    if case["expect_citation_header"]:
        ok = CITATION_HEADER in text
        checks.append(("citation_header", ok, "引用清单节在场" if ok else f"缺「{CITATION_HEADER}」节"))
    if case["expect_id_token"]:
        found = ID_TOKEN_RE.findall(text)
        ok = bool(found)
        checks.append(("id_token", ok, f"{len(found)} 个 BOHAI ID" if ok else "无 *-BOHAI-* ID"))
    checks.append(("is_error", not is_error, "False" if not is_error else "True（协议层错误）"))
    return checks


def summarize_text(text: str, max_lines: int = 4) -> str:
    """回答首行摘要（走查记录每调用一行的素材；全文用 --full）。"""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return "（空回答）"
    head = lines[:max_lines]
    tail = f" …（共 {len(lines)} 行）" if len(lines) > max_lines else ""
    return " / ".join(head) + tail


# ---------- 协议面（仅 _HAS_MCP 时可跑） ----------


def _text_of(result) -> str:
    """CallToolResult → 文本（TextContent 块按序拼接）。"""
    blocks = []
    for item in result.content or []:
        kind = getattr(item, "type", None)
        if kind == "text":
            blocks.append(item.text)
        else:  # 未知块类型如实登记，不静默吞
            blocks.append(f"【非文本内容块 type={kind}】")
    return "\n".join(blocks)


async def _run_async(ontology_dir: str, cases: list, full: bool, out) -> tuple:
    """一次连接顺序实调全部用例，返回 (是否全过, 结果记录列表)。"""
    server_cmd = [sys.executable, str(SERVER_SCRIPT), ontology_dir]
    params = StdioServerParameters(
        command=server_cmd[0], args=server_cmd[1:], cwd=str(REPO_ROOT))
    all_ok = True
    records = []

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            # pydantic 字段是 snake_case（实测 2.2.0：server_info.name / protocol_version）
            server_name = getattr(getattr(init, "server_info", None), "name", "?")
            protocol = getattr(init, "protocol_version", "?")
            init_ok = server_name == SERVER_NAME_EXPECTED
            all_ok &= init_ok
            print(f"[init] server={server_name}（期望 {SERVER_NAME_EXPECTED}）"
                  f" protocol={protocol}"
                  f" → {'PASS' if init_ok else 'FAIL'}", file=out)
            if not init_ok:
                return False, records

            tools = await session.list_tools()
            tool_names = sorted(t.name for t in tools.tools)
            expected_tools = sorted({c["tool"] for c in cases})
            tools_ok = tool_names == expected_tools
            all_ok &= tools_ok
            print(f"[tools] {tool_names}（期望 {expected_tools}）"
                  f" → {'PASS' if tools_ok else 'FAIL'}", file=out)
            if not tools_ok:
                return False, records

            for case in cases:
                print(f"[{case['id']}] tool={case['tool']} args="
                      f"{json.dumps(case['args'], ensure_ascii=False)}", file=out)
                try:
                    result = await session.call_tool(
                        case["tool"], case["args"],
                        read_timeout_seconds=CALL_TIMEOUT_SECONDS)
                    text = _text_of(result)
                    is_error = bool(result.is_error)
                except Exception as exc:  # 协议/子进程异常=该用例失败，不中断后续用例
                    text = f"【调用异常】{type(exc).__name__}: {exc}"
                    is_error = True
                checks = evaluate_case(case, text, is_error)
                case_ok = all(ok for _, ok, _ in checks)
                all_ok &= case_ok
                print(f"     响应: is_error={is_error} 字符数={len(text)}", file=out)
                print(f"     摘要: {summarize_text(text)}", file=out)
                for name, ok, detail in checks:
                    print(f"     断言 {'过' if ok else '红'}: {name}（{detail}）", file=out)
                if full:
                    print("     --- 回答全文 ---", file=out)
                    for line in text.splitlines():
                        print(f"     | {line}", file=out)
                print(f"     → {'PASS' if case_ok else 'FAIL'}（{case['note']}）", file=out)
                records.append({
                    "id": case["id"], "tool": case["tool"], "args": case["args"],
                    "pass": case_ok, "text": text,
                    "checks": [(n, bool(ok), d) for n, ok, d in checks],
                })
    return all_ok, records


def run_all(ontology_dir: str = DEFAULT_ONTOLOGY, full: bool = False,
            out=None) -> tuple:
    """实弹入口：起服 → 实调全部用例。返回 (退出码, 结果记录)。"""
    out = out if out is not None else sys.stdout
    if not _HAS_MCP:
        print(INSTALL_HINT, file=sys.stderr)
        return 2, []
    if not SERVER_SCRIPT.is_file():
        print(f"server 脚本不存在: {SERVER_SCRIPT}", file=sys.stderr)
        return 2, []
    try:
        ok, records = asyncio.run(_run_async(ontology_dir, CASES, full, out))
    except KeyboardInterrupt:  # pragma: no cover
        raise
    except Exception as exc:
        print(f"【协议异常】起服/会话失败: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1, []
    if not records:
        print("\n合计: 未进入用例实调（init/工具清单未过，见上方 FAIL 行）", file=out)
        return (0 if ok else 1), records
    passed = sum(1 for r in records if r["pass"])
    print(f"\n合计: {passed}/{len(records)} 用例过"
          f"（mcp {sdk_version()} / Python {sys.version.split()[0]}；"
          f"起服式 {Path(sys.executable).name} tools/semantic_mcp_server.py {ontology_dir}）",
          file=out)
    return (0 if ok else 1), records


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="MCP 端到端实弹 smoke 客户端（票 24；四工具实调+出厂集同源断言）")
    ap.add_argument("ontology", nargs="?", default=DEFAULT_ONTOLOGY,
                    help=f"本体目录，相对仓根（缺省 {DEFAULT_ONTOLOGY}）")
    ap.add_argument("--full", action="store_true", help="打印每个回答全文（走查留证）")
    ap.epilog = ("多域示例（票 72）：python3 tools/mcp_smoke_client.py ontology/his "
                 "——注意 smoke 用例与 ID 断言正则为 bohai 词面（ID_TOKEN_RE），"
                 "跨域实跑前先核用例面；pkb 为豁免注记域（无 smoke 用例）。")
    ap.add_argument("--list", action="store_true", help="只列用例表不实调")
    args = ap.parse_args(argv)

    if args.list:
        for c in CASES:
            exp = "；".join(c["expect_contains"])
            print(f"{c['id']} {c['tool']} {json.dumps(c['args'], ensure_ascii=False)}"
                  f"\n    期望: {exp}\n    注: {c['note']}")
        return 0

    code, _ = run_all(args.ontology, full=args.full)
    return code


if __name__ == "__main__":
    sys.exit(main())
