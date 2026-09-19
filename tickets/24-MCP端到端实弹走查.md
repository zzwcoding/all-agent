# 票 24：MCP 端到端实弹走查（venv + 官方 SDK）

Status: done
Belongs to: 第三批拆票方案（2026-09-19 用户批准，venv 方案已批）；PRD F11
Touches: .gitignore、tools/mcp_smoke_client.py、docs/walkthrough/、lessons/24

## What to build

- venv 隔离安装官方 mcp SDK（仅发布侧，不进 CI 依赖）
- smoke 客户端实弹：起 server → 四工具实调 → 与出厂集行为一致性核对
- 走查记录落 docs/walkthrough/ + lessons/24

## 设计裁决（L0 已定）

- **venv 方案**（用户批准）：`python3 -m venv .venv-mcp && .venv-mcp/bin/pip install mcp`；`.gitignore` 增 `.venv*/`；服务器/客户端一律用 `.venv-mcp/bin/python` 起。venv 不入库（gitignore 挡，归档闸天然不看）。
- **smoke 客户端** `tools/mcp_smoke_client.py`：mcp SDK 客户端 API，stdio 方式拉起 `semantic_mcp_server.py ontology/bohai`，顺序实调四工具各≥1 次，逐调用打印请求/响应摘要（走查证据）；importorskip 同纪律（无 SDK 时 exit 2 指引建 venv）。退出码 = 全部用例过 0 / 有失败 1。
- **行为一致性核对单**（与出厂集同源）：ask 三形态（日产量口径=answered 带 AGG-BOHAI-002 / 桶油成本=refused_missing / 老完成率=refused_banned 指路 RULE-BOHAI-009）+ query/closure/impact 各一（用 AGG-BOHAI-001）+ 禁用词例。客户端内置这些用例与期望断言（ID 命中/status 字段），人工复核其输出。
- 走查记录：docs/walkthrough/ 顺延编号（现有 step1–6，本票 = step7-mcp-e2e.md）：起服方式、每调用的请求/响应摘录、与出厂集行为对照表、发现的问题清单。
- **红线：ontology/、skills/、tools/ 既有文件零改动**（smoke client 是新文件；若实弹暴露票 22/23 的 bug：小修可在本票修但必须回补对应出厂集断言并记录，大修则停手回报）。

## 验收（注源）

- [x] AC1–4 全过（源：本票 AC 表）
- [x] venv 不入库（git status 干净、归档闸不看它）（源：派生物纪律）
- [x] `bash tools/ci.sh` 四闸绿且未引入 mcp 依赖（源：CI 免疫红线）

## 交接包（L2 自主档）

任务: venv 装 SDK + smoke 客户端 + 实弹走查 + 记录。
先读: docs/mcp-server.md（票 23 消费文档）；tools/semantic_mcp_server.py + semantic_service_core.py；fixtures/mcp-publisher/ 与 fixtures/semantic-service/（行为基准）；mcp 官方 SDK 文档（客户端 API，凭实际安装版本为准）。
框架红线: 全部实弹在 .venv-mcp 内；客户端断言内置（id/status 与出厂集同源）；走查记录必须含真实命令与真实输出摘录（不表演）；发现 bug 的处置按设计裁决分档。
边界红线: 只动 .gitignore、tools/mcp_smoke_client.py（新）、docs/walkthrough/step7-mcp-e2e.md（新）、lessons/24；venv 为执行面。
产出: venv（执行面）+ smoke client + 单测（可测面：用例表装载与期望结构，协议面 skipUnless）+ step7 走查记录 + lessons/24。
验收: AC1–4 全过；`bash tools/ci.sh` 四闸绿；git status 不出现 .venv。
回报: 走查记录摘要（每调用一行：工具/入参/结果）+ AC 实证 + ci.sh 摘要 + 发现的问题与处置 + 偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | smoke client 全量实调 | 四工具各≥1 次成功，退出 0 |
| AC2 | ask 三形态 + 禁用词例 | status/ID 与出厂集行为一致（客户端内置断言过） |
| AC3 | 全部回答 | 带 ID 引用（引用清单/ID token 可 grep） |
| AC4 | CI 与仓库 | 四闸绿；git status 无 .venv；未装 SDK 的裸环境 CI 照常全绿 |
