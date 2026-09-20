# design/ddd · DDD 设计件格式真源

> 本文件是四类 DDD 设计件（聚合卡/领域事件表/聚合↔表映射/仓储边界声明）的**格式唯一真源**：
> 字段 schema + 语义说明 + 最小合法样例（样例内嵌本文件代码块，`design/ddd/` 下不放 `.yaml` 样例文件——真设计件随被建域由 ddd-modeler 工序产出，草案进仓走 MR）。
> 字段骨架来源：`references/ddd-as-code-digest.md` §1（战术层 DSL 的字段面：聚合根布尔标记/属性引用即类型/领域愿景）与 §4（聚合卡蓝图：不变量清单/纠正策略/访问途径/不变量→红灯三元组）。
> 消费方：ddd-modeler skill（票 52 起，工序=按本格式产草案）；`tools/ddd_check.py`（票 51 起，闸=按本格式五查）；归档闸 design-card 产物类（status 机判面，specs/archive-registry.json）。
> 变更：本文件是规范——改字段 schema 走票；闸与工序不得私改格式。

## 0. 通用约定（四类设计件共用）

1. **落盘位置**：`design/ddd/<域>/`，与 `ontology/<域>/` 平级同名（设计件只对已接入本体域存在——无词条不建模）。
2. **status 恰一处**：每个设计件 YAML 顶层恰一处行首 `status:` 行，合法值只有 `草案`/`已审`；翻转人=Owner（MR 人审）。这是归档闸机判面（按文件内首个 `status:` 行取值），因此**不得使用含 `status` 子串的其他键名**（如 `xxx_status`）。
3. **domain 字段**：顶层 `domain` 必填，值与 `ontology/<域>/` 目录名一致。
4. **引用即类型**：属性与事件载荷一律用 `- 词条ID` 引用语法（一杠一 ID）；词条 ID 真源=`ontology/`（本仓 ID 形态：`前缀-域-序号`，如 `GLS-BOHAI-001`；前缀即类型标签，登记于 `ontology/schema/model-deps.json`）。**不许裸列名、裸文本指代**——词条悬空=闸红。
5. **跨聚合只许 ID 引用**：跨聚合引用必须是对方聚合的 ID/词条 ID，不得内嵌对方属性（防 JOIN 暗桩）；聚合之间靠领域事件串联（见 §2），不共享字段。
6. **kind 判别字段**：顶层 `kind` 标明设计件类别（四值见各节）；一文件一类别。
7. **草案头声明**：草案头部固定语义「设计件=草案，业务裁决待 Owner 确认」——机器面由 `status: 草案` 承载，人读面由文件头注释行承载。

## 1. 聚合卡（kind: aggregate-card）

**语义**：一个聚合=一个一致性边界（"同时成立、同时改、不出现中间态"的数据放一个聚合，宁小勿大）。聚合卡是聚合的全部世界：数据（属性/实体/值对象）+ 行为（不变量唯一一份封在聚合方法）+ 事件 + 入口。一个事务只改一个聚合。

**字段 schema**：

| 字段 | 必填 | 语义 |
|---|---|---|
| `kind: aggregate-card` | 是 | 类别判别 |
| `status` | 是 | 草案/已审（通用约定 2） |
| `domain` | 是 | 所属域（通用约定 3） |
| `aggregate` | 是 | 聚合名（=聚合根对象词条 ID 或其短名） |
| `aggregate_root` | 是 | 布尔标记；聚合卡描述的即聚合根本体 |
| `domain_vision` | 否 | 一句话领域愿景（这张卡守什么） |
| `properties` | 是 | 聚合根直接属性表，逐条 `- 词条ID`（引用即类型） |
| `entities` | 是 | 聚合内实体（有身份有生命周期），各带自有 `properties` |
| `value_objects` | 是 | 聚合内值对象（无身份、按值判等、不可变），可为空列表 |
| `invariants` | 是 | **不变量三元组清单，不得为空**（防空壳聚合/贫血回潮）：`trigger`（触发操作）→ `expect_fail`（期望失败，DomainError 语义）→ `method`（指向聚合方法） |
| `corrective_policies` | 否 | 纠正策略：不变量/下游失败触发后的恢复动作（不静默吞） |
| `domain_events` | 否 | 本聚合产出的领域事件名表（详表落 §2 文件） |
| `ways_to_access` | 是 | 访问途径清单（仓储/工厂等入口），每条指向本聚合 |

**最小合法样例**（示意订单域，词条 ID 形态照本仓惯例）：

```yaml
# design/ddd/order/aggregate-order.yaml —— 头注释：设计件=草案，业务裁决待 Owner 确认
kind: aggregate-card
status: 草案                      # 唯一合法值 草案/已审，恰一处
domain: order
aggregate: AGG-ORDER-001          # 聚合根（订单）
aggregate_root: true
domain_vision: "订单与订单行必须同时成立、同时改，不出现中间态"
properties:
  - GLS-ORDER-001                 # 订单编号（引用即类型：词条 ID 即属性类型来源）
  - GLS-ORDER-002                 # 下单时间
entities:
  - entity: AGG-ORDER-002         # 订单行（有身份：行号）
    properties:
      - GLS-ORDER-003             # 行数量
      - GLS-ORDER-004             # 行单价
value_objects:
  - value_object: GLS-ORDER-005   # 收货地址（无身份、不可变）
invariants:                       # 不变量三元组：触发操作→期望失败→指向聚合方法
  - trigger: "submit（提交订单）"
    expect_fail: "订单行为空则拒，DomainError: EMPTY_ORDER"
    method: "Order.submit()"
  - trigger: "changeQuantity（改行数量）"
    expect_fail: "数量非正数则拒，DomainError: BAD_QUANTITY"
    method: "Order.changeQuantity()"
corrective_policies:
  - on: "DomainError: STOCK_SHORT"
    action: "订单转待补货态并发出 STOCK_SHORT 事件，不静默吞"
domain_events:
  - ORDER_SUBMITTED
ways_to_access:
  - repository: "OrderRepository" # 每聚合一个仓储（见 §4）
  - factory: "Order.place()"
```

## 2. 领域事件表（kind: domain-events）

**语义**：领域事件是聚合间唯一合法通道（跨聚合不直改、不 JOIN）。载荷引用词条 ID 不用裸列名。交付通道三档（起步=进程内发布订阅 / 认真做=事务内落事件表再轮询投递 / 拆分后=消息队列）——换通道不改架构，字段记录当前档位。一域一表文件。

**字段 schema**：

| 字段 | 必填 | 语义 |
|---|---|---|
| `kind: domain-events` | 是 | 类别判别 |
| `status` / `domain` | 是 | 通用约定 |
| `events[]` | 是 | 事件条目清单，不得为空 |
| `events[].event` | 是 | 事件名（大写下划线，动宾过去式语义） |
| `events[].producer` | 是 | 生产聚合（聚合 ID/短名，须与某聚合卡 `aggregate` 对应） |
| `events[].consumers` | 是 | 消费聚合清单（跨聚合才需要事件；单聚合内部流转不进表） |
| `events[].payload` | 是 | 载荷=词条 ID 表（逐条 `- 词条ID`，禁裸列名） |
| `events[].delivery` | 否 | 交付档位：`inprocess` / `outbox` / `mq`（缺省视为 inprocess） |

**最小合法样例**：

```yaml
# design/ddd/order/domain-events.yaml
kind: domain-events
status: 草案
domain: order
events:
  - event: ORDER_SUBMITTED
    producer: AGG-ORDER-001        # 生产聚合=订单
    consumers:
      - AGG-ORDER-010              # 消费聚合=库存（跨聚合拆事务+事件串联）
    payload:                       # 载荷=词条 ID 表
      - GLS-ORDER-001
      - GLS-ORDER-002
    delivery: outbox
```

## 3. 聚合↔表映射（kind: table-mapping）

**语义**：表是聚合的持久化投影——DDD 不破坏范式，聚合内多表=一个事务整体保存；聚合边界内的表只允许一个代码库写（谁的表谁写），跨聚合不 JOIN。列与词条双向可解析（防映射腐烂：表改了词条没改=闸红）。一域一映射文件。

**字段 schema**：

| 字段 | 必填 | 语义 |
|---|---|---|
| `kind: table-mapping` | 是 | 类别判别 |
| `status` / `domain` | 是 | 通用约定 |
| `mappings[]` | 是 | 聚合映射条目，须覆盖域内全部聚合卡 |
| `mappings[].aggregate` | 是 | 聚合（对应聚合卡） |
| `mappings[].tables[]` | 是 | 该聚合投影的表（可多表） |
| `mappings[].tables[].table` | 是 | 表名 |
| `mappings[].tables[].columns[]` | 是 | 列映射：`column`（列名）+ `term`（词条 ID），双向可解析 |
| `mappings[].write_side` | 否 | 写入方声明（谁的表谁写） |

**最小合法样例**：

```yaml
# design/ddd/order/table-mapping.yaml
kind: table-mapping
status: 草案
domain: order
mappings:
  - aggregate: AGG-ORDER-001
    tables:
      - table: t_order
        columns:
          - column: order_no
            term: GLS-ORDER-001    # 列↔词条，防映射腐烂
          - column: created_at
            term: GLS-ORDER-002
      - table: t_order_item        # 聚合内多表=一个事务整体保存
        columns:
          - column: quantity
            term: GLS-ORDER-003
    write_side: "仅订单模块代码库写；跨聚合不 JOIN"
```

## 4. 仓储边界声明（kind: repository-boundaries）

**语义**：仓储是聚合↔表映射的存取器——**每聚合一个仓储，只返回本聚合**（整体存取，不暴露逐字段 UPDATE；不返回他聚合对象，返回=绕过聚合边界）。一域一声明文件。

**字段 schema**：

| 字段 | 必填 | 语义 |
|---|---|---|
| `kind: repository-boundaries` | 是 | 类别判别 |
| `status` / `domain` | 是 | 通用约定 |
| `repositories[]` | 是 | 仓储条目，须与聚合卡一一对应（每聚合恰一个仓储） |
| `repositories[].repository` | 是 | 仓储名 |
| `repositories[].aggregate` | 是 | 管辖聚合（不得两仓储共管一聚合） |
| `repositories[].returns` | 是 | 返回面声明：仅本聚合（聚合+其内实体/值对象整体） |
| `repositories[].persistence` | 否 | 存取纪律：整体 save/load，不暴露逐字段更新 |

**最小合法样例**：

```yaml
# design/ddd/order/repository-boundaries.yaml
kind: repository-boundaries
status: 草案
domain: order
repositories:
  - repository: OrderRepository
    aggregate: AGG-ORDER-001      # 每聚合一个仓储
    returns: "仅本聚合（订单+订单行+值对象整体），不返回他聚合对象"
    persistence: "整体存取：save/load 整个聚合，不暴露逐字段 UPDATE"
```

## 5. 闸与工序的分工（本格式怎么被执行）

| 角色 | 承载 | 票 |
|---|---|---|
| 格式真源 | 本文件（改 schema 走票） | 票 50 |
| 确定性闸 | `tools/ddd_check.py` 五查：跨聚合仅 ID 引用 / 字段与载荷解析到词条 ID（悬空=红）/ 不变量三元组齐备 / 表映射无断链 / 重名与前缀合规；一次收集全部错误批量返回；粒度/完备性不硬闸，出「待人审清单」 | 票 51 |
| 工序 | ddd-modeler skill：本体模型+行为清单 → 四类设计件草案 → 闸自检 → 草案走 MR | 票 52 |
| 状态翻转 | `status: 草案 → 已审` 只由 Owner 在 MR 人审翻转（归档闸机判合法值） | 票 50 登记 |

> 票 51 判定补注（README 未覆盖的机判边界，落闸细则见 tools/ddd_check.py 头注与 lessons/52）：字段路径点号条目（`AGG-X.field` 形态）归 ddd-cross-agg-embed 判定——左段解析到**另一聚合卡**聚合主词条即红、本聚合自身结构引用合法、左段解析不到归 ddd-term-ref（红因不混）；词条集合=schema_check collect_definitions 同族口径（`id`/`*Id` 定义键、非 ref 键、值带 `model-deps.json` idPrefixes 注册前缀，覆盖 M1 聚合/DICT/GLS 词条）；事件生产者/消费者/仓储聚合不在设计件聚合集合属完备性，出「待人审清单」软节不硬闸（映射聚合缺席例外，硬闸 ddd-mapping）；文件不可判读（语法错/顶层非映射/kind 不在四类）报兜底码 ddd-file-kind，防坏文件静默逃逸五查。
