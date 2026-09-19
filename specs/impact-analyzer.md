# spec · impact-analyzer（变更影响分析器 skill）

触及: skill `impact-analyzer`

> 断言真源（2026-09-19 起）：tickets/08 票面 AC 表 + fixtures/impact-analyzer/assertions.json；本表为一期原始基线。

## 出厂集断言表

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | 最小域本体 + "改对象 X 的字段" | 影响链含直接引用 X 的全部节点 |
| AC2 | 同上 | 报告含建议落地顺序（先改谁后改谁） |
| AC3 | 改动波及字典项 | 提示"字典停用不删除"纪律与引用扫描结果 |
| AC4 | 无下游引用的对象 | 明确报"无影响"，不硬凑 |

## 行为约定

- 只读仓；报告落 `docs/impact/NN-*.md`；每条影响项给出传播依据（哪条 ref）
