# docs/mcp-server.md · 语义服务 MCP 服务器消费文档（票 23）

## 定位

`tools/semantic_mcp_server.py` 是本体仓能力的 **MCP（Model Context Protocol）发布面**（PRD F11）：把运行时语义服务的四个只读工具以官方 mcp SDK 的 stdio 服务器形态发布给 Agent 平台消费。它只是发布包装——判定核心与话术纪律全部继承既有确定性工具（票 22 四步瀑布核心 + 票 04 图索引），本服务器零图算法、零瀑布逻辑、不自答。能力清单（服务名/域概览/四工具契约）的机读发布物是 `exports/mcp/capability-manifest.json`，由 `tools/mcp_manifest_gen.py` 从本体仓确定性生成（零时间戳，禁手改）。

## 前提

- **Python 3.10+**（官方 mcp SDK 要求；票 24 实测 Python 3.11）。
- **安装 mcp SDK（仅发布侧，钉版安装）**：`pip install -r tools/requirements-mcp.txt`。版本钉**以 tools/requirements-mcp.txt 为准**（当前 `mcp==2.2.0`；票 24 实测组合为 mcp 2.2.0 + Python 3.11）。启动时 server 自动检出：比对已装版本（`importlib.metadata`）与钉版——一致静默；不一致/钉版文件缺失打 stderr 警告继续启动，`--strict` 可改为不符即退（退出码 2，票 40）。升级纪律：改钉版文件版本号 → 重跑票 24 smoke client（`.venv-mcp/bin/python tools/mcp_smoke_client.py --full`，9/9）→ 同步更新钉版文件与本文（升级不重跑 smoke = 违纪）。本体仓的构建/CI 链路**不安装也不依赖它**——未装 SDK 时起服会打印安装指引并以退出码 2 结束（四闸照常全绿，这是票 23 的 CI 免疫红线）。
- **PyYAML（server 子进程链需要，勿漏装）**：server 经子进程调 core/graph_index，二者解析本体 YAML 要用 PyYAML——**它不在 mcp SDK 的依赖树里**（票 26 实测 mcp 2.2.0 的 Requires 无 pyyaml），隔离环境须显式安装 `pip install pyyaml`（票 24 的 .venv-mcp 实测装有 PyYAML 6.0.3）。
- **建议 venv 隔离**：`python3 -m venv .venv-mcp && .venv-mcp/bin/pip install -r tools/requirements-mcp.txt pyyaml`，之后一律用 `.venv-mcp/bin/python` 起 server（票 24 实弹方案，用户已批）。

## 运行

```bash
# stdio 形态（缺省）：Agent 平台把 server 当子进程拉起，零端口零鉴权
python3 tools/semantic_mcp_server.py ontology/bohai
```

- 目标本体目录**显式传**（本体仓根或单域目录；不设默认——发布面不猜）。
- 版本检出（票 40）：起服自动比对已装 mcp 与 `tools/requirements-mcp.txt` 钉版——一致静默；不一致 stderr 警告继续（`已装 mcp X ≠ 钉版 2.2.0——核对 docs/mcp-server.md`）；钉版文件缺失/不可读降级警告不崩；`--strict` 时「不符」即退出 2（降级类仍只警告——检出是提示性非硬闸）。
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

## 发布检查位（L5 评分硬闸，票 44）

**语义服务对外发布或新域接入验收前，L5 全量跑，红则不发**（设计案 docs/design-l5-scoring.md §5.2：发布前为硬闸）：12 问评分集逐问机判先绿后，每问派发 3 个全新子 agent 评分（派发契约见 skills/semantic-service/references/l5-dispatch.md，评者≠答者），tools/l5_score.py 聚合判定，留痕落 docs/meta/l5-评分-<日期>.md/.json 随交付物引用。复评仍红走仲裁升级——换更强模型重派该问（design §2 C 子集形态）。与批收官软闸的分工：批收官只留痕开单不阻塞（AGENTS.md 续跑协议第 9 条第 ⑤ 件），本检查位是发布语义的硬闸；L5 红不覆盖机判四闸结论（design §6：冲突信机判，人裁 L5）。

## 与 semantic-service skill 的关系

**同一个判定核心，两种成稿形态**。`skills/semantic-service/` 是 LLM 工序：按检索瀑布操作 `tools/graph_index.py` 人工（对话内）取证，把票 22 core 的确定性裁决**成稿为自然语言回答**（多候选消歧、缺件归因、话术组织都是它的事）。本 MCP 服务器是纯机器发布面：同一 core 经子进程包装直接给出骨架回答，不经 LLM 成稿——回答是裁决结构的文本化装配，确定性可回归。两者共用 `tools/semantic_service_core.py` 与 `tools/graph_index.py`，行为基准同源（`fixtures/semantic-service/` CORE 八问 = `fixtures/mcp-publisher/cases/` 对照单）；票 24 smoke client 按该对照单逐条核对 MCP 实调与出厂集行为一致。
