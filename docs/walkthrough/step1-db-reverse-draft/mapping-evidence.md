# 映射证据 · 表字段 → 对象属性（票 09 端到端走查 · 工序①）

> **证据非权威，待 Owner 确认。** 输入：`fixtures/db-reverse/input/bohai-8tables.sql`（R5·设定书附录 A 忠实转写，逐字段注源见 `fixtures/db-reverse/input/source-map.md`）。本文件按 db-reverse 工序步骤 4 产出：每条属性映射可回溯到 DDL 列 + R5·A.x 出处，证据等级 D（DDL 结构直证）/ C（注释文字）/ I（推断）随行标注。
> 与出厂集参照产物 `fixtures/db-reverse/expected-output/mapping-evidence.md` 逐列核对一致（50 列全覆盖、补记处数一致：类型补记 33 处、列名补记 5 处）。

## 映射约定（细则见 skills/db-reverse/references/reverse-guide.md §3–§5）

- **类型映射**：VARCHAR/CHAR→String；DECIMAL→Decimal；INT→Integer；DATE→Date；TIMESTAMP→DateTime；DDL 注释给出完整值集→Enum（enumValues 逐字取注释），值集不全→String 保留待确认。
- **PK→标识映射**：单列主键→属性保留列名 camelCase + `unique: true`；复合主键→成分列照常映射、不设属性级 unique，键构成记入聚合根描述。
- **命名规范化**：列名 snake_case → lowerCamelCase；表名 → alias 大驼峰；中文 label 为语义直译（字典只给英文列名），逐条待 Owner 确认（证据等级 I）。
- **零推断边界**：DDL 无外键 → 不建引用/关联；无字典表声明 → 不建数据字典，完整值集直接用 enumValues。

## 逐表逐字段映射（50 列 → 50 属性，全覆盖）

### well_info → AGG-BOHAI-001 井档案（9 列）

| DDL 列 | 类型（来源/等级） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| well_info.well_id | VARCHAR(8)（字典原文·D） | wellId | String | PK，单列主键 → unique: true；疑点：旧写法 N2/N-2 并存（C·D6） |
| well_info.well_name | VARCHAR(64)（类型补记·I） | wellName | String | 样本直译（C） |
| well_info.well_type | CHAR(2)（字典原文·D） | wellType | Enum [EW, IW] | 值集来自字典注释（C）；疑点：个别改型未留版本 |
| well_info.first_prod_date | DATE（字典原文·D） | firstProdDate | Date | — |
| well_info.platform | VARCHAR(16)（类型补记·I） | platform | String | 样本 CEP-A/CEP-B（C） |
| well_info.block_name | VARCHAR(16)（类型补记·I） | blockName | String | 取值渤南/渤中/渤西（C） |
| well_info.field_name | VARCHAR(32)（类型补记·I） | fieldName | String | 疑点：行内冗余=反规范化样例（C·D8） |
| well_info.current_status | VARCHAR(16)（类型补记·I） | currentStatus | Enum [生产中, 停产, 检修, 待弃置] | 值集来自字典（C）；疑点：状态滞后 N-11（C·D7） |
| well_info.remarks | VARCHAR(255)（类型补记·I） | remarks | String | 疑点：曾塞入注入指令（C） |

### oil_production_daily → AGG-BOHAI-002 日产计量（9 列）

| DDL 列 | 类型（来源/等级） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| oil_production_daily.well_id | VARCHAR(8)（字典原文·D） | wellId | String | 复合主键成分（不设属性级 unique） |
| oil_production_daily.prod_date | DATE（类型补记·I） | prodDate | Date | 复合主键成分 |
| oil_production_daily.oil_output | DECIMAL(10,2)（字典原文·D） | oilOutput | Decimal | 单位吨（C）；**疑点：吨方混写（D1）** |
| oil_production_daily.liquid_output | DECIMAL(10,2)（类型补记·I） | liquidOutput | Decimal | 单位方（C） |
| oil_production_daily.water_cut | DECIMAL(5,2)（类型补记·I） | waterCut | Decimal | 单位%；疑点：化验折算与 fluid_test 打架（C·D3） |
| oil_production_daily.plan_output | DECIMAL(10,2)（类型补记·I） | planOutput | Decimal | 疑点：配产版本切换日双值行（C·D4） |
| oil_production_daily.open_days | DECIMAL(4,1)（类型补记·I） | openDays | Decimal | 单位天；疑点：停井日仍>0 矛盾行（C·D5） |
| oil_production_daily.oil_pressure | DECIMAL(6,2)（类型补记·I） | oilPressure | Decimal | 单位 MPa（C） |
| oil_production_daily.report_shift | CHAR(1)（字典原文·D） | reportShift | Enum [A, B, C] | 疑点：同井同日 A/B 两行，与主键声明冲突（C·D2） |

### water_injection_daily → AGG-BOHAI-003 注水日计量（5 列）

| DDL 列 | 类型（来源/等级） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| water_injection_daily.well_id | VARCHAR(8)（字典原文·D） | wellId | String | 复合主键成分 |
| water_injection_daily.inj_date | DATE（列名+类型补记·I） | injDate | Date | 列名补记：字典仅给键「井号+日期」 |
| water_injection_daily.inj_volume | DECIMAL(10,2)（类型补记·I） | injVolume | Decimal | 单位方（C） |
| water_injection_daily.pump_pressure | DECIMAL(6,2)（类型补记·I） | pumpPressure | Decimal | 单位 MPa（C） |
| water_injection_daily.layer_split | VARCHAR(64)（类型补记·I） | layerSplit | String | 疑点：两层/三层口径不一、偶为累计值 → 不结构化（C·D9） |

### well_overhaul → AGG-BOHAI-004 井检修记录（6 列）

| DDL 列 | 类型（来源/等级） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| well_overhaul.well_id | VARCHAR(8)（字典原文·D） | wellId | String | 复合主键成分 |
| well_overhaul.overhaul_start | DATE（字典原文·D） | overhaulStart | Date | 复合主键成分；样本 2026-08-28（C） |
| well_overhaul.overhaul_end | DATE（字典原文·D） | overhaulEnd | Date | 疑点：跨月作业口径切割（C·D10） |
| well_overhaul.overhaul_type | VARCHAR(32)（类型补记·I） | overhaulType | String | 样本仅「检泵」，值集不全 → 不建枚举（C） |
| well_overhaul.affected_output | DECIMAL(10,2)（类型补记·I） | affectedOutput | Decimal | 疑点：各作业区估算口径不一（C） |
| well_overhaul.batch_id | VARCHAR(32)（类型补记·I） | batchId | String | 疑点：补录样本 20260911-T3（C·D11） |

### well_measures → AGG-BOHAI-005 井措施记录（7 列）

| DDL 列 | 类型（来源/等级） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| well_measures.well_id | VARCHAR(8)（字典原文·D） | wellId | String | 复合主键成分 |
| well_measures.measure_seq | INT（列名+类型补记·I） | measureSeq | Integer | 复合主键成分；列名补记：字典仅给键「井号+措施次」 |
| well_measures.measure_type | VARCHAR(16)（类型补记·I） | measureType | Enum [压裂, 酸化, 补孔, 调剖] | 值集来自字典（C） |
| well_measures.job_date | DATE（类型补记·I） | jobDate | Date | — |
| well_measures.effective_from | DATE（类型补记·I） | effectiveFrom | Date | 疑点：约 30% 缺失（C·D12） |
| well_measures.effective_to | DATE（类型补记·I） | effectiveTo | Date | 疑点：约 30% 缺失（C·D12） |
| well_measures.incr_oil_annual | DECIMAL(10,2)（类型补记·I） | incrOilAnnual | Decimal | 疑点：两作业区算法不一致=事故 7（C·D13） |

### fluid_test → AGG-BOHAI-006 流体化验记录（5 列）

| DDL 列 | 类型（来源/等级） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| fluid_test.well_id | VARCHAR(8)（字典原文·D） | wellId | String | 复合主键成分 |
| fluid_test.sample_date | DATE（列名+类型补记·I） | sampleDate | Date | 列名补记：字典仅给键「井号+取样日期」 |
| fluid_test.water_cut_lab | DECIMAL(5,2)（类型补记·I） | waterCutLab | Decimal | 疑点：与 waterCut 折算口径打架（C·D3） |
| fluid_test.density | DECIMAL(5,3)（类型补记·I） | density | Decimal | 单位 t/m³（C） |
| fluid_test.api_gravity | DECIMAL(5,2)（类型补记·I） | apiGravity | Decimal | 单位 °API（C） |

### equip_status → AGG-BOHAI-007 设备状态记录（6 列）

| DDL 列 | 类型（来源/等级） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| equip_status.equip_id | VARCHAR(16)（列名+类型补记·I） | equipId | String | 复合主键成分；列名补记：字典仅给键「设备号」 |
| equip_status.status_time | TIMESTAMP（列名+类型补记·I） | statusTime | DateTime | 复合主键成分 |
| equip_status.equip_type | VARCHAR(16)（类型补记·I） | equipType | Enum [电泵, 螺杆泵, 加热炉] | 值集来自字典（C） |
| equip_status.load | DECIMAL(8,2)（类型补记·I） | load | Decimal | 单位字典未声明（照实标注） |
| equip_status.current | DECIMAL(8,2)（类型补记·I） | current | Decimal | 单位字典未声明（照实标注） |
| equip_status.stop_reason_code | VARCHAR(16)（类型补记·I） | stopReasonCode | String | **疑点：新旧编码并存（旧 R3=皮带断，新 BELT）**；值集不全 → 不建枚举（C·D14） |

### monthly_settlement → AGG-BOHAI-008 区块月度结算（3 列）

| DDL 列 | 类型（来源/等级） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| monthly_settlement.block_name | VARCHAR(16)（类型补记·I） | blockName | String | 复合主键成分；渤南/渤中/渤西（C） |
| monthly_settlement.settle_date | DATE（类型补记·I） | settleDate | Date | 复合主键成分；粒度=结算月；v2 兼容声明：settle_date 为规范名（C） |
| monthly_settlement.net_weight | DECIMAL(12,2)（类型补记·I） | netWeight | Decimal | 单位吨；疑点：扣自用油与输差，与井口口径天然不等（C·D15） |

## 映射统计

- 输入：8 表 50 列 → 输出：8 聚合根 50 属性，**零列丢失、零列新增**。
- 类型补记 33 处、列名补记 5 处（全部在 `fixtures/db-reverse/input/source-map.md` 逐条留痕，证据等级 I）。
- 未建：数据字典（无字典表证据）、聚合关联/引用（无外键证据）、M2–M7/MU 文件（无业务过程证据）——「不发明 DDL 里不存在的业务语义」的落实；业务面素材（R5·§1/§3/§4/§5/§7）的建模在工序② Owner 裁决后进仓。
