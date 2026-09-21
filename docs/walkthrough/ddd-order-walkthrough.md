# 订单域端到端走查（票 53）· ddd-modeler 五步工序实弹

> 走查对象：`skills/ddd-modeler/SKILL.md` 五步工序 × 第八套出厂集本体输入 `fixtures/ddd-modeler/inputs/ontology/order`（票 51 合成最小订单域，自造不借真域）。
> 工序真源：`skills/ddd-modeler/SKILL.md` + `references/term-anchoring.md` + `references/slicing-playbook.md`；格式真源：`design/ddd/README.md`。
> 纪律：所有输出均为真实命令的真实输出（原样摘录，不表演）；先例照一期票 09 走查（`docs/walkthrough/step7-mcp-e2e.md`）。
> 红线核对：**ontology/（含渤海域真域）、skills/、tools/、design/ddd/、fixtures/ 零改动**——走查只读这些；设计件演示件落本目录（`docs/walkthrough/`），**不进 `design/ddd/` 真产物区**（走查演示与真实产物分离，取舍见 lessons/54）。

## 走查留痕五件（索引）

| 件 | 文件 | 内容 |
|---|---|---|
| 1 | `docs/walkthrough/ddd-order-walkthrough.md` | 本件：五步工序主记录 + 两闸绿输出留痕 |
| 2 | `docs/walkthrough/ddd-order-rounds.md` | 行为清单素材原文 + 轮 1–4 中间件 YAML 全文（`input_of_round` 链条可核） |
| 3 | `docs/walkthrough/ddd-order-design-artifacts.md` | 四类设计件五份 YAML 全文（聚合卡×2/事件表/映射/仓储边界，走查演示件） |
| 4 | `docs/walkthrough/ddd-order-human-review.md` | 《待人审清单》演示件（机器软节转写+粒度完备性+分流挂起） |
| 5 | `docs/walkthrough/ddd-order-diagrams.md` | Mermaid 三图（classDiagram/flowchart/erDiagram） |

工作区说明：工序运行时中间件与成稿 YAML 落 `tmp/ddd/order*/`（`tmp/` 不入仓，票 52 已设；`ddd_check` target 取「等价物」），仓内留痕=本目录五件 .md 内嵌全文。

## 〇、输入三件验收（term-anchoring §1，工序开工前置）

| # | 输入 | 验收结果 |
|---|---|---|
| 1 | 本体域目录 | `fixtures/ddd-modeler/inputs/ontology/order/` 真实存在：m1-object-model.yaml（3 聚合）+ glossary-model.yaml（GLS-ORDER-001..007）+ manifest.json（profile v9-full，只备 M1+GLS 如实 omittedModels） |
| 2 | 本体侧语义闸全绿 | 实跑见下，exit 0 |
| 3 | 行为/规则清单素材 | 走查演示素材一份（5 条编号行为，合成——订单域最小行为集，原文全文见件 2）；素材里的概念同样须锚词条，锚不到走三分流 |

skill 命令形态适配注记：SKILL.md 步 1 写 `schema_check.py ontology/<域>`；走查输入为 fixtures 域目录，命令同形换路径（`ddd_check` 头注同款「等价物」口径）。

```
$ python3 tools/schema_check.py fixtures/ddd-modeler/inputs/ontology/order
语义闸 schema_check — /Users/divh/Downloads/All-agent/fixtures/ddd-modeler/inputs/ontology/order
域: order(profile=v9-full,2文件)；模型文件 2 个
L1: 0 | L2: 0 | L3: 0 | L4: 0
语义闸: 全过
（exit=0）
```

## 一、步 1 · 术语锚定（无词条不建模）

行为清单素材 5 条逐条锚定（锚定证据落点=轮 1 中间件 `origin`/`terms`/`open_questions` 字段，不散落对话——term-anchoring §4）：

| 素材 | 锚定结果 | 去向 |
|---|---|---|
| B1 提交订单 | 订单编号→GLS-ORDER-001、下单时间→GLS-ORDER-002、行数量→GLS-ORDER-003、行单价→GLS-ORDER-004；聚合 AGG-ORDER-001/002 | 进轮 1 事件 ORDER_SUBMITTED |
| B2 支付扣款成功 | 支付金额→GLS-ORDER-006、支付状态→GLS-ORDER-007；聚合 AGG-ORDER-003 | 进轮 1 事件 PAYMENT_SUCCEEDED |
| B3 取消订单 | 订单编号→GLS-ORDER-001；已支付拒取消=不变量候选 | 进轮 1 事件 ORDER_CANCELLED |
| B4 优惠券抵扣 | **「优惠券」词条集合无对应 term——概念缺词条** | 三分流①：回 onto-modeler 补本体，本工序挂起（不就地造 ID）；记录于轮 1 `open_questions`，转《待人审清单》 |
| B5 改货（必要时允许顾客改货） | 改什么/何时/何约束未定——**素材自身含糊** | 三分流③：进《待人审清单》，明确后再锚定 |

锚定核对：全部引用写词条 ID 不写裸名；GLS-ORDER-005（收货地址）在册但素材未提及——不硬拉进设计件，完备性交人审（见件 4）。**本工序不发明业务事实**：设计判断全部可回溯到 B1–B5 或本体输入。

## 二、步 2 · 事件时间轴→命令→聚合候选（三轮切片）

三轮逐轮推进，每轮产一份中间件 YAML（全文见件 2，`tmp/ddd/order/round-*.yaml` 实跑原件）：

- 轮 1 事件时间轴：3 事件（ORDER_SUBMITTED / PAYMENT_SUCCEEDED / ORDER_CANCELLED）+ 2 条分流 open_questions；
- 轮 2 命令清单：3 命令（提交订单/确认支付回调/取消订单），每命令挂触发事件+发起方；支付回调发起方=支付网关（外部系统）如实记，不硬造内部 actor；轮 1 分流项**原地挂起不流入**（新鲜上下文纪律 §3.2）；
- 轮 3 聚合候选：3 候选（=M1 三个 AGGREGATE_ROOT，M1 把订单项也标了根——候选线索照实列出，合并裁决留给轮 4），每候选带一句一致性锚；**只列候选不合并**。

**新鲜上下文降级声明（如实）**：本走查在单代理施工窗口内执行，「每轮新开上下文」以降级形态执行——每轮产出定稿落盘后，下一轮只重读上一轮定稿中间件文件本体再产出，不带前轮过程散文与草稿。真·新开上下文派发待运行时多代理编排接线（与 lessons/48 L5 派发降级同款问题，如实留痕； lessons/54 记该工序体感）。

## 三、步 3 · 合并候选显式追问（必走步）

轮 4 逐组追问「是否必须同时成立/同时改？」，判据事实作答（全文见件 2 轮 4）：

| 追问 | 判据事实 | verdict |
|---|---|---|
| AGG-ORDER-001（订单）× AGG-ORDER-002（订单项）？ | 是——B1「至少一行」存在依赖；轮 2 命令全量核对无任何脱离订单单独改订单项的命令；「有单无行/有行无单」中间态不被 B1 接受 | **merge**（并入 AGG-ORDER-001） |
| AGG-ORDER-001（订单）× AGG-ORDER-003（支付）？ | 否——时间轴上订单先成立（B1）支付后发生（B2），订单可长期待支付；「订单随支付变已支付」是跨聚合事实，走事件串联不共享字段 | **keep-apart** |

两问 `decided_by: 待 Owner`：走查形态 Owner 不在场，判据事实满足者按判据走、**裁决复核权逐条入《待人审清单》**（不擅自免问，也不机械拆分凑数）；`pending_questions: []`（两问均有判据事实答案，无挂起疑问）。

## 四、步 4 · 成稿→五查自检→人审清单

按轮 4 定稿候选（订单聚合吸收订单项；支付独立）把中间件翻修成四类设计件五份（字段 schema 一字照 `design/ddd/README.md`，草案头固定注释，`status: 草案`；全文见件 3）。五查实跑（`tmp/ddd/order-design/` 为 target 等价物）：

```
$ python3 tools/ddd_check.py tmp/ddd/order-design --ontology fixtures/ddd-modeler/inputs/ontology/order
DDD 设计件闸 ddd_check — /Users/divh/Downloads/All-agent/tmp/ddd/order-design
本体: /Users/divh/Downloads/All-agent/fixtures/ddd-modeler/inputs/ontology/order（词条 10 条）；设计件 5 个（聚合卡 2 / 事件表 1 / 映射 1 / 仓储 1）
五查: cross-agg-embed 0 | term-ref 0 | invariant 0 | mapping 0 | naming 0 | file-kind 0
待人审清单（软节，不进退出码）:
  - 聚合 AGG-ORDER-001 零事件（事件表无其生产条目）——跨聚合协作缺失嫌疑，粒度人审裁决（票 51 人审清单，digest §3）
DDD 闸: 全过
（exit=0）
```

软节一条，同源可解释：ORDER_SUBMITTED/ORDER_CANCELLED 按格式真源 §2「单聚合内部流转不进表」未进事件表（本素材无跨聚合消费方），闸按设计如实提示嫌疑、粒度交人审——**软节提示与工序判断的张力正是人审清单该承载的**，已逐条转写（件 4，抄录不消化）。《待人审清单》另收：轮 4 两问复核、GLS-ORDER-005 覆盖缝隙、不变量完备性（Payment 的 INCOMPLETE_PAYMENT 是 B2 的走查化读法）、事件交付档位、两条分流挂起项。

## 五、步 5 · Mermaid 图（人审靠图）

三图合成见件 5：聚合卡→classDiagram（不变量方法入类，跨聚合不画线）、事件表→flowchart LR（生产→事件→消费逐事件一链）、映射→erDiagram（聚合↔表投影）。与《待人审清单》一起交 Owner。

## 六、与票 51 出厂集样本（`fixtures/ddd-modeler/expected/`）的差异对照

同输入域（词条/聚合全同）、同一格式真源，两套设计件**均过五查**；差异全部来自行为素材不同（出厂集样本为任务口径中性设定，本走查素材为订单域最小行为集）——印证「聚合设计=素材+判据的产物，不是词条的唯一推论」：

| 判断点 | 出厂集样本 | 本走查 | 根因 |
|---|---|---|---|
| ORDER_SUBMITTED 进事件表 | 进（消费方=支付，outbox） | 不进（素材无「支付消费订单已提交」事实，单聚合内部流转） | 素材事实面不同 |
| 订单不变量第二集 | changeQuantity 拒非正数 | cancel 拒已支付 | 素材行为集不同（B3 有取消、无改量） |
| 收货地址值对象 | 入卡（GLS-ORDER-005） | 不入+人审清单缝隙项 | 素材未提及该概念 |
| 订单项不变量/纠正策略 | 有 | 无（素材无对应事实，不发明） | 同上 |

## 七、工序体感（skill 迭代输入，详见 lessons/54）

1. **新鲜上下文在单代理只能降级执行**（见步 2 声明）——skill 正文未写单代理形态怎么自处，建议补一句降级声明话术；
2. **行为/规则清单素材无最小格式约定**——输入契约只说"用户提供的素材"，本走查自拟「编号行为条目+动宾+涉及名词」最小形态可用，建议 skill 给个建议格式（不落闸）；
3. **不变量 `method` 字段与方法命名**（`Order.submit()` 式）贴着"不做代码生成"红线——走查按「设计件命名级字段、非代码」处理，建议 skill 正文一句澄清边界；
4. **闸不查词条覆盖率**：GLS-ORDER-005 在册却可零覆盖过闸——完备性人审的真实示例（软节设计只盯事件/聚合结构面），已在人审清单收口；
5. 五步顺序、三分流、软节→人审清单转写链路**好用**，轮间 `input_of_round` 链条机核可用。
