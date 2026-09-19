# docs/mcp-server.md · 语义服务 MCP 服务器消费文档（票 23）

## 定位

`tools/semantic_mcp_server.py` 是本体仓能力的 **MCP（Model Context Protocol）发布面**（PRD F11）：把运行时语义服务的四个只读工具以官方 mcp SDK 的 stdio 服务器形态发布给 Agent 平台消费。它只是发布包装——判定核心与话术纪律全部继承既有确定性工具（票 22 四步瀑布核心 + 票 04 图索引），本服务器零图算法、零瀑布逻辑、不自答。能力清单（服务名/域概览/四工具契约）的机读发布物是 `exports/mcp/capability-manifest.json`，由 `tools/mcp_manifest_gen.py` 从本体仓确定性生成（零时间戳，禁手改）。

## 前提

- **Python 3.10+**（官方 mcp SDK 要求；票 24 实测 Python 3.11）。
- **安装 mcp SDK（仅发布侧）**：`pip install "mcp==2.2.0"`。版本钉：票 24 实测组合为 **mcp 2.2.0 + Python 3.11**，升级 SDK 版本须重跑票 24 smoke（`tools/mcp_smoke_client.py`）复验行为一致。本体仓的构建/CI 链路**不安装也不依赖它**——未装 SDK 时起服会打印安装指引并以退出码 2 结束（四闸照常全绿，这是票 23 的 CI 免疫红线）。
- **PyYAML（server 子进程链需要，勿漏装）**：server 经子进程调 core/graph_index，二者解析本体 YAML 要用 PyYAML——**它不在 mcp SDK 的依赖树里**（票 26 实测 mcp 2.2.0 的 Requires 无 pyyaml），隔离环境须显式安装 `pip install pyyaml`（票 24 的 .venv-mcp 实测装有 PyYAML 6.0.3）。
- **建议 venv 隔离**：`python3 -m venv .venv-mcp && .venv-mcp/bin/pip install "mcp==2.2.0" pyyaml`，之后一律用 `.venv-mcp/bin/python` 起 server（票 24 实弹方案，用户已批）。

## 运行

```bash
# stdio 形态（缺省）：Agent 平台把 server 当子进程拉起，零端口零鉴权
python3 tools/semantic_mcp_server.py ontology/bohai
```

- 目标本体目录**显式传**（本体仓根或单域目录；不设默认——发布面不猜）。
- stdio 说明：server 经标准输入/输出与 MCP 客户端对话（JSON-RPC），适合本地子进程形态；配置到 Agent 平台时把上面的命令填为启动命令即可。
- HTTP 形态（R3·tech-selection §3）：只改末行——`mcp.run()` 换成 `mcp.run(transport="http", port=8000, path="/mcp")`（v2 起 transport 参数在 `run()` 上）。HTTP 档需自行考虑鉴权与部署面。
- 再生发布物（本体演进后必须做，防陈旧）：

```bash
python3 tools/mcp_manifest_gen.py ontology --out exports/mcp/capability-manifest.json
# 自检：现场重生成与入库副本逐字节比对（一致 exit 0）
python3 tools/mcp_manifest_gen.py ontology --check exports/mcp/capability-manifest.json
```

## 四工具契约

描述真源 = 生成器模板常量（`tools/mcp_manifest_gen.py` 的 `TOOL_CONTRACTS`），manifest 由它生成、server 起服时装载入库 manifest 并与模板逐项核对（漂移即 stderr 报注并回退模板）。完整 inputSchema 见 `exports/mcp/capability-manifest.json`。

| 工具 | 入参 | 行为 | 示例 |
|---|---|---|---|
| `semantic_ask` | `question: string`（可含 `@元素ID` 显式锚定） | 调票 22 四步瀑布核心（子进程 `--json`），返回确定性骨架回答：裁决 status/命中/缺件/禁用词处置/装配指令，**必带「本回答引用的元素 ID」清单**（ID 可 grep 追溯）；拒答三分支（面外/仓内没有/禁用词）原样继承，绝不编造 | `{"question": "日产量口径是什么？"}` |
| `semantic_query` | `element_id: string` | 调 `graph_index --query`：节点存在性、模型归属、域、文件位置与属性简报；未找到明确报错不猜 | `{"element_id": "AGG-BOHAI-001"}` |
| `semantic_closure` | `element_id: string`，`hops: integer`（≥1，默认 3） | 调 `graph_index --closure N`：沿 ref 正向 N 跳的下游节点集（逐条带引用字段与跳数） | `{"element_id": "GLS-BOHAI-002", "hops": 1}` |
| `semantic_impact` | `element_id: string` | 调 `graph_index --impact`：沿依赖边反向的受影响节点集（谁引用它：行为/规则/流程/查询出口） | `{"element_id": "AGG-BOHAI-001"}` |

只读边界：四工具不写仓；改口径/补概念等写意图一律回「走提案流程」（进仓走 MR + 语义 CI）。

## 与 semantic-service skill 的关系

**同一个判定核心，两种成稿形态**。`skills/semantic-service/` 是 LLM 工序：按检索瀑布操作 `tools/graph_index.py` 人工（对话内）取证，把票 22 core 的确定性裁决**成稿为自然语言回答**（多候选消歧、缺件归因、话术组织都是它的事）。本 MCP 服务器是纯机器发布面：同一 core 经子进程包装直接给出骨架回答，不经 LLM 成稿——回答是裁决结构的文本化装配，确定性可回归。两者共用 `tools/semantic_service_core.py` 与 `tools/graph_index.py`，行为基准同源（`fixtures/semantic-service/` CORE 八问 = `fixtures/mcp-publisher/cases/` 对照单）；票 24 smoke client 按该对照单逐条核对 MCP 实调与出厂集行为一致。
