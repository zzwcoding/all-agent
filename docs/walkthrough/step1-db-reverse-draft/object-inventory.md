# 对象清单 · 渤海域 8 表全量逆向（票 09 端到端走查 · 工序①）

> **证据非权威，待 Owner 确认。**
> 本清单由 db-reverse 工序对渤海域 8 表全量逆向产出（票 09 步骤①）。
> 输入：`fixtures/db-reverse/input/bohai-8tables.sql`（R5·设定书附录 A 的忠实转写，逐字段注源见 `fixtures/db-reverse/input/source-map.md`）——票 06 出厂集固定输入，本走查直接复用作输入面（素材边界：R5 真源 = /Users/divh/Downloads/teach-petro-agent/docs/business-setting.md，附录 A 为 8 表字段级字典）。
> 工序依据：`skills/db-reverse/SKILL.md` 六步 + `references/reverse-guide.md`（一表一候选聚合根、键/注释直译、零关系推断——DDL 无外键声明）。
> **与出厂集参照产物的交叉核对**：本走查草案与 `fixtures/db-reverse/expected-output/`（票 06 按同一工序对同一输入的手工参照产物）逐对象逐属性核对一致（8 聚合根、50 属性、键约定、Enum 值集、疑点落点全部吻合）——同一工序对同一素材重跑一致，参照产物可信。差异仅一处：本走查版对象 ID 前缀同为 `AGG-BOHAI-`，序号按源表清单顺序编发，与参照产物同序。

## 清单（8/8 输入表全覆盖）

| # | 源表（注源） | 对象 ID | 对象名（直译） | alias | 键 → 标识约定 | 属性数 | 主要疑点（详见 dirty-signs.md） |
|---|---|---|---|---|---|---|---|
| 1 | well_info（R5·设定书附录 A.1，标题「井档案」） | AGG-BOHAI-001 | 井档案 | WellInfo | PK well_id → wellId（单列主键，unique） | 9 | 井号旧写法并存（D6）；状态滞后（D7）；行内冗余（D8） |
| 2 | oil_production_daily（R5·设定书附录 A.2，标题「日产计量」★核心事实源） | AGG-BOHAI-002 | 日产计量 | OilProductionDaily | PK (well_id, prod_date) → 复合键记入描述 | 9 | 吨方混写（D1）；A/B 班重复行与主键声明冲突（D2）；化验/折算打架（D3）；配产双值行（D4）；停井 openDays>0（D5） |
| 3 | water_injection_daily（R5·设定书附录 A.3，键「井号+日期」，无中文标题） | AGG-BOHAI-003 | 注水日计量（直译） | WaterInjectionDaily | 键（井号+日期）→ (wellId, injDate) | 5 | layerSplit 口径不一/偶为累计值（D9） |
| 4 | well_overhaul（R5·设定书附录 A.4，键「井号+起止」） | AGG-BOHAI-004 | 井检修记录（直译） | WellOverhaul | 键（井号+起止）→ (wellId, overhaulStart, overhaulEnd) | 6 | 跨月作业（D10）；批次补录（D11）；估算口径不一 |
| 5 | well_measures（R5·设定书附录 A.5，键「井号+措施次」） | AGG-BOHAI-005 | 井措施记录（直译） | WellMeasures | 键（井号+措施次）→ (wellId, measureSeq) | 7 | 有效期 30% 缺失（D12）；年增油算法不一（D13） |
| 6 | fluid_test（R5·设定书附录 A.6，键「井号+取样日期」） | AGG-BOHAI-006 | 流体化验记录（直译） | FluidTest | 键（井号+取样日期）→ (wellId, sampleDate) | 5 | 取样频次不齐；与折算含水口径打架（D3） |
| 7 | equip_status（R5·设定书附录 A.7，键「设备号+时间戳」） | AGG-BOHAI-007 | 设备状态记录（直译） | EquipStatus | 键（设备号+时间戳）→ (equipId, statusTime) | 6 | 停机原因码新旧编码并存（D14） |
| 8 | monthly_settlement（R5·设定书附录 A.8，键「区块+结算月」） | AGG-BOHAI-008 | 区块月度结算（直译） | MonthlySettlement | 键（区块+结算月）→ (blockName, settleDate) | 3 | 净重与井口口径天然不等（D15） |

## 划分与命名的保守边界（待 Owner 确认项汇总）

1. **一表一对象**：8 表 → 8 候选聚合根，未做合并/拆分/提升（如「区块/油田/平台」在 R5·§5 是实体草案但无源表，本工序不替 Owner 提升对象；R5·§5 的「受效关系」实体同样无源表，均不入草案，留工序② Owner 裁决）。
2. **对象中文名**：仅 A.1「井档案」/A.2「日产计量」为字典标题原文；其余 6 个为表名直译，逐条待 Owner 确认。
3. **零关系登记**：DDL 无 FOREIGN KEY，草案无 AggregateRootRef/ASSOC/DICT；同名键列（well_id 等）的关联推断全部留在疑点清单（D6）。
4. **零行为/规则/主体**：DDL 无业务过程证据，草案 profile 取 v9-core（M1 单文件）；行为/规则/主体/流程/查询出口须业务素材（R5·§1/§3/§4/§5/§7），属工序② Owner 裁决后的进仓内容，不在本草案。

草案 YAML 全文见 `draft-m1-object-model.md`（嵌入形态，MR 前形态）；映射证据见 `mapping-evidence.md`；疑点全集见 `dirty-signs.md`。
