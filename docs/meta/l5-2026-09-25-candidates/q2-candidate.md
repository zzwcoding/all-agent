# Q2 candidate（2026-09-25 L5 评分面，成稿窗零上下文派发）

机判 status：`answered`（`python3 tools/semantic_service_core.py ontology/bohai --ask "@AGG-BOHAI-001 有哪些行为？" --json`，waterfall_level=一级·显式锚定，hits=8，citations=32）。

## 答案

问题带 @AGG-BOHAI-001，**显式锚定直接命中**，未走名称模糊检索。检索面检查：`AGG-BOHAI-001` 前缀 AGG- → 对象模型 M1，camp=business-core（ontology/schema/model-registry.json），在检索面内，进入闭包装配。

锚定对象 `AGG-BOHAI-001`（井，AGGREGATE_ROOT，别名 Well）名下行为共 **7 条**，按 ownerEntity 挂靠方式分两类（机判经 `--impact` 反向收集 ownerEntity 得出，hops=1/2 区分，可复现命令：`python3 tools/graph_index.py ontology/bohai --query AGG-BOHAI-001 --impact --json`）：

**一、直接挂靠（ownerEntity 即本对象，hops=1）——1 条：**

- `BH-BOHAI-QueryWellDailyOutput`（查询单井日产量，QUERY）：轨迹 `AGG-BOHAI-001` ←(ownerEntity)← `BH-BOHAI-QueryWellDailyOutput`；其查询出口为 `QR-BOHAI-001`（单井日产量明细查询，behaviorRef 回指本行为）。

**二、经子对象挂靠（ownerEntity 指向本聚合的子对象，hops=2）——6 条：**

- 经 `AGG-BOHAI-002`（日产计量）挂靠，挂靠链 `BH-BOHAI-RecordDailyOutput` →(ownerEntity)→ `AGG-BOHAI-002` →(ASSOC-BOHAI-001)→ `AGG-BOHAI-001`：
  - `BH-BOHAI-RecordDailyOutput`（录入日产计量，COMMAND）
  - `BH-BOHAI-RunDailyQualityCheck`（执行日产质检，COMMAND）
  - `BH-BOHAI-QueryBlockMonthlyCompletion`（查询区块月度产量完成率，QUERY），查询出口 `QR-BOHAI-002`（区块月度产量完成率统计）
  - `BH-BOHAI-QueryBlockWaterCut`（查询区块综合含水率，QUERY），查询出口 `QR-BOHAI-004`（区块综合含水率统计）
- 经 `AGG-BOHAI-004`（井检修记录）挂靠，挂靠链 `BH-BOHAI-RecordOverhaul` →(ownerEntity)→ `AGG-BOHAI-004` →(ASSOC-BOHAI-003)→ `AGG-BOHAI-001`：
  - `BH-BOHAI-RecordOverhaul`（补录井检修台账，COMMAND）
- 经 `AGG-BOHAI-006`（流体化验记录）挂靠，挂靠链 `BH-BOHAI-RecordFluidTest` →(ownerEntity)→ `AGG-BOHAI-006` →(ASSOC-BOHAI-005)→ `AGG-BOHAI-001`：
  - `BH-BOHAI-RecordFluidTest`（录入流体化验结果，COMMAND）

以上 7 条行为即机判命中集（hits）的全部内容，回答只基于该装配证据集；集合外的关联不展开。

## 本回答引用的元素 ID

- AGG-BOHAI-001（井——显式锚定对象，一级直达，AGGREGATE_ROOT）
- BH-BOHAI-QueryWellDailyOutput（查询单井日产量——直接挂靠行为，hops=1）
- QR-BOHAI-001（单井日产量明细查询——上条查询行为的查询出口）
- AGG-BOHAI-002（日产计量——hops=2 挂靠子对象）
- ASSOC-BOHAI-001（井 1..* 日产计量——挂靠链关联）
- BH-BOHAI-RecordDailyOutput（录入日产计量——经子对象挂靠行为）
- BH-BOHAI-RunDailyQualityCheck（执行日产质检——经子对象挂靠行为）
- BH-BOHAI-QueryBlockMonthlyCompletion（查询区块月度产量完成率——经子对象挂靠行为）
- QR-BOHAI-002（区块月度产量完成率统计——上条查询行为的查询出口）
- BH-BOHAI-QueryBlockWaterCut（查询区块综合含水率——经子对象挂靠行为）
- QR-BOHAI-004（区块综合含水率统计——上条查询行为的查询出口）
- AGG-BOHAI-004（井检修记录——hops=2 挂靠子对象）
- ASSOC-BOHAI-003（井 1..* 井检修记录——挂靠链关联）
- BH-BOHAI-RecordOverhaul（补录井检修台账——经子对象挂靠行为）
- AGG-BOHAI-006（流体化验记录——hops=2 挂靠子对象）
- ASSOC-BOHAI-005（井 1..* 流体化验记录——挂靠链关联）
- BH-BOHAI-RecordFluidTest（录入流体化验结果——经子对象挂靠行为）
