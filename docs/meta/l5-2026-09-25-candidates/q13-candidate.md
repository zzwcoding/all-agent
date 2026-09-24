# Q13 candidate（2026-09-25 L5 评分面，成稿窗零上下文派发）
机判 status：refused_banned（semantic_service_core.py 实跑，瀑布级=二级·ID/名称解析·GLS 禁用词处置；退出码 1=拒答问属正常）

**结论先行：「老完成率」在术语表登记为禁用词，本服务不把它当可用口径作答——所以「它具体怎么算」没有现行答案，其旧算法也不予复现。**

**禁用说明（术语条目即答案的一部分）**：名称解析命中的是术语条目 `GLS-BOHAI-001`（老完成率）——termType=禁用词，status=禁用（替代：产量完成率），Owner=开发室。登记定义只交代口径差别：v1 口径（不含自用油折算），2024 年废弃，禁用旧称，替代口径=产量完成率。同一条禁用注记也承载在替代指标的规则描述里：`RULE-BOHAI-009` description 明示「禁用旧称『老完成率』——v1 口径（不含自用油折算），2024 年废弃，替代即本指标」。

**为什么不给旧算法**：v1 口径的具体计算公式在仓内没有任何承载——规则模型里只有替代口径 `RULE-BOHAI-009` 的公式，没有「老完成率」的计算条目。按「未找到不猜」纪律，本服务不反推、不复现这个公式；任何「大概是这么算」的表述都是补猜，一律不给。

**替代口径指路（真实 ID，可追溯）**：你要的「完成率怎么算」，现行口径真源是产量完成率，四件套齐全：

- 口径真源：`RULE-BOHAI-009`（产量完成率，CALCULATION）expression 为 `actualOilSum / planOutputSum * 100`，即 Σ实际产油（`dailyProduction.oilOutput` 区块月合计）/ Σ计划配产（`dailyProduction.planOutput` 区块月合计）× 100%，粒度=月/区块/%，Owner=开发室；
- 执行行为：`BH-BOHAI-QueryBlockMonthlyCompletion`（查询区块月度产量完成率，QUERY）appliedRules 引用 `RULE-BOHAI-009`，前置条件=统计月已封账（封账规则待 Owner 确认）；
- 查询出口：`QR-BOHAI-002`（区块月度产量完成率统计）结果列 completionPct（产量完成率（%）），sourceExpression `SUM(d.oilOutput) / SUM(d.planOutput) * 100`，口径真源注记即 `RULE-BOHAI-009`；
- 分母净化注记：配产版本切换日双值行按「当日最后班次非空 planOutput」取版（`RULE-BOHAI-022`），双值行不阻断、全量出清单供人复核，产量完成率分母按此口径净化。

闭包轨迹：`RULE-BOHAI-009` →(reusedBy)→ `BH-BOHAI-QueryBlockMonthlyCompletion`；`QR-BOHAI-002` →(behaviorRef)→ `BH-BOHAI-QueryBlockMonthlyCompletion`，每跳可复核。

**下一步**：报表与问答一律改用产量完成率口径（`RULE-BOHAI-009` / `QR-BOHAI-002`）。若确需对 v1 口径做考古式补注（例如补记其历史公式），请走提案流程（进仓走 MR + 语义 CI）由 Owner 裁决；本服务只读，不产文件、不改仓。

## 本回答引用的元素 ID

- GLS-BOHAI-001（老完成率——GLS 禁用词条目，禁用说明即答案一部分）
- RULE-BOHAI-009（产量完成率——替代口径真源，公式与禁用注记承载）
- BH-BOHAI-QueryBlockMonthlyCompletion（查询区块月度产量完成率——替代口径的执行行为）
- QR-BOHAI-002（区块月度产量完成率统计——替代口径的查询出口，completionPct 列）
- RULE-BOHAI-022（配产单值校验——分母取版净化注记）
