# 票 53：DDD 线文档对齐 + 订单域端到端走查 + Q8 清偿（小票）

Status: done

> 注（L0 拆票时点）：依赖票 50–52 全落地。Q8 修复=Owner 已拍板并入本票（prd.md 决策追认 2026-09-20）。
Belongs to: docs/第四期DDD线拆票方案.md 批次二；lessons/48（Q8 挂账）
Touches: docs/prd.md、CONTEXT.md、AGENTS.md、docs/walkthrough/、fixtures/semantic-service/expected-answers/（Q8）、fixtures/semantic-service/rubrics/（Q8 对应 rubric 锚例同步）、lessons/53

## What to build

1. **文档对齐**：PRD F15 转正（"第四期已建"口径）+ CONTEXT.md 增「聚合卡」「DDD 建模线」词条 + AGENTS.md 锚点推进。
2. **端到端走查**：最小订单域全工序实弹——本体草案输入 → ddd-modeler 五步工序 → 聚合卡/事件表/映射产出 → ddd_check 绿 → 待人审清单产出 → Mermaid 副产物在场。留痕落 `docs/walkthrough/`（照一期票 09 走查先例）。
3. **Q8 参照答案矛盾清偿**（lessons/48 挂账）：实查 Q8 参照答案内部矛盾点 → 裁决修复（修答案 or 修 rubric，逐条注源）→ **同步检查 rubric 锚例**（锚 5 例引参照答案原文，答案变则锚例同步）→ check_citations + l5_score 格式校验复绿。
4. **批收官候选确认**：ddd_check 对仓内真实 design/ 目录的全量跑挂批收官软闸（方案"批收官清单适配"节）写进 AGENTS.md 或批收官清单。

## 设计裁决（L0 已定）

- Q8 修复原则：参照答案与 rubric 锚例同源同步改，不允许只改一边（锚例引原文是票 43 契约）。
- 走查用最小订单域（fixtures 既有样本扩展），不动渤海域真域。

## 验收（注源）

- [x] AC1 PRD F15 转正 + CONTEXT 词条 ×2 + AGENTS 锚点（源：实读）
- [x] AC2 走查留痕在场：五步工序产出+ddd_check 绿+人审清单+Mermaid 图（源：docs/walkthrough/ 实读）
- [x] AC3 Q8 矛盾修复注源 + rubric 锚例同步 + check_citations/l5_score 复绿（源：实跑）
- [x] AC4 批收官软闸候选条款在场（源：实读）
- [x] AC5 `bash tools/ci.sh` 四闸绿（源：CI）

## 交接包（L2 自主档）

任务: 文档对齐三件+订单域走查+Q8 清偿+批收官候选。
先读: docs/prd.md F15 与决策追认；lessons/48（Q8 矛盾实录——修复靶子以它为准）；fixtures/semantic-service/expected-answers/ 与 rubrics/（Q8 相关件）；docs/walkthrough/（票 09 走查先例）；skills/ddd-modeler/（票 52 正文——走查按它跑）；design/ddd/README.md。
框架红线: 无点名框架。
边界红线: 只动 Touches 清单；走查不动渤海域真域；Q8 修复限 expected-answers/rubrics 两处且注源。
产出: 文档三件+走查留痕+Q8 修复+lessons/53。
验收: AC1–5 全过；`bash tools/ci.sh` 四闸绿。
回报: 产物路径+五项 AC 实证+Q8 裁决摘要+ci.sh 摘要+偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | prd/CONTEXT/AGENTS | F15 转正+词条×2+锚点在场 |
| AC2 | docs/walkthrough/ | 订单域走查留痕五件齐 |
| AC3 | Q8 相关件 | 矛盾修复注源、锚例同步、双闸复绿 |
| AC4 | 批收官清单 | ddd_check 真实目录软闸条款在场 |
| AC5 | CI | 四闸全绿 |
