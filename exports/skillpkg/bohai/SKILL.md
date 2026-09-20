---
name: bohai-semantic
description: "渤海油田产量域（bohai）可对话技能包骨架——口径问答/对象问答/术语问答；tools/skill_pack_gen.py 自本体切片确定性装配（零 LLM 零时间戳）"
domain: bohai
slice-models: ["M1", "M2", "M3", "M7", "GLS"]
citation-prefixes: ["AGG-", "ASSOC-", "DICT-", "BH-", "RULE-", "QR-", "RPT-", "GLS-"]
status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）
---

# 渤海油田产量域 可对话技能包（skillpkg · bohai）

status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）

- 生成器: tools/skill_pack_gen.py（确定性装配：本体切片 + schema 注册表 camp 面，零 LLM 零时间戳）
- 本体来源: ontology/bohai（profile=v9-full）
- 切片声明: --models M1,M2,M3,M7,GLS（5 模型，全部 camp=business-core）
- 口径同源: 口径问答卡命中集与语义服务 CORE 行为同源（出厂集 fixtures/skill-pack-gen AC1 探针机核）
- 防陈旧: python3 tools/skill_pack_gen.py ontology/bohai --models M1,M2,M3,M7,GLS --check exports/skillpkg/bohai/SKILL.md

## 一、工序路由（问答四步·静态化）

> 问答纪律的静态化表述：检索瀑布运行时真源见语义服务（skills/semantic-service）；成稿润色归人审后的使用方，本包只供确定性骨架。

- ① 显式锚定: 问句带 @ID 时按前缀定模型定阵营（先阵营后存在性）：面内确认存在并反向收名下行为；面外拒答，不返回该元素任何细节。
- ② 名称解析: 无锚定/锚定失败降级：候选词对 name/alias/属性标签/术语确定性分层匹配，不猜不模糊；多义列候选请锚定修饰词，不擅自合并。
- ③ 闭包装配: 命中元素沿引用/影响两向装配证据集（承载/行为/规则/查询出口/术语），只引用装配集内 ID，装配指令可复现。
- ④ 可拒答: 面外/仓内没有/禁用词三分支如实拒答：缺件分层说明+近邻指路；禁用词给替代口径真实 ID；写意图走提案流程。

## 二、口径问答卡（M7 逐口径·与语义服务 CORE 同源）

### 口径 QR-BOHAI-001 · 单井日产量明细查询

- 问题样例: 单井日产量明细查询
- 描述: 按井号查单井日产计量明细（R5·A.2 全字段出口）；D2 班次重复行注记：明细行含 reportShift，去重口径待 Owner。
- 查询出口: QR-BOHAI-001（DETAIL_QUERY）
- 行为: BH-BOHAI-QueryWellDailyOutput 查询单井日产量（QUERY，ownerEntity=AGG-BOHAI-001）
- 承载对象: AGG-BOHAI-002 日产计量（主）、AGG-BOHAI-001 井
- 参数: wellId（井号，String，必填）
- 命中 ID 集: QR-BOHAI-001 BH-BOHAI-QueryWellDailyOutput AGG-BOHAI-002 AGG-BOHAI-001 RULE-BOHAI-005 RULE-BOHAI-002 RULE-BOHAI-003 RULE-BOHAI-004 RULE-BOHAI-008 RULE-BOHAI-009 RULE-BOHAI-019 RULE-BOHAI-010
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-BOHAI-005 井号归一化（TRANSFORMATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: normalizeWellId(rawWellId)
  - RULE-BOHAI-002 计量化验含水偏差校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(waterCut - waterCutLab) <= 5
  - RULE-BOHAI-003 日产油非空率校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: (totalCount - nullCount) / totalCount >= 0.995
  - RULE-BOHAI-004 日产恒值检测（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: 同井生产日期连续 30 日内 oilOutput 全部相同时判为恒值异常，返回 false（告警）
  - RULE-BOHAI-008 区块物质平衡校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(blockInjVolume - blockLiquidVolume - retentionDelta) / blockLiquidVolume <= 0.03
  - RULE-BOHAI-009 产量完成率（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: actualOilSum / planOutputSum * 100
  - RULE-BOHAI-019 有效产量（剔检口径）（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: SUM(dailyProduction.oilOutput WHERE well.currentStatus <> '检修')
  - RULE-BOHAI-010 综合含水率（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: (liquidSum - oilSum) / liquidSum * 100

### 口径 QR-BOHAI-002 · 区块月度产量完成率统计

- 问题样例: 区块月度产量完成率统计
- 描述: 口径真源 RULE-BOHAI-009（完成率）与 RULE-BOHAI-019（有效产量·剔检口径）；D4 配产双值行影响分母注记。剔检列依赖井状态（w.currentStatus）；statMonth 由 prodDate 按月归组（月粒度函数语法随实现层）。
- 查询出口: QR-BOHAI-002（STATISTICAL_QUERY）
- 行为: BH-BOHAI-QueryBlockMonthlyCompletion 查询区块月度产量完成率（QUERY，ownerEntity=AGG-BOHAI-002）
- 承载对象: AGG-BOHAI-002 日产计量（主）、AGG-BOHAI-001 井
- 参数: blockName（区块，String）；statMonth（统计月，String，必填）
- 命中 ID 集: QR-BOHAI-002 BH-BOHAI-QueryBlockMonthlyCompletion AGG-BOHAI-002 AGG-BOHAI-001 RULE-BOHAI-009 RULE-BOHAI-019 RULE-BOHAI-005 RULE-BOHAI-002 RULE-BOHAI-003 RULE-BOHAI-004 RULE-BOHAI-008 RULE-BOHAI-010
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-BOHAI-009 产量完成率（CALCULATION；via=behavior.appliedRules(BH-BOHAI-QueryBlockMonthlyCompletion)）: actualOilSum / planOutputSum * 100
  - RULE-BOHAI-019 有效产量（剔检口径）（CALCULATION；via=behavior.appliedRules(BH-BOHAI-QueryBlockMonthlyCompletion)）: SUM(dailyProduction.oilOutput WHERE well.currentStatus <> '检修')
  - RULE-BOHAI-005 井号归一化（TRANSFORMATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: normalizeWellId(rawWellId)
  - RULE-BOHAI-002 计量化验含水偏差校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(waterCut - waterCutLab) <= 5
  - RULE-BOHAI-003 日产油非空率校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: (totalCount - nullCount) / totalCount >= 0.995
  - RULE-BOHAI-004 日产恒值检测（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: 同井生产日期连续 30 日内 oilOutput 全部相同时判为恒值异常，返回 false（告警）
  - RULE-BOHAI-008 区块物质平衡校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(blockInjVolume - blockLiquidVolume - retentionDelta) / blockLiquidVolume <= 0.03
  - RULE-BOHAI-010 综合含水率（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: (liquidSum - oilSum) / liquidSum * 100

### 口径 QR-BOHAI-003 · 区块月度商品量结算查询

- 问题样例: 区块月度商品量结算查询
- 描述: 商品量=净重（扣自用油与输差，R5·A.8/§3 指标 11）；与井口口径天然不等=事故 7 另一面（D15），两口径并列展示不互替。
- 查询出口: QR-BOHAI-003（DETAIL_QUERY）
- 行为: BH-BOHAI-QueryMonthlySettlement 查询区块月度商品量结算（QUERY，ownerEntity=AGG-BOHAI-008）
- 承载对象: AGG-BOHAI-008 区块月度结算（主）
- 参数: blockName（区块，String）
- 命中 ID 集: QR-BOHAI-003 BH-BOHAI-QueryMonthlySettlement AGG-BOHAI-008
- 口径要点（关联规则 expression/narrative 摘录）:
  - （无关联 M3 规则）

### 口径 QR-BOHAI-004 · 区块综合含水率统计

- 问题样例: 区块综合含水率统计
- 描述: 口径真源 RULE-BOHAI-010（f_w=Q_w/(Q_o+Q_w)，Q_w=Q_液−Q_油 换算待 Owner）；化验 vs 计量打架由 RULE-BOHAI-002 容差承载；与注采比同受物质平衡约束（§3 注记）。
- 查询出口: QR-BOHAI-004（STATISTICAL_QUERY）
- 行为: BH-BOHAI-QueryBlockWaterCut 查询区块综合含水率（QUERY，ownerEntity=AGG-BOHAI-002）
- 承载对象: AGG-BOHAI-002 日产计量（主）、AGG-BOHAI-001 井
- 参数: blockName（区块，String）；statMonth（统计月，String，必填）
- 命中 ID 集: QR-BOHAI-004 BH-BOHAI-QueryBlockWaterCut AGG-BOHAI-002 AGG-BOHAI-001 RULE-BOHAI-010 RULE-BOHAI-005 RULE-BOHAI-002 RULE-BOHAI-003 RULE-BOHAI-004 RULE-BOHAI-008 RULE-BOHAI-009 RULE-BOHAI-019
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-BOHAI-010 综合含水率（CALCULATION；via=behavior.appliedRules(BH-BOHAI-QueryBlockWaterCut)）: (liquidSum - oilSum) / liquidSum * 100
  - RULE-BOHAI-005 井号归一化（TRANSFORMATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: normalizeWellId(rawWellId)
  - RULE-BOHAI-002 计量化验含水偏差校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(waterCut - waterCutLab) <= 5
  - RULE-BOHAI-003 日产油非空率校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: (totalCount - nullCount) / totalCount >= 0.995
  - RULE-BOHAI-004 日产恒值检测（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: 同井生产日期连续 30 日内 oilOutput 全部相同时判为恒值异常，返回 false（告警）
  - RULE-BOHAI-008 区块物质平衡校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(blockInjVolume - blockLiquidVolume - retentionDelta) / blockLiquidVolume <= 0.03
  - RULE-BOHAI-009 产量完成率（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: actualOilSum / planOutputSum * 100
  - RULE-BOHAI-019 有效产量（剔检口径）（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: SUM(dailyProduction.oilOutput WHERE well.currentStatus <> '检修')

## 三、引用纪律与拒答边界

- ID 引用格式: 回答必带元素 ID 引用（前缀形态真实 ID，如 AGG-BOHAI-002），逐条可经 `python3 tools/graph_index.py <域> --query <ID> --json` 复核；成稿须含「本回答引用的元素 ID」清单节，与正文 ID token 双向一致（tools/check_citations.py 检具）。
- camp 面外: SCR-（MU UI 模型，camp=build-contract） → 面外拒答，不返回该面任何细节（建造契约由 build 侧消费方在建造链路消费）
- 切片外: ACTOR-/ROLE-/PERM-（M5 主体模型，camp=business-core）；FLOW-（M6 流程模型，camp=business-core） → business-core 但未入本包切片，按缺件如实说明不硬凑
- 禁用词: 老完成率（GLS-BOHAI-001，status=禁用（替代：产量完成率）） → 问面命中即拦，指替代口径真实 ID，不得作为可用口径作答
- 可拒答声明：仓内没有就说明缺什么，绝不编造；写意图一律回「走提案流程」（进仓走 MR + 语义 CI）；本包只读——运行面语义消费，不做本体写入。
