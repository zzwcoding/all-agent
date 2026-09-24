# HIS 医院数据报表域 开发包（devkit · his）

status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）

- 生成器: tools/app_pack_gen.py（确定性装配：YAML 机读 + 提案 frontmatter 扫描，零 LLM 零时间戳）
- 本体来源: ontology/his（profile=v9-full）
- 声明模型: M1 对象模型 / M2 行为模型 / M3 规则模型 / M7 查询统计与报表模型
- 固定输入: fixtures/app-pack-gen/inputs/tech-constraints.md（出厂集固定输入（合成））、fixtures/app-pack-gen/inputs/dev-guide.md（出厂集固定输入（合成））
- 开放提案开关: 启用（docs/proposals）
- 防陈旧: python3 tools/app_pack_gen.py ontology/his --check exports/devkit/his/devkit.md

## 技术架构约束（固定输入，原样装配）

出厂集固定输入（合成）——中性示例文本，非任何真实项目规约；生成器按原样装配进开发包头部约束节，文件内容不参与判定。

## 技术架构约束

- 服务端形态：Python 服务端 + 关系库，三层架构（接入 / 领域 / 数据）。
- 数据访问：一切业务数据经语义层数据字典取数，禁直连物理表名。
- 集成边界：对外只暴露查询出口与行为接口，不出裸表。

（以上为合成中性约束，仅作开发包装配通路的固定输入。）

## 开发指导书（固定输入，原样装配）

出厂集固定输入（合成）——中性示例文本，非任何真实项目规约；生成器按原样装配进开发包头部约束节，文件内容不参与判定。

## 开发指导书

- 装配顺序：先数据字典后接口——数据字典是接口签名的唯一依据。
- 口径实现：统计口径以规则清单（M3）的 expression/narrative 为准，查询出口（M7）只是实现形态，两处不一致时以规则为准并回提案流程。
- 疑点处置：开发包第④节开放疑点逐条过目，命中疑点的实现先挂起待 Owner 裁决，不自行拍板。

（以上为合成中性指导，仅作开发包装配通路的固定输入。）

---

## 一、数据字典（M1 对象模型）

### AGG-HIS-001 挂号记录（RegisterRecord）

- AGGREGATE_ROOT；描述: 患者就诊的登记枢纽行（R13·详细设计 §5.3 register：关联患者/科室/医生， 用于就诊状态流/年龄金字塔/地域分布/复诊率）。行粒度=一次挂号（case_number 就诊号唯一，PRD §1.3）。visitStatus 状态集按 §1.3 流程图推定（Q2 待 Owner 确认）；支付方式五值取自 §5.2.4 regist_method 字段示例。
- lifecycle: 挂号/候诊/接诊中/已诊断/已开方/已收费/已完成/已退号

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| caseNumber | 就诊号 | String | unique |
| patientName | 患者姓名 | String |  |
| patientAge | 患者年龄 | Integer |  |
| patientGender | 患者性别 | Enum | 字典值集: 男/女 |
| deptName | 就诊科室 | String |  |
| doctorName | 接诊医生 | String |  |
| visitStatus | 就诊状态 | Enum | 字典值集: 挂号/候诊/接诊中/已诊断/已开方/已收费/已完成/已退号 |
| registMethod | 支付方式 | Enum | 字典值集: 现金/银行卡/微信/支付宝/医保卡 |
| registerFee | 挂号费 | Decimal |  |
| visitDay | 就诊日期 | Date |  |

### AGG-HIS-002 门诊病历（OutpatientMedicalRecord）

- AGGREGATE_ROOT；描述: 医生接诊书写的门诊病历（R13·§5.3 medical_record：主诉/现病史/既往史/ 过敏史/体格检查）。5 维度完整率雷达图（PRD §6.1 模块五）的判定载体—— 每维度非空即完整（RULE-HIS-006 口径）。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| caseRef | 所属就诊 | AggregateRootRef | 引用→AGG-HIS-001 |
| chiefComplaint | 主诉 | String |  |
| presentHistory | 现病史 | String |  |
| pastHistory | 既往史 | String |  |
| allergyHistory | 过敏史 | String |  |
| physicalExam | 体格检查 | String |  |

### AGG-HIS-003 诊断记录（DiagnosisRecord）

- AGGREGATE_ROOT；描述: 医生对一次就诊给出的诊断（R13·§5.3 medical_record_disease：病历-疾病 关联表，关联 disease 表取 ICD-10 中文病名）。行粒度=一次就诊×一个诊断。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| caseRef | 所属就诊 | AggregateRootRef | 引用→AGG-HIS-001 |
| diseaseCode | 疾病编码 | String |  |
| diseaseName | 疾病名称 | String |  |
| diagnosisDay | 诊断日期 | Date |  |

### AGG-HIS-004 处方（Prescription）

- AGGREGATE_ROOT；描述: 医生开具的药品处方（R13·§5.3 prescription：关联 drug_info）。行粒度= 一张处方；退药退费以 refundFlag 承载（§5.2.7 refund_presc 的判定字段， 退费冲减规则 Q4 待 Owner）。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| caseRef | 所属就诊 | AggregateRootRef | 引用→AGG-HIS-001 |
| drugId | 药品 ID | Integer |  |
| drugName | 药品名称 | String |  |
| quantity | 数量 | Integer |  |
| usage | 用法 | String |  |
| prescribeDay | 开立日期 | Date |  |
| refundFlag | 退药退费标记 | Boolean |  |

### AGG-HIS-005 检验申请（InspectionRequest）

- AGGREGATE_ROOT；描述: 医生开具的检验/检查申请单（R13·§5.3 inspection_request：关联 medical_technology 项目字典）。完成率及平均耗时的载体（PRD §4.3 指标 6）。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| caseRef | 所属就诊 | AggregateRootRef | 引用→AGG-HIS-001 |
| itemName | 医技项目 | String |  |
| requestStatus | 申请状态 | Enum | 字典值集: 已申请/已完成 |
| fee | 费用 | Decimal |  |
| requestDay | 申请日期 | Date |  |

聚合关联（aggregate_associations）:

| 关联 | 源 → 靶 | 类型 | 基数 | 引用字段 | 角色 |
|---|---|---|---|---|---|
| ASSOC-HIS-001 | AGG-HIS-001 → AGG-HIS-004 | REFERENCE | ONE_TO_MANY | caseRef | 就诊→处方 |
| ASSOC-HIS-002 | AGG-HIS-001 → AGG-HIS-003 | REFERENCE | ONE_TO_MANY | caseRef | 就诊→诊断记录 |

## 二、口径四件套（M7 查询出口 × M2 行为 × M3 规则 × M1 承载）

### 口径 QR-HIS-001 · 院长驾驶舱 KPI 查询

- 问题样例: 院长驾驶舱 KPI 查询
- 查询出口: QR-HIS-001（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryDashboard 查询院长驾驶舱（QUERY/，ownerEntity=AGG-HIS-001）
- 承载对象: AGG-HIS-001 挂号记录（主）、AGG-HIS-004 处方、AGG-HIS-003 诊断记录
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 结果列: visitDay=统计日期（r.visitDay）；registerCnt=挂号人次（COUNT(r.caseNumber)）；registerRevenue=挂号收入（元）（SUM(r.registerFee)）；refundCnt=退号数（COUNT(CASE WHEN r.visitStatus = '已退号' THEN 1 END)）；prescriptionCnt=处方数（COUNT(p.prescribeDay)）；diseaseTypes=疾病种数（COUNT(DISTINCT d.diseaseCode)）；refundRate=退号率（%）（refundCnt / registerCnt * 100）
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
- 查询出口: QR-HIS-002（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryOutpatient 查询门诊运营（QUERY/，ownerEntity=AGG-HIS-001）
- 承载对象: AGG-HIS-001 挂号记录（主）
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 结果列: deptName=科室名称（r.deptName）；totalVisits=接诊量（COUNT(r.caseNumber)）；refundCount=退号量（COUNT(CASE WHEN r.visitStatus = '已退号' THEN 1 END)）；refundRate=退号率（%）（refundCount / totalVisits * 100）；totalRevenue=总收入（元）（SUM(r.registerFee)）；avgFee=均次费用（元）（totalRevenue / totalVisits）
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
- 查询出口: QR-HIS-003（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryFinance 查询收费结算（QUERY/，ownerEntity=AGG-HIS-001）
- 承载对象: AGG-HIS-001 挂号记录（主）
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 结果列: visitDay=就诊日期（r.visitDay）；registMethod=支付方式（r.registMethod）；visitCount=挂号笔数（COUNT(r.caseNumber)）；revenue=该方式收入（元）（SUM(r.registerFee)）；revenuePct=收入占比（%）（revenue / SUM(revenue) OVER (visitDay) * 100）
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
- 查询出口: QR-HIS-004（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryDrug 查询药品处方（QUERY/，ownerEntity=AGG-HIS-004）
- 承载对象: AGG-HIS-004 处方（主）
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 结果列: drugName=药品名称（p.drugName）；totalQty=销售总量（SUM(p.quantity)）；totalSales=销售总额（元）（SUM(p.quantity * 药品单价)）；overallRank=总排名（RANK() OVER (ORDER BY totalSales DESC)）；refundRate=处方退费率（%）（COUNT(CASE WHEN p.refundFlag THEN 1 END) / COUNT(p.prescribeDay) * 100）
- 命中 ID 集: QR-HIS-004 BH-HIS-QueryDrug AGG-HIS-004 RULE-HIS-005
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HIS-005 处方退费率口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryDrug)）: refundPresc / totalPresc * 100

### 口径 QR-HIS-005 · 疾病诊断分布查询

- 问题样例: 疾病诊断分布查询
- 查询出口: QR-HIS-005（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryDisease 查询疾病诊断（QUERY/，ownerEntity=AGG-HIS-003）
- 承载对象: AGG-HIS-003 诊断记录（主）、AGG-HIS-002 门诊病历
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 结果列: diseaseCode=疾病编码（d.diseaseCode）；diseaseName=疾病名称（d.diseaseName）；diagCount=诊断次数（COUNT(d.diseaseCode)）；icdChapter=ICD-10 章节（SUBSTR(d.diseaseCode, 1, 1)）；recordCompleteRate=病历完整率（%）（(非空维度计数) / 5 * 100）
- 命中 ID 集: QR-HIS-005 BH-HIS-QueryDisease AGG-HIS-003 AGG-HIS-002 RULE-HIS-006
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HIS-006 病历完整率口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryDisease)）: filledDims / 5 * 100

### 口径 QR-HIS-006 · 患者画像查询

- 问题样例: 患者画像查询
- 查询出口: QR-HIS-006（STATISTICAL_QUERY）
- 行为: BH-HIS-QueryPatient 查询患者画像（QUERY/，ownerEntity=AGG-HIS-001）
- 承载对象: AGG-HIS-001 挂号记录（主）
- 参数: startDay（开始日期，Date，必填）；endDay（结束日期，Date，必填）
- 结果列: ageGroup=年龄段（CASE 分组(r.patientAge)）；patientGender=性别（r.patientGender）；patientCnt=患者数（COUNT(DISTINCT r.patientName)）；revisitRate=复诊率（%）（窗口期内≥2 次挂号患者数 / 总患者数 * 100）
- 命中 ID 集: QR-HIS-006 BH-HIS-QueryPatient AGG-HIS-001 RULE-HIS-007 RULE-HIS-002 RULE-HIS-003 RULE-HIS-001 RULE-HIS-005 RULE-HIS-004
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HIS-007 复诊率口径（CALCULATION；via=behavior.appliedRules(BH-HIS-QueryPatient)）: revisitPatients / totalPatients * 100
  - RULE-HIS-002 支付方式收入占比合计校验（VALIDATION；via=ownerObjectBehaviors(AGG-HIS-001)）: pctSum == 100
  - RULE-HIS-003 退号率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: refundCount / registerCount * 100
  - RULE-HIS-001 退号率告警阈值（VALIDATION；via=ownerObjectBehaviors(AGG-HIS-001)）: refundRate <= 10
  - RULE-HIS-005 处方退费率口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: refundPresc / totalPresc * 100
  - RULE-HIS-004 均次费用口径（CALCULATION；via=ownerObjectBehaviors(AGG-HIS-001)）: totalRevenue / totalVisits

## 三、行为与规则清单（M2/M3 全量，注源=模型文件 [R<n>·…] 注释标签）

### 行为（M2 · 14 条）

- BH-HIS-Register 挂号登记 [COMMAND/USER_ACTION] ownerEntity=AGG-HIS-001 appliedRules=—
- BH-HIS-WriteMedicalRecord 书写病历 [COMMAND/USER_ACTION] ownerEntity=AGG-HIS-002 appliedRules=RULE-HIS-006
- BH-HIS-Diagnose 开具诊断 [COMMAND/USER_ACTION] ownerEntity=AGG-HIS-003 appliedRules=—
- BH-HIS-Prescribe 开具处方 [COMMAND/USER_ACTION] ownerEntity=AGG-HIS-004 appliedRules=—
- BH-HIS-RequestInspection 开具检验申请 [COMMAND/USER_ACTION] ownerEntity=AGG-HIS-005 appliedRules=—
- BH-HIS-Settle 收费结算 [COMMAND/USER_ACTION] ownerEntity=AGG-HIS-001 appliedRules=RULE-HIS-002
- BH-HIS-CancelRegister 退号 [COMMAND/USER_ACTION] ownerEntity=AGG-HIS-001 appliedRules=RULE-HIS-003
- BH-HIS-RefundPrescription 退药退费 [COMMAND/USER_ACTION] ownerEntity=AGG-HIS-004 appliedRules=RULE-HIS-005
- BH-HIS-QueryDashboard 查询院长驾驶舱 [QUERY/] ownerEntity=AGG-HIS-001 appliedRules=RULE-HIS-001,RULE-HIS-003,RULE-HIS-005
- BH-HIS-QueryOutpatient 查询门诊运营 [QUERY/] ownerEntity=AGG-HIS-001 appliedRules=RULE-HIS-001,RULE-HIS-003,RULE-HIS-004
- BH-HIS-QueryFinance 查询收费结算 [QUERY/] ownerEntity=AGG-HIS-001 appliedRules=RULE-HIS-002,RULE-HIS-004
- BH-HIS-QueryDrug 查询药品处方 [QUERY/] ownerEntity=AGG-HIS-004 appliedRules=RULE-HIS-005
- BH-HIS-QueryDisease 查询疾病诊断 [QUERY/] ownerEntity=AGG-HIS-003 appliedRules=RULE-HIS-006
- BH-HIS-QueryPatient 查询患者画像 [QUERY/] ownerEntity=AGG-HIS-001 appliedRules=RULE-HIS-007

### 规则（M3 · 7 条）

- RULE-HIS-001 退号率告警阈值 [VALIDATION]  — refundRate <= 10
- RULE-HIS-002 支付方式收入占比合计校验 [VALIDATION]  — pctSum == 100
- RULE-HIS-003 退号率口径 [CALCULATION]  — refundCount / registerCount * 100
- RULE-HIS-004 均次费用口径 [CALCULATION]  — totalRevenue / totalVisits
- RULE-HIS-005 处方退费率口径 [CALCULATION]  — refundPresc / totalPresc * 100
- RULE-HIS-006 病历完整率口径 [CALCULATION]  — filledDims / 5 * 100
- RULE-HIS-007 复诊率口径 [CALCULATION]  — revisitPatients / totalPatients * 100

## 四、开放疑点（docs/proposals 扫描）

无开放提案。
