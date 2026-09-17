# 对象清单 · 渤海域 8 表逆向（db-reverse 参照产物 AC1，票 06）

> **证据非权威，待 Owner 确认。** 本清单由 `input/bohai-8tables.sql`（R5·设定书附录 A 忠实转写）按 db-reverse 工序产出：一表 → 一候选聚合根，键/注释直译，零关系推断（DDL 无外键声明）。

## 清单（8/8 输入表全覆盖）

| # | 源表（注源） | 对象 ID | 对象名（直译） | alias | 键 → 标识约定 | 属性数 | 主要疑点（详见 dirty-signs.md） |
|---|---|---|---|---|---|---|---|
| 1 | well_info（R5·设定书附录 A.1） | AGG-BOHAI-001 | 井档案 | WellInfo | PK well_id → wellId（单列主键，unique） | 9 | 井号旧写法并存；状态滞后；行内冗余 |
| 2 | oil_production_daily（R5·设定书附录 A.2） | AGG-BOHAI-002 | 日产计量 | OilProductionDaily | PK (well_id, prod_date) → 复合键记入描述 | 9 | 吨方混写；A/B 班重复行与主键声明冲突；化验/折算打架 |
| 3 | water_injection_daily（R5·设定书附录 A.3） | AGG-BOHAI-003 | 注水日计量 | WaterInjectionDaily | 键（井号+日期）→ (wellId, injDate) | 5 | layerSplit 口径不一/偶为累计值 |
| 4 | well_overhaul（R5·设定书附录 A.4） | AGG-BOHAI-004 | 井检修记录 | WellOverhaul | 键（井号+起止）→ (wellId, overhaulStart, overhaulEnd) | 6 | 跨月作业；估算口径不一；批次补录 |
| 5 | well_measures（R5·设定书附录 A.5） | AGG-BOHAI-005 | 井措施记录 | WellMeasures | 键（井号+措施次）→ (wellId, measureSeq) | 7 | 有效期 30% 缺失；年增油算法不一 |
| 6 | fluid_test（R5·设定书附录 A.6） | AGG-BOHAI-006 | 流体化验记录 | FluidTest | 键（井号+取样日期）→ (wellId, sampleDate) | 5 | 取样频次不齐；与折算含水口径打架 |
| 7 | equip_status（R5·设定书附录 A.7） | AGG-BOHAI-007 | 设备状态记录 | EquipStatus | 键（设备号+时间戳）→ (equipId, statusTime) | 6 | 停机原因码新旧编码并存 |
| 8 | monthly_settlement（R5·设定书附录 A.8） | AGG-BOHAI-008 | 区块月度结算 | MonthlySettlement | 键（区块+结算月）→ (blockName, settleDate) | 3 | 净重与井口口径天然不等 |

## 划分与命名的保守边界（待 Owner 确认项汇总）

1. **一表一对象**：8 表 → 8 候选聚合根，未做合并/拆分（合并如「井档案+日产计量」归属同一聚合，属业务判断，DDL 无证据，不替人决定）。
2. **对象中文名**：仅 A.1「井档案」/A.2「日产计量」为字典标题原文；其余 6 个为表名直译，逐条待 Owner 确认。
3. **零关系登记**：DDL 无 FOREIGN KEY，草案无 AggregateRootRef/ASSOC/DICT；同名键列（well_id 等）的关联推断全部留在疑点清单。
4. **零行为/规则/主体**：DDL 无业务过程证据，profile 取 v9-core，仅产 M1 文件。

草案落盘：`bohai/manifest.json` + `bohai/m1-object-model.yaml`（映射证据见 mapping-evidence.md，疑点全集见 dirty-signs.md）。
