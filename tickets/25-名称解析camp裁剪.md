# 票 25：core 名称解析补 camp 裁剪（P1 功能正确性尾款）

Status: todo
Belongs to: docs/reviews/2026-09-19-phase3-review-tickets20-24-and-sddflow2-audit.md P1；R1 检索面纪律（瀑布 §0）
Touches: tools/semantic_service_core.py、tools/test_semantic_service_core.py、fixtures/semantic-service/、skills/semantic-service/、specs/modules.md、lessons/25

## What to build

- core 名称解析命中集补 camp 裁剪（面外元素不得出现在 hits/citations/装配指令）
- 审查复现用例改写为出厂集负变体断言（钉死不回归）
- CORE 八问断言从单向包含升级为 ID 集相等
- skill 侧补 core 单源声明（双真源单向→双向）

## 设计裁决（L0 已定）

- **裁剪点位=候选 ID 产生处**：名称解析算出候选集后立即按前缀→模型→camp 过滤（R1 纪律"任何候选 ID 先过阵营检查"），面外元素不进 hits、不进 citations、不进 scaffold_commands；@锚定路径维持现状（已合规）。
- **裁决语义**：命中集全为面外时 status 仍为 answered（有 business-core 命中）或按既有 refused 语义；面外元素被滤除不另行报错——检索面外本来就是"不在服务面"，不是错误。
- **负变体断言**：审查复现用例（最小域 fixtures/graph_index/ontology-base + 「单井日产量录入」）改写为 CORE- 新断言：cmd 用 python -c 解析 --json 输出，断言 SCR-BOHAI-01 不在 hits/citations 且 AGG-BOHAI-001 在（fixture_run 无"输出不含"断言型，python -c 探针是既定手法，票 23 先例）。
- **集相等升级**：CORE-01–08 从 outputContains 单向包含改为 python -c 精确比对（hits ID 集与冻结期望集相等）；期望集在 camp 修复后从实测冻结，并逐集与参照答案 ID 清单交叉核对（不得含面外 ID）。
- **单源声明双向化**：semantic-service 卡依赖 script 行增 `tools/semantic_service_core.py`；SKILL.md 细则索引或契约节补一句"可机判判定已提纯于 `tools/semantic_service_core.py`（MCP 服务器与出厂集共用同一核心），本 skill 工序语义与其保持一致，改判定先改 core 再对齐正文"；改完 sync 安装位。

## 验收（注源）

- [ ] AC1 复现用例翻绿：同问同域 hits/citations 无 SCR-BOHAI-01（源：本票 AC 表）
- [ ] AC2 CORE-01–08 集相等断言全过（源：本票 AC 表）
- [ ] AC3 单源声明双向：卡依赖登记、skill 正文有声明、sync 零漂移（源：字段纪律 3）
- [ ] AC4 四闸绿、既有断言零倒（源：CI）

## 交接包（L2 自主档）

任务: camp 裁剪修复 + 断言升级 + 单源声明。
先读: docs/reviews/2026-09-19-phase3-review-tickets20-24-and-sddflow2-audit.md P1 节；tools/semantic_service_core.py（名称解析与 citations 组装路径）；fixtures/semantic-service/assertions.json CORE- 现状；expected-answers/ 八份 ID 清单；specs/modules.md semantic-service 卡。
框架红线: TDD（先写复现单测红→修→绿）；裁剪只动 core 的候选过滤与集合组装，瀑布四级骨架/退出码契约/其他判定不动；全量绿灯红线。
边界红线: 只动 Touches 清单；ontology/、tools/ 其他脚本零改动。
产出: 修复 + 负变体断言 + CORE 升级 + 卡/正文/说明书改动 + sync 证明 + lessons/25（含"正向闭包只对 GLS 命中跑"取舍补记——票 22 偏差 5 的账）。
验收: AC1–4 全过；`bash tools/ci.sh` 四闸绿；`python3 tools/install_skills.py --check` 零漂移。
回报: 修复 diff 摘要 + 复现用例前后对照 + 八问冻结期望集清单 + ci.sh 摘要 + 偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | 最小域 + 「单井日产量录入」（审查复现用例） | answered；SCR-BOHAI-01 不在 hits/citations；AGG-BOHAI-001 在 hits |
| AC2 | CORE-01–08 升级版断言 | 八问 hits 期望集精确相等全过 |
| AC3 | 卡与正文 | 依赖行含 core；正文含单源声明句；--check 零漂移 |
| AC4 | 全厂集+四闸 | 零倒，全绿 |
