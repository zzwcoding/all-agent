# 影响分析报告 01 · 改对象 AGG-BOHAI-001 的日产量字段

- 变更对象: AGG-BOHAI-001（M1 · 域 bohai-fixture）
- 变更内容: 调整 dailyOutput 字段定义（出厂集固定变更场景 C1，见 changes/change-list.md）
- 取证命令: `python3 tools/graph_index.py fixtures/graph_index/ontology-base --query AGG-BOHAI-001 --impact`
- 图统计: 节点=16 边=29；影响集 14 个受影响节点（沿依赖反向走）

## 影响链（每行=受影响 ID / 模型 / 跳数 / 传播依据 / 建议落地顺序）

- AGG-BOHAI-002（M1）hops=1 via=targetAggregate（path: AGG-BOHAI-002 → AGG-BOHAI-001）｜顺序 2
- ASSOC-BOHAI-001（M1）hops=1 via=sourceAggregate（path: ASSOC-BOHAI-001 → AGG-BOHAI-001）｜顺序 2
- BH-BOHAI-QueryWellDailyOutput（M2）hops=1 via=ownerEntity（path: BH-BOHAI-QueryWellDailyOutput → AGG-BOHAI-001）｜顺序 3
- BH-BOHAI-UpdateWellStatus（M2）hops=1 via=ownerEntity（path: BH-BOHAI-UpdateWellStatus → AGG-BOHAI-001）｜顺序 3
- FLOW-BOHAI-001（M6）hops=1 via=businessObjectRefs（path: FLOW-BOHAI-001 → AGG-BOHAI-001）｜顺序 4
- QR-BOHAI-001（M7）hops=1 via=objectRef（path: QR-BOHAI-001 → AGG-BOHAI-001）｜顺序 4
- BH-BOHAI-RecordDailyOutput（M2）hops=2 via=ownerEntity（path: BH-BOHAI-RecordDailyOutput → AGG-BOHAI-002 → AGG-BOHAI-001）｜顺序 5
- PERM-BOHAI-QueryWellDailyOutput（M5）hops=2 via=targetRef（path: PERM-BOHAI-QueryWellDailyOutput → BH-BOHAI-QueryWellDailyOutput → AGG-BOHAI-001）｜顺序 5
- SCR-BOHAI-01（MU）hops=2 via=dataSource（path: SCR-BOHAI-01 → QR-BOHAI-001 → AGG-BOHAI-001）｜顺序 6
- PERM-BOHAI-RecordDailyOutput（M5）hops=3 via=targetRef（path: PERM-BOHAI-RecordDailyOutput → BH-BOHAI-RecordDailyOutput → AGG-BOHAI-002 → AGG-BOHAI-001）｜顺序 7
- RULE-BOHAI-001（M3）hops=3 via=reusedBy（path: RULE-BOHAI-001 → BH-BOHAI-RecordDailyOutput → AGG-BOHAI-002 → AGG-BOHAI-001）｜顺序 7
- RULE-BOHAI-002（M3）hops=3 via=reusedBy（path: RULE-BOHAI-002 → BH-BOHAI-RecordDailyOutput → AGG-BOHAI-002 → AGG-BOHAI-001）｜顺序 7
- ROLE-BOHAI-001（M5）hops=3 via=permissions（path: ROLE-BOHAI-001 → PERM-BOHAI-QueryWellDailyOutput → BH-BOHAI-QueryWellDailyOutput → AGG-BOHAI-001）｜顺序 7
- ACTOR-BOHAI-001（M5）hops=4 via=roles（path: ACTOR-BOHAI-001 → ROLE-BOHAI-001 → PERM-BOHAI-QueryWellDailyOutput → BH-BOHAI-QueryWellDailyOutput → AGG-BOHAI-001）｜顺序 8

直接引用者（hops=1）共 6 个：AGG-BOHAI-002、ASSOC-BOHAI-001、BH-BOHAI-QueryWellDailyOutput、BH-BOHAI-UpdateWellStatus、FLOW-BOHAI-001、QR-BOHAI-001——字段语义变化必查这六处的读写与展示面。间接受影响 8 个（hops=2 起）经上述节点传导。

## 建议落地顺序（被依赖者优先）

原则: 先改被依赖者，后改依赖者；方向依据 ontology/schema/model-deps.json 依赖白名单的 ref 方向（ref 字段从引用方指向被依赖方，被指向者先落地）。主序取 --impact 跳数升序（跳数小者离被依赖核心近），同跳数内按依赖方向微调（被依赖方在前，查询出口与界面等消费末端最后）。

1. 顺序 1 — AGG-BOHAI-001 本体字段（变更对象本体先行；M1 数据结构层，被 6 处直接引用）
2. 顺序 2 — AGG-BOHAI-002、ASSOC-BOHAI-001（hops=1 · 数据结构层，经 targetAggregate/sourceAggregate 挂靠）
3. 顺序 3 — BH-BOHAI-QueryWellDailyOutput、BH-BOHAI-UpdateWellStatus（hops=1 · 行为层，ownerEntity 直挂）
4. 顺序 4 — FLOW-BOHAI-001、QR-BOHAI-001（hops=1 · 流程与查询出口，展示/取数面适配）
5. 顺序 5 — BH-BOHAI-RecordDailyOutput（hops=2 · 行为，经 AGG-BOHAI-002 传导）、PERM-BOHAI-QueryWellDailyOutput（hops=2 · 权限，经行为传导）
6. 顺序 6 — SCR-BOHAI-01（hops=2 · 界面，经查询出口传导，消费末端）
7. 顺序 7 — PERM-BOHAI-RecordDailyOutput、RULE-BOHAI-001、RULE-BOHAI-002、ROLE-BOHAI-001（hops=3，权限/规则/角色链尾随适配）
8. 顺序 8 — ACTOR-BOHAI-001（hops=4，链路末端，通常仅需知会）

## 特例处置

本场景未命中字典项/无下游引用特例（变更对象有 14 个下游受影响节点）。间接受影响节点（顺序 5–8）按传导链适配即可，不为它们单独排期。

## 边界说明

- 本报告只读仓产出，不改任何本体文件；影响链全部来自 --impact 反向走，每行 via= 即传播依据，取证命令重跑可复现同一影响集。
- 机械面只覆盖 ID ref 通道：行为/规则中对字段语义的文字表述（如校验表达式的字段名）不进图，顺序 3/5 的行为与规则改动时需人工复核其表达式对 dailyOutput 的语义依赖，发现出入标「待 Owner 确认」。
