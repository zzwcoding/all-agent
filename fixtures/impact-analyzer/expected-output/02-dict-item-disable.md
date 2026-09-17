# 影响分析报告 02 · 停用字典项 DICT-BOHAI-01/PRODUCING（在产）

- 变更对象: DICT-BOHAI-01（M1 · 数据字典 WELL_STATUS）的字典项 PRODUCING（在产，现 enabled=true）
- 变更内容: 将该字典项置 enabled=false（出厂集固定变更场景 C2，见 changes/change-list.md）
- 取证命令: `python3 tools/graph_index.py fixtures/graph_index/ontology-base --query DICT-BOHAI-01 --impact`
- 图统计: 节点=16 边=29；影响集 15 个受影响节点（沿依赖反向走）

## 字典纪律（先于影响链）

- **停用不删除**: 字典项只能置 enabled=false，不从 types.items 删除 code——存量数据与历史单据可能仍携带该 code，删除即历史口径失真。域内已有先例: SUSPENDED（停产）即 enabled=false 保留在册。
- 字典项 code 级引用不进图: 图索引只沿元素 ID 的 ref 字段建边，PRODUCING 是字典项 code 不是元素 ID，机械取证不含它——下列影响链之外必须人工扫描取值域使用面。本次人工扫描发现: BH-BOHAI-RecordDailyOutput 的前置条件「井状态为在产」以文字语义依赖 PRODUCING，停用后该行为对新单据是否放行需业务裁决（待 Owner 确认，不静默吞掉）。

## 字典引用扫描

直接引用方（via=dictionaryId）: AGG-BOHAI-001——attributes.status 的 dictionaryRef.dictionaryId 指向 DICT-BOHAI-01，井状态字段的取值域来源即此字典。

沿 ref 反向全链 15 个受影响节点（每行带传播依据，机器取证与 --impact 输出一致）:

- AGG-BOHAI-001（M1）hops=1 via=dictionaryId（path: AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 2
- AGG-BOHAI-002（M1）hops=2 via=targetAggregate（path: AGG-BOHAI-002 → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 3
- ASSOC-BOHAI-001（M1）hops=2 via=sourceAggregate（path: ASSOC-BOHAI-001 → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 3
- BH-BOHAI-QueryWellDailyOutput（M2）hops=2 via=ownerEntity（path: BH-BOHAI-QueryWellDailyOutput → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 3
- BH-BOHAI-UpdateWellStatus（M2）hops=2 via=ownerEntity（path: BH-BOHAI-UpdateWellStatus → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 3
- FLOW-BOHAI-001（M6）hops=2 via=businessObjectRefs（path: FLOW-BOHAI-001 → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 3
- QR-BOHAI-001（M7）hops=2 via=objectRef（path: QR-BOHAI-001 → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 3
- BH-BOHAI-RecordDailyOutput（M2）hops=3 via=ownerEntity（path: BH-BOHAI-RecordDailyOutput → AGG-BOHAI-002 → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 4
- PERM-BOHAI-QueryWellDailyOutput（M5）hops=3 via=targetRef（path: PERM-BOHAI-QueryWellDailyOutput → BH-BOHAI-QueryWellDailyOutput → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 4
- SCR-BOHAI-01（MU）hops=3 via=dataSource（path: SCR-BOHAI-01 → QR-BOHAI-001 → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 4
- PERM-BOHAI-RecordDailyOutput（M5）hops=4 via=targetRef（path: PERM-BOHAI-RecordDailyOutput → BH-BOHAI-RecordDailyOutput → AGG-BOHAI-002 → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 5
- RULE-BOHAI-001（M3）hops=4 via=reusedBy（path: RULE-BOHAI-001 → BH-BOHAI-RecordDailyOutput → AGG-BOHAI-002 → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 5
- RULE-BOHAI-002（M3）hops=4 via=reusedBy（path: RULE-BOHAI-002 → BH-BOHAI-RecordDailyOutput → AGG-BOHAI-002 → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 5
- ROLE-BOHAI-001（M5）hops=4 via=permissions（path: ROLE-BOHAI-001 → PERM-BOHAI-QueryWellDailyOutput → BH-BOHAI-QueryWellDailyOutput → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 5
- ACTOR-BOHAI-001（M5）hops=5 via=roles（path: ACTOR-BOHAI-001 → ROLE-BOHAI-001 → PERM-BOHAI-QueryWellDailyOutput → BH-BOHAI-QueryWellDailyOutput → AGG-BOHAI-001 → DICT-BOHAI-01）｜顺序 6

## 建议落地顺序（被依赖者优先）

原则: 先改被依赖者，后改依赖者；字典是取值域被依赖方（多个对象字段共指），字典先行。

1. 顺序 1 — DICT-BOHAI-01 字典项置 enabled=false（变更对象本体；取值域被依赖方先行）
2. 顺序 2 — AGG-BOHAI-001（hops=1 · 直接引用方，核对字段取值域声明与新单据录入面的可选值）
3. 顺序 3 — AGG-BOHAI-002、ASSOC-BOHAI-001、BH-BOHAI-QueryWellDailyOutput、BH-BOHAI-UpdateWellStatus、FLOW-BOHAI-001、QR-BOHAI-001（hops=2，查询/界面取值过滤随动）
4. 顺序 4 — BH-BOHAI-RecordDailyOutput、PERM-BOHAI-QueryWellDailyOutput、SCR-BOHAI-01（hops=3；BH-BOHAI-RecordDailyOutput 前置条件的语义依赖见特例处置，须 Owner 裁决后落地）
5. 顺序 5 — PERM-BOHAI-RecordDailyOutput、RULE-BOHAI-001、RULE-BOHAI-002、ROLE-BOHAI-001（hops=4，链路尾随）
6. 顺序 6 — ACTOR-BOHAI-001（hops=5，链路末端，通常仅需知会）

## 特例处置（字典项，命中）

- 停用不删除（见字典纪律节）；落地动作仅为 enabled 翻转。
- 停用后的存量数据: 已带 PRODUCING 的历史记录不受影响（code 仍在册），仅新单据不可再选。
- code 级语义依赖（前置条件文字）不进图，人工扫描结论已列入字典纪律节，落地前须 Owner 确认。

## 边界说明

- 本报告只读仓产出，不改任何本体文件；影响链全部来自 --impact 反向走，每行 via= 即传播依据，取证命令重跑可复现同一影响集。
- 机械面只覆盖 ID ref 通道；字典项 code 与文字表述的语义依赖不进图，已按特例处置人工补充并标注，不做无依据的机器断言。
