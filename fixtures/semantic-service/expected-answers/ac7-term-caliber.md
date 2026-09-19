# 参照答案 Q7（票 17 AC1）· 剔检产量是什么口径？

- Golden Question: 「剔检产量是什么口径？」
- 走到的瀑布级: 二级 ID/名称解析（术语词先落 GLS）→ 三级闭包装配（沿 relatedObjectRefs 指路实体 + 口径四件套）
- 证据域: 解析自 bohai 真域（ontology/bohai——GLS 术语条目在真域；票 04 最小域无 GLS 文件，问答本体不扩）
- 断言面: GLS 命中 + 术语条目即答案一部分 + 关联对象/承载规则指路 + 引用清单齐

## 答案（示范格式）

「剔检产量」在本体是登记在册的术语：二级名称解析以候选词「剔检产量」通读候选域模型文件的 id/name/alias，命中术语条目 `GLS-BOHAI-002`，经图索引 `--query` 确认存在。检索面检查：GLS- 前缀 → 术语模型（GLOSSARY），camp=business-core，在检索面内，进入装配。

**术语条目本身是答案的一部分**：`GLS-BOHAI-002`（term 剔检产量，别名「净产量」，termType=别名，status=有效，Owner 开发室，注源 R5·设定书 §6）——定义：剔除检修井口径的产量（即净产量）。本条目单指不歧义，术语释义直接作答。

**沿 relatedObjectRefs 指路实体（三级正向闭包，`--closure 1` 可复现）**：`GLS-BOHAI-002` →(relatedObjectRefs)→ `AGG-BOHAI-001`（井）与 `AGG-BOHAI-002`（单井日产量记录）——量承载于 `AGG-BOHAI-002` 的 oilOutput（日产油量，吨）；剔检判据是 `AGG-BOHAI-001` 的 currentStatus（当前状态，Enum 含「检修」值）。

**承载规则（口径真源）**：`RULE-BOHAI-019`（有效产量·剔检口径，CALCULATION）expression `SUM(dailyProduction.oilOutput WHERE well.currentStatus <> '检修')`——区块月合计中剔除当前状态为「检修」的井后求和。注记如实转达：与开井日历折算支两支口径并列，该支公式待 Owner 补全；跨月检修的当月口径归属待 Owner（争议 D10 在案）。

**执行行为与查询出口**：`BH-BOHAI-QueryBlockMonthlyCompletion`（查询区块月度产量完成率）appliedRules 引用 `RULE-BOHAI-019`；查询出口 `QR-BOHAI-002`（区块月度产量完成率统计）结果列 effectiveOutputSum（有效产量·剔检，吨）sourceExpression `SUM(CASE WHEN w.currentStatus <> '检修' THEN d.oilOutput ELSE 0 END)`——与规则口径一致，链路闭合。

**一句话口径**：剔检产量（别名净产量）= 从统计合计中剔除状态为「检修」的井后的产油量；字段承载 oilOutput × currentStatus，口径真源 `RULE-BOHAI-019`，执行行为 `BH-BOHAI-QueryBlockMonthlyCompletion`，查询出口 `QR-BOHAI-002`。

## 本回答引用的元素 ID

- GLS-BOHAI-002（剔检产量——二级解析命中的术语条目，定义/别名/状态即答案一部分）
- AGG-BOHAI-001（井——relatedObjectRefs 指路；currentStatus 剔检判据字段宿主）
- AGG-BOHAI-002（单井日产量记录——relatedObjectRefs 指路；oilOutput 量承载）
- RULE-BOHAI-019（有效产量·剔检口径——承载规则，口径真源）
- BH-BOHAI-QueryBlockMonthlyCompletion（执行行为——appliedRules 引用 RULE-BOHAI-019）
- QR-BOHAI-002（区块月度产量完成率统计——查询出口，effectiveOutputSum 列）
