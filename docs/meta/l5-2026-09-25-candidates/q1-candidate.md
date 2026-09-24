# Q1 candidate（2026-09-25 L5 评分面，成稿窗零上下文派发）

机判 status：answered（瀑布二级·ID/名称解析命中；ambiguous=true，多候选，机判 note：列候选请锚定修饰词，不擅自合并）

## 答案

「日产量」在本域不是一个单一口径：名称解析命中多个落点（二级多义），核心承载是 `AGG-BOHAI-002`（日产计量），下面按口径四件套（承载字段/校验规则/执行行为/查询出口）装配作答，多义候选与修饰词消歧一并列出。

**1. 承载字段（对象+属性）**：日产量的承载对象是 `AGG-BOHAI-002`（日产计量，别名 OilProductionDaily，源表 oil_production_daily，★核心事实源）：

- `oilOutput`（日产油量（吨），Decimal）与 `liquidOutput`（日产液量（方），Decimal）是日产量两个基本量；
- **行粒度=班次**：复合主键（wellId, prodDate, reportShift），班次值集 A/B/C——**日口径=同井同日各班合计**（Owner 裁决 PROP-BOHAI-007=A：A/B 班各行各含当班真实产量，非重复录入）；
- 计量行经 `ASSOC-BOHAI-001` 挂井：井（`AGG-BOHAI-001`）1..* 日产计量，引用字段 wellRef。

**2. 校验规则**：日产量数据面挂四条 M3 规则——`RULE-BOHAI-003`（日产油非空率 ≥99.5%，数据集级）、`RULE-BOHAI-004`（同井连续 30 日 oilOutput 恒值检测）、`RULE-BOHAI-027`（单井日产油环比日降幅 >40% 且次日未恢复至降幅前 70% 触发核实单）、`RULE-BOHAI-030`（键完整性：(wellId, prodDate, reportShift) 三元组唯一，缺失/重复行进问题单不静默去重）。

**3. 执行行为**：录入走 `BH-BOHAI-RecordDailyOutput`（录入日产计量，ownerEntity=`AGG-BOHAI-002`，挂井号归一化 RULE-BOHAI-005）；日度质检批走 `BH-BOHAI-RunDailyQualityCheck`（执行日产质检，SYSTEM 触发、15 分钟级闭环调度，appliedRules 含上述 RULE-BOHAI-003/004）；查询行为 `BH-BOHAI-QueryWellDailyOutput`（查询单井日产量）装配接线了 `RULE-BOHAI-027`/`RULE-BOHAI-030`（日产突变告警与班次键完整性属日产量口径面）。闭包轨迹：`AGG-BOHAI-002` ←(ownerEntity)← `BH-BOHAI-RecordDailyOutput`；`QR-BOHAI-001` →(behaviorRef)→ `BH-BOHAI-QueryWellDailyOutput`。

**4. 查询出口**：`QR-BOHAI-001`（单井日产量明细查询）——按井号出单井日产计量明细，结果列 oilOutput（日产油量（吨））sourceExpression `d.oilOutput`、liquidOutput、waterCut，明细行含 reportShift（班次重复行注记：去重口径待 Owner）。

**口径边界（双口径并存，勿混）**：井口口径（`AGG-BOHAI-002`.oilOutput 合计）与商品量（`AGG-BOHAI-008` 区块月度结算 netWeight，扣自用油与输差）**并存披露不互替**（Owner 裁决 PROP-BOHAI-020）：生产类指标用井口口径、经营/结算类指标用商品量；两口径之差=自用+输差，折算关系 商品量 = 井口合计 ×（1−自用率−输差率）；经营侧出口是 `QR-BOHAI-003`（区块月度商品量结算查询）。

**多义候选与修饰词锚定**（机判命中多落点，请锚定修饰词，本答不擅自合并）：

- 问「单井逐日明细」→ 上文四件套即所问（出口 `QR-BOHAI-001`）；
- 问「剔检产量（别名：净产量）」→ 剔除检修井口径的产量，见 `GLS-BOHAI-002`（剔检判据=井状态 currentStatus「检修」），口径落点 `RULE-BOHAI-019`（有效产量·剔检口径，剔除 currentStatus=检修 的井后合计）；
- 问「有效产量」→ 一词两译（开井日历支 / 剔检支，两支并列），见 `GLS-BOHAI-003`，单说必须追问修饰词；
- 禁用词处置：`GLS-BOHAI-001`「老完成率」为禁用词（v1 口径，2024 年废弃），不得作为可用口径——替代口径是 `RULE-BOHAI-009`（产量完成率）。

**一句话口径**：日产量 = 井按日·按班次（A/B/C）记录在 `AGG-BOHAI-002`（日产计量）的产量数值（oilOutput 吨 / liquidOutput 方），**日口径=同井同日各班合计**；生产类统计走井口口径，与商品量（`AGG-BOHAI-008`.netWeight）不互替；质检由 `RULE-BOHAI-003`/`RULE-BOHAI-004`/`RULE-BOHAI-027`/`RULE-BOHAI-030` 把关，明细出口 `QR-BOHAI-001`。

## 本回答引用的元素 ID

- AGG-BOHAI-002（日产计量——日产量承载对象，行粒度=班次、日口径=各班合计）
- AGG-BOHAI-001（井——日产计量所属井，wellRef 挂靠宿主）
- ASSOC-BOHAI-001（井 1..* 日产计量——挂井关联）
- RULE-BOHAI-003（日产油非空率校验——数据集级质检规则）
- RULE-BOHAI-004（日产恒值检测——连续 30 日同值告警规则）
- RULE-BOHAI-027（日产油突变告警——降幅 >40% 核实单规则）
- RULE-BOHAI-030（日产键完整性校验——班次三元组唯一）
- RULE-BOHAI-005（井号归一化——录入行为 appliedRules 承载）
- RULE-BOHAI-019（有效产量·剔检口径——剔检支口径落点，多义候选之一）
- RULE-BOHAI-009（产量完成率——「老完成率」禁用词的替代口径）
- BH-BOHAI-RecordDailyOutput（录入日产计量——规则执行行为）
- BH-BOHAI-RunDailyQualityCheck（执行日产质检——质检批行为）
- BH-BOHAI-QueryWellDailyOutput（查询单井日产量——查询行为，装配接线 027/030）
- QR-BOHAI-001（单井日产量明细查询——查询出口）
- AGG-BOHAI-008（区块月度结算——商品量口径宿主，双口径并存边界）
- QR-BOHAI-003（区块月度商品量结算查询——经营/结算侧出口）
- GLS-BOHAI-001（老完成率——禁用词处置）
- GLS-BOHAI-002（剔检产量——别名术语指路）
- GLS-BOHAI-003（有效产量——一词两译，须修饰词消歧）
