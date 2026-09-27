# 参照答案 Q2（AC2）· @AGG-BOHAI-001 有哪些行为？

- Golden Question: 「@AGG-BOHAI-001 有哪些行为？」
- 走到的瀑布级: 一级显式锚定（@ID 直达，未走名称模糊检索）→ 闭包反向收集行为
- 再锚定注记（票 71，2026-09-27）：行为参照集与现行 bohai M2 对齐——旧答引用的「刷新井状态」行为 ID 已不存在（过期实锤，本票根因）；现行集=机判 CORE-02 冻结七件，按触达路径如实分述。
- 断言面: 显式锚定直接命中 + 行为集（CORE-02 冻结七件）+ 引用清单齐

## 答案（示范格式）

问题带 @AGG-BOHAI-001，**显式锚定直接命中**，未走名称模糊检索。检索面检查：AGG- 前缀 → 对象模型（M1），camp=business-core，在检索面内，进入闭包收集。

锚定对象 `AGG-BOHAI-001`（井）的行为闭包共七件，按触达路径如实分述（每件归属 ownerEntity 照登，不混淆）：

**直接名下（ownerEntity=AGG-BOHAI-001）**：
- `BH-BOHAI-QueryWellDailyOutput`（查询单井日产量，QUERY，USER_ACTION）——需权限 `PERM-BOHAI-QueryWellDailyOutput`，查询出口 `QR-BOHAI-001`（behaviorRef 回指本行为）。

**经日产计量载体 `AGG-BOHAI-002` 触达（ownerEntity=AGG-BOHAI-002）**：
- `BH-BOHAI-RecordDailyOutput`（录入日产计量，COMMAND，USER_ACTION）——appliedRules 挂 `RULE-BOHAI-005`（井号归一化）。
- `BH-BOHAI-RunDailyQualityCheck`（执行日产质检，COMMAND）
- `BH-BOHAI-QueryBlockMonthlyCompletion`（查询区块月度产量完成率，QUERY）
- `BH-BOHAI-QueryBlockWaterCut`（查询区块综合含水率，QUERY）

**经井检修台账 `AGG-BOHAI-004` 触达（ownerEntity=AGG-BOHAI-004）**：
- `BH-BOHAI-RecordOverhaul`（补录井检修台账，COMMAND）

**经流体化验台账 `AGG-BOHAI-006` 触达（ownerEntity=AGG-BOHAI-006）**：
- `BH-BOHAI-RecordFluidTest`（录入流体化验结果，COMMAND）

（七件行为同属井作业链：录入/质检/查询经三类数据载体触达井——闭包边界如实到机判集，无增无漏；每件归属载体照登，不把载体名下行为说成井直接名下。）

## 本回答引用的元素 ID

- AGG-BOHAI-001（井——显式锚定对象，一级直达）
- BH-BOHAI-QueryWellDailyOutput（查询单井日产量——直接名下行为）
- PERM-BOHAI-QueryWellDailyOutput（上述行为所需权限）
- QR-BOHAI-001（上述行为的查询出口）
- BH-BOHAI-RecordDailyOutput（经 AGG-BOHAI-002 触达）
- BH-BOHAI-RunDailyQualityCheck（经 AGG-BOHAI-002 触达）
- BH-BOHAI-QueryBlockMonthlyCompletion（经 AGG-BOHAI-002 触达）
- BH-BOHAI-QueryBlockWaterCut（经 AGG-BOHAI-002 触达）
- RULE-BOHAI-005（RecordDailyOutput 的井号归一化规则）
- BH-BOHAI-RecordOverhaul（经 AGG-BOHAI-004 触达）
- BH-BOHAI-RecordFluidTest（经 AGG-BOHAI-006 触达）
- AGG-BOHAI-002（日产计量载体——触达路径）
- AGG-BOHAI-004（井检修台账载体——触达路径）
- AGG-BOHAI-006（流体化验台账载体——触达路径）
