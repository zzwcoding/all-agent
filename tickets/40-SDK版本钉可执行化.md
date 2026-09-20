# 票 40：MCP SDK 版本钉可执行化

Status: todo
Belongs to: docs/第三期B线拆票方案.md 批次一；docs/二期收官报告.md §6 #4
Touches: tools/requirements-mcp.txt、tools/semantic_mcp_server.py、tools/test_semantic_mcp_server.py、references/repo-layout.json、docs/mcp-server.md、lessons/40

## What to build

- mcp==2.2.0 从文档注记落进可执行处：钉版文件 + 启动时版本检出提示
- 安装/升级纪律成文

## 设计裁决（L0 已定）

- **钉版文件** `tools/requirements-mcp.txt`：内容 `mcp==2.2.0` + 注释行（用途：MCP 发布侧依赖，仅 venv 安装——`python3 -m venv .venv-mcp && .venv-mcp/bin/pip install -r tools/requirements-mcp.txt`；升级须重跑票 24 smoke client 实弹并更新本文件与 docs/mcp-server.md）。布局：tools patterns 增 `requirements*.txt`（实跑归档闸驱动）。
- **启动版本检出**：semantic_mcp_server 在 import mcp 成功后读钉版文件比对已装版本（`importlib.metadata.version("mcp")`），不一致 → stderr 警告"已装 X ≠ 钉版 2.2.0，请核对 docs/mcp-server.md；继续启动（或 --strict 退出）"——**默认警告继续，--strict 时不符即退**（提示性检出非硬闸，照票 40 方案"检出提示"措辞）。钉版文件缺失/不可读 → 同为警告不崩。单测：版本一致无警告/不一致有警告/--strict 退出/钉版文件缺失降级，四路径。
- **文档对齐**：docs/mcp-server.md 安装命令改为 `pip install -r tools/requirements-mcp.txt`，版本钉段指向钉版文件为准。
- CI 免疫红线不变：无 mcp 环境四闸照常全绿（检出逻辑单测全部注入式）。

## 验收（注源）

- [ ] AC1 钉版文件在场、布局登记、归档闸绿（源：本票 AC 表）
- [ ] AC2 版本检出四路径单测（一致/不一致/--strict/钉版缺失）（源：本票 AC 表）
- [ ] AC3 docs/mcp-server.md 指向钉版文件为准（源：本票 AC 表）
- [ ] AC4 `bash tools/ci.sh` 四闸绿（源：CI）

## 交接包（L2 自主档）

任务: 钉版文件+检出+文档对齐。
先读: tools/semantic_mcp_server.py（importorskip 结构）；docs/mcp-server.md；references/repo-layout.json tools 条目；tickets/24 smoke 手法（升级纪律的引用对象）。
框架红线: TDD（注入式，单测不装 mcp 不碰真 venv）；CI 免疫红线；全量绿灯红线。
边界红线: 只动 Touches 清单；票 24 smoke client 与 venv 零改动。
产出: 钉版文件+检出逻辑+单测+布局增补+docs 对齐+lessons/40。
验收: AC1–4 全过；`bash tools/ci.sh` 四闸绿。
回报: 产物路径+AC 实证+ci.sh 摘要+偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | tools/requirements-mcp.txt | 在场含 mcp==2.2.0；归档闸绿 |
| AC2 | 版本检出 | 四路径单测全过（一致静默/不一致警告/--strict 退出/钉版缺失降级） |
| AC3 | docs/mcp-server.md | 安装命令指向 requirements-mcp.txt；升级纪律成文 |
| AC4 | CI | 四闸全绿（无 mcp 环境） |
