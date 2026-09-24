---
name: his-semantic
description: "HIS 医院数据报表域（his）可对话技能包骨架——口径问答/对象问答/术语问答；tools/skill_pack_gen.py 自本体切片确定性装配（零 LLM 零时间戳）"
domain: his
slice-models: ["M1", "M2", "M3", "M7", "GLS"]
citation-prefixes: ["AGG-", "ASSOC-", "DICT-", "BH-", "RULE-", "QR-", "RPT-", "GLS-"]
status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）
---

# HIS 医院数据报表域 可对话技能包（skillpkg · his）

status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）

- 生成器: tools/skill_pack_gen.py（确定性装配：本体切片 + schema 注册表 camp 面，零 LLM 零时间戳）
- 本体来源: ontology/his（profile=v9-full）
- 切片声明: --models M1,M2,M3,M7,GLS（5 模型，全部 camp=business-core）
- 口径同源: 口径问答卡命中集与语义服务 CORE 行为同源（出厂集 fixtures/skill-pack-gen AC1 探针机核）
- 防陈旧: python3 tools/skill_pack_gen.py ontology/his --models M1,M2,M3,M7,GLS --check exports/skillpkg/his/SKILL.md

## 一、工序路由（问答四步·静态化）

> 问答纪律的静态化表述：检索瀑布运行时真源见语义服务（skills/semantic-service）；成稿润色归人审后的使用方，本包只供确定性骨架。

- ① 显式锚定: 问句带 @ID 时按前缀定模型定阵营（先阵营后存在性）：面内确认存在并反向收名下行为；面外拒答，不返回该元素任何细节。
- ② 名称解析: 无锚定/锚定失败降级：候选词对 name/alias/属性标签/术语确定性分层匹配，不猜不模糊；多义列候选请锚定修饰词，不擅自合并。
- ③ 闭包装配: 命中元素沿引用/影响两向装配证据集（承载/行为/规则/查询出口/术语），只引用装配集内 ID，装配指令可复现。
- ④ 可拒答: 面外/仓内没有/禁用词三分支如实拒答：缺件分层说明+近邻指路；禁用词给替代口径真实 ID；写意图走提案流程。

## 二、口径问答卡（M7 逐口径·与语义服务 CORE 同源）

### 口径 QR-HIS-001 · 院长驾驶舱 KPI 查询

- 问题样例: 院长驾驶舱 KPI 查询
- 描述: 日粒度院长驾驶舱出口（R13·§5.2.1 七字段对应五 KPI 卡）；异常预警面=退号率 RULE-HIS-001 阈值。ADS 实现=ads_dashboard_kpi。
- 查询出口: QR-HIS-001（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryDashboard 查询院长驾驶舱（QUERY，ownerEntity=AGG-HIS-001）
- 承载对象: AGG-HIS-001 挂号记录（主）、AGG-HIS-004 处方、AGG-HIS-003 诊断记录
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 命中 ID 集: QR-HIS-001 BH-HIS-QueryDashboard AGG-HIS-001 AGG-HIS-004 AGG-HIS-003 RULE-HIS-001 RULE-HIS-003 RULE-HIS-005 RULE-HIS-002 RULE-HIS-004 RULE-HIS-007 RULE-HIS-006
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HIS-001 退号率告警阈值（VALIDATION；via=behavior.appliedRules(BH-HIS-QueryDashboard)）: refundRate <= 10
  - RULE-HIS-003 退号率口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryDashboard)）: refundCount / registerCount * 100
  - RULE-HIS-005 处方退费率口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryDashboard)）: refundPresc / totalPresc * 100
  - RULE-HIS-002 支付方式收入占比合计校验（VALIDATION；via=ownerObjectBehaviors(AGG-HIS-001)）: pctSum == 100
  - RULE-HIS-004 均次费用口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: totalRevenue / totalVisits
  - RULE-HIS-007 复诊率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: revisitPatients / totalPatients * 100
  - RULE-HIS-006 病历完整率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-003)）: filledDims / 5 * 100

### 口径 QR-HIS-002 · 科室接诊排行查询

- 问题样例: 科室接诊排行查询
- 描述: 天+科室粒度接诊排行（R13·§5.2.2 八字段全对应）：接诊量/退号量/退号率/总收入/均次费用，退号率>10% 红色标注（RULE-HIS-001）。ADS 实现=ads_dept_visit_rank。
- 查询出口: QR-HIS-002（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryOutpatient 查询门诊运营（QUERY，ownerEntity=AGG-HIS-001）
- 承载对象: AGG-HIS-001 挂号记录（主）
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 命中 ID 集: QR-HIS-002 BH-HIS-QueryOutpatient AGG-HIS-001 RULE-HIS-001 RULE-HIS-003 RULE-HIS-004 RULE-HIS-002 RULE-HIS-005 RULE-HIS-007
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HIS-001 退号率告警阈值（VALIDATION；via=behavior.appliedRules(BH-HIS-QueryOutpatient)）: refundRate <= 10
  - RULE-HIS-003 退号率口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryOutpatient)）: refundCount / registerCount * 100
  - RULE-HIS-004 均次费用口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryOutpatient)）: totalRevenue / totalVisits
  - RULE-HIS-002 支付方式收入占比合计校验（VALIDATION；via=ownerObjectBehaviors(AGG-HIS-001)）: pctSum == 100
  - RULE-HIS-005 处方退费率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: refundPresc / totalPresc * 100
  - RULE-HIS-007 复诊率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: revisitPatients / totalPatients * 100

### 口径 QR-HIS-003 · 支付方式收入查询

- 问题样例: 支付方式收入查询
- 描述: 天+支付方式粒度收入构成（R13·§5.2.4 六字段全对应）：五方式占比合计=100% 校验（RULE-HIS-002）。ADS 实现=ads_revenue_payment。
- 查询出口: QR-HIS-003（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryFinance 查询收费结算（QUERY，ownerEntity=AGG-HIS-001）
- 承载对象: AGG-HIS-001 挂号记录（主）
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 命中 ID 集: QR-HIS-003 BH-HIS-QueryFinance AGG-HIS-001 RULE-HIS-002 RULE-HIS-004 RULE-HIS-003 RULE-HIS-001 RULE-HIS-005 RULE-HIS-007
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HIS-002 支付方式收入占比合计校验（VALIDATION；via=behavior.appliedRules(BH-HIS-QueryFinance)）: pctSum == 100
  - RULE-HIS-004 均次费用口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryFinance)）: totalRevenue / totalVisits
  - RULE-HIS-003 退号率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: refundCount / registerCount * 100
  - RULE-HIS-001 退号率告警阈值（VALIDATION；via=ownerObjectBehaviors(AGG-HIS-001)）: refundRate <= 10
  - RULE-HIS-005 处方退费率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: refundPresc / totalPresc * 100
  - RULE-HIS-007 复诊率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: revisitPatients / totalPatients * 100

### 口径 QR-HIS-004 · 药品销售排行查询

- 问题样例: 药品销售排行查询
- 描述: 药品粒度销售 TOP20+类型占比+退费率趋势三出口合一（R13·§5.2.5/6/7 字段对应）：总额/总量/排名按总销售额降序。ADS 实现=ads_drug_sales_top20 + ads_drug_type_ratio + ads_presc_refund_rate。
- 查询出口: QR-HIS-004（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryDrug 查询药品处方（QUERY，ownerEntity=AGG-HIS-004）
- 承载对象: AGG-HIS-004 处方（主）
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 命中 ID 集: QR-HIS-004 BH-HIS-QueryDrug AGG-HIS-004 RULE-HIS-005
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HIS-005 处方退费率口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryDrug)）: refundPresc / totalPresc * 100

### 口径 QR-HIS-005 · 疾病诊断分布查询

- 问题样例: 疾病诊断分布查询
- 描述: 诊断粒度 TOP20+ICD-10 章节分布+病历完整率雷达三出口合一（R13·§6.1 模块五 + §5.3 disease/medical_record）：ICD 章节=DICT-HIS-001 编码段首字母映射（推定，待 Owner）。
- 查询出口: QR-HIS-005（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryDisease 查询疾病诊断（QUERY，ownerEntity=AGG-HIS-003）
- 承载对象: AGG-HIS-003 诊断记录（主）、AGG-HIS-002 门诊病历
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 命中 ID 集: QR-HIS-005 BH-HIS-QueryDisease AGG-HIS-003 AGG-HIS-002 RULE-HIS-006
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HIS-006 病历完整率口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryDisease)）: filledDims / 5 * 100

### 口径 QR-HIS-006 · 患者画像查询

- 问题样例: 患者画像查询
- 描述: 就诊粒度患者画像（R13·§6.1 模块六）：年龄-性别金字塔+复诊率详情卡。地域分布 TOP10 素材无源字段（§5.3 register 无地域列）——缺口如实记，不建列；患者主数据未建，同一人判定按 patientName 推定（RULE-HIS-007 注记）。
- 查询出口: QR-HIS-006（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryPatient 查询患者画像（QUERY，ownerEntity=AGG-HIS-001）
- 承载对象: AGG-HIS-001 挂号记录（主）
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 命中 ID 集: QR-HIS-006 BH-HIS-QueryPatient AGG-HIS-001 RULE-HIS-007 RULE-HIS-002 RULE-HIS-003 RULE-HIS-001 RULE-HIS-005 RULE-HIS-004
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HIS-007 复诊率口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryPatient)）: revisitPatients / totalPatients * 100
  - RULE-HIS-002 支付方式收入占比合计校验（VALIDATION；via=ownerObjectBehaviors(AGG-HIS-001)）: pctSum == 100
  - RULE-HIS-003 退号率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: refundCount / registerCount * 100
  - RULE-HIS-001 退号率告警阈值（VALIDATION；via=ownerObjectBehaviors(AGG-HIS-001)）: refundRate <= 10
  - RULE-HIS-005 处方退费率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: refundPresc / totalPresc * 100
  - RULE-HIS-004 均次费用口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: totalRevenue / totalVisits

## 三、引用纪律与拒答边界

- ID 引用格式: 回答必带元素 ID 引用（前缀形态真实 ID，如 AGG-BOHAI-002），逐条可经 `python3 tools/graph_index.py <域> --query <ID> --json` 复核；成稿须含「本回答引用的元素 ID」清单节，与正文 ID token 双向一致（tools/check_citations.py 检具）。
- camp 面外: SCR-（MU UI 模型，camp=build-contract） → 面外拒答，不返回该面任何细节（建造契约由 build 侧消费方在建造链路消费）
- 切片外: ACTOR-/ROLE-/PERM-（M5 主体模型，camp=business-core）；FLOW-（M6 流程模型，camp=business-core） → business-core 但未入本包切片，按缺件如实说明不硬凑
- 禁用词: 无禁用术语（GLS status 全非禁用）
- 可拒答声明：仓内没有就说明缺什么，绝不编造；写意图一律回「走提案流程」（进仓走 MR + 语义 CI）；本包只读——运行面语义消费，不做本体写入。
