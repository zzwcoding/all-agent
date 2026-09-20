# 订单域走查 · 行为清单素材与逐轮中间件（票 53 走查留痕件 2）

> 中间件是**工作件不是设计件**：无 status 字段、不写 design/ddd/、不进 MR（slicing-playbook §3.4）。
> 实跑原件在 `tmp/ddd/order/`（tmp/ 不入仓）；本件为留痕全文摘录，与原件一字一致。
> 新鲜上下文纪律：每轮只喂上一轮定稿（`input_of_round` 字段留痕，链条机核可用）；单代理降级形态声明见件 1 步 2。

## 行为清单素材（走查演示输入 · 合成）

> 工序输入契约第三件「用户提供的该域行为/规则清单素材」——本素材为走查演示拟制的最小订单域行为集（skill 无素材格式约定，此形态见件 1 §七体感 2）。素材是事件/命令的**来源线索不是词条来源**；素材内概念同样必须锚词条。

```
订单域行为清单（演示素材 v1）
B1 提交订单：顾客提交订单，系统生成订单编号与下单时间；订单至少含一行订单项（行数量、行单价），订单行为空则拒收。
B2 支付扣款成功：支付网关回调扣款成功，支付单落支付金额，支付状态由待支付变已支付；订单随之由待支付变已支付。
B3 取消订单：顾客取消尚未支付的订单，订单关闭；已支付订单不可取消。
B4 优惠券抵扣：顾客提交订单时可使用优惠券抵扣部分货款。（「优惠券」词条集合无对应词条——三分流①演示项）
B5 改货：必要时允许顾客改货。（表述含糊——三分流③演示项）
```

## 轮 1 · 事件时间轴（`tmp/ddd/order/round-1-event-timeline.yaml`）

```yaml
# 工序中间件·轮 1/4：事件时间轴（ddd-modeler 工序；工作件不入仓——票 53 走查实跑件）
round: 1
artifact: event-timeline
domain: order
input_of_round: fixtures/ddd-modeler/inputs/ontology/order（本体模型产物：m1-object-model+glossary-model+manifest，schema_check 全绿 exit 0）
events:
  - event: ORDER_SUBMITTED
    position: 顾客提交订单成功后（订单生成时点）
    terms:
      - GLS-ORDER-001
      - GLS-ORDER-002
      - GLS-ORDER-003
      - GLS-ORDER-004
    origin: 行为清单 B1「提交订单」——订单生成订单编号与下单时间，至少含一行订单项（行数量、行单价）
  - event: PAYMENT_SUCCEEDED
    position: 支付网关回调扣款成功后
    terms:
      - GLS-ORDER-006
      - GLS-ORDER-007
    origin: 行为清单 B2「支付扣款成功」——支付单落支付金额，支付状态由待支付变已支付
  - event: ORDER_CANCELLED
    position: 取消受理后（仅限未支付订单）
    terms:
      - GLS-ORDER-001
    origin: 行为清单 B3「取消订单」——未支付订单可取消；已支付拒取消（不变量候选）
open_questions:
  - item: B4「优惠券抵扣」——「优惠券」在词条集合（GLS-ORDER-001..007）无对应词条，概念缺词条
    routing: 分流①回 onto-modeler 工序补本体词条，本工序挂起等词条进仓（不就地造 ID）
  - item: B5「改货：必要时允许顾客改货」——改什么/何时/何约束未定，素材自身含糊
    routing: 分流③进《待人审清单》，Owner 明确后再锚定
```

## 轮 2 · 命令清单（`tmp/ddd/order/round-2-commands.yaml`）

```yaml
# 工序中间件·轮 2/4：命令清单（ddd-modeler 工序；工作件不入仓——票 53 走查实跑件）
# 新鲜上下文纪律：本轮新开上下文，只喂轮 1 定稿（tmp/ddd/order/round-1-event-timeline.yaml）。
round: 2
artifact: commands
domain: order
input_of_round: tmp/ddd/order/round-1-event-timeline.yaml
commands:
  - command: 提交订单
    actor: 顾客
    triggers_event: ORDER_SUBMITTED
    terms:
      - GLS-ORDER-001
      - GLS-ORDER-002
      - GLS-ORDER-003
      - GLS-ORDER-004
  - command: 确认支付回调
    actor: 支付网关（外部系统回调）
    triggers_event: PAYMENT_SUCCEEDED
    terms:
      - GLS-ORDER-006
      - GLS-ORDER-007
  - command: 取消订单
    actor: 顾客
    triggers_event: ORDER_CANCELLED
    terms:
      - GLS-ORDER-001
open_questions: []   # 轮 1 分流项（B4 缺词条/B5 含糊）原地挂起，不流入本轮主体清单
```

## 轮 3 · 聚合候选（`tmp/ddd/order/round-3-aggregate-candidates.yaml`）

```yaml
# 工序中间件·轮 3/4：聚合候选（ddd-modeler 工序；工作件不入仓——票 53 走查实跑件）
# 新鲜上下文纪律：本轮新开上下文，只喂轮 2 定稿（tmp/ddd/order/round-2-commands.yaml）。
# 只列候选不合并——切碎了没关系，轮 4 收口。
round: 3
artifact: aggregate-candidates
domain: order
input_of_round: tmp/ddd/order/round-2-commands.yaml
candidates:
  - candidate: AGG-ORDER-001        # 订单（M1 AGGREGATE_ROOT）
    member_terms:
      - GLS-ORDER-001
      - GLS-ORDER-002
    consistency_anchor: 订单编号与下单时间在订单生成时一次成型、共同在位——无编号的订单不成立
  - candidate: AGG-ORDER-002        # 订单项（M1 亦标 AGGREGATE_ROOT——候选线索照实列，合并裁决在轮 4）
    member_terms:
      - GLS-ORDER-003
      - GLS-ORDER-004
    consistency_anchor: 行数量与行单价必须同时成立，且随所属订单同生共死（B1「至少一行」的存在依赖）
  - candidate: AGG-ORDER-003        # 支付（M1 AGGREGATE_ROOT）
    member_terms:
      - GLS-ORDER-006
      - GLS-ORDER-007
    consistency_anchor: 支付金额与支付状态必须同时落库同时可读——金额与状态不同步即对账事故（B2）
open_questions: []
```

## 轮 4 · 合并追问记录（`tmp/ddd/order/round-4-merge-review.yaml`）

```yaml
# 工序中间件·轮 4/4：合并追问记录（必走步；ddd-modeler 工序；工作件不入仓——票 53 走查实跑件）
# 新鲜上下文纪律：本轮新开上下文，只喂轮 3 定稿（tmp/ddd/order/round-3-aggregate-candidates.yaml）。
# 追问话术："这几个候选是否必须同时成立/同时改？"——判据事实作答；Owner 不在场，
# 裁决复核权留 Owner（decided_by: 待 Owner，逐条入《待人审清单》），不擅自免问也不机械拆分。
round: 4
artifact: merge-review
domain: order
input_of_round: tmp/ddd/order/round-3-aggregate-candidates.yaml
merge_questions:
  - question: 候选 AGG-ORDER-001（订单）与 AGG-ORDER-002（订单项）是否必须同时成立/同时改？
    candidates:
      - AGG-ORDER-001
      - AGG-ORDER-002
    answer: 是——B1 订单至少含一行订单项（存在依赖）；轮 2 命令全量核对无任何脱离订单单独修改订单项的命令；「有单无行/有行无单」的中间态不被 B1 接受
    verdict: merge
    merged_into: AGG-ORDER-001
    decided_by: 待 Owner   # 判据事实满足 merge；走查形态 Owner 不在场，粒度裁决复核入《待人审清单》
  - question: 候选 AGG-ORDER-001（订单）与 AGG-ORDER-003（支付）是否必须同时成立/同时改？
    candidates:
      - AGG-ORDER-001
      - AGG-ORDER-003
    answer: 否——时间轴上订单先成立（B1）、支付后发生（B2），订单可长期处于待支付态，二者分别成立；「订单随支付变已支付」是跨聚合事实，走事件串联（PAYMENT_SUCCEEDED→订单）不共享字段
    verdict: keep-apart
    decided_by: 待 Owner   # 判据事实支持拆分；复核入《待人审清单》
resolved_candidates:
  - aggregate: AGG-ORDER-001
    absorbed:
      - AGG-ORDER-002
  - aggregate: AGG-ORDER-003
    absorbed: []
pending_questions: []
```
