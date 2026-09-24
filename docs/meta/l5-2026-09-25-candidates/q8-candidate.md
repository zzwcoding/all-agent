# Q8 candidate（2026-09-25 L5 评分面，成稿窗零上下文派发）

机判 status：`refused_banned`（semantic_service_core，瀑布走到二级·ID/名称解析的 GLS 禁用词处置；拒答问退出码 1 属预期，机判 JSON 为唯一证据源）。

**结论先行：不能再用。**「老完成率」在渤海域术语表中登记为**禁用词**：二级名称解析以候选词「老完成率」命中术语条目 `GLS-BOHAI-001`（GLS- 前缀 → 术语模型，camp=business-core，在检索面内；机判已确认命中）。按检索瀑布禁用词处置纪律：命中禁用术语即回答禁用说明 + 替代口径真实 ID 指路，**不得把禁用词当作可用口径作答**——本回答即是禁用处置，不是口径作答。

**禁用说明（术语条目本身是答案的一部分）**：`GLS-BOHAI-001`（term=老完成率，termType=禁用词，status=禁用（替代：产量完成率），Owner=开发室，源 R5·设定书 §6）——定义：v1 口径（不含自用油折算），2024 年废弃；禁用旧称，替代口径=产量完成率。该禁用注记同时承载于替代指标的口径真源描述：`RULE-BOHAI-009`（产量完成率）description 含「禁用旧称『老完成率』——v1 口径（不含自用油折算），2024 年废弃，替代即本指标」。术语条目沿 relatedObjectRefs 指路承载实体 `AGG-BOHAI-002`（日产计量——完成率量在日产计量：oilOutput 分子 / planOutput 配产分母）。缺口如实说明：禁用词的强制拦截面（校验侧禁用）已建——schema_check banned-term 闸（`GLS-BOHAI-001` notes 在案），即校验侧亦有拦截，非仅运行时问答侧。

**替代口径指路（真实 ID，可追溯）**：请改以产量完成率作答，口径四件套齐——

- 口径真源（校验规则）：`RULE-BOHAI-009`（产量完成率，CALCULATION）expression `actualOilSum / planOutputSum * 100`，即 Σ实际产油/Σ计划配产×100%（粒度=月/区块，Owner=开发室）；
- 承载字段（对象+属性）：`AGG-BOHAI-002`（日产计量，行粒度=班次，日口径=同井同日各班合计）——分子 oilOutput（日产油量·吨）、分母 planOutput（配产量·吨）；分母取版口径已裁（Owner 2026-09-21，PROP-BOHAI-009=A 经 `RULE-BOHAI-022`）：配产版本切换日双值行按「当日最后班次非空 planOutput」取版，双值行检出不阻断、全量出清单供人复核，`RULE-BOHAI-009` 分母按此口径净化；
- 执行行为：`BH-BOHAI-QueryBlockMonthlyCompletion`（查询区块月度产量完成率，QUERY，ownerEntity=`AGG-BOHAI-002`）appliedRules 引用 `RULE-BOHAI-009`；
- 查询出口：`QR-BOHAI-002`（区块月度产量完成率统计，STATISTICAL_QUERY）behaviorRef 挂 `BH-BOHAI-QueryBlockMonthlyCompletion`，结果列 completionPct（产量完成率 %，sourceExpression `SUM(d.oilOutput) / SUM(d.planOutput) * 100`，注记口径真源 `RULE-BOHAI-009`）。

**下一步**：报表与问答一律以产量完成率口径为准（真源 `RULE-BOHAI-009`、出口 `QR-BOHAI-002`）。校验侧禁用闸已建（见上）；如需在运行时侧对「老完成率」用词再落强制拦截，或对口径本身有补充修改，请走提案流程（进仓走 MR + 语义 CI）。本服务只读，不产文件、不改仓。

## 本回答引用的元素 ID

- GLS-BOHAI-001（二级解析命中的禁用词条目——禁用说明即答案的一部分）
- AGG-BOHAI-002（日产计量——GLS relatedObjectRefs 指路的承载实体；替代口径分子 oilOutput / 分母 planOutput 承载）
- RULE-BOHAI-009（产量完成率——替代口径真源，description 承载禁用注记）
- RULE-BOHAI-022（配产单值校验——`RULE-BOHAI-009` 分母双值行取版口径的净化依据）
- BH-BOHAI-QueryBlockMonthlyCompletion（执行行为——appliedRules 引用 `RULE-BOHAI-009`）
- QR-BOHAI-002（查询出口——completionPct 列，behaviorRef 挂执行行为）
