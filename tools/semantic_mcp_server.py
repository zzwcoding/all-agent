#!/usr/bin/env python3
"""semantic_mcp_server.py —— 语义服务 MCP stdio 服务器（票 23，PRD F11/R3）。

本体仓能力的 MCP 发布面：四工具 = 运行时语义服务的 stdio 包装——
  semantic_ask                    → tools/semantic_service_core.py（四步瀑布
                                    可机判核心，票 22；--json 裁决 → 骨架回答）
  semantic_query/closure/impact   → tools/graph_index.py --json（票 04）
判定核心与话术纪律（拒答三分支、ID 引用清单、只读）全部继承既有工具——本文件
只做子进程包装与回答骨架组装：零图算法、零瀑布逻辑、不自答。

回答文本必含 ID token：answered/拒答两态都有「本回答引用的元素 ID」清单节
（拒答态列禁用词条目/替代口径/近邻指路的真实 ID；检索面外态不泄细节、仅锚定
ID 可 grep）——票 24 实弹按此 grep。

CI 免疫红线（票 23 L0）：本仓 CI 不安装 mcp——SDK 缺席时本模块必须可 import
（try/except 收敛为 _HAS_MCP 标志），起服打印安装指引退出 2（AC4）；协议面
测试 skipUnless(_HAS_MCP)，出厂集只测引导路径与 manifest 装载，CI 全绿不碰 SDK。

API 面选型（记 lessons/23）：官方 SDK v2 `from mcp.server import MCPServer`
（references/tech-selection.md §3：2.x 已把 FastMCP 更名 MCPServer，transport
参数移到 run()）；v1 兼容回退 `mcp.server.fastmcp.FastMCP`。两线共用
`@server.tool(description=...)` 装饰器与 `.run()`（缺省 stdio）。HTTP 形态
（R3）：末行换 `mcp.run(transport="http", port=8000, path="/mcp")`。
票 24 实弹若实际安装版本 API 不符：允许小修本文件，出厂集不受影响（CI 不跑协议面）。

工具描述真源链：TOOL_CONTRACTS 模板常量（tools/mcp_manifest_gen.py，本文件
import 同源复用，防两处漂移）→ 生成 manifest → 起服装载入库 manifest 并与
模板逐项核对（防陈旧哨兵）；装载失败/漂移时回退模板常量并 stderr 报注。

CLI: python3 tools/semantic_mcp_server.py <ontology目录> [--strict]
  显式传本体目录（本体仓根或单域；不设默认——发布面不猜）。
  --strict：启动版本检出不符（已装 mcp ≠ tools/requirements-mcp.txt 钉版）
  即退出 2；缺省只 stderr 警告继续（提示性检出非硬闸，票 40）。

依赖：stdlib + PyYAML（既有工具侧）；mcp 仅本文件发布侧 import。
退出码：0 正常退出；2 无 mcp SDK（安装指引见 stderr）或 --strict 版本检出不符。

版本钉可执行化（票 40）：mcp==2.2.0 的唯一真源是 tools/requirements-mcp.txt
（升级须重跑票 24 smoke client，纪律见该文件注释与 docs/mcp-server.md）。
本文件在其上只做提示性检出：import mcp 成功后比对已装版本与钉版，一致静默、
不一致/钉版缺失 stderr 警告——默认警告继续，--strict 时不符即退。检出逻辑
抽成模块级纯函数 check_version（CLI 薄调用），无 SDK 环境也可全路径单测。
"""

import argparse
import importlib.metadata
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = Path(__file__).resolve().parent
CORE_CLI = TOOLS_DIR / "semantic_service_core.py"
GRAPH_INDEX = TOOLS_DIR / "graph_index.py"
MANIFEST_PATH = REPO_ROOT / "exports" / "mcp" / "capability-manifest.json"
PIN_FILE = TOOLS_DIR / "requirements-mcp.txt"

SUBPROCESS_TIMEOUT = 120
CITATION_HEADER = "本回答引用的元素 ID"

# ---------- SDK 引导（CI 免疫红线：缺席可 import，起服指路退出 2） ----------

try:  # 官方 SDK v2（tech-selection §3；2.x 起 FastMCP 更名 MCPServer）
    from mcp.server import MCPServer as _SdkServer
    _HAS_MCP = True
    _MCP_API = "v2 mcp.server.MCPServer"
except ImportError:  # v1 兼容回退
    try:
        from mcp.server.fastmcp import FastMCP as _SdkServer
        _HAS_MCP = True
        _MCP_API = "v1 mcp.server.fastmcp.FastMCP"
    except ImportError:
        _HAS_MCP = False
        _MCP_API = None

# 工具契约模板常量同源复用（描述真源=生成器；stdlib 零依赖，import 不可能失败）
from mcp_manifest_gen import SERVER_NAME, TOOL_CONTRACTS

INSTALL_HINT = (
    "未安装 mcp SDK，无法启动语义 MCP 服务器（all-agent-semantic）。\n"
    "  本服务器是发布侧组件：本体仓构建/CI 链路不安装 mcp（PRD「仅发布侧安装」）。\n"
    "  安装：pip install mcp（要求 Python 3.10+；建议 venv：\n"
    "    python3 -m venv .venv-mcp && .venv-mcp/bin/pip install mcp ）。\n"
    "  钉版安装（票 40）：python3 -m venv .venv-mcp && "
    ".venv-mcp/bin/pip install -r tools/requirements-mcp.txt。\n"
    "  详见 docs/mcp-server.md 与 references/tech-selection.md §3。")


# ---------- 版本检出（票 40：提示性非硬闸；纯函数可独立单测） ----------

_PIN_LINE = re.compile(r"^mcp==(\S+)$")


def _installed_mcp_version() -> str | None:
    """已装 mcp 版本（importlib.metadata 视角）；未装返回 None。"""
    try:
        return importlib.metadata.version("mcp")
    except importlib.metadata.PackageNotFoundError:
        return None


def _version_verdict(installed: str | None,
                     pin_path: Path) -> tuple[str | None, bool]:
    """（警告, 是否版本不符）。一致 → (None, False)；钉版缺失 → (降级警告, False)。"""
    pinned = _read_pin(pin_path)
    if pinned is None:
        return (f"mcp 版本检出降级：钉版文件缺失/不可读/无 mcp== 行"
                f"（{pin_path}）——跳过版本核对继续启动"
                f"（钉版以 tools/requirements-mcp.txt 为准，见 docs/mcp-server.md）。",
                False)
    if installed == pinned:
        return (None, False)
    shown = installed if installed is not None else "未检出（mcp 未安装？）"
    return (f"mcp 版本检出：已装 mcp {shown} ≠ 钉版 {pinned}"
            f"——核对 docs/mcp-server.md；继续启动（--strict 可改为强退）。",
            True)


def _read_pin(pin_path: Path) -> str | None:
    """读钉版文件的 mcp==X 行；缺失/不可读/无钉版行 → None（降级，不崩）。"""
    try:
        text = pin_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        m = _PIN_LINE.match(line)
        if m:
            return m.group(1)
    return None


def check_version(installed: str | None,
                  pin_path: Path = PIN_FILE) -> str | None:
    """版本检出纯函数（票 40）：返回警告文本，一致返回 None。

    - installed 与钉版一致 → None（静默）；
    - 不一致 → 不一致警告（--strict 时调用方据此强退）；
    - 钉版文件缺失/不可读/无 mcp== 行 → 降级警告（提示性检出非硬闸，不崩不挡）。
    CLI 侧薄调用（main → _version_verdict 取 mismatch 标志）；独立成纯函数
    是为了无 mcp SDK 环境也能注入式测全四路径（单测不装真包）。
    """
    return _version_verdict(installed, pin_path)[0]


class ManifestError(ValueError):
    """capability manifest 缺失/不可解析/与工具契约模板漂移。"""


# ---------- manifest 装载（描述真源核对 + 防陈旧哨兵） ----------


def _contract_fingerprint() -> list[tuple]:
    return [(c["name"], c["description"], c["inputSchema"])
            for c in TOOL_CONTRACTS]


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    """装载入库 capability manifest 并与模板契约逐项核对（防两处漂移）。"""
    if not path.is_file():
        raise ManifestError(
            f"capability manifest 不存在: {path}"
            f"（生成：python3 tools/mcp_manifest_gen.py ontology --out {path}）")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ManifestError(f"capability manifest 不是合法 JSON: {exc}") from exc
    tools = data.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ManifestError("capability manifest 缺 tools")
    fingerprint = [(t.get("name"), t.get("description"), t.get("inputSchema"))
                   for t in tools if isinstance(t, dict)]
    if fingerprint != _contract_fingerprint():
        names = [f[0] for f in fingerprint]
        expected = [c["name"] for c in TOOL_CONTRACTS]
        raise ManifestError(
            f"manifest 工具契约与生成器模板漂移: manifest={names} 模板={expected}"
            f"（再制：python3 tools/mcp_manifest_gen.py ontology --out {path}）")
    return data


def tool_descriptions(manifest: dict) -> dict:
    """manifest 是描述真源：装载核对通过后按此取描述。"""
    return {t["name"]: t.get("description", "") for t in manifest["tools"]}


def contract_descriptions() -> dict:
    """回退描述（manifest 缺失/漂移时）：同源模板常量。"""
    return {c["name"]: c["description"] for c in TOOL_CONTRACTS}


# ---------- 回答骨架组装（纯函数；ID token 纪律） ----------


def assemble_ask_text(verdict: dict) -> str:
    """core --json 裁决 → 骨架回答文本（成稿归 skill/LLM 工序，这里只装配）。"""
    lines = [f"【裁决】{verdict.get('status', '?')}"
             f"（{verdict.get('waterfall_level', '')}）"]
    if verdict.get("anchor"):
        lines.append(f"【锚定】@{verdict['anchor']}")
    hits = verdict.get("hits") or []
    if hits:
        lines.append("【命中】")
        lines.extend(f"- {h.get('id')} ({h.get('model')}) {h.get('name', '')}"
                     f" [{h.get('via', '')}]" for h in hits)
    if verdict.get("ambiguous"):
        lines.append("【注】命中多个候选（多义）：请用 @元素ID 锚定修饰，不擅自合并。")
    for term in verdict.get("terms") or []:
        lines.append(f"- 术语 {term.get('id')}「{term.get('term')}」"
                     f"status={term.get('status')}：{term.get('definition', '')}")
    for layer, state in (verdict.get("missing") or {}).items():
        lines.append(f"【缺件】{layer}: {state}")
    banned = verdict.get("banned")
    if banned:
        lines.append(f"【禁用词】{banned.get('term')}（{banned.get('id')}，"
                     f"{banned.get('status')}）——不得作为可用口径作答。")
    if verdict.get("reason"):
        lines.append(f"【理由】{verdict['reason']}")
    if verdict.get("note"):
        lines.append(f"【注】{verdict['note']}")
    scaffold = verdict.get("scaffold_commands") or []
    if scaffold:
        lines.append("【装配指令（证据集可复现）】")
        lines.extend(f"- {cmd}" for cmd in scaffold)
    citations = verdict.get("citations") or []
    lines.append(f"【{CITATION_HEADER}】")
    lines.append(" ".join(citations) if citations
                 else "（本裁决无可引用元素——拒答裁决见上，不返回面外细节）")
    return "\n".join(lines)


def assemble_graph_text(report: dict) -> str:
    """graph_index --json 报告 → 文本简报（节点/闭包/影响逐条带 ID）。"""
    if not report.get("found"):
        return (f"【查询】{report.get('query', '?')} 未找到\n"
                f"【说明】{report.get('error', '图内无此 ID（不做名称猜测）')}")
    node = report.get("node") or {}
    file_line = Path(node.get("file", "")).name
    lines = [f"【节点】{node.get('id')} ({node.get('model')})"
             f" 域={node.get('domain')}"
             f" 位置={file_line}:{node.get('line')}"]
    element = node.get("element") or {}
    labels = [f"{key}={element[key]}" for key in ("name", "alias")
              if element.get(key)]
    if labels:
        lines.append(f"【属性】{'；'.join(labels)}")
    closure = report.get("closure")
    if closure is not None:
        lines.append(f"【闭包 --closure】{len(closure)} 个下游节点")
        lines.extend(f"- {row['id']} ({row['model']}) hops={row['hops']}"
                     f" via={row['via']}" for row in closure)
    impact = report.get("impact")
    if impact is not None:
        lines.append(f"【影响 --impact】{len(impact)} 个受影响节点（依赖方）")
        lines.extend(f"- {row['id']} ({row['model']}) hops={row['hops']}"
                     f" via={row['via']}" for row in impact)
    stats = report.get("stats") or {}
    lines.append(f"【图统计】节点={stats.get('nodes')} 边={stats.get('edges')}")
    return "\n".join(lines)


# ---------- 子进程包装（判定核心的唯一通道；本文件零图算法零瀑布） ----------


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True,
                          cwd=str(REPO_ROOT), timeout=SUBPROCESS_TIMEOUT)


def _ask_text(ontology_dir: str, question: str) -> str:
    """semantic_ask → semantic_service_core --json（0 answered / 1 refused /
    2 配置错误；拒答也是有效裁决）。"""
    cmd = [sys.executable, str(CORE_CLI), ontology_dir,
           "--ask", question, "--json"]
    try:
        proc = _run(cmd)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return f"【配置错误】semantic_service_core 调用失败: {exc}"
    if proc.returncode not in (0, 1):
        detail = (proc.stderr or proc.stdout or "").strip()
        return f"【配置错误】semantic_service_core 退出码 {proc.returncode}: {detail}"
    try:
        verdict = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return f"【配置错误】core --json 输出不可解析: {exc}"
    return assemble_ask_text(verdict)


def _graph_text(ontology_dir: str, element_id: str, extra: tuple = ()) -> str:
    """semantic_query/closure/impact → graph_index --json（0 命中 / 1 未找到 /
    2 配置错误；未找到是有效结论）。"""
    cmd = [sys.executable, str(GRAPH_INDEX), ontology_dir,
           "--query", element_id, "--json", *extra]
    try:
        proc = _run(cmd)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return f"【配置错误】graph_index 调用失败: {exc}"
    if proc.returncode == 2:
        return f"【配置错误】graph_index: {(proc.stderr or '').strip()}"
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return f"【配置错误】graph_index --json 输出不可解析: {exc}"
    return assemble_graph_text(report)


def _closure_text(ontology_dir: str, element_id: str, hops: int) -> str:
    if hops < 1:
        return "【用法错误】hops 需要 >= 1（0 跳闭包无意义）"
    return _graph_text(ontology_dir, element_id, ("--closure", str(hops)))


# ---------- server 组装（仅 _HAS_MCP 时可调；协议面归票 24 实弹） ----------


def build_server(ontology_dir: str):
    """构建 MCP server 实例：manifest 装载（best-effort）+ 四工具注册。"""
    try:
        descriptions = tool_descriptions(load_manifest())
    except ManifestError as exc:
        print(f"注: capability manifest 装载失败（{exc}）；"
              f"工具描述回退生成器模板常量。", file=sys.stderr)
        descriptions = contract_descriptions()

    mcp = _SdkServer(SERVER_NAME)

    @mcp.tool(description=descriptions["semantic_ask"])
    def semantic_ask(question: str) -> str:
        """语义问答（描述真源=capability manifest/生成器模板）。"""
        return _ask_text(ontology_dir, question)

    @mcp.tool(description=descriptions["semantic_query"])
    def semantic_query(element_id: str) -> str:
        """按 ID 查节点（描述真源=capability manifest/生成器模板）。"""
        return _graph_text(ontology_dir, element_id)

    @mcp.tool(description=descriptions["semantic_closure"])
    def semantic_closure(element_id: str, hops: int = 3) -> str:
        """引用闭包（描述真源=capability manifest/生成器模板）。"""
        return _closure_text(ontology_dir, element_id, hops)

    @mcp.tool(description=descriptions["semantic_impact"])
    def semantic_impact(element_id: str) -> str:
        """影响分析（描述真源=capability manifest/生成器模板）。"""
        return _graph_text(ontology_dir, element_id, ("--impact",))

    return mcp


def main(argv=None) -> int:
    if not _HAS_MCP:  # 引导路径先于一切（含参数校验）：免疫出口唯一且稳定
        print(INSTALL_HINT, file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(
        description="语义服务 MCP stdio 服务器（票 23；四工具，判定核心=票 22/04）")
    ap.add_argument("ontology", help="本体目录（本体仓根或单域；显式传，不设默认）")
    ap.add_argument("--strict", action="store_true",
                    help="版本检出不符即退出 2（缺省仅 stderr 警告继续；票 40）")
    args = ap.parse_args(argv)

    # 启动版本检出（票 40）：先于 build_server——strict 不符即退，不起服
    warning, mismatch = _version_verdict(_installed_mcp_version(), PIN_FILE)
    if warning:
        print(warning, file=sys.stderr)
        if args.strict and mismatch:
            return 2

    mcp = build_server(args.ontology)
    print(f"{SERVER_NAME} MCP 服务器就绪：ontology={args.ontology} "
          f"API={_MCP_API} 工具=4（stdio；HTTP 形态见 docs/mcp-server.md）",
          file=sys.stderr)
    mcp.run()  # 缺省 stdio；HTTP（R3）：mcp.run(transport="http", port=8000, path="/mcp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
