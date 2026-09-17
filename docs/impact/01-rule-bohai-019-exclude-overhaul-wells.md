# 影响分析报告 01 · 产量统计口径剔除检修井（RULE-BOHAI-019 口径修订）

- 变更对象: RULE-BOHAI-019（M3 · 域 bohai · 有效产量（剔检口径））
- 变更内容: 「产量口径剔除检修井」——把日产量统计合计从"全井求和"修订为"剔除 currentStatus=检修 的井后求和"（R5·§3 指标 2 有效产量两支口径之「检修剔除」支的落地；别名「剔检产量」，R5·§6）。伴生人工项：QR-BOHAI-002 结果列 effectiveOutputSum 的出口表达式同步（见边界说明）。
- 取证命令: `python3 tools/graph_index.py ontology/bohai --query RULE-BOHAI-019 --impact`
- 图统计: 节点=69 边=109；影响集 6 个受影响节点（沿依赖反向走）

## 影响链（每行=受影响 ID / 模型 / 跳数 / 传播依据 / 建议落地顺序）

- BH-BOHAI-QueryBlockMonthlyCompletion（M2）hops=1 via=appliedRules（path: BH-BOHAI-QueryBlockMonthlyCompletion → RULE-BOHAI-019）｜顺序 2
- RULE-BOHAI-009（M3）hops=2 via=reusedBy（path: RULE-BOHAI-009 → BH-BOHAI-QueryBlockMonthlyCompletion → RULE-BOHAI-019）｜顺序 3
- PERM-BOHAI-QueryBlockMonthlyCompletion（M5）hops=2 via=targetRef（path: PERM-BOHAI-QueryBlockMonthlyCompletion → BH-BOHAI-QueryBlockMonthlyCompletion → RULE-BOHAI-019）｜顺序 3
- FLOW-BOHAI-001（M6）hops=2 via=behaviorRef（path: FLOW-BOHAI-001 → BH-BOHAI-QueryBlockMonthlyCompletion → RULE-BOHAI-019）｜顺序 3
- QR-BOHAI-002（M7）hops=2 via=behaviorRef（path: QR-BOHAI-002 → BH-BOHAI-QueryBlockMonthlyCompletion → RULE-BOHAI-019）｜顺序 3
- ROLE-BOHAI-003（M5）hops=3 via=permissions（path: ROLE-BOHAI-003 → PERM-BOHAI-QueryBlockMonthlyCompletion → BH-BOHAI-QueryBlockMonthlyCompletion → RULE-BOHAI-019）｜顺序 4

直接引用者（hops=1）共 1 个：BH-BOHAI-QueryBlockMonthlyCompletion（查询区块月度产量完成率）经 appliedRules 引用本规则——口径修订先落到该行为的统计语义。间接受影响 5 个（hops=2 起）经该行为传导。

## 建议落地顺序（被依赖者优先）

原则: 先改被依赖者，后改依赖者；方向依据 ontology/schema/model-deps.json 依赖白名单的 ref 方向（ref 字段从引用方指向被依赖方，被指向者先落地）。主序取 --impact 跳数升序，同跳数内按依赖方向微调（规则→行为→权限角色→流程→查询出口，消费末端最后）。

1. 顺序 1 — RULE-BOHAI-019 本体（变更对象本体先行；口径真源，expression/narrative 同步修订：剔检支落地 + 开井日历折算支保持待 Owner 占位）
2. 顺序 2 — BH-BOHAI-QueryBlockMonthlyCompletion（hops=1 · 行为层：统计语义随口径改，preconditions「统计月已封账」复核不受影响）
3. 顺序 3 — RULE-BOHAI-009（hops=2 · 同行为的并列口径规则：完成率分子Σ实际产油是否同步剔检**待 Owner 裁决**——R5·§3 指标 1 公式原文不含剔检，机械面仅提示同行为共现，不改其表达式）、PERM-BOHAI-QueryBlockMonthlyCompletion（hops=2 · 权限，targetRef 指向行为，通常仅知会）、FLOW-BOHAI-001（hops=2 · 流程，ACT-BOHAI-102 经 behaviorRef 拉数，归因脚本引用口径名需对齐）、QR-BOHAI-002（hops=2 · 查询出口，消费末端：结果列 effectiveOutputSum 的 sourceExpression 与修订后口径对齐）
4. 顺序 4 — ROLE-BOHAI-003（hops=3 · 业务 Owner 产量口径（开发室），链路末端知会/确认——R5·§1 该口径的 Owner 即此角色，裁决人）

## 特例处置

本场景未命中字典项/无下游引用特例（变更对象有 6 个下游受影响节点）。无字典项卷入：本域未建 data_dictionaries（枚举以 enumValues 承载），「检修」是 AGG-BOHAI-001.currentStatus 的 Enum 值而非字典项 code——其停用/改值的影响分析路径（Enum 值不进图）见边界说明。

## 边界说明

- 本报告只读仓产出，不改任何本体文件；影响链全部来自 --impact 反向走，每行 via= 即传播依据，取证命令重跑可复现同一影响集（节点=69 边=109 恒定，图每次从 YAML 全量重建）。
- **机械面只覆盖 ID ref 通道**，以下文字依赖不进图、须人工复核（标「待 Owner 确认」）：
  1. 本规则表达式读写 `AGG-BOHAI-001.currentStatus`（枚举值「检修」）与 `AGG-BOHAI-002.oilOutput`——字段语义/枚举值集变化不在本影响集内（Enum 值与属性名不是元素 ID）；QR-BOHAI-002.effectiveOutputSum 的 sourceExpression 为同一依赖的文字形态。
  2. **联动指标（R5·§3「指标不是独立数字」物质平衡约束）**：日产量合计口径变化联动注采比（RULE-BOHAI-011）、综合含水率（RULE-BOHAI-010）与物质平衡校验（RULE-BOHAI-008，分母/分子共享日产合计）——三者在机读面**不可达**（不共享 appliedRules 行为），必须人工检查，这是本报告最大的人工复核面。
  3. 跨月检修切割（R5·附录 A.4「8-28→9-06」，疑点 D10）：剔检按「当前状态」判定，跨月作业的当月归属规则未定，影响剔检口径的月度切分——待 Owner。
- 高影响变更审批：R5·§1 数据治理领导组（Review Board）审批属治理面，本报告只提供取证，不代审批。
