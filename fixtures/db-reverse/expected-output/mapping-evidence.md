# 映射证据 · 表字段 → 对象属性（db-reverse 参照产物 AC2，票 06）

> **证据非权威，待 Owner 确认。** 输入：`input/bohai-8tables.sql`（R5·设定书附录 A 忠实转写，逐字段注源见 input/source-map.md）。本文件是 AC2 要求的映射证据文件：每条属性映射都可回溯到 DDL 列 + R5·A.x 出处。

## 映射约定（细则见 db-reverse 逆向指导书）

- **类型映射**：VARCHAR/CHAR→String；DECIMAL/NUMERIC→Decimal；INT→Integer；DATE→Date；TIMESTAMP/DATETIME→DateTime；布尔→Boolean；DDL 注释给出完整值集→Enum（enumValues），值集不全→String 保留待确认。
- **主键（PK）→ 标识映射**：单列主键 → 属性保留列名 camelCase 并标 unique；复合主键 → 全部成分列照常映射，不设属性级 unique，键构成记入聚合根描述。
- **命名规范化**：列名 snake_case → 属性名 lowerCamelCase；表名 → alias 大驼峰；属性中文 label 为语义直译（字典只给英文列名），逐条待 Owner 确认。
- **零推断边界**：DDL 无外键 → 不建引用/关联；字典未声明字典表 → 不建数据字典，完整值集直接用 enumValues。

## 逐表逐字段映射（50 列 → 50 属性，全覆盖）

### well_info → AGG-BOHAI-001 井档案（9 列）

| DDL 列 | 类型（来源） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| well_info.well_id | VARCHAR(8)（字典原文） | wellId | String | PK，单列主键 → unique: true；疑点：旧写法 N2/N-2 并存 |
| well_info.well_name | VARCHAR(64)（类型补记） | wellName | String | 样本直译 |
| well_info.well_type | CHAR(2)（字典原文） | wellType | Enum [EW, IW] | 值集来自字典注释；疑点：个别改型未留版本 |
| well_info.first_prod_date | DATE（字典原文） | firstProdDate | Date | — |
| well_info.platform | VARCHAR(16)（类型补记） | platform | String | — |
| well_info.block_name | VARCHAR(16)（类型补记） | blockName | String | — |
| well_info.field_name | VARCHAR(32)（类型补记） | fieldName | String | 疑点：行内冗余（反规范化样例） |
| well_info.current_status | VARCHAR(16)（类型补记） | currentStatus | Enum [生产中, 停产, 检修, 待弃置] | 值集来自字典；疑点：状态滞后 |
| well_info.remarks | VARCHAR(255)（类型补记） | remarks | String | 疑点：曾被塞入注入指令 |

### oil_production_daily → AGG-BOHAI-002 日产计量（9 列）

| DDL 列 | 类型（来源） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| oil_production_daily.well_id | VARCHAR(8)（字典原文） | wellId | String | 复合主键成分（不设属性级 unique） |
| oil_production_daily.prod_date | DATE（类型补记） | prodDate | Date | 复合主键成分 |
| oil_production_daily.oil_output | DECIMAL(10,2)（字典原文） | oilOutput | Decimal | 单位吨；**疑点：吨方混写（个别行误录为方）** |
| oil_production_daily.liquid_output | DECIMAL(10,2)（类型补记） | liquidOutput | Decimal | 单位方 |
| oil_production_daily.water_cut | DECIMAL(5,2)（类型补记） | waterCut | Decimal | 单位%；疑点：化验折算与 fluid_test 打架 |
| oil_production_daily.plan_output | DECIMAL(10,2)（类型补记） | planOutput | Decimal | 疑点：配产版本切换日双值行 |
| oil_production_daily.open_days | DECIMAL(4,1)（类型补记） | openDays | Decimal | 疑点：停井日仍>0 矛盾行 |
| oil_production_daily.oil_pressure | DECIMAL(6,2)（类型补记） | oilPressure | Decimal | 单位 MPa |
| oil_production_daily.report_shift | CHAR(1)（字典原文） | reportShift | Enum [A, B, C] | 疑点：同井同日 A/B 两行（重复行），与主键声明冲突 |

### water_injection_daily → AGG-BOHAI-003 注水日计量（5 列）

| DDL 列 | 类型（来源） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| water_injection_daily.well_id | VARCHAR(8)（字典原文） | wellId | String | 复合主键成分 |
| water_injection_daily.inj_date | DATE（列名+类型补记） | injDate | Date | 列名补记：字典仅给键「井号+日期」 |
| water_injection_daily.inj_volume | DECIMAL(10,2)（类型补记） | injVolume | Decimal | 单位方 |
| water_injection_daily.pump_pressure | DECIMAL(6,2)（类型补记） | pumpPressure | Decimal | 单位 MPa |
| water_injection_daily.layer_split | VARCHAR(64)（类型补记） | layerSplit | String | 疑点：两层/三层口径不一、偶为累计值（故不结构化） |

### well_overhaul → AGG-BOHAI-004 井检修记录（6 列）

| DDL 列 | 类型（来源） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| well_overhaul.well_id | VARCHAR(8)（字典原文） | wellId | String | 复合主键成分 |
| well_overhaul.overhaul_start | DATE（字典原文） | overhaulStart | Date | 复合主键成分 |
| well_overhaul.overhaul_end | DATE（字典原文） | overhaulEnd | Date | 疑点：跨月作业（口径切割争议源） |
| well_overhaul.overhaul_type | VARCHAR(32)（类型补记） | overhaulType | String | 样本仅「检泵」，值集不全 → 不建枚举 |
| well_overhaul.affected_output | DECIMAL(10,2)（类型补记） | affectedOutput | Decimal | 疑点：各作业区估算口径不一 |
| well_overhaul.batch_id | VARCHAR(32)（类型补记） | batchId | String | 疑点：补录（样本 20260911-T3，T-3 案例） |

### well_measures → AGG-BOHAI-005 井措施记录（7 列）

| DDL 列 | 类型（来源） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| well_measures.well_id | VARCHAR(8)（字典原文） | wellId | String | 复合主键成分 |
| well_measures.measure_seq | INT（列名+类型补记） | measureSeq | Integer | 复合主键成分 |
| well_measures.measure_type | VARCHAR(16)（类型补记） | measureType | Enum [压裂, 酸化, 补孔, 调剖] | 值集来自字典 |
| well_measures.job_date | DATE（类型补记） | jobDate | Date | — |
| well_measures.effective_from | DATE（类型补记） | effectiveFrom | Date | 疑点：约 30% 缺失 |
| well_measures.effective_to | DATE（类型补记） | effectiveTo | Date | 疑点：约 30% 缺失 |
| well_measures.incr_oil_annual | DECIMAL(10,2)（类型补记） | incrOilAnnual | Decimal | 疑点：两作业区算法不一致（口径争议） |

### fluid_test → AGG-BOHAI-006 流体化验记录（5 列）

| DDL 列 | 类型（来源） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| fluid_test.well_id | VARCHAR(8)（字典原文） | wellId | String | 复合主键成分 |
| fluid_test.sample_date | DATE（列名+类型补记） | sampleDate | Date | 列名补记：字典仅给键「井号+取样日期」 |
| fluid_test.water_cut_lab | DECIMAL(5,2)（类型补记） | waterCutLab | Decimal | 疑点：与 waterCut 折算口径打架 |
| fluid_test.density | DECIMAL(5,3)（类型补记） | density | Decimal | 单位 t/m³ |
| fluid_test.api_gravity | DECIMAL(5,2)（类型补记） | apiGravity | Decimal | 单位 °API |

### equip_status → AGG-BOHAI-007 设备状态记录（6 列）

| DDL 列 | 类型（来源） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| equip_status.equip_id | VARCHAR(16)（列名+类型补记） | equipId | String | 复合主键成分；列名补记：字典仅给键「设备号」 |
| equip_status.status_time | TIMESTAMP（列名+类型补记） | statusTime | DateTime | 复合主键成分 |
| equip_status.equip_type | VARCHAR(16)（类型补记） | equipType | Enum [电泵, 螺杆泵, 加热炉] | 值集来自字典 |
| equip_status.load | DECIMAL(8,2)（类型补记） | load | Decimal | 疑点：单位字典未声明 |
| equip_status.current | DECIMAL(8,2)（类型补记） | current | Decimal | 疑点：单位字典未声明 |
| equip_status.stop_reason_code | VARCHAR(16)（类型补记） | stopReasonCode | String | **疑点：新旧编码并存（旧 R3=皮带断，新 BELT）**；值集不全 → 不建枚举 |

### monthly_settlement → AGG-BOHAI-008 区块月度结算（3 列）

| DDL 列 | 类型（来源） | → 属性 | 属性类型 | 证据/疑点 |
|---|---|---|---|---|
| monthly_settlement.block_name | VARCHAR(16)（类型补记） | blockName | String | 复合主键成分 |
| monthly_settlement.settle_date | DATE（类型补记） | settleDate | Date | 复合主键成分；粒度=结算月（v2 兼容声明：规范名） |
| monthly_settlement.net_weight | DECIMAL(12,2)（类型补记） | netWeight | Decimal | 单位吨；疑点：与井口口径天然不等 |

## 映射统计

- 输入：8 表 50 列 → 输出：8 聚合根 50 属性，**零列丢失、零列新增**。
- 类型补记 33 处、列名补记 5 处（全部在 input/source-map.md 逐条留痕）。
- 未建：数据字典（无字典表证据）、聚合关联/引用（无外键证据）、M2/M3/M5/M6/M7/MU 文件（无业务过程证据）——三者都是「不发明 DDL 里不存在的业务语义」的落实。
