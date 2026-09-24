# Q7 candidate（2026-09-25 L5 评分面，成稿窗零上下文派发）

机判 status：**answered**（waterfall_level = 二级·ID/名称解析（GLS 术语）；hits = `GLS-BOHAI-002`，术语条目即答案一部分，装配集见 citations）

## 答案

「剔检产量」是渤海域本体里登记在册的术语：本问无显式 @ID 锚定，走二级名称解析，以候选词「剔检产量」对候选域模型文件的 id/name/alias 通读，命中术语条目 `GLS-BOHAI-002`，经图索引 `--query` 确认存在。阵营检查：GLS- 前缀 → 术语模型（GLOSSARY），camp=business-core，在检索面内，进入闭包装配。

**术语条目本身是答案的一部分**：`GLS-BOHAI-002`（term 剔检产量，别名「净产量」，termType=别名，status=有效，Owner 开发室，注源 R5·设定书 §6）——定义：**剔除检修井口径的产量（即净产量）**。本条目单指不歧义，术语释义直接作答。

**沿 relatedObjectRefs 指路实体（三级正向闭包，`--closure 1` 可复现）**：`GLS-BOHAI-002` →(relatedObjectRefs)→ `AGG-BOHAI-001`（井）与 `AGG-BOHAI-002`（日产计量）——产量的量承载于 `AGG-BOHAI-002` 的 oilOutput 属性（日产油量，吨）；剔检的判据字段是 `AGG-BOHAI-001` 的 currentStatus（当前状态，Enum 值集含「检修」）。两实体间的承接关系见 `ASSOC-BOHAI-001`（井 1..* 日产计量，REFERENCE，referenceField=wellRef）。

**承载规则（口径真源）**：`RULE-BOHAI-019`（有效产量（剔检口径），CALCULATION）expression：`SUM(dailyProduction.oilOutput WHERE well.currentStatus <> '检修')`——区块月合计中剔除当前状态为「检修」的井后求和。注记如实转达（依据 `RULE-BOHAI-019` description/narrative）：该规则为**两支口径并列**——（a）开井日历折算支：Σ(oilOutput × openDays/24)，openDays 按开井小时数（0.5h 粒度）；（b）检修剔除支（即本问「剔检产量」，R5·§6 别名）。双口径披露约定：剔检支用于与历史可比，日历支用于当月真实贡献；两支差异 >3% 时口径页并列展示并注明差异来源。跨月检修的当月口径归属已裁——按日历天数劈分，承载于专项规则 `RULE-BOHAI-024`（跨月检修归属期切割，expression=overlapDays(overhaulStart, overhaulEnd, 当自然月)），剔检口径（`RULE-BOHAI-019`）按月扣减当月检修天数。

**执行行为与查询出口（口径四件套收口）**：执行行为 `BH-BOHAI-QueryBlockMonthlyCompletion`（查询区块月度产量完成率，QUERY，ownerEntity=`AGG-BOHAI-002`）appliedRules 引用 `RULE-BOHAI-019`（轨迹：`BH-BOHAI-QueryBlockMonthlyCompletion` →(appliedRules)→ `RULE-BOHAI-019`）；查询出口 `QR-BOHAI-002`（区块月度产量完成率统计，STATISTICAL_QUERY，behaviorRef=`BH-BOHAI-QueryBlockMonthlyCompletion`）结果列 effectiveOutputSum（有效产量·剔检，吨）sourceExpression `SUM(CASE WHEN w.currentStatus <> '检修' THEN d.oilOutput ELSE 0 END)`，列级注记口径真源=`RULE-BOHAI-019`——规则与出口两处口径一致，链路闭合。四件套齐备：承载字段（`AGG-BOHAI-002`.oilOutput + `AGG-BOHAI-001`.currentStatus）、校验/计算规则（`RULE-BOHAI-019`）、执行行为（`BH-BOHAI-QueryBlockMonthlyCompletion`）、查询出口（`QR-BOHAI-002`）。

**一句话口径**：剔检产量（别名「净产量」）= 从区块月度产量统计合计中剔除当前状态为「检修」的井之后的产油量；量承载于日产计量 oilOutput（吨），剔检判据是井的 currentStatus「检修」值，口径真源 `RULE-BOHAI-019`（与开井日历折算支两支口径并列披露），跨月检修按日历天数劈分（`RULE-BOHAI-024`），执行行为 `BH-BOHAI-QueryBlockMonthlyCompletion`，查询出口 `QR-BOHAI-002`。

## 本回答引用的元素 ID

- GLS-BOHAI-002（剔检产量——二级名称解析命中的术语条目，定义/别名/状态即答案一部分）
- AGG-BOHAI-001（井——relatedObjectRefs 指路；currentStatus「检修」为剔检判据字段宿主）
- AGG-BOHAI-002（日产计量——relatedObjectRefs 指路；oilOutput 日产油量（吨）为量承载）
- ASSOC-BOHAI-001（井 1..* 日产计量——两实体的承接关系）
- RULE-BOHAI-019（有效产量（剔检口径）——承载规则，口径真源，expression 即剔检口径公式）
- RULE-BOHAI-024（跨月检修归属期切割——跨月检修按日历天数劈分，由 RULE-BOHAI-019 注记引用承载）
- BH-BOHAI-QueryBlockMonthlyCompletion（查询区块月度产量完成率——执行行为，appliedRules 引用 RULE-BOHAI-019）
- QR-BOHAI-002（区块月度产量完成率统计——查询出口，effectiveOutputSum 列口径与规则一致）
