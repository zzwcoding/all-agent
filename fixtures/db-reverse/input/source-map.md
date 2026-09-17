# source-map · 8 表 DDL 逐表逐字段注源（票 06 出厂集）

> 信源登记：**R5** = teach-petro-agent《渤海油田业务设定书》docs/business-setting.md（v3，2026-09-15）。
> 8 表字段级真源 = R5 附录 A「生产域 8 表数据字典」（v2 §2 收编版）。注源写法：`R5·设定书附录 A.x`。
> 转写文件：`bohai-8tables.sql`。本表逐字段声明「字典原文给了什么 / 转写补记了什么」——补记不发明字典没有的约束与语义。

## A.1 `well_info`（R5·设定书附录 A.1，中文标题「井档案」）

| DDL 字段 | 来源 | 字典原文 / 转写注记 |
|---|---|---|
| well_id | R5·设定书附录 A.1 | VARCHAR(8) 照抄；样本 `N-02`；旧写法 N2/N-2 并存（字典原文脏特征）；PK well_id 照抄 |
| well_name | R5·设定书附录 A.1 | 类型补记 VARCHAR(64)；样本 渤中28-1-N2 |
| well_type | R5·设定书附录 A.1 | CHAR(2) 照抄；EW 采油·IW 注水；「个别改型未留版本」（字典原文） |
| first_prod_date | R5·设定书附录 A.1 | DATE 照抄 |
| platform | R5·设定书附录 A.1 | 类型补记 VARCHAR(16)；样本 CEP-A/B |
| block_name | R5·设定书附录 A.1 | 类型补记 VARCHAR(16)；渤南/渤中/渤西 |
| field_name | R5·设定书附录 A.1 | 类型补记 VARCHAR(32)；「渤海油田，行内冗余=反规范化样例」（字典原文） |
| current_status | R5·设定书附录 A.1 | 类型补记 VARCHAR(16)；「生产中·停产·检修·待弃置」；「状态滞后：N-11 已停仍"生产中"」（字典原文） |
| remarks | R5·设定书附录 A.1 | 类型补记 VARCHAR(255)；「供应商导入塞过注入指令」（字典原文） |
| PRIMARY KEY (well_id) | R5·设定书附录 A.1 | 「一井一行；PK well_id」照抄 |

## A.2 `oil_production_daily`（R5·设定书附录 A.2，中文标题「日产计量」；字典标注★核心事实源）

| DDL 字段 | 来源 | 字典原文 / 转写注记 |
|---|---|---|
| well_id | R5·设定书附录 A.2 | 键成分 |
| prod_date | R5·设定书附录 A.2 | 键成分；类型 DATE 补记 |
| oil_output | R5·设定书附录 A.2 | DECIMAL(10,2) 照抄；单位吨；「个别行误录为方」（字典原文=吨方混写疑点） |
| liquid_output | R5·设定书附录 A.2 | 类型补记 DECIMAL(10,2)；单位方 |
| water_cut | R5·设定书附录 A.2 | 类型补记 DECIMAL(5,2)；单位 %；「化验折算，与 fluid_test 打架」（字典原文） |
| plan_output | R5·设定书附录 A.2 | 类型补记 DECIMAL(10,2)；单位吨；「配产版本切换日双值行」（字典原文） |
| open_days | R5·设定书附录 A.2 | 类型补记 DECIMAL(4,1)（样本含 24、6.5）；单位天；「停井日仍>0 矛盾行」（字典原文） |
| oil_pressure | R5·设定书附录 A.2 | 类型补记 DECIMAL(6,2)；单位 MPa |
| report_shift | R5·设定书附录 A.2 | CHAR(1) 照抄；A/B/C；「班次手抄汇总：同井同日 A/B 两行」（字典原文——与 PK 声明并存的字典内矛盾，照原样保留） |
| PRIMARY KEY (well_id, prod_date) | R5·设定书附录 A.2 | 「一井一日；PK well_id+prod_date」照抄 |

## A.3 `water_injection_daily`（R5·设定书附录 A.3，键「井号+日期」；字典未给中文标题）

| DDL 字段 | 来源 | 字典原文 / 转写注记 |
|---|---|---|
| well_id | R5·设定书附录 A.3 | 键成分 |
| inj_date | R5·设定书附录 A.3 | **列名补记**（字典仅声明键「井号+日期」）；类型 DATE 补记 |
| inj_volume | R5·设定书附录 A.3 | 类型补记 DECIMAL(10,2)；单位方 |
| pump_pressure | R5·设定书附录 A.3 | 类型补记 DECIMAL(6,2)；单位 MPa |
| layer_split | R5·设定书附录 A.3 | 类型补记 VARCHAR(64)；「`P1:60,P2:40`；两层/三层口径不一、偶为累计值」（字典原文） |
| PRIMARY KEY (well_id, inj_date) | R5·设定书附录 A.3 | 「（井号+日期）」照抄，日期列按补记名 |

## A.4 `well_overhaul`（R5·设定书附录 A.4，键「井号+起止」；字典未给中文标题）

| DDL 字段 | 来源 | 字典原文 / 转写注记 |
|---|---|---|
| well_id | R5·设定书附录 A.4 | 键成分 |
| overhaul_start | R5·设定书附录 A.4 | DATE 照抄；样本 2026-08-28 |
| overhaul_end | R5·设定书附录 A.4 | DATE 照抄；「跨月 8-28→9-06：当月口径切割争议源」（字典原文） |
| overhaul_type | R5·设定书附录 A.4 | 类型补记 VARCHAR(32)；样本「检泵」 |
| affected_output | R5·设定书附录 A.4 | 类型补记 DECIMAL(10,2)；单位吨；「各作业区估算口径不一」（字典原文） |
| batch_id | R5·设定书附录 A.4 | 类型补记 VARCHAR(32)；「补录：N-11 batch=20260911-T3——底稿 24 的 T-3 案例源」（字典原文） |
| PRIMARY KEY (well_id, overhaul_start, overhaul_end) | R5·设定书附录 A.4 | 「（井号+起止）」照抄 |

## A.5 `well_measures`（R5·设定书附录 A.5，键「井号+措施次」；字典未给中文标题）

| DDL 字段 | 来源 | 字典原文 / 转写注记 |
|---|---|---|
| well_id | R5·设定书附录 A.5 | 键成分 |
| measure_seq | R5·设定书附录 A.5 | **列名补记+类型补记** INT（字典仅声明键「井号+措施次」） |
| measure_type | R5·设定书附录 A.5 | 类型补记 VARCHAR(16)；「压裂/酸化/补孔/调剖」（字典原文值集） |
| job_date | R5·设定书附录 A.5 | 类型补记 DATE |
| effective_from | R5·设定书附录 A.5 | 类型补记 DATE；「30% 缺失」（字典原文） |
| effective_to | R5·设定书附录 A.5 | 类型补记 DATE；「30% 缺失」（字典原文） |
| incr_oil_annual | R5·设定书附录 A.5 | 类型补记 DECIMAL(10,2)；单位吨；「递减增油口径，两作业区算法不一致=事故 7」（字典原文） |
| PRIMARY KEY (well_id, measure_seq) | R5·设定书附录 A.5 | 「（井号+措施次）」照抄 |

## A.6 `fluid_test`（R5·设定书附录 A.6，键「井号+取样日期」；字典未给中文标题）

| DDL 字段 | 来源 | 字典原文 / 转写注记 |
|---|---|---|
| well_id | R5·设定书附录 A.6 | 键成分 |
| sample_date | R5·设定书附录 A.6 | **列名补记**（字典仅声明键「井号+取样日期」）；类型 DATE 补记 |
| water_cut_lab | R5·设定书附录 A.6 | 类型补记 DECIMAL(5,2)；化验含水 |
| density | R5·设定书附录 A.6 | 类型补记 DECIMAL(5,3)；密度（t/m³） |
| api_gravity | R5·设定书附录 A.6 | 类型补记 DECIMAL(5,2)；°API |
| 表级：取样频次 | R5·设定书附录 A.6 | 「频次不齐（高产周报/低产半月报），缺失插补规则争议」（字典原文） |
| PRIMARY KEY (well_id, sample_date) | R5·设定书附录 A.6 | 「（井号+取样日期）」照抄 |

## A.7 `equip_status`（R5·设定书附录 A.7，键「设备号+时间戳」；字典未给中文标题）

| DDL 字段 | 来源 | 字典原文 / 转写注记 |
|---|---|---|
| equip_id | R5·设定书附录 A.7 | **列名补记**（字典仅声明键「设备号」）；类型 VARCHAR(16) 补记 |
| status_time | R5·设定书附录 A.7 | **列名补记+类型补记** TIMESTAMP（字典仅声明键「时间戳」） |
| equip_type | R5·设定书附录 A.7 | 类型补记 VARCHAR(16)；「电泵/螺杆泵/加热炉」（字典原文值集） |
| load | R5·设定书附录 A.7 | 类型补记 DECIMAL(8,2)；字典未给单位（照实标注） |
| current | R5·设定书附录 A.7 | 类型补记 DECIMAL(8,2)；字典未给单位（照实标注） |
| stop_reason_code | R5·设定书附录 A.7 | 类型补记 VARCHAR(16)；「新旧编码并存：旧 R3=皮带断，新 BELT——归一化素材」（字典原文） |
| PRIMARY KEY (equip_id, status_time) | R5·设定书附录 A.7 | 「（设备号+时间戳）」照抄 |

## A.8 `monthly_settlement`（R5·设定书附录 A.8，键「区块+结算月」；字典未给中文标题）

| DDL 字段 | 来源 | 字典原文 / 转写注记 |
|---|---|---|
| block_name | R5·设定书附录 A.8 | 键成分；类型 VARCHAR(16) 补记；渤南/渤中/渤西 |
| settle_date | R5·设定书附录 A.8 | 类型补记 DATE；粒度=结算月；v2 兼容声明（附录 A 卷首）：settle_date 为规范名 |
| net_weight | R5·设定书附录 A.8 | 类型补记 DECIMAL(12,2)；单位吨；「扣自用油与输差；与井口口径天然不等——事故 7 另一面」（字典原文） |
| PRIMARY KEY (block_name, settle_date) | R5·设定书附录 A.8 | 「（区块+结算月）」照抄 |

## 全局转写注记

- 外键：R5 附录 A 全字典**无任何外键声明**，DDL 相应不建 FOREIGN KEY——同名键列（如各表 well_id）的关联只是推断，留待逆向工序标注疑点、Owner 裁决。
- 主键：8 张表的主键声明全部来自各小节括号内的键语义原文。
- 样本行：R5·A.1–A.4 附样本行（本 DDL 只转写结构不插数据行；样本中的脏特征已随列注释保留）。
