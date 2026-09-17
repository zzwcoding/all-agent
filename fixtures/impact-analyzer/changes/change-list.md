# 固定变更输入清单（impact-analyzer 出厂集 · 票 08）

分析用本体：`fixtures/graph_index/ontology-base`（票 04 图索引最小域，只读复用，同票 07 手法；16 节点 29 边）。三个固定变更场景各产一份影响分析报告（expected-output/01–03，即 docs/impact/NN-*.md 的规范样例格式）。

## C1 · 改对象字段（AC1 影响链 + AC2 落地顺序）

变更：AGG-BOHAI-001（井）的 dailyOutput 字段定义调整。

期望：影响链覆盖全部直接引用者——hops=1 共 6 个：AGG-BOHAI-002（via=targetAggregate）/ ASSOC-BOHAI-001（via=sourceAggregate）/ BH-BOHAI-QueryWellDailyOutput 与 BH-BOHAI-UpdateWellStatus（via=ownerEntity）/ FLOW-BOHAI-001（via=businessObjectRefs）/ QR-BOHAI-001（via=objectRef）；全链 14 个受影响节点每行带 via= 传播依据；报告含建议落地顺序（先改被依赖者，后改依赖者）。

## C2 · 改字典项（AC3 字典停用）

变更：停用 DICT-BOHAI-01（井状态字典）的字典项 PRODUCING（在产）——置 enabled=false。

期望：报告含「停用不删除」纪律语（域内已有先例：SUSPENDED 即 enabled=false 保留在册）；字典引用扫描给出直接引用方 AGG-BOHAI-001（via=dictionaryId）与全链 15 个受影响节点（每行带传播依据）；字典项 code 级引用不进图的边界说明（行为前置条件的文字语义依赖须人工复核）。

## C3 · 改无下游对象（AC4 无影响）

变更：ACTOR-BOHAI-001（采油工）的 attributes.department 文案调整。

期望：--impact 沿依赖反向走零命中（实测：影响集 0 个受影响节点）→ 报告明确「无影响」+ 核验方式（取证命令 + 图统计对照），不硬凑、不出现任何受影响 ID 列表。
