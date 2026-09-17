# 脏特征疑点清单 · 渤海域 8 表逆向（db-reverse 参照产物 AC4，票 06）

> **证据非权威，待 Owner 确认。** 疑点全部来自输入 DDL 注释（= R5·设定书附录 A 字典原文），逆向工序不静默吞掉任何一条：每条都问 Owner 一个可裁决的问题。草案（m1-object-model.yaml）各聚合根描述已点名对应疑点。

## 疑点全集（15 条）

| # | 位置（表.列） | 特征 | 字典原文证据（注源） | 待 Owner 裁决的问题 |
|---|---|---|---|---|
| D1 | oil_production_daily.oil_output | **吨方混写**（单位吨，个别行误录为方） | R5·设定书附录 A.2「oil_output DECIMAL(10,2) 吨（个别行误录为方）」 | 单位语义收进属性定义还是立清洗规则？本草案暂记单属性 Decimal |
| D2 | oil_production_daily（行级） | **A/B 班重复行**（同井同日 A/B 两行）与主键声明冲突 | R5·设定书附录 A.2「班次手抄汇总：同井同日 A/B 两行」vs「一井一日；PK well_id+prod_date」 | 班次行是业务事实还是应去重？reportShift 属性是否保留枚举 |
| D3 | oil_production_daily.water_cut ↔ fluid_test.water_cut_lab | 化验折算与化验表**口径打架** | R5·设定书附录 A.2「（化验折算，与 fluid_test 打架）」；A.6 | 两属性并存还是其一为权威源 |
| D4 | oil_production_daily.plan_output | 配产版本切换日**双值行** | R5·设定书附录 A.2「配产版本切换日双值行」 | 双值是版本事实还是脏行 |
| D5 | oil_production_daily.open_days | 停井日仍>0 **矛盾行** | R5·设定书附录 A.2「停井日仍>0 矛盾行」 | 矛盾行的取舍规则 |
| D6 | well_info.well_id（波及各表同名键列） | 井号**旧写法并存**（N2/N-2 vs N-02） | R5·设定书附录 A.1「旧写法 N2/N-2 并存」 | 归一化在源侧还是语义层；同名键列间的关联是否成立（DDL 无外键，草案零引用登记） |
| D7 | well_info.current_status | **状态滞后**（N-11 已停仍记「生产中」） | R5·设定书附录 A.1「状态滞后」 | 状态时效责任方；是否需要状态时间戳属性 |
| D8 | well_info.field_name | 行内**冗余**（反规范化样例） | R5·设定书附录 A.1「行内冗余=反规范化样例」 | 保留为属性还是提升为独立对象（提升=业务判断，草案未做） |
| D9 | water_injection_daily.layer_split | **口径不一**（两层/三层）、偶为**累计值** | R5·设定书附录 A.3「两层/三层口径不一、偶为累计值」 | 保持 String 还是结构化（结构化=发明格式规范，草案未做） |
| D10 | well_overhaul（overhaul_start→end） | **跨月**作业（当月口径切割争议源） | R5·设定书附录 A.4「跨月 8-28→9-06：当月口径切割争议源」 | 跨月作业的归属期规则 |
| D11 | well_overhaul.batch_id | **补录**（样本 20260911-T3，T-3 案例） | R5·设定书附录 A.4「补录：N-11 batch=20260911-T3」 | 迟到数据是否需要接收时间属性 |
| D12 | well_measures.effective_from / effective_to | 约 **30% 缺失** | R5·设定书附录 A.5「30% 缺失」 | 缺失属正常业务还是质量问题；属性 required 与否 |
| D13 | well_measures.incr_oil_annual | 年增油**算法不一致**（两作业区） | R5·设定书附录 A.5「两作业区算法不一致=事故 7」 | 口径统一前的使用边界 |
| D14 | equip_status.stop_reason_code | **新旧编码并存**（旧 R3=皮带断，新 BELT） | R5·设定书附录 A.7「新旧编码并存……归一化素材」 | 映射表归属；值集不全故草案保持 String 不建枚举 |
| D15 | monthly_settlement.net_weight | 净重与井口口径**天然不等**（扣自用油与输差） | R5·设定书附录 A.8「与井口口径天然不等——事故 7 另一面」 | 与日产计量对象并存的口径标注方式 |

## 低烈度注记（不单列裁决项）

- fluid_test 取样频次不齐（高产周报/低产半月报），缺失插补规则有争议（R5·设定书附录 A.6）——影响数据可用性，不影响对象/属性结构。
- well_type 个别改型未留版本（R5·设定书附录 A.1）——枚举值集 [EW, IW] 暂按字典注释，历史改型语义待 Owner 确认。
- equip_status.load / current 单位字典未声明——属性照建，单位待 Owner 确认。

## 统计与落点

- 疑点 15 条（D1–D15）+ 低烈度注记 3 条；来源全部为输入注释（R5·设定书附录 A），零推测增补。
- 草案落点：AGG-BOHAI-001（D6/D7/D8）、AGG-BOHAI-002（D1–D5）、AGG-BOHAI-003（D9）、AGG-BOHAI-004（D10/D11）、AGG-BOHAI-005（D12/D13）、AGG-BOHAI-006（D3/低烈度1）、AGG-BOHAI-007（D14/低烈度3）、AGG-BOHAI-008（D15）。
- 全部待 Owner 确认；在 Owner 裁决前，本草案不得作为已定稿本体消费。
