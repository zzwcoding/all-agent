# 逆向草案 · M1 对象模型全文（票 09 端到端走查 · 工序①，MR 前形态）

> **证据非权威，待 Owner 确认。** 本文件是 db-reverse 工序步骤 4 产出的草案全文（嵌入形态）。按票 09 步骤②「模拟 MR 流程」，本草案经 Owner 裁决（裁决记录 `../step2-mr-adjudication.md`）后落 `ontology/bohai/`；**语义闸（schema_check）跑在进仓位 `ontology/bohai/`**——`docs/walkthrough/` 下无 `schema/` 上文，闸不在草案位运行（工具约定：schema 解析只看本目录与上一级）。
> 与出厂集参照产物 `fixtures/db-reverse/expected-output/bohai/m1-object-model.yaml` 逐元素核对一致（同一工序、同一输入）。

```yaml
# =====================================================================
# 渤海域 8 表逆向草案 · M1 对象模型（票 09 端到端走查 · 工序①草案）
# 输入: fixtures/db-reverse/input/bohai-8tables.sql（R5·设定书附录 A 忠实转写）
# ────────────────────────────────────────────────────────────────
# 证据非权威，待 Owner 确认。
# 证据等级: 全部元素=DDL 字段/键/注释直译（D/C 级），关系与聚合划分零推断
#   ——DDL 无外键声明，故无 AggregateRootRef/ASSOC/DICT；同名键列的关联
#   推断只进 dirty-signs.md 疑点清单。对象中文名与属性中文名为直译
#   （字典只给英文列名），逐条待 Owner 确认。
# =====================================================================
model_type: OBJECT
version: "1.0.0"
domain: bohai
aggregates:
  # [R5·A.1] well_info → 井档案（一井一行；单列主键 well_id → wellId 标 unique）
  - id: AGG-BOHAI-001
    name: 井档案
    alias: WellInfo
    description: "源表 well_info（R5·设定书附录 A.1），一井一行。疑点：井号旧写法 N2/N-2 并存（D6）；wellType 个别改型未留版本；fieldName 行内冗余（反规范化样例，D8）；currentStatus 状态滞后（N-11 已停仍记「生产中」，D7）；remarks 曾被塞入注入指令——均待 Owner 确认。"
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: wellId, label: 井号, type: String, unique: true }
      - { name: wellName, label: 井名, type: String }
      - { name: wellType, label: 井别, type: Enum, enumValues: [EW, IW] }
      - { name: firstProdDate, label: 首次投产日期, type: Date }
      - { name: platform, label: 平台, type: String }
      - { name: blockName, label: 区块, type: String }
      - { name: fieldName, label: 油田, type: String }
      - { name: currentStatus, label: 当前状态, type: Enum, enumValues: [生产中, 停产, 检修, 待弃置] }
      - { name: remarks, label: 备注, type: String }
  # [R5·A.2] oil_production_daily → 日产计量（★核心事实源；复合主键不设属性级 unique，键构成记于此）
  - id: AGG-BOHAI-002
    name: 日产计量
    alias: OilProductionDaily
    description: "源表 oil_production_daily（R5·设定书附录 A.2，字典标注核心事实源），一井一日，复合主键（wellId, prodDate）。疑点：oilOutput 单位吨但个别行误录为方（吨方混写，D1）；同井同日存在 A/B 两行（班次手抄汇总，D2）与主键声明冲突；waterCut 化验折算与 fluid_test 化验值打架（D3）；planOutput 配产版本切换日双值行（D4）；openDays 停井日仍>0 矛盾行（D5）——均待 Owner 确认。"
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: wellId, label: 井号, type: String }
      - { name: prodDate, label: 生产日期, type: Date }
      - { name: oilOutput, label: 日产油量, type: Decimal }
      - { name: liquidOutput, label: 日产液量, type: Decimal }
      - { name: waterCut, label: 含水率, type: Decimal }
      - { name: planOutput, label: 配产量, type: Decimal }
      - { name: openDays, label: 开井时长, type: Decimal }
      - { name: oilPressure, label: 油压, type: Decimal }
      - { name: reportShift, label: 报表班次, type: Enum, enumValues: [A, B, C] }
  # [R5·A.3] water_injection_daily → 注水日计量（字典未给中文标题，对象名为直译）
  - id: AGG-BOHAI-003
    name: 注水日计量
    alias: WaterInjectionDaily
    description: "源表 water_injection_daily（R5·设定书附录 A.3），键=井号+日期，复合主键（wellId, injDate）；injDate 为列名转写补记；对象中文名直译（字典未给标题）。疑点：layerSplit 两层/三层口径不一、偶为累计值（D9）——待 Owner 确认。"
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: wellId, label: 井号, type: String }
      - { name: injDate, label: 注水日期, type: Date }
      - { name: injVolume, label: 注水量, type: Decimal }
      - { name: pumpPressure, label: 泵压, type: Decimal }
      - { name: layerSplit, label: 分层配注, type: String }
  # [R5·A.4] well_overhaul → 井检修记录（键=井号+起止）
  - id: AGG-BOHAI-004
    name: 井检修记录
    alias: WellOverhaul
    description: "源表 well_overhaul（R5·设定书附录 A.4），键=井号+起止，复合主键（wellId, overhaulStart, overhaulEnd）。疑点：跨月作业（样本 2026-08-28→2026-09-06，当月口径切割争议源，D10）；affectedOutput 各作业区估算口径不一；batchId 存在补录（样本 20260911-T3，T-3 案例，D11）——均待 Owner 确认。"
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: wellId, label: 井号, type: String }
      - { name: overhaulStart, label: 检修开始日期, type: Date }
      - { name: overhaulEnd, label: 检修结束日期, type: Date }
      - { name: overhaulType, label: 检修类型, type: String }
      - { name: affectedOutput, label: 影响产量, type: Decimal }
      - { name: batchId, label: 批次号, type: String }
  # [R5·A.5] well_measures → 井措施记录（键=井号+措施次）
  - id: AGG-BOHAI-005
    name: 井措施记录
    alias: WellMeasures
    description: "源表 well_measures（R5·设定书附录 A.5），键=井号+措施次，复合主键（wellId, measureSeq）；measureSeq 为列名转写补记；对象中文名直译。疑点：effectiveFrom/effectiveTo 约 30% 缺失（D12）；incrOilAnnual 两作业区算法不一致=事故 7（D13）——均待 Owner 确认。"
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: wellId, label: 井号, type: String }
      - { name: measureSeq, label: 措施次序, type: Integer }
      - { name: measureType, label: 措施类型, type: Enum, enumValues: [压裂, 酸化, 补孔, 调剖] }
      - { name: jobDate, label: 施工日期, type: Date }
      - { name: effectiveFrom, label: 有效期起, type: Date }
      - { name: effectiveTo, label: 有效期止, type: Date }
      - { name: incrOilAnnual, label: 年增油量, type: Decimal }
  # [R5·A.6] fluid_test → 流体化验记录（键=井号+取样日期）
  - id: AGG-BOHAI-006
    name: 流体化验记录
    alias: FluidTest
    description: "源表 fluid_test（R5·设定书附录 A.6），键=井号+取样日期，复合主键（wellId, sampleDate）；sampleDate 为列名转写补记；对象中文名直译。疑点：取样频次不齐（高产周报/低产半月报）、缺失插补规则有争议；waterCutLab 与 AGG-BOHAI-002.waterCut 化验折算口径打架（D3）——均待 Owner 确认。"
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: wellId, label: 井号, type: String }
      - { name: sampleDate, label: 取样日期, type: Date }
      - { name: waterCutLab, label: 化验含水率, type: Decimal }
      - { name: density, label: 密度, type: Decimal }
      - { name: apiGravity, label: API 度, type: Decimal }
  # [R5·A.7] equip_status → 设备状态记录（键=设备号+时间戳）
  - id: AGG-BOHAI-007
    name: 设备状态记录
    alias: EquipStatus
    description: "源表 equip_status（R5·设定书附录 A.7），键=设备号+时间戳，复合主键（equipId, statusTime）；equipId/statusTime 为列名转写补记；对象中文名直译。疑点：stopReasonCode 新旧编码并存（旧 R3=皮带断，新 BELT，D14），值集不全故不建枚举；load/current 单位字典未声明——均待 Owner 确认。"
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: equipId, label: 设备号, type: String }
      - { name: statusTime, label: 状态时间戳, type: DateTime }
      - { name: equipType, label: 设备类型, type: Enum, enumValues: [电泵, 螺杆泵, 加热炉] }
      - { name: load, label: 负载, type: Decimal }
      - { name: current, label: 电流, type: Decimal }
      - { name: stopReasonCode, label: 停机原因码, type: String }
  # [R5·A.8] monthly_settlement → 区块月度结算（键=区块+结算月）
  - id: AGG-BOHAI-008
    name: 区块月度结算
    alias: MonthlySettlement
    description: "源表 monthly_settlement（R5·设定书附录 A.8），键=区块+结算月，复合主键（blockName, settleDate），settleDate 粒度为月。疑点：netWeight 为扣自用油与输差的净重，与日产计量（井口）口径天然不等=事故 7 另一面（D15）——待 Owner 确认。"
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: blockName, label: 区块, type: String }
      - { name: settleDate, label: 结算月, type: Date }
      - { name: netWeight, label: 净重, type: Decimal }
# 无 data_dictionaries：DDL/字典未声明任何字典表，枚举值集直接落在 enumValues
#   （stop_reason_code / overhaul_type 值集不全，保持 String 不建枚举）。
# 无 aggregate_associations：DDL 无外键声明，零关系证据——关系推断见
#   dirty-signs.md（D6 等），待 Owner 裁决。
```

## 草案 manifest（MR 前形态）

```json
{
  "domain": "bohai",
  "label": "渤海油田产量域（db-reverse 逆向草案）",
  "profile": "v9-core",
  "schemaVersion": "1.0.0",
  "description": "票 09 工序①草案：从 8 表 DDL 逆向。证据非权威，待 Owner 确认。DDL 证据仅支撑 M1 对象层（8 聚合根），故 profile 取注册表最小核心组合 v9-core；工序② Owner 裁决引入业务素材（R5·§1/§3/§4/§5/§7）后进仓位 manifest 另行声明（见 ontology/bohai/manifest.json）。"
}
```
