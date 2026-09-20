# 参照答案 Q8（票 17 AC2/AC3）· 老完成率还能用吗？

- Golden Question: 「老完成率还能用吗？」
- 走到的瀑布级: 二级 ID/名称解析（术语词先落 GLS）→ GLS 命中禁用术语 → 禁用词处置（回答=禁用说明+替代口径真实 ID 指路，不把禁用词当作可用口径作答）
- 证据域: 解析自 bohai 真域（ontology/bohai——GLS 术语条目在真域；票 04 最小域无 GLS 文件，问答本体不扩）
- 断言面: 禁用说明 + 替代指路（RULE-BOHAI-009/QR-BOHAI-002）+ 守卫正则（禁用词不得被答成可用口径）+ 引用清单齐

## 答案（示范格式）

**结论先行：不能再用。**「老完成率」在术语表登记为**禁用词**：二级名称解析以候选词「老完成率」命中术语条目 `GLS-BOHAI-001`（经图索引 `--query` 确认存在；GLS- 前缀 → 术语模型，camp=business-core，在检索面内）。命中禁用术语时，本服务不把它当可用口径作答——回答即禁用处置。

**禁用说明（术语条目即答案的一部分）**：`GLS-BOHAI-001`（term 老完成率，termType=禁用词，status=禁用（替代：产量完成率），Owner 开发室）——定义：v1 口径（不含自用油折算），2024 年废弃；禁用旧称。该禁用注记同时承载于替代指标的描述（`RULE-BOHAI-009` description 含「禁用旧称『老完成率』——v1 口径（不含自用油折算），2024 年废弃，替代即本指标」）。缺口如实说明：禁用词的强制拦截面（校验侧禁用）已建——schema_check banned-term 闸（条目 notes 在案），运行时禁用处置之外校验侧亦拦。

**替代口径指路（真实 ID，可追溯）**：请改以产量完成率作答——

- 口径真源：`RULE-BOHAI-009`（产量完成率，CALCULATION）expression `actualOilSum / planOutputSum * 100`（Σ实际产油/Σ计划配产×100%，月/区块/%）；字段承载于 `AGG-BOHAI-002` 的 oilOutput（分子）与 planOutput（配产分母；配产双值行争议 D4 注记在案）；
- 执行行为：`BH-BOHAI-QueryBlockMonthlyCompletion`（查询区块月度产量完成率）appliedRules 引用 `RULE-BOHAI-009`；
- 查询出口：`QR-BOHAI-002`（区块月度产量完成率统计）结果列 completionPct（产量完成率，%）。

**下一步**：报表与问答一律以产量完成率口径为准（上述 `RULE-BOHAI-009` / `QR-BOHAI-002`）。校验侧禁用闸已建；如需运行时侧对「老完成率」用词再落强制拦截，请走提案流程。本服务只读，不产文件、不改仓。

## 本回答引用的元素 ID

- GLS-BOHAI-001（老完成率——二级解析命中的禁用词条目，禁用说明即答案一部分）
- AGG-BOHAI-002（单井日产量记录——relatedObjectRefs 指路；oilOutput/planOutput 替代口径分子分母承载）
- RULE-BOHAI-009（产量完成率——替代口径真源）
- BH-BOHAI-QueryBlockMonthlyCompletion（执行行为——appliedRules 引用 RULE-BOHAI-009）
- QR-BOHAI-002（区块月度产量完成率统计——替代口径查询出口，completionPct 列）
