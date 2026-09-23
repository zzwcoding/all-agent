# 走查留痕 · pkb 新仓开工交接（票 60，2026-09-23）

> All-agent 侧留痕：新仓 `/Users/divh/Downloads/personal-weknora/`（独立 git 仓，sdd-flow 治理）开工交接实录。

## 交接内容

| 项 | 落位 |
|---|---|
| 新仓址 | `/Users/divh/Downloads/personal-weknora/`（git init 首提交 `8fbf859`） |
| PRD | `docs/prd.md` 状态=已定稿；devkit 消费位=`exports/devkit/pkb/devkit.md`（锚定 905f037）；五行为 BH-PKB-* 与 AGG-PKB-001 逐条落功能清单 |
| CONTEXT.md | GLS 六词投影 + INV-1（chunk 唯一事实源、四维投影禁手改） |
| modules.md | 八卡（store/ingest/retrieval/graph/wiki/gateway/cli/mcp_server）+ 边界规则 4 条 + 页面映射 N/A（CLI+MCP） |
| 技术选型定稿 | `docs/tech-selection.md`：SQLite+sqlite-vec / BM25 手写 / agent-key gateway（fake stub 同接口）/ 本地 embedding 预留档（Q9）/ CLI+MCP（Q7）/ 千条量级 |
| CI 四门 | `tools/ci.sh`：spec gate（sdd-flow check_specs 原版）/ 边界闸（check_boundary.py：4 条规则+厂商 SDK 黑名单扫描）/ unittest（骨架契约 5 例）/ **上游 devkit 锚定复核**（条件门——跨仓 verify All-agent devkit，上游再生即信号） |
| 纪律 | 阶段 2 收口前禁业务编码（架构图 v1 用户过审为前置）；框架点名=验收对象 |

## CI 实跑记录

首跑抓出 4 处骨架失配（状态行带注记不合 validator 单 token 契约 / 边界规则表 4 列不合三列契约 / 页面清单标题误触 Web 产品契约 / 自写契约测试自缠），逐处修复后复跑：

```
=== 门1 spec gate ===  spec gate: PASS（0 警告）
=== 门2 边界闸 ===  边界规则 4 条登记 / 边界闸: 绿
=== 门3 单测 ===  Ran 5 tests ... OK
=== 门4 上游 devkit 锚定复核 ===  已审且哈希一致（锚定 commit=5a44504…）
CI: 全绿
```

## 下一步（阶段路由）

1. **阶段 2 收口**：架构图 v1（Mermaid）出图 → Owner 导览过审（记 ADR）→ 按 modules.md 建目录骨架；
2. 新仓阶段 3/4：五功能 spec + 内部拆票（新仓 tickets/ 01 起）；
3. 新仓 L2 施工（gateway/store 先行，fake stub 全绿后接真实 API）；
4. All-agent 票 61 端到端实弹走查（Owner 备：真实素材 + golden ≥5 题）→ 票 62 批收官。
