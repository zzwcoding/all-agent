# Q10 candidate（2026-09-25 L5 评分面，成稿窗零上下文派发）

机判 status：answered（瀑布二级·ID/名称解析命中；ambiguous=true，多候选已按瀑布 §2 列分、不合并）

## 答案

「产量完成率」名称解析命中口径真源 `RULE-BOHAI-009`（产量完成率，CALCULATION 型规则，月/区块粒度，Owner=开发室）。按口径四件套装配如下：

- **公式**：actualOilSum / planOutputSum × 100，即 Σ实际产油 ÷ Σ计划配产 × 100%。
- **承载字段**（规则 inputParams sourceField，承载对象 `AGG-BOHAI-002` 日产计量，源表 oil_production_daily，行粒度=班次）：分子=日产油量 dailyProduction.oilOutput（区块月合计）；分母=配产量 dailyProduction.planOutput（区块月合计）。区块维度取自 `AGG-BOHAI-001`（井）的 blockName，按 prodDate 月归组。
- **校验规则**：分母 planOutput 存在配产版本切换日「双值行」，版本语义已裁（双值=版本事实非脏行）：日配产口径=当日最后班次的非空值，双值行全量出清单供人复核、不阻断（`RULE-BOHAI-022` 配产单值校验；`RULE-BOHAI-009` 分母按此口径净化）。
- **执行行为**：`BH-BOHAI-QueryBlockMonthlyCompletion`（查询区块月度产量完成率，QUERY）appliedRules 引用真源；其前置条件为「统计月已封账」，但封账规则本体仓内未建、标注待 Owner——此缺口照实说明，属仓内缺件而非口径本身。
- **查询出口**：`QR-BOHAI-002`（区块月度产量完成率统计，STATISTICAL_QUERY）结果列 completionPct（产量完成率（%）），区块 × 统计月分组。

**多义列分（瀑布 §2，不擅自合并）**：名称解析另命中两个候选，均非口径本身——

- `RULE-BOHAI-019`（有效产量·剔检口径）：`QR-BOHAI-002` 同出口的并列列 effectiveOutputSum（有效产量·剔检，吨）的真源，与完成率并列展示、互不替代，不是完成率口径的组成部分。
- `FLOW-BOHAI-001`（产量下滑归因，R5·§7 剧本 1）：消费本完成率的流程（其步骤 1 即拉取完成率与构成），非口径定义。

**禁用词处置**：旧称「老完成率」是禁用术语（`GLS-BOHAI-001`，termType=禁用词）——v1 口径（不含自用油折算），2024 年废弃；不得再当可用口径使用，替代口径即本回答的 `RULE-BOHAI-009`。

**一句话口径**：产量完成率 = 区块月 Σ实际产油 ÷ Σ计划配产 × 100（真源 `RULE-BOHAI-009`，出口 `QR-BOHAI-002` 的 completionPct 列），月/区块粒度；分母双值行按最后班次取版（`RULE-BOHAI-022`），封账前置在仓内暂无规则判据。

## 本回答引用的元素 ID

- RULE-BOHAI-009（产量完成率——二级名称解析主命中，口径真源）
- AGG-BOHAI-002（日产计量——分子/分母承载对象）
- AGG-BOHAI-001（井——区块维度 blockName 来源）
- RULE-BOHAI-022（配产单值校验——分母双值行取版口径）
- BH-BOHAI-QueryBlockMonthlyCompletion（查询区块月度产量完成率——执行行为）
- QR-BOHAI-002（区块月度产量完成率统计——查询出口）
- RULE-BOHAI-019（有效产量·剔检口径——同出口并列列真源，非本答）
- FLOW-BOHAI-001（产量下滑归因——口径消费流程，非本答）
- GLS-BOHAI-001（老完成率——禁用术语条目，替代口径指路）
