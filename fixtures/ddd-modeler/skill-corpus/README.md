# skill-corpus · ddd-modeler skill 轨出厂集样例（票 52）

固定本体输入（`../inputs/ontology/order`，票 51 自造最小订单域词条）上，ddd-modeler 五步工序的**逐轮中间件样例**：

| 文件 | 工序步 | 运行时落位 |
|---|---|---|
| round-1-event-timeline.yaml | 步 2·轮 1 事件时间轴 | tmp/ddd/order/round-1-event-timeline.yaml |
| round-2-commands.yaml | 步 2·轮 2 命令清单 | tmp/ddd/order/round-2-commands.yaml |
| round-3-aggregate-candidates.yaml | 步 2·轮 3 聚合候选 | tmp/ddd/order/round-3-aggregate-candidates.yaml |
| round-4-merge-review.yaml | 步 3 合并追问记录 | tmp/ddd/order/round-4-merge-review.yaml |
| human-review.md | 步 4 待人审清单 | design/ddd/order/human-review.md（随草案进 MR） |

要点：

- **中间件是工作件不是设计件**：无 status、不写 design/ddd/、不进 MR（tmp/ 不入仓——归档闸 design-card 类要求 status，五查闸只认四类设计件，中间件混入任一面都是红，票 52 实跑确认）。本目录样例是唯一入仓形态：fixtures/** 布局允许，teaching corpus 性质。
- **成稿终态=../expected/**（单一真源不复制，anti-drift 沿票 51 取舍）：轮 4 `resolved_candidates` 即 expected/ 两张聚合卡（订单项 AGG-ORDER-002 经追问并入订单 AGG-ORDER-001 成实体；支付 AGG-ORDER-003 独立）。
- **断言面**：本套断言全部在上一级 `../assertions.json`（S 前缀标签）——fixture_run 按 fixtures/ 直接子目录发现套件、每套只读根 assertions.json，**不递归**，本目录不设独立 assertions.json（设了也不会被发现，票 52 实跑确认记 lessons/53）。
- 中间件格式真源：skills/ddd-modeler/references/slicing-playbook.md §4；本样例与其互为镜像。
