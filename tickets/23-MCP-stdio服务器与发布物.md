# 票 23：MCP stdio 服务器 + capability manifest 发布物

Status: todo
Belongs to: 第三批拆票方案（2026-09-19 用户批准）；PRD F11；技术栈 R3（mcp 官方 SDK，仅发布侧）
Touches: tools/semantic_mcp_server.py、tools/mcp_manifest_gen.py、exports/、fixtures/mcp-publisher/、references/repo-layout.json、specs/archive-registry.json、docs/mcp-server.md、specs/modules.md、lessons/23

## What to build

- `tools/semantic_mcp_server.py`：stdio MCP 服务器，四工具（ask/query/closure/impact），启动全量重建图
- `tools/mcp_manifest_gen.py`：capability manifest 生成器（发布器的"生成物"）→ `exports/mcp/capability-manifest.json`
- 对外消费文档 docs/mcp-server.md；出厂集 fixtures/mcp-publisher/

## 设计裁决（L0 已定）

- **CI 免疫红线**：`import mcp` 必须 importorskip——缺 SDK 时 server 打印安装指引（`pip install mcp`）退出 2；单测对 mcp 相关路径 `skipUnless`。**四闸在无 mcp 环境必须照常全绿**（本仓 CI 不引入 mcp 依赖——PRD"仅发布侧安装"）。
- **四工具契约**：`semantic_ask(question)` → 调票 22 core（子进程 CLI），返回结构化裁决+骨架答案（必带 ID 引用；拒答纪律原样）；`semantic_query(id)` / `semantic_closure(id, hops)` / `semantic_impact(id)` → graph_index 子进程包装。工具 description 从 capability manifest 取（manifest 是描述真源）。
- **manifest 生成器确定性**：读 ontology 根（域清单+model-registry camp）生成 `{server, domains[], tools[{name,description,inputSchema}], generatedFrom}`；**无时间戳**（确定性可回归）；生成幂等（两次字节一致）。
- **派生物纪律**：manifest 入库（exports/mcp/）但必须过"再生一致"断言防陈旧——出厂集断言：重新生成 → 与入库副本 file-equals-golden 等价（gen 到 stdout 再比对，或临时目录生成后比对）。
- 布局表/登记表：exports/ 新目录按归档闸实测登记（patterns + registry 产物类必备字段，照 adr README 事件的教训一步到位）。
- **本票不装 mcp、不起真 server**——实弹是票 24（venv，用户已批）。

## 验收（注源）

- [ ] AC1–5 全过（源：本票 AC 表）
- [ ] 无 mcp 环境四闸全绿（源：CI 免疫红线）
- [ ] 布局表/登记表登记完整、归档闸绿（源：主线 2）

## 交接包（L2 自主档）

任务: server + manifest 生成器 + 出厂集 + 布局登记 + 消费文档。
先读: references/tech-selection.md（mcp 选型结论）；tools/semantic_service_core.py CLI（票 22 产物）；tools/graph_index.py --json；tools/archive_check.py + references/repo-layout.json + specs/archive-registry.json（登记机制）；tools/fixture_run.py 断言类型；ontology/schema/model-registry.json（camp）。
框架红线: stdlib 主体；mcp 只在 server 单文件 importorskip；TDD（manifest 生成器全量单测；server 的可测面=缺 mcp 引导路径+manifest 装载，协议面留票 24 实弹）；确定性零时间戳；全量绿灯红线。
边界红线: 只动 Touches 清单；不动 skills/、ontology/、schema/；票 22 的 core 零改动（发现 bug 报告不私修）。
产出: server + manifest 生成器 + 单测 + exports/mcp/capability-manifest.json（入库副本）+ fixtures/mcp-publisher/{cases/, assertions.json}（含再生一致断言 + server 缺 mcp 引导 cmd-fails）+ 布局/登记两表 + docs/mcp-server.md + modules.md 脚本清单两行 + lessons/23。
验收: AC1–5 全过；`bash tools/ci.sh` 四闸绿。
回报: 产物路径 + manifest 内容摘要 + AC 实证 + ci.sh 摘要 + 偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | manifest 生成器对 ontology/ 连跑两次 | 字节一致（幂等） |
| AC2 | 入库 manifest vs 现场重生成 | file-equals-golden 等价（防陈旧） |
| AC3 | manifest 内容 | 四工具齐、domains 含 bohai、inputSchema 可 json.loads |
| AC4 | 无 mcp 环境起 server | exit 2，stderr 含 pip install mcp 指引 |
| AC5 | 全厂集+四闸 | 无 mcp 环境全绿（CI 免疫实证） |
