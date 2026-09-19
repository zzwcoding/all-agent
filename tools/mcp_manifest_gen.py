#!/usr/bin/env python3
"""mcp_manifest_gen.py —— MCP capability manifest 生成器（票 23，PRD F11）。

读本体仓根，确定性生成语义 MCP 服务器的能力清单（发布物的「生成物」）：
  - 域发现：扫 */manifest.json（照 graph_index.discover_domains 同一手法的
    第三个读者——域目录 = 含 manifest.json 的目录，target 本身是域则单域）；
  - 每域 profile/camp 概览：读 ontology/schema/model-registry.json，按该域
    profile 圈定模型面、剔除域 manifest 的 omittedModels，逐模型登
    name/modelType/camp（检索面=业务核 business-core 的机械概览）；
  - 四工具契约：name/description/inputSchema 手写为模板常量 TOOL_CONTRACTS
    （描述真源；semantic_mcp_server 从本模块 import 同一常量，防两处漂移）。

确定性红线（票 23 L0）：**零时间戳**——输出不含任何日期/时间形态 token，
同本体仓任意机器重生成字节一致。入库副本 exports/mcp/capability-manifest.json
是派生物禁手改，防陈旧断言 = fixtures/mcp-publisher AC2（--check 再生一致）。

CLI: python3 tools/mcp_manifest_gen.py <ontology目录> [--out <路径>] [--check <路径>]
  缺省        manifest JSON 打到 stdout
  --out <路径> 写文件（UTF-8；stdout 保持安静）
  --check <路径> 现场重生成并与给定入库副本逐字节比对：
               一致退出 0；不一致/副本缺失退出 1（防陈旧断言的载体）
退出码：0 成功/一致；1 --check 不一致或副本缺失；2 配置错误
（目标不存在/无域/registry 缺失或坏/域缺 profile——拒收部分清单）。

依赖：Python3 stdlib 零第三方（只读 JSON，不碰 YAML——模型面概览取自注册表）。
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SERVER_NAME = "all-agent-semantic"

# ---------- 四工具契约模板（描述真源；semantic_mcp_server import 同源复用） ----------

TOOL_CONTRACTS = (
    {
        "name": "semantic_ask",
        "description": (
            "语义问答（受控检索瀑布：显式锚定→ID/名称解析→闭包装配→可拒答）。"
            "返回确定性骨架回答，必带「本回答引用的元素 ID」清单（ID 可 grep 追溯）；"
            "仓内没有/检索面外/禁用词按裁决拒答并说明缺口，绝不编造；"
            "写意图一律回「走提案流程」（本服务只读）。问题可含 @元素ID 显式锚定。"),
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string",
                             "description": "业务问题（可含 @元素ID 显式锚定）"},
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    },
    {
        "name": "semantic_query",
        "description": (
            "按元素 ID 查询单个本体节点：存在性、模型归属、域、文件位置与属性简报；"
            "未找到明确报错不猜（不做名称猜测、不做近似拼写建议）。"),
        "inputSchema": {
            "type": "object",
            "properties": {
                "element_id": {"type": "string",
                               "description": "元素 ID（如 AGG-BOHAI-001）"},
            },
            "required": ["element_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "semantic_closure",
        "description": (
            "引用闭包：沿 ref 正向走 N 跳，返回该元素引用的下游节点集"
            "（逐条带引用字段与跳数；N>=1，默认 3）。"),
        "inputSchema": {
            "type": "object",
            "properties": {
                "element_id": {"type": "string", "description": "元素 ID"},
                "hops": {"type": "integer", "minimum": 1, "default": 3,
                         "description": "闭包跳数（>=1，默认 3）"},
            },
            "required": ["element_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "semantic_impact",
        "description": (
            "影响分析：沿依赖边反向走到底，返回受影响节点集"
            "（谁引用它：行为/规则/流程/查询出口等，逐条带引用字段与跳数）。"),
        "inputSchema": {
            "type": "object",
            "properties": {
                "element_id": {"type": "string", "description": "元素 ID"},
            },
            "required": ["element_id"],
            "additionalProperties": False,
        },
    },
)


class ConfigError(ValueError):
    """本体根/注册表配置不可用（退出码 2）。"""


# ---------- 读取（只读 JSON，零第三方） ----------


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"{path} 不存在") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ConfigError(f"{path} 不是合法 JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"{path} 顶层必须是映射")
    return data


def resolve_schema_dir(target: Path) -> Path | None:
    """schema 目录定位（照 schema_check/graph_index 同一手法）。"""
    for cand in (target / "schema", target.parent / "schema"):
        if cand.is_dir():
            return cand
    return None


def discover_domains(target: Path) -> list[Path]:
    """域目录 = 含 manifest.json 的目录；target 本身是域则单域（同 graph_index）。"""
    if (target / "manifest.json").is_file():
        return [target]
    return sorted(sub for sub in target.iterdir()
                  if sub.is_dir() and sub.name != "schema"
                  and (sub / "manifest.json").is_file())


def source_label(target: Path) -> str:
    """generatedFrom.source：仓内取仓根相对 posix 路径，仓外取绝对路径。"""
    try:
        return target.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(target.resolve())


# ---------- 清单组装（确定性：注册表序 + 域名字典序，零时间戳） ----------


def domain_overview(domain_dir: Path, registry_models: dict) -> dict:
    """单域概览：manifest 字段 + profile 圈定模型面（剔除 omittedModels）。"""
    manifest = load_json(domain_dir / "manifest.json")
    profile = manifest.get("profile")
    if not profile:
        raise ConfigError(f"{domain_dir / 'manifest.json'} 缺 profile（域声明必备）")
    omitted = [{"model": o.get("model"), "reason": o.get("reason")}
               for o in manifest.get("omittedModels", [])
               if isinstance(o, dict) and o.get("model")]
    omitted_names = {o["model"] for o in omitted}
    models = []
    for model_id, info in registry_models.items():
        if not isinstance(info, dict):
            continue
        if profile not in (info.get("profiles") or []):
            continue
        if model_id in omitted_names:
            continue
        models.append({"model": model_id, "name": info.get("name", model_id),
                       "modelType": info.get("modelType"),
                       "camp": info.get("camp")})
    row = {"domain": manifest.get("domain", domain_dir.name),
           "label": manifest.get("label", ""), "profile": profile,
           "models": models}
    if "schemaVersion" in manifest:
        row["schemaVersion"] = manifest["schemaVersion"]
    if omitted:
        row["omittedModels"] = omitted
    return row


def build_manifest(target: Path) -> dict:
    """对本体根组装完整 manifest（纯函数式：同输入同输出，零副作用）。"""
    target = target.resolve()
    if not target.is_dir():
        raise ConfigError(f"目标目录不存在: {target}")
    schema_dir = resolve_schema_dir(target)
    if schema_dir is None:
        raise ConfigError(f"{target} 及其上级都没有 schema/ 目录")
    registry = load_json(schema_dir / "model-registry.json")
    registry_models = registry.get("models")
    if not isinstance(registry_models, dict) or not registry_models:
        raise ConfigError(f"{schema_dir / 'model-registry.json'} 缺 models")
    domain_dirs = discover_domains(target)
    if not domain_dirs:
        raise ConfigError(f"{target} 下未找到任何域（域目录须含 manifest.json）")
    domains = sorted(
        (domain_overview(d, registry_models) for d in domain_dirs),
        key=lambda row: row["domain"])
    return {
        "status": "已生成",
        "server": {
            "name": SERVER_NAME,
            "title": "All-agent 语义服务 MCP 服务器",
            "transport": "stdio",
            "entry": "tools/semantic_mcp_server.py",
            "run": "python3 tools/semantic_mcp_server.py <ontology目录>",
            "sdk": "官方 mcp SDK（仅发布侧安装；本体仓构建/CI 链路不依赖）",
            "docs": "docs/mcp-server.md",
        },
        "domains": domains,
        "tools": [
            {"name": c["name"], "description": c["description"],
             "inputSchema": c["inputSchema"]}
            for c in TOOL_CONTRACTS
        ],
        "generatedFrom": {
            "generator": "tools/mcp_manifest_gen.py",
            "source": source_label(target),
            "registryVersion": registry.get("version", ""),
            "note": "确定性派生物：零时间戳，同本体仓任意机器重生成字节一致；"
                    "禁手改，防陈旧断言=fixtures/mcp-publisher AC2（--check 再制一致）",
        },
    }


def render(target: Path) -> str:
    """manifest → 确定性文本（ensure_ascii=False + indent=2 + 尾换行）。"""
    return json.dumps(build_manifest(target), ensure_ascii=False,
                      indent=2) + "\n"


# ---------- CLI ----------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="MCP capability manifest 生成器（票 23；零时间戳确定性派生物）")
    ap.add_argument("target", help="ontology 目录（本体仓根或单域目录）")
    ap.add_argument("--out", default=None, metavar="路径",
                    help="写出文件（缺省打印 stdout）")
    ap.add_argument("--check", default=None, metavar="入库路径",
                    help="重生成并与入库副本逐字节比对（一致 0 / 不一致 1）")
    args = ap.parse_args(argv)

    try:
        fresh = render(Path(args.target))
    except ConfigError as exc:
        print(f"配置错误: {exc}", file=sys.stderr)
        return 2

    if args.check:
        check_path = Path(args.check)
        if not check_path.is_file():
            print(f"再制不一致：入库副本不存在: {check_path}"
                  f"（生成：--out {check_path}）")
            return 1
        stored = check_path.read_text(encoding="utf-8")
        if stored == fresh:
            print(f"再制一致：{check_path} 与现场重生成逐字节一致")
            return 0
        print(f"再制不一致：{check_path} 与现场重生成有差异（入库副本陈旧或被手改；"
              f"再制：python3 tools/mcp_manifest_gen.py {args.target} "
              f"--out {check_path}）")
        return 1

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(fresh, encoding="utf-8")
        return 0

    sys.stdout.write(fresh)
    return 0


if __name__ == "__main__":
    sys.exit(main())
