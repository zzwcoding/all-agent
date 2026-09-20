# 订单域走查 · 四类设计件成稿（票 53 走查留痕件 3 · 走查演示件）

> **本件是走查演示件，不是真产物**：真产物区=`design/ddd/<域>/`（design/ddd/README.md §0.1，与 ontology/<域>/ 平级，草案走 MR）。
> 本走查按票 53 裁决**不进真目录**——走查演示与真实产物分离（取舍见 lessons/54）；`ddd_check` 实跑 target 为工作区 `tmp/ddd/order-design/`（「等价物」口径），五份 YAML 原件在彼处（tmp/ 不入仓），本件为留痕全文，与原件一字一致。
> 五查结果：**全过 exit 0**（输出全文见件 1 步 4；软节一条转写件 4）。
> 每份头部固定注释「设计件=草案，业务裁决待 Owner 确认」；`status: 草案` 翻转只由 Owner（MR 人审）。

## 1. 聚合卡 · 订单（aggregate-order.yaml，吸收 AGG-ORDER-002）

```yaml
# 头注释：设计件=草案，业务裁决待 Owner 确认（design/ddd/README.md §0.7）
# 票 53 走查演示件：真产物区=design/ddd/<域>/，本目录是走查工作区 tmp/（演示与真产物分离，lessons/54）
kind: aggregate-card
status: 草案                      # 唯一合法值 草案/已审，恰一处；翻转只由 Owner（MR 人审）
domain: order
aggregate: AGG-ORDER-001          # 聚合根（订单；轮 4 追问裁决 merge 吸收 AGG-ORDER-002）
aggregate_root: true
domain_vision: "订单头与订单行必须同时成立、同时改，不出现中间态"
properties:
  - GLS-ORDER-001                 # 订单编号（引用即类型：词条 ID 即属性类型来源）
  - GLS-ORDER-002                 # 下单时间
entities:
  - entity: AGG-ORDER-002         # 订单项（有身份：行号；轮 4 合并追问裁决并入本聚合）
    properties:
      - GLS-ORDER-003             # 行数量
      - GLS-ORDER-004             # 行单价
value_objects: []                 # GLS-ORDER-005 收货地址词条在册但行为素材未提及——完备性待 Owner（人审清单）
invariants:                       # 不变量三元组：从轮 2 命令反推（trigger=命令、expect_fail=拒答条件、method=聚合方法）
  - trigger: "submit（提交订单，B1）"
    expect_fail: "订单行为空则拒，DomainError: EMPTY_ORDER"
    method: "Order.submit()"
  - trigger: "cancel（取消订单，B3）"
    expect_fail: "已支付订单拒取消，DomainError: ALREADY_PAID"
    method: "Order.cancel()"
domain_events:                    # 本聚合产出的事件名表（详表=domain-events.yaml；仅跨聚合者进表）
  - ORDER_SUBMITTED               # 单聚合内部流转（无跨聚合消费方，README §2 不进事件表）
  - ORDER_CANCELLED               # 同上
ways_to_access:
  - repository: "OrderRepository" # 每聚合一个仓储（README §4）
  - factory: "Order.submit()"
```

## 2. 聚合卡 · 支付（aggregate-payment.yaml，轮 4 keep-apart 独立）

```yaml
# 头注释：设计件=草案，业务裁决待 Owner 确认（design/ddd/README.md §0.7）
# 票 53 走查演示件：真产物区=design/ddd/<域>/，本目录是走查工作区 tmp/（演示与真产物分离，lessons/54）
kind: aggregate-card
status: 草案                      # 唯一合法值 草案/已审，恰一处；翻转只由 Owner（MR 人审）
domain: order
aggregate: AGG-ORDER-003          # 聚合根（支付；轮 4 追问裁决 keep-apart 独立聚合）
aggregate_root: true
domain_vision: "支付金额与支付状态同时落库同时可读，不出现半截支付"
properties:
  - GLS-ORDER-006                 # 支付金额
  - GLS-ORDER-007                 # 支付状态
entities: []
value_objects: []
invariants:
  - trigger: "confirm（支付回调确认，B2）"
    expect_fail: "支付金额与支付状态缺一则拒确认，DomainError: INCOMPLETE_PAYMENT"
    method: "Payment.confirm()"   # B2「落支付金额+状态待支付→已支付」同时落库的走查化读法，完备性待人审
domain_events:
  - PAYMENT_SUCCEEDED             # 跨聚合事件（订单随支付变已支付）——进事件表
ways_to_access:
  - repository: "PaymentRepository"
  - factory: "Payment.confirm()"
```

## 3. 领域事件表（domain-events.yaml）

```yaml
# 头注释：设计件=草案，业务裁决待 Owner 确认（design/ddd/README.md §0.7）
# 票 53 走查演示件：真产物区=design/ddd/<域>/，本目录是走查工作区 tmp/（演示与真产物分离，lessons/54）
kind: domain-events
status: 草案
domain: order
events:
  - event: PAYMENT_SUCCEEDED
    producer: AGG-ORDER-003        # 生产聚合=支付
    consumers:
      - AGG-ORDER-001              # 消费聚合=订单（B2：订单随支付待支付→已支付）
    payload:                       # 载荷=词条 ID 表，禁裸列名
      - GLS-ORDER-006
      - GLS-ORDER-007
    delivery: inprocess            # 起步档（README §2 三档；档位与部署阶段匹配性入人审清单）
# ORDER_SUBMITTED / ORDER_CANCELLED 未进本表：订单聚合内部流转、无跨聚合消费方（README §2）；
# 与票 51 出厂集样本（ORDER_SUBMITTED 消费方=支付，任务口径设定）差异的取舍见走查主记录 §六。
```

## 4. 聚合↔表映射（table-mapping.yaml）

```yaml
# 头注释：设计件=草案，业务裁决待 Owner 确认（design/ddd/README.md §0.7）
# 票 53 走查演示件：真产物区=design/ddd/<域>/，本目录是走查工作区 tmp/（演示与真产物分离，lessons/54）
kind: table-mapping
status: 草案
domain: order
mappings:                          # 表名来源：m1-object-model.yaml description（t_order/t_order_item/t_payment 投影）
  - aggregate: AGG-ORDER-001
    tables:
      - table: t_order
        columns:
          - column: order_no
            term: GLS-ORDER-001    # 列↔词条双向可解析，防映射腐烂
          - column: created_at
            term: GLS-ORDER-002
      - table: t_order_item        # 聚合内多表=一个事务整体保存
        columns:
          - column: quantity
            term: GLS-ORDER-003
          - column: unit_price
            term: GLS-ORDER-004
    write_side: "仅订单模块代码库写；跨聚合不 JOIN"
  - aggregate: AGG-ORDER-003
    tables:
      - table: t_payment
        columns:
          - column: amount
            term: GLS-ORDER-006
          - column: status
            term: GLS-ORDER-007
    write_side: "仅支付模块代码库写"
```

## 5. 仓储边界声明（repository-boundaries.yaml）

```yaml
# 头注释：设计件=草案，业务裁决待 Owner 确认（design/ddd/README.md §0.7）
# 票 53 走查演示件：真产物区=design/ddd/<域>/，本目录是走查工作区 tmp/（演示与真产物分离，lessons/54）
kind: repository-boundaries
status: 草案
domain: order
repositories:
  - repository: OrderRepository
    aggregate: AGG-ORDER-001      # 每聚合一个仓储（轮 4 定稿两聚合→两仓储）
    returns: "仅本聚合（订单+订单项整体），不返回他聚合对象"
    persistence: "整体存取：save/load 整个聚合，不暴露逐字段 UPDATE"
  - repository: PaymentRepository
    aggregate: AGG-ORDER-003
    returns: "仅本聚合（支付单整体），不返回他聚合对象"
    persistence: "整体存取：save/load 整个聚合，不暴露逐字段 UPDATE"
```
