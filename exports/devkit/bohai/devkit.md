# 渤海油田产量域 开发包（devkit · bohai）

status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）

- 生成器: tools/app_pack_gen.py（确定性装配：YAML 机读 + 提案 frontmatter 扫描，零 LLM 零时间戳）
- 本体来源: ontology/bohai（profile=v9-full）
- 声明模型: M1 对象模型 / M2 行为模型 / M3 规则模型 / M7 查询统计与报表模型
- 固定输入: fixtures/app-pack-gen/inputs/tech-constraints.md（出厂集固定输入（合成））、fixtures/app-pack-gen/inputs/dev-guide.md（出厂集固定输入（合成））
- 开放提案开关: 启用（docs/proposals）
- 防陈旧: python3 tools/app_pack_gen.py ontology/bohai --check exports/devkit/bohai/devkit.md

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

### AGG-BOHAI-001 井（Well）

- 注源: R5·A.1 井档案 + §5 实体「井」
- AGGREGATE_ROOT；描述: 源表 well_info（R5·设定书附录 A.1，字典标题「井档案」；§5 实体草案名「井」），一井一行。§1 组织规模：3 作业区 120 口在产井（采油 86/注水 34）、5 平台。疑点残留：井号旧写法 N2/N-2 并存（D6，归一化落 RULE-BOHAI-005，全集待素材）；fieldName 行内冗余（D8）——待 Owner 确认。状态滞后（D7）已裁：责任方=作业区录入+治理稽核检出（PROP-BOHAI-012，2026-09-21）。
- lifecycle: 生产中/停产/检修/待弃置

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| wellId | 井号 | String | unique |
| wellName | 井名 | String |  |
| wellType | 井别 | Enum | 字典值集: EW/IW |
| firstProdDate | 首次投产日期 | Date |  |
| platform | 平台 | String |  |
| blockName | 区块 | String |  |
| fieldName | 油田 | String |  |
| currentStatus | 当前状态 | Enum | 字典值集: 生产中/停产/检修/待弃置 |
| remarks | 备注 | String |  |

### AGG-BOHAI-002 日产计量（OilProductionDaily）

- 注源: R5·A.2 日产计量（★核心事实源）+ §5 Join 白名单 oil ⋈ well ✓
- AGGREGATE_ROOT；描述: 源表 oil_production_daily（R5·设定书附录 A.2，字典标注核心事实源），**行粒度=班次**（Owner 2026-09-21，PROP-BOHAI-007 裁决=A：A/B 班各行各含当班真实产量，非重复录入），复合主键（wellId, prodDate, reportShift）；**日口径=同井同日各班合计**（SUM 天然兼容，下游按日聚合规则不受影响）。§3 指标 1/3/4/5/7/10/14 的承载事实源。疑点残留：吨方混写（D1→RULE-BOHAI-020 检出位已建）；配产双值行（D4）；openDays 停井日>0（D5，值域已下沉 refRules）——均待 Owner 确认。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| wellRef | 所属井 | AggregateRootRef | 引用→AGG-BOHAI-001 |
| wellId | 井号 | String |  |
| prodDate | 生产日期 | Date |  |
| oilOutput | 日产油量（吨） | Decimal |  |
| liquidOutput | 日产液量（方） | Decimal |  |
| waterCut | 含水率（%） | Decimal | 值域[含水率值域]: value >= 0 and value <= 100 |
| planOutput | 配产量（吨） | Decimal |  |
| openDays | 开井时长（天） | Decimal | 值域[开井时长值域]: value >= 0 and value <= 24 |
| oilPressure | 油压（MPa） | Decimal |  |
| reportShift | 报表班次 | Enum | 字典值集: A/B/C |

### AGG-BOHAI-003 注水日计量（WaterInjectionDaily）

- 注源: R5·A.3 + §5
- AGGREGATE_ROOT；描述: 源表 water_injection_daily（R5·设定书附录 A.3），键=井号+日期，复合主键（wellId, injDate）；injDate 为列名转写补记。layerSplit 保持 String 已裁决确认（D9，PROP-BOHAI-014 方向裁决 2026-09-21：不发明格式，规范待 Owner 素材）。§5：oil_production_daily ⋈ 本对象直连禁止（须经 AGG-BOHAI-009 受效关系）。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| wellRef | 所属井 | AggregateRootRef | 引用→AGG-BOHAI-001 |
| wellId | 井号 | String |  |
| injDate | 注水日期 | Date |  |
| injVolume | 注水量（方） | Decimal |  |
| pumpPressure | 泵压（MPa） | Decimal |  |
| layerSplit | 分层配注 | String |  |

### AGG-BOHAI-004 井检修记录（WellOverhaul）

- 注源: R5·A.4
- AGGREGATE_ROOT；描述: 源表 well_overhaul（R5·设定书附录 A.4），键=井号+起止，复合主键（wellId, overhaulStart, overhaulEnd）。疑点残留：跨月作业口径切割（D10，波及 RULE-BOHAI-016/019）；affectedOutput 估算口径不一；batchId 补录（D11，BH-BOHAI-RecordOverhaul 前置条件承载）。术语注记（R5·§6）：作业区口语「躺井」指停产待检泵——限作业区语境（Owner=采油工艺所）。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| wellRef | 所属井 | AggregateRootRef | 引用→AGG-BOHAI-001 |
| wellId | 井号 | String |  |
| overhaulStart | 检修开始日期 | Date |  |
| overhaulEnd | 检修结束日期 | Date |  |
| overhaulType | 检修类型 | String |  |
| affectedOutput | 影响产量（吨） | Decimal |  |
| batchId | 批次号 | String |  |

### AGG-BOHAI-005 井措施记录（WellMeasures）

- 注源: R5·A.5
- AGGREGATE_ROOT；描述: 源表 well_measures（R5·设定书附录 A.5），键=井号+措施次，复合主键（wellId, measureSeq）；measureSeq 为列名转写补记。疑点残留：有效期 30% 缺失（D12）；incrOilAnnual 两作业区算法不一致=事故 7（D13）。§7 剧本 2《注水井措施评估》的台账面。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| wellRef | 所属井 | AggregateRootRef | 引用→AGG-BOHAI-001 |
| wellId | 井号 | String |  |
| measureSeq | 措施次序 | Integer |  |
| measureType | 措施类型 | Enum | 字典值集: 压裂/酸化/补孔/调剖 |
| jobDate | 施工日期 | Date |  |
| effectiveFrom | 有效期起 | Date |  |
| effectiveTo | 有效期止 | Date |  |
| incrOilAnnual | 年增油量（吨） | Decimal |  |

### AGG-BOHAI-006 流体化验记录（FluidTest）

- 注源: R5·A.6
- AGGREGATE_ROOT；描述: 源表 fluid_test（R5·设定书附录 A.6），键=井号+取样日期，复合主键（wellId, sampleDate）；sampleDate 为列名转写补记。权威源裁决已落定（Owner 2026-09-21，PROP-BOHAI-008=C）：本表化验实测为月度/正式指标权威源，日度监控用计量折算，>5pp 以化验校正（容差检测 RULE-BOHAI-002）。取样频次与插补已由 RULE-BOHAI-029 承载（提取件二 R-16，2026-09-21）。§5 Join 白名单：oil_production_daily ⋈ 本对象直连禁止（须井号+取样日期双键+时间容差经中间视图）。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| wellRef | 所属井 | AggregateRootRef | 引用→AGG-BOHAI-001 |
| wellId | 井号 | String |  |
| sampleDate | 取样日期 | Date |  |
| waterCutLab | 化验含水率（%） | Decimal |  |
| density | 密度（t/m³） | Decimal |  |
| apiGravity | API 度 | Decimal |  |

### AGG-BOHAI-007 设备状态记录（EquipStatus）

- 注源: R5·A.7
- AGGREGATE_ROOT；描述: 源表 equip_status（R5·设定书附录 A.7），键=设备号+时间戳，复合主键（equipId, statusTime）；equipId/statusTime 为列名转写补记。疑点残留：stopReasonCode 新旧编码并存（D14，RULE-BOHAI-006 映射全集已到）。load/current 单位已声明（kN/A，Owner 素材 2026-09-21 §PROP-025）。§5 未声明设备—井关系，故不建 wellRef（零证据零引用，待 Owner）。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| equipId | 设备号 | String |  |
| statusTime | 状态时间戳 | DateTime |  |
| equipType | 设备类型 | Enum | 字典值集: 电泵/螺杆泵/加热炉 |
| load | 负载 | Decimal |  |
| current | 电流 | Decimal |  |
| stopReasonCode | 停机原因码 | String |  |

### AGG-BOHAI-008 区块月度结算（MonthlySettlement）

- 注源: R5·A.8
- AGGREGATE_ROOT；描述: 源表 monthly_settlement（R5·设定书附录 A.8），键=区块+结算月，复合主键（blockName, settleDate），settleDate 粒度为月（v2 兼容声明：规范名）。口径仲裁已落定（Owner 2026-09-21，PROP-BOHAI-020=①+②+③）：商品量（netWeight，扣自用油与输差）与井口口径（AGG-BOHAI-002.oilOutput 区块合计）**并存披露不互替**；使用边界：生产类指标用井口口径、经营/结算类指标用商品量；折算关系成文：商品量 = 井口合计 ×（1−自用率−输差率）——输差率口径框架本裁确立，具体阈值待 Owner 后续提案（事故 7/13 同源问题的标准答案：两口径之差=自用+输差）。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| blockName | 区块 | String |  |
| settleDate | 结算月 | Date |  |
| netWeight | 商品量净重（吨） | Decimal |  |

### AGG-BOHAI-009 受效关系（EffectuationRelation）

- 注源: R5·§5 业务实体，无源表
- AGGREGATE_ROOT；描述: R5·§5 Ontology 域草案实体：「受效关系（注水井→受效油井，多对多，属性=劈分系数 Σ=1、响应起始日——由王飞系数劈分强制要求，业务规则驱动建模的实证）」。8 表无源表。物理落表裁决（Owner 2026-09-21，PROP-BOHAI-021）：**维持无源虚拟实体**——语义层概念位（Join 白名单「oil ⋈ water_injection 直连 ✗ 须经本实体」与 §3 指标 10 劈分的承载），劈分系数暂由人工台账维护；新建源表属源系统工程决策（超语义平台裁决面，登记为源系统侧建议），由现有表推导缺推导规则素材（待定义）。不建它则 Join 白名单与递减增油劈分无承载——本体位不可删。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| injectorWellRef | 注水井 | AggregateRootRef | 引用→AGG-BOHAI-001 |
| producerWellRef | 受效油井 | AggregateRootRef | 引用→AGG-BOHAI-001 |
| splitCoefficient | 劈分系数 | Decimal | 值域[劈分系数值域]: value > 0 and value <= 1 |
| responseStartDate | 响应起始日 | Date |  |

- 不变量 同一注水井劈分系数合计为 1: 对同一 injectorWellRef 的全部受效关系，splitCoefficient 之和 = 1（enforcedAt=ALWAYS）

### AGG-BOHAI-010 区块（Block）

- 注源: R5·§5 业务实体，维形位
- AGGREGATE_ROOT；描述: R5·§5 实体草案「井—隶属→区块」。无源表（8 表之外）维形位（Owner 2026-09-21，PROP-BOHAI-013）：blockName 现值渤南/渤中/渤西（AGG-BOHAI-001.blockName 属性与 AGG-BOHAI-008 复合主键成分两处承载），区块密度基准 0.86/0.89/0.91（R5·§2.2）的自然归属。同族四实体裁不建：油田（D8 不提升——fieldName 保持行内冗余属性，无业务驱动拆对象）/平台（井的 String 属性已够用）/井筒/配注层——均无源表无属性素材，建即空壳，素材到时另立 add 提案。井/结算的 blockName 是否改引用 blockRef 暂不动（引用改造走影响分析另提案）。

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| blockName | 区块名 | String |  |
| densityBenchmark | 密度基准（t/m³） | Decimal |  |

聚合关联（aggregate_associations）:

| 关联 | 源 → 靶 | 类型 | 基数 | 引用字段 | 角色 |
|---|---|---|---|---|---|
| ASSOC-BOHAI-001 | AGG-BOHAI-001 → AGG-BOHAI-002 | REFERENCE | ONE_TO_MANY | wellRef | 井→日产计量 |
| ASSOC-BOHAI-002 | AGG-BOHAI-001 → AGG-BOHAI-003 | REFERENCE | ONE_TO_MANY | wellRef | 井→注水日计量 |
| ASSOC-BOHAI-003 | AGG-BOHAI-001 → AGG-BOHAI-004 | REFERENCE | ONE_TO_MANY | wellRef | 井→井检修记录 |
| ASSOC-BOHAI-004 | AGG-BOHAI-001 → AGG-BOHAI-005 | REFERENCE | ONE_TO_MANY | wellRef | 井→井措施记录 |
| ASSOC-BOHAI-005 | AGG-BOHAI-001 → AGG-BOHAI-006 | REFERENCE | ONE_TO_MANY | wellRef | 井→流体化验记录 |
| ASSOC-BOHAI-006 | AGG-BOHAI-001 → AGG-BOHAI-009 | DEPENDENCY | ONE_TO_MANY | injectorWellRef | 注水井→受效关系（注水方） |
| ASSOC-BOHAI-007 | AGG-BOHAI-001 → AGG-BOHAI-009 | DEPENDENCY | ONE_TO_MANY | producerWellRef | 受效油井→受效关系（受效方） |

## 二、口径四件套（M7 查询出口 × M2 行为 × M3 规则 × M1 承载）

### 口径 QR-BOHAI-001 · 单井日产量明细查询

- 注源: R5·§3 抽查面 + §5 Join 白名单 oil ⋈ well ✓
- 问题样例: 单井日产量明细查询
- 查询出口: QR-BOHAI-001（DETAIL_QUERY）
- 行为: BH-BOHAI-QueryWellDailyOutput 查询单井日产量（QUERY/USER_ACTION，ownerEntity=AGG-BOHAI-001）
- 承载对象: AGG-BOHAI-002 日产计量（主）、AGG-BOHAI-001 井
- 参数: wellId（井号，String，必填，运算符 EQ/LIKE）
- 结果列: wellId=井号（w.wellId）；prodDate=生产日期（d.prodDate）；oilOutput=日产油量（吨）（d.oilOutput）；liquidOutput=日产液量（方）（d.liquidOutput）；waterCut=含水率（%）（d.waterCut）；reportShift=报表班次（d.reportShift）
- 命中 ID 集: QR-BOHAI-001 BH-BOHAI-QueryWellDailyOutput AGG-BOHAI-002 AGG-BOHAI-001 RULE-BOHAI-027 RULE-BOHAI-030 RULE-BOHAI-005 RULE-BOHAI-002 RULE-BOHAI-003 RULE-BOHAI-004 RULE-BOHAI-008 RULE-BOHAI-009 RULE-BOHAI-019 RULE-BOHAI-010
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-BOHAI-027 日产油突变告警（VALIDATION；via=behavior.appliedRules(BH-BOHAI-QueryWellDailyOutput)）: not (日降幅 > 40% 且次日未恢复至降幅前 70%)
  - RULE-BOHAI-030 日产键完整性校验（VALIDATION；via=behavior.appliedRules(BH-BOHAI-QueryWellDailyOutput)）: count(rows by (wellId, prodDate, reportShift)) == 1 and reportShift in [A, B, C]
  - RULE-BOHAI-005 井号归一化（TRANSFORMATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: normalizeWellId(rawWellId)：trim→upper→全角连字符/下划线归一→去内部空格→匹配 ^([A-Z]+)\-?(\d{1,3})$ → 前缀+'-'+数字左补零至2位；匹配失败返回 not-ok 落问题单（不猜测归一）。示例：N2/N-2/N02/n-02/N 02 → N-02（Owner 素材 2026-09-21 §PROP-011）
  - RULE-BOHAI-002 计量化验含水偏差校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(waterCut - waterCutLab) <= 5
  - RULE-BOHAI-003 日产油非空率校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: (totalCount - nullCount) / totalCount >= 0.995
  - RULE-BOHAI-004 日产恒值检测（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: 同井生产日期连续 30 日内 oilOutput 全部相同时判为恒值异常，返回 false（告警）
  - RULE-BOHAI-008 区块物质平衡校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(blockInjVolume - blockLiquidVolume - retentionDelta) / blockLiquidVolume <= 0.03
  - RULE-BOHAI-009 产量完成率（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: actualOilSum / planOutputSum * 100
  - RULE-BOHAI-019 有效产量（剔检口径）（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: SUM(dailyProduction.oilOutput WHERE well.currentStatus <> '检修')
  - RULE-BOHAI-010 综合含水率（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: sum(case when waterCutLab is not null and abs(waterCutLab - waterCut) > 5 then liquidOutput * waterCutLab / 100 else liquidOutput - oilOutput end) / sum(liquidOutput) * 100  # B′ 化验校正（PROP-031，2026-09-21）：井·月粒度；化验配对经 RULE-BOHAI-002 中间视图（井号+取样日期双键+时间容差）

### 口径 QR-BOHAI-002 · 区块月度产量完成率统计

- 注源: R5·§3 指标 1 产量完成率 + 指标 2 有效产量（剔检支）
- 问题样例: 区块月度产量完成率统计
- 查询出口: QR-BOHAI-002（STATISTICAL_QUERY）
- 行为: BH-BOHAI-QueryBlockMonthlyCompletion 查询区块月度产量完成率（QUERY/USER_ACTION，ownerEntity=AGG-BOHAI-002）
- 承载对象: AGG-BOHAI-002 日产计量（主）、AGG-BOHAI-001 井
- 参数: blockName（区块，String，运算符 EQ）；statMonth（统计月，String，必填，运算符 EQ）
- 结果列: blockName=区块（w.blockName）；statMonth=统计月（MONTH(d.prodDate)）；planOutputSum=计划配产合计（吨）（d.planOutput，SUM）；actualOilSum=实际产油合计（吨）（d.oilOutput，SUM）；completionPct=产量完成率（%）（SUM(d.oilOutput) / SUM(d.planOutput) * 100）；effectiveOutputSum=有效产量·剔检（吨）（SUM(CASE WHEN w.currentStatus <> '检修' THEN d.oilOutput ELSE 0 END)）
- 命中 ID 集: QR-BOHAI-002 BH-BOHAI-QueryBlockMonthlyCompletion AGG-BOHAI-002 AGG-BOHAI-001 RULE-BOHAI-009 RULE-BOHAI-019 RULE-BOHAI-022 RULE-BOHAI-005 RULE-BOHAI-002 RULE-BOHAI-003 RULE-BOHAI-004 RULE-BOHAI-008 RULE-BOHAI-010 RULE-BOHAI-027 RULE-BOHAI-030
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-BOHAI-009 产量完成率（CALCULATION；via=behavior.appliedRules(BH-BOHAI-QueryBlockMonthlyCompletion)）: actualOilSum / planOutputSum * 100
  - RULE-BOHAI-019 有效产量（剔检口径）（CALCULATION；via=behavior.appliedRules(BH-BOHAI-QueryBlockMonthlyCompletion)）: SUM(dailyProduction.oilOutput WHERE well.currentStatus <> '检修')
  - RULE-BOHAI-022 配产单值校验（VALIDATION；via=reusedBy(BH-BOHAI-QueryBlockMonthlyCompletion)）: count(non-null planOutput rows by (wellId, prodDate)) <= 1
  - RULE-BOHAI-005 井号归一化（TRANSFORMATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: normalizeWellId(rawWellId)：trim→upper→全角连字符/下划线归一→去内部空格→匹配 ^([A-Z]+)\-?(\d{1,3})$ → 前缀+'-'+数字左补零至2位；匹配失败返回 not-ok 落问题单（不猜测归一）。示例：N2/N-2/N02/n-02/N 02 → N-02（Owner 素材 2026-09-21 §PROP-011）
  - RULE-BOHAI-002 计量化验含水偏差校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(waterCut - waterCutLab) <= 5
  - RULE-BOHAI-003 日产油非空率校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: (totalCount - nullCount) / totalCount >= 0.995
  - RULE-BOHAI-004 日产恒值检测（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: 同井生产日期连续 30 日内 oilOutput 全部相同时判为恒值异常，返回 false（告警）
  - RULE-BOHAI-008 区块物质平衡校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(blockInjVolume - blockLiquidVolume - retentionDelta) / blockLiquidVolume <= 0.03
  - RULE-BOHAI-010 综合含水率（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: sum(case when waterCutLab is not null and abs(waterCutLab - waterCut) > 5 then liquidOutput * waterCutLab / 100 else liquidOutput - oilOutput end) / sum(liquidOutput) * 100  # B′ 化验校正（PROP-031，2026-09-21）：井·月粒度；化验配对经 RULE-BOHAI-002 中间视图（井号+取样日期双键+时间容差）
  - RULE-BOHAI-027 日产油突变告警（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-001)）: not (日降幅 > 40% 且次日未恢复至降幅前 70%)
  - RULE-BOHAI-030 日产键完整性校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-001)）: count(rows by (wellId, prodDate, reportShift)) == 1 and reportShift in [A, B, C]

### 口径 QR-BOHAI-003 · 区块月度商品量结算查询

- 注源: R5·§3 指标 11 商品量
- 问题样例: 区块月度商品量结算查询
- 查询出口: QR-BOHAI-003（DETAIL_QUERY）
- 行为: BH-BOHAI-QueryMonthlySettlement 查询区块月度商品量结算（QUERY/USER_ACTION，ownerEntity=AGG-BOHAI-008）
- 承载对象: AGG-BOHAI-008 区块月度结算（主）
- 参数: blockName（区块，String，运算符 EQ）
- 结果列: blockName=区块（m.blockName）；settleDate=结算月（m.settleDate）；netWeight=商品量净重（吨）（m.netWeight）
- 命中 ID 集: QR-BOHAI-003 BH-BOHAI-QueryMonthlySettlement AGG-BOHAI-008
- 口径要点（关联规则 expression/narrative 摘录）:
  - （无关联 M3 规则）

### 口径 QR-BOHAI-004 · 区块综合含水率统计

- 注源: R5·§3 指标 5 综合含水率
- 问题样例: 区块综合含水率统计
- 查询出口: QR-BOHAI-004（STATISTICAL_QUERY）
- 行为: BH-BOHAI-QueryBlockWaterCut 查询区块综合含水率（QUERY/USER_ACTION，ownerEntity=AGG-BOHAI-002）
- 承载对象: AGG-BOHAI-002 日产计量（主）、AGG-BOHAI-001 井
- 参数: blockName（区块，String，运算符 EQ）；statMonth（统计月，String，必填，运算符 EQ）
- 结果列: blockName=区块（w.blockName）；statMonth=统计月（MONTH(d.prodDate)）；liquidSum=月产液合计（方）（d.liquidOutput，SUM）；oilSum=月产油合计（吨）（d.oilOutput，SUM）；waterCutPct=综合含水率（%）（(SUM(d.liquidOutput) - SUM(d.oilOutput)) / SUM(d.liquidOutput) * 100）
- 命中 ID 集: QR-BOHAI-004 BH-BOHAI-QueryBlockWaterCut AGG-BOHAI-002 AGG-BOHAI-001 RULE-BOHAI-010 RULE-BOHAI-005 RULE-BOHAI-002 RULE-BOHAI-003 RULE-BOHAI-004 RULE-BOHAI-008 RULE-BOHAI-009 RULE-BOHAI-019 RULE-BOHAI-027 RULE-BOHAI-030
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-BOHAI-010 综合含水率（CALCULATION；via=behavior.appliedRules(BH-BOHAI-QueryBlockWaterCut)）: sum(case when waterCutLab is not null and abs(waterCutLab - waterCut) > 5 then liquidOutput * waterCutLab / 100 else liquidOutput - oilOutput end) / sum(liquidOutput) * 100  # B′ 化验校正（PROP-031，2026-09-21）：井·月粒度；化验配对经 RULE-BOHAI-002 中间视图（井号+取样日期双键+时间容差）
  - RULE-BOHAI-005 井号归一化（TRANSFORMATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: normalizeWellId(rawWellId)：trim→upper→全角连字符/下划线归一→去内部空格→匹配 ^([A-Z]+)\-?(\d{1,3})$ → 前缀+'-'+数字左补零至2位；匹配失败返回 not-ok 落问题单（不猜测归一）。示例：N2/N-2/N02/n-02/N 02 → N-02（Owner 素材 2026-09-21 §PROP-011）
  - RULE-BOHAI-002 计量化验含水偏差校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(waterCut - waterCutLab) <= 5
  - RULE-BOHAI-003 日产油非空率校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: (totalCount - nullCount) / totalCount >= 0.995
  - RULE-BOHAI-004 日产恒值检测（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: 同井生产日期连续 30 日内 oilOutput 全部相同时判为恒值异常，返回 false（告警）
  - RULE-BOHAI-008 区块物质平衡校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: abs(blockInjVolume - blockLiquidVolume - retentionDelta) / blockLiquidVolume <= 0.03
  - RULE-BOHAI-009 产量完成率（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: actualOilSum / planOutputSum * 100
  - RULE-BOHAI-019 有效产量（剔检口径）（CALCULATION；via=ownerObjectBehaviors(AGG-BOHAI-002)）: SUM(dailyProduction.oilOutput WHERE well.currentStatus <> '检修')
  - RULE-BOHAI-027 日产油突变告警（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-001)）: not (日降幅 > 40% 且次日未恢复至降幅前 70%)
  - RULE-BOHAI-030 日产键完整性校验（VALIDATION；via=ownerObjectBehaviors(AGG-BOHAI-001)）: count(rows by (wellId, prodDate, reportShift)) == 1 and reportShift in [A, B, C]

## 三、行为与规则清单（M2/M3 全量，注源=模型文件 [R<n>·…] 注释标签）

### 行为（M2 · 8 条）

- BH-BOHAI-RecordDailyOutput 录入日产计量 [COMMAND/USER_ACTION] ownerEntity=AGG-BOHAI-002 appliedRules=RULE-BOHAI-005 — 注源: R5·§2.1 手工录入环节 + A.2 班次报表
- BH-BOHAI-RecordFluidTest 录入流体化验结果 [COMMAND/USER_ACTION] ownerEntity=AGG-BOHAI-006 appliedRules=RULE-BOHAI-001 — 注源: R5·A.6 化验台账 + §4 规则 3 折算密度域
- BH-BOHAI-RecordOverhaul 补录井检修台账 [COMMAND/USER_ACTION] ownerEntity=AGG-BOHAI-004 appliedRules=RULE-BOHAI-007 — 注源: R5·A.4 batch_id 补录标记（样本 20260911-T3，T-3 案例）+ §4 规则 9 状态迁移
- BH-BOHAI-RunDailyQualityCheck 执行日产质检 [COMMAND/SYSTEM] ownerEntity=AGG-BOHAI-002 appliedRules=RULE-BOHAI-002,RULE-BOHAI-003,RULE-BOHAI-004,RULE-BOHAI-008 — 注源: R5·§2.1「ETL 入数据仓库（15 分钟级闭环调度）」+ §4 质量闭环流程「规则命中→问题单生成」
- BH-BOHAI-QueryWellDailyOutput 查询单井日产量 [QUERY/USER_ACTION] ownerEntity=AGG-BOHAI-001 appliedRules=RULE-BOHAI-027,RULE-BOHAI-030 — 注源: R5·§3 指标抽查面 + §5 Join 白名单 oil ⋈ well ✓
- BH-BOHAI-QueryBlockMonthlyCompletion 查询区块月度产量完成率 [QUERY/USER_ACTION] ownerEntity=AGG-BOHAI-002 appliedRules=RULE-BOHAI-009,RULE-BOHAI-019 — 注源: R5·§3 指标 1 产量完成率 + 指标 2 有效产量（两支口径）
- BH-BOHAI-QueryBlockWaterCut 查询区块综合含水率 [QUERY/USER_ACTION] ownerEntity=AGG-BOHAI-002 appliedRules=RULE-BOHAI-010 — 注源: R5·§3 指标 5 综合含水率
- BH-BOHAI-QueryMonthlySettlement 查询区块月度商品量结算 [QUERY/USER_ACTION] ownerEntity=AGG-BOHAI-008 appliedRules=— — 注源: R5·§3 指标 11 商品量

### 规则（M3 · 35 条）

- RULE-BOHAI-001 化验折算密度值域校验 [VALIDATION] — 注源: R5·§4 规则 3 — density >= 0.82 and density <= 0.98
- RULE-BOHAI-002 计量化验含水偏差校验 [VALIDATION] — 注源: R5·§4 规则 4 — abs(waterCut - waterCutLab) <= 5
- RULE-BOHAI-003 日产油非空率校验 [VALIDATION] — 注源: R5·§4 规则 2 — (totalCount - nullCount) / totalCount >= 0.995
- RULE-BOHAI-004 日产恒值检测 [VALIDATION] — 注源: R5·§4 规则 10 — 同井生产日期连续 30 日内 oilOutput 全部相同时判为恒值异常，返回 false（告警）
- RULE-BOHAI-005 井号归一化 [TRANSFORMATION] — 注源: R5·§4 规则 7 — normalizeWellId(rawWellId)：trim→upper→全角连字符/下划线归一→去内部空格→匹配 ^([A-Z]+)\-?(\d{1,3})$ → 前缀+'-'+数字左补零至2位；匹配失败返回 not-ok 落问题单（不猜测归一）。示例：N2/N-2/N02/n-02/N 02 → N-02（Owner 素材 2026-09-21 §PROP-011）
- RULE-BOHAI-006 停机原因码归一化 [TRANSFORMATION] — 注源: R5·§4 规则 8 — 新旧映射全集（Owner 素材 2026-09-21）：R1↔PUMP_CHK 检泵作业 / R2↔CIRCUIT 电路故障 / R3↔BELT 皮带断 / R4↔PIPE_LEAK 管线刺漏 / R5↔MOTOR_BURN 电机烧毁 / R6↔SAND_CTRL 防砂失效 / R7↔OP_COORD 作业配合 / R8↔WELL_TEST 测井测试占用 / R9↔POWER_OUT 平台电力中断 / R10↔VALVE_JAM 阀门卡死 / R11↔INSTR_FAIL 计量仪表故障（不折减产量日历） / R12↔WEATHER 海况恶劣关井；映射表全命中为通过判据
- RULE-BOHAI-007 井状态迁移校验 [VALIDATION] — 注源: R5·§4 规则 9 — fromStatus→toStatus 落在合法迁移表内才返回 true；生产中→停产 必须存在检修/停产台账记录佐证（R5·§4 规则 9）
- RULE-BOHAI-008 区块物质平衡校验 [VALIDATION] — 注源: R5·§4 规则 12 — abs(blockInjVolume - blockLiquidVolume - retentionDelta) / blockLiquidVolume <= 0.03
- RULE-BOHAI-009 产量完成率 [CALCULATION] — 注源: R5·§3 指标 1 — actualOilSum / planOutputSum * 100
- RULE-BOHAI-022 配产单值校验 [VALIDATION]  — count(non-null planOutput rows by (wellId, prodDate)) <= 1
- RULE-BOHAI-010 综合含水率 [CALCULATION] — 注源: R5·§3 指标 5 — sum(case when waterCutLab is not null and abs(waterCutLab - waterCut) > 5 then liquidOutput * waterCutLab / 100 else liquidOutput - oilOutput end) / sum(liquidOutput) * 100  # B′ 化验校正（PROP-031，2026-09-21）：井·月粒度；化验配对经 RULE-BOHAI-002 中间视图（井号+取样日期双键+时间容差）
- RULE-BOHAI-011 注采比 [CALCULATION] — 注源: R5·§3 指标 6 — injVolumeSum / liquidVolumeSum
- RULE-BOHAI-012 累积亏空 [CALCULATION] — 注源: R5·§3 指标 7 — cumInjVolume - cumLiquidVolume
- RULE-BOHAI-013 自然递减率（月度） [CALCULATION] — 注源: R5·§3 指标 3 — (1 - qt / qtPrev) * 100
- RULE-BOHAI-014 综合递减率（月度） [CALCULATION] — 注源: R5·§3 指标 4 — (1 - qt / qtCompare) * 100
- RULE-BOHAI-015 措施有效期 [CALCULATION] — 注源: R5·§3 指标 9 — effectiveTo - effectiveFrom
- RULE-BOHAI-016 检泵周期 [CALCULATION] — 注源: R5·§3 指标 13 — currentOverhaulStart - previousOverhaulStart
- RULE-BOHAI-017 抽油机时率 [CALCULATION] — 注源: R5·§3 指标 14 — openDaysSum / calendarDaysSum * 100
- RULE-BOHAI-018 递减增油 [CALCULATION] — 注源: R5·§3 指标 10 — (actualOil - baselineOil) * splitCoefficient
- RULE-BOHAI-019 有效产量（剔检口径） [CALCULATION] — 注源: R5·§3 指标 2 — SUM(dailyProduction.oilOutput WHERE well.currentStatus <> '检修')
- RULE-BOHAI-023 停井日 openDays 联动校验 [VALIDATION]  — openDays > 0 implies well.currentStatus in [生产中]
- RULE-BOHAI-024 跨月检修归属期切割 [CALCULATION]  — overlapDays(overhaulStart, overhaulEnd, 当自然月)
- RULE-BOHAI-025 补录窗口阈值校验 [VALIDATION]  — (today - businessDate) <= 5
- RULE-BOHAI-038 设备电流零值告警 [VALIDATION]  — not (当日批内全部记录 current == 0)
- RULE-BOHAI-026 注水恒值滑窗预警 [VALIDATION]  — not (injVolume 连续 7 日逐字节相同)
- RULE-BOHAI-027 日产油突变告警 [VALIDATION]  — not (日降幅 > 40% 且次日未恢复至降幅前 70%)
- RULE-BOHAI-028 配注量量纲核验 [VALIDATION]  — injVolume >= 0 and injVolume <= 500
- RULE-BOHAI-029 化验取样频次与插补 [VALIDATION]  — 取样间隔 <= (高产 7 日 / 低产 15 日)
- RULE-BOHAI-030 日产键完整性校验 [VALIDATION]  — count(rows by (wellId, prodDate, reportShift)) == 1 and reportShift in [A, B, C]
- RULE-BOHAI-031 结算对账容差校验 [VALIDATION]  — abs(netWeight - 当月井口合计) / 当月井口合计 <= 0.015
- RULE-BOHAI-032 停机码非空与映射命中校验 [VALIDATION]  — stopReasonCode 非空且命中 RULE-BOHAI-006 新码表
- RULE-BOHAI-033 检修补录批次号格式校验 [VALIDATION]  — match(batchId, '^\\d{8}-T\\d+$')
- RULE-BOHAI-020 吨方混写存量行检出 [VALIDATION]  — oilOutput <= liquidOutput
- RULE-BOHAI-034 措施有效率 [CALCULATION]  — 100 * count(有效措施) / count(判据齐备措施)
- RULE-BOHAI-035 机采系统能效 [CALCULATION]  — effectivePower / inputPower * 100

## 四、开放疑点（docs/proposals 扫描）

指向本域的 open 提案 3 条（裁决与详情看提案原文）:

- PROP-BOHAI-014 为注水日计量 layerSplit 补格式规范与配注目标承载裁决（AGG-BOHAI-003）［modify → M1/AGG-BOHAI-003］（docs/proposals/PROP-BOHAI-014.md）
- PROP-BOHAI-026 新增桶油增产成本指标位待投入字段（RULE-BOHAI-036）［add → M3/RULE-BOHAI-036］（docs/proposals/PROP-BOHAI-026.md）
- PROP-BOHAI-029 补全有效产量开井日历折算支公式（RULE-BOHAI-019）［modify → M3/RULE-BOHAI-019］（docs/proposals/PROP-BOHAI-029.md）
