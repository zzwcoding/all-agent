# OMF 规范字段级摘要（ontology_modeling_framework v6 / v9）

> 供 All-agent 设计本体仓 Schema（Git+YAML、本体为唯一真源、多输入多输出）参考。
> 本文为**字段级事实提取**，不做评价。
>
> 信源（一手原文，2026-09-17 抓取）：
> - `ontology_modeling_framework_v6.md`（v6.0，11 模型，144,107 字符）——下文引用记为 `v6 §x.y`
> - `ontology_modeling_framework_v9.md`（v9.0，7 模型，63,818 字符）——记为 `v9 §x.y`
> - 仓库 `README`（版本演进对照、文件约定、建模顺序）——记为 `README §x`
> - 仓库地址：https://github.com/sharptoolbox/ontology_modeling_framework

---

## 0. 总览：版本与模型矩阵

模型清单矩阵（`README §五`；v6/v9 正文 §1.2 逐模型确认）：

| 编号 | 模型 | v6 | v9 | YAML 元文件名 |
|---|---|---|---|---|
| M1 | 对象模型 Object Model | ✓ | ✓ | `m1-object-model.yaml` |
| M2 | 行为模型 Behavior Model | ✓ | ✓（syncTriggers 替代 producedEvents） | `m2-behavior-model.yaml` |
| M3 | 规则模型 Rule Model | ✓ | ✓（移除 EVENT_DRIVEN） | `m3-rule-model.yaml` |
| ME | 事件模型 Event Model | ✓ | — | `me-event-model.yaml` |
| M4 | 场景模型 Scenario Model | ✓ | — | `m4-scenario-model.yaml` |
| M5 | 主体模型 Actor Model | ✓ | ✓（移除 ExternalEntity） | `m5-actor-model.yaml` |
| M6 | 流程模型 Flow Model | ✓ | ✓（同步编排） | `m6-flow-model.yaml` |
| M7 | 查询统计与报表模型 | ✓ | ✓（参考 SQL 可选） | `m7-report-model.yaml` |
| MU | UI 模型 UI Model | ✓ | ✓（重定义层级） | `mu-ui-model.yaml` |
| MM | 对象-数据表映射模型 | ✓ | — | `m-mapping-model.yaml` |
| MI | 接口模型 Interface Model | ✓ | — | `mi-interface-model.yaml` |

每个 YAML 元文件的公共顶层字段：`model_type`（如 OBJECT/BEHAVIOR/RULE/EVENT/SCENARIO/ACTOR/FLOW/REPORT/UI/MAPPING/INTERFACE）、`version`、`domain`（各模型 YAML 模板第一行，v6/v9 各章示例）。

注意：v6 文件头写"九大模型元文件"，实际 §1.2 表格为 11 行——规范自身的已知不一致（`README §十二`）。

---

## 1. M1 对象模型

顶层结构（v6 §2.4 / v9 §2.4 YAML 模板）：`aggregates[]`、`data_dictionaries[]`、`aggregate_associations[]`。

### 1.1 聚合根 AggregateRoot（v6 §2.3.1 / v9 §2.3.1）

| 字段 | 类型 | 必填 | 说明/枚举 |
|---|---|---|---|
| id | String/UUID | ✓ | 全局唯一，建议 UUID v4 |
| name | String | ✓ | 中文名，需唯一 |
| alias | String | ✓ | 英文标识符，用于代码映射 |
| description | String | 可选 | |
| aggregateType | Enum | ✓ | 固定 `AGGREGATE_ROOT` |
| lifecycle | Enum[] | 可选 | 生命周期状态列表，如 [草稿, 生效, 注销] |
| attributes | Attribute[] | ✓ | |
| entities | Entity[] | 可选 | 子实体（组合） |
| valueObjects | ValueObject[] | 可选 | |
| invariants | Invariant[] | 可选 | |
| tags | String[] | 可选 | 如 [核心域, 支撑域] |

### 1.2 子实体 Entity（v6 §2.3.2）

name、alias、description、`localId`（聚合内唯一标识字段名）、attributes、`cardinality`（枚举 ONE / ZERO_OR_ONE / ONE_OR_MORE / ZERO_OR_MORE）、`cascadeDelete`（Boolean，默认 true）。

### 1.3 值对象 ValueObject（v6 §2.3.3）

name、alias、description、attributes、`immutable`（默认 true）、`equalityFields`（String[]，判等字段）。

### 1.4 属性 Attribute（v6 §2.3.4 / v9 §2.3.4，两版字段一致）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| name | String | ✓ | 英文 camelCase |
| label | String | ✓ | 中文展示名 |
| type | Enum(DataType) | ✓ | `String / Integer / Decimal / Date / DateTime / Boolean / Enum / Money / ValueObject / AggregateRootRef / DictionaryRef` |
| required | Boolean | 可选 | |
| unique | Boolean | 可选 | 仅对聚合根属性有效 |
| defaultValue | Any | 可选 | |
| enumValues | String[] | type=Enum 时 | |
| valueObjectRef | String | type=ValueObject 时 | 引用值对象名称 |
| targetAggregate | AggregateRef | type=AggregateRootRef 时**必填** | 指向目标聚合根 ID；禁止只在 description 里写引用关系 |
| dictionaryRef | DictionaryTypeRef | type=DictionaryRef 时**必填** | 含 `dictionaryId` + `typeCode`；不得同时声明 enumValues |
| refRules | AttributeRule[] | 可选 | 只依赖当前属性值的局部规则 |

`AggregateRootRef` = 存另一个聚合根 ID 的标量属性（不是内嵌对象/外键对象）；v9 明确其在 MU 中显示为"跳选框（POPUP_SELECT）"控件，`DictionaryRef`/`Enum` 显示为下拉框（v9 §2.3.4）。

AttributeRule / refRules（v6 §2.3.4）：`name`、`description`、`expression`（用 `value` 表示当前属性值）、`violationMessage`、`enforcedAt`（枚举 ON_CREATE / ON_UPDATE / ON_DELETE / ALWAYS）。

### 1.5 规则分层判定（v6 §4.1.1 / v9 §4.1.1，逐级下沉）

内置字段（required/unique 等）→ 只依赖当前属性值 → `Attribute.refRules` → 只依赖同聚合内部 → `Aggregate.invariants` → 跨对象/跨行为/复用 → M3 规则。

### 1.6 数据字典（v6 §2.3.5 / v9 §2.3.5）

- 数据字典对象：`id`、`name`、`description`、`types[]`（v9 直接从 types 起列）
- 字典类型 DictionaryType：`typeCode`（对象内唯一稳定编码）、`typeName`、`description`、`items[]`
- 字典项 DictionaryItem：`code`（稳定存储值）、`label`（显示文本，可改）、`enabled`（已用项停用不删除）、`sortOrder`、`description`（v6 有，v9 无）
- 约束：**平级结构，不定义 parentCode**；被引用后重命名/删除须影响分析（v6 §2.3.5）

### 1.7 聚合不变性 Invariant（v6 §2.3.6）

`name`、`expression`（可跨聚合内子实体/值对象）、`violationMessage`、`enforcedAt`（同上四枚举）。

### 1.8 聚合间关联 AggregateAssociation（v6 §2.3.7）

| 字段 | 类型 | 枚举 |
|---|---|---|
| id | String | 关联唯一标识（示例 `ASSOC-001`） |
| sourceAggregate / targetAggregate | AggregateRef | M1 聚合根 ID |
| associationType | Enum | `REFERENCE / DEPENDENCY` |
| sourceRole / targetRole | String | 端角色名 |
| cardinality | Enum | `ONE_TO_ONE / ONE_TO_MANY / MANY_TO_ONE / MANY_TO_MANY` |
| referenceField | String | 存目标聚合根 ID 的字段名 |

---

## 2. M2 行为模型

### 2.1 行为 Behavior（v6 §3.2.1 vs v9 §3.2.1）

| 字段 | 类型 | v6 | v9 | 说明 |
|---|---|---|---|---|
| id | String | ✓ | ✓ | 建议格式 `{EntityAlias}_{ActionName}`，如 `Order_ConfirmPayment` |
| name | String | ✓ | ✓ | 中文动宾短语 |
| ownerEntity | EntityRef | ✓ | ✓ | 行为所属对象（M1 聚合根 ID） |
| behaviorType | Enum | ✓ | ✓ | v6：`COMMAND / QUERY / EVENT_HANDLER`；v9：`COMMAND / QUERY` |
| triggerType | Enum | ✓ | ✓ | v6：`USER_ACTION / SYSTEM / EVENT / EXTERNAL`；v9：`USER_ACTION / SYSTEM` |
| preconditions | Condition[] | ✓ | ✓ | 谓词表达式，全部满足才可执行 |
| postconditions | StateChange[] | ✓ | ✓ | `{field, setValue}`，如 `order.status = '已支付'` |
| appliedRules | RuleRef[] | ✓ | ✓ | 调用的 M3 规则 |
| requiredPermissions | PermissionRef[] | ✓ | ✓ | 引用 M5 权限 |
| producedEvents | EventRef[] | ✓ | **移除** | v6 仅放事件 ID 引用，完整定义在 ME（v6 §3.2.2） |
| syncTriggers | SyncTrigger[] | — | **新增** | v9 的跨对象联动载体（v9 §3.2.2） |
| queryReportRef | QueryReportRef | ✓ | ✓ | 仅 `behaviorType=QUERY` 且绑定 M7 对象时填；与 M7 `behaviorRef` **严格一对一** |
| uiEventRefs | EventRef[] | 可选（v5 新增） | — | 反向追溯：调用本行为的 MU 事件（v6 §3.4.1） |

### 2.2 SyncTrigger（v9 §3.2.2，v9 特有）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| ruleRef | RuleRef | 可选 | 填写=规则满足才触发；必须引用 M3 规则，规则只判断不改状态 |
| behaviorRef | BehaviorRef | **必填** | 同步调用的下游行为 |
| description | String | 可选 | |

约束（v9 §3.2.2）：省略 ruleRef=无条件联动；同一行为可多条、按声明顺序执行；**下游行为必须作用于另一个独立聚合**（禁止同聚合自我联动）；联动失败语义必须在 postconditions 或 M6 中明确，禁止隐含吞异常。查询行为 `syncTriggers` 必须为空（v9 §3.3 说明）。

---

## 3. M3 规则模型

### 3.1 通用规则属性（v6 §4.3.1 / v9 §4.3.1）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | String | 建议 `RULE-{Domain}-{Seq}` |
| name | String | |
| ruleType | Enum | v6：`VALIDATION / CALCULATION / DERIVATION / TRANSFORMATION / RISK / EVENT_DRIVEN`（6 类）；v9：前 5 类（移除 EVENT_DRIVEN） |
| description | String | |
| inputParams | Param[] | 见 3.2 |
| outputType | DataType | 事件驱动规则通常 Boolean 或结构化判断结果 |
| expression | String | 伪代码或 DSL，不限定语言 |
| reusedBy | BehaviorRef[] | 引用本规则的行为列表（反向追踪） |
| externalEngine | String | 可选；外部规则引擎名（如 Drools, OPA） |
| version | String | 规则独立版本管理 |

### 3.2 输入参数 Param（v6 §4.3.3）

`name`、`type`、`sourceField`（如 `"order.totalAmount"` 或 `"event.payload.contractId"`）、`required`、`description`。

### 3.3 事件驱动规则专属字段（v6 §4.3.2，v9 已移除）

`triggerType: EVENT`、`subscribedEvents[]`、`triggeredBehaviors[]`（判断满足后直接触发的行为）、`producedEvents[]`（可选，仅新事实时用）、`eventTriggerCondition`、`executionMode`（SYNC/ASYNC）、`timeout`（如 `PT5S`）。

强制语义边界（v6 §4.1 / v9 §1.4）：**事件只答"发生了什么"、规则只答"条件是否满足"、行为只答"改变什么状态"**；禁止把条件结论写进事件或源行为。

---

## 4. ME 事件模型（仅 v6，v9 移除）

### 4.1 事件 Event（v6 §5.4.1）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| eventId | String | ✓ | 建议格式 `{Entity}.{State}_{Past}`，如 `Order.PaymentConfirmed`（过去时态强制，v6 §5.9.1） |
| eventName | String | ✓ | 中文 |
| description | String | ✓ | 只解释事实本身，不得含资格判断/后续结论（v6 §5.1.1） |
| producerType | Enum | ✓ | `BEHAVIOR / RULE`（单一生产者原则，v6 §5.3.1） |
| producerBehaviorRef | BehaviorRef | producerType=BEHAVIOR 时必填 | |
| producerRuleRef | RuleRef | producerType=RULE 时必填 | |
| producerEntityRef | EntityRef | 可选 | 用于可视化 |
| triggerCondition | String | ✓ | 只允许 `postcondition.success == true` 这类事实描述（v6 §5.1.1） |
| payload | PayloadField[] | ✓ | |
| subscribers | Subscriber[] | 有下游影响时必填 | 订阅者只能是行为或规则 |
| ordering | Enum | ✓ | `AT_LEAST_ONCE / EXACTLY_ONCE / BEST_EFFORT` |
| version | String | 可选 | 事件 schema 演进 |
| uiEventPath | ScreenRef[] | 可选（v5） | UI 入口事件追溯（v6 §5.11.1） |

### 4.2 订阅者 Subscriber（v6 §5.4.2）

`subscriberType`（BEHAVIOR/RULE）、`subscriberBehaviorRef` / `subscriberRuleRef`（二选一必填）、`subscriberEntityRef`（仅行为订阅者）、`priority`（Integer，越小越先，可选）、`filterCondition`（可选）。

### 4.3 载荷 PayloadField（v6 §5.4.3）

`name`、`type`（String/Integer/Decimal/Date/DateTime/Boolean/Object）、`required`、`description`、`sourceField`（如 `"order.orderId"`）。

### 4.4 跨对象 CUD 事件识别原则（v6 §5.1.2，强制）

源对象完成 CUD/状态变更后还要驱动**另一个独立对象**做 CUD/状态流转/流程启动 → 必须拆为"源对象行为 → 事实事件 → 消费规则或行为 → 目标行为"；禁止源行为直接跨聚合写目标。不识别为事件：仅查询、仅改自身属性、同聚合内子实体修改、仅格式转换/展示/校验。

---

## 5. M4 场景模型（仅 v6，v9 移除）

### 5.1 事件协同场景（v6 §6.3.1）

顶层根集合为 `event_scenarios[]`（评审清单明确禁止 `business_processes`/`use_cases` 层，v6 §14.2）。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | String | 建议 `SCN-{DOMAIN}-{NNN}` |
| name / description | String | |
| sourceObjectRef | AggregateRef | 事件源聚合根 |
| targetObjectRefs | AggregateRef[] | 被影响的目标聚合根（须与源不同） |
| triggerEventRef | EventRef | 启动场景的事实事件 |
| preconditions / postconditions | String[] | |
| steps | ScenarioStep[] | 语义链 |
| uiTriggerScreen | ScreenRef | 可选（v5），启动场景的 MU 屏幕（v6 §6.6.1） |

### 5.2 场景步骤 ScenarioStep（v6 §6.3.2）

`stepId`、`stepType`（**仅三类**：`BEHAVIOR_CALL / EVENT_EMIT / RULE_EVALUATE`）、`behaviorRef` / `eventRef` / `ruleRef`（按 stepType 对应必填）、`nextSteps[]`（允许一个事件连多个独立消费者）。

**禁止**（v6 §6.3.2）：`GATEWAY`、`USER_TASK`、`APPROVAL_TASK`、`SUB_FLOW_CALL`、角色分配——一律进 M6。

---

## 6. M5 主体模型

### 6.1 参与者 Actor（v6 §7.3.1 vs v9 §5.3.1）

| 字段 | 类型 | v6 | v9 |
|---|---|---|---|
| actorId | String | ✓ | ✓ |
| actorType | Enum | `HUMAN / SYSTEM / EXTERNAL` | `HUMAN / SYSTEM`（移除 EXTERNAL） |
| roles | RoleRef[] | ✓ | ✓ |
| attributes | Map | ✓（ABAC 条件用，如 department/level） | ✓ |
| externalContract | Contract | ✓（仅 EXTERNAL） | **移除** |

externalContract 子字段（v6 §7.3.1）：`protocol`（REST/SOAP/MQ/gRPC/SFTP）、`dataFormat`（JSON/XML/CSV/Binary）、`authMethod`（API_KEY/OAuth2/mTLS/NONE）、`timeoutMs`（Integer）。

### 6.2 角色 Role（v6 §7.3.2 / v9 §5.3.2）

`roleId`、`name`、`inheritsFrom`（RoleRef[]，支持多继承）、`permissions`、`permissionGroups`。角色是 M6 人工任务的**唯一**参与人类型；删除/重命名前必须分析 M6 的 roleRefs（v6 §7.3.2）。

### 6.3 权限 Permission（v6 §7.3.3 / v9 §5.3.3）

| 字段 | 类型 | 枚举 |
|---|---|---|
| permissionId | String | 建议 `PERM-{Domain}-{Action}` |
| targetType | Enum | `BEHAVIOR / ENTITY` |
| targetRef | Ref | 行为 ID 或实体 |
| dataScope | Enum | `ALL / OWN / DEPT / CUSTOM` |
| abacCondition | String | 如 `actor.dept == resource.dept` |
| uiControlledElements | ScreenRef[] | v5/v6 可选；控件级可用/可见控制（v6 §7.5.1；v9 移除 MU 元素级权限，仅 actionPoint.permissionRef） |

---

## 7. M6 流程模型

### 7.1 流程 Flow（v6 §8.3.1 / v9 §6.3.1，两版一致）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | String | 建议 `FLOW-{DOMAIN}-{NNN}` |
| name / description | String | |
| flowType | Enum | `COLLABORATION`（端到端协同流）/ `APPROVAL`（审批流） |
| businessObjectRefs | AggregateRef[] | 涉及的 M1 聚合根 |
| roleRefs | RoleRef[] | 流程中允许承担人工活动的角色集合 |
| trigger | FlowTrigger | 启动方式 |
| preconditions / postconditions | String[] | |
| startActivity | ActivityRef | **有且仅有一个** |
| endActivities | ActivityRef[] | ≥1，必须指向 END 活动 |
| activities | FlowActivity[] | |
| version | String | |

### 7.2 流程触发器 FlowTrigger（v6 §8.3.2 vs v9 §6.3.2）

`triggerType`：v6 `MANUAL / BEHAVIOR / EVENT / SCHEDULE / SUB_FLOW`；v9 `MANUAL / BEHAVIOR / SCHEDULE / SUB_FLOW`（移除 EVENT）。配套 `behaviorRef`、`eventRef`（v6）、`scheduleExpression`（Cron/伪代码）。

### 7.3 流程活动 FlowActivity（v6 §8.3.3 vs v9 §6.3.3）

| 字段 | 类型 | 说明 |
|---|---|---|
| activityId / name | String | |
| activityType | Enum | v6：`START / END / USER_TASK / APPROVAL_TASK / SYSTEM_TASK / BEHAVIOR_CALL / SCENARIO_CALL / SUB_FLOW_CALL / GATEWAY / EVENT_WAIT`；v9：移除 `SCENARIO_CALL`、`EVENT_WAIT` |
| roleRef | RoleRef | USER_TASK / APPROVAL_TASK **必填，只能引用 M5 roleId**（禁止 actorId/自由文本/具体用户，v6 §8.1） |
| behaviorRef | BehaviorRef | BEHAVIOR_CALL 或落领域行为的任务 |
| scenarioRef | ScenarioRef | v6 SCENARIO_CALL 引用 M4；从场景 triggerEventRef 衔接，不重复执行来源行为 |
| subFlowRef | FlowRef | SUB_FLOW_CALL；禁止直接或间接循环 |
| ruleRef | RuleRef | 可选；M3 规则作为进入/完成/网关判断条件 |
| conditionExpression | String | 流程局部条件（不需复用时） |
| approvalOutcomes | Enum[] | `APPROVE / REJECT / RETURN` |
| eventRef | EventRef | v6 EVENT_WAIT 等待的事件 |
| timeout | Duration | 可选 |
| nextActivities | ActivityRef[] | |
| branches | FlowBranch[] | GATEWAY 专用 |
| screenRef | ScreenRef | v5/v6 可选；活动↔MU 屏幕映射（v6 §8.7.1；v9 无此字段，v9 由二级菜单挂屏幕） |

### 7.4 流程分支 FlowBranch（v6 §8.3.4）

`branchName`、`ruleRef`、`conditionExpression`（与 ruleRef 至少填一个，默认分支除外）、`approvalOutcome`（APPROVE/REJECT/RETURN）、`targetActivity`、`isDefault`（同一网关最多一个默认分支）。

---

## 8. M7 查询统计与报表模型

### 8.1 查询报表对象 QueryReportObject（v6 §9.4.1 / v9 §7.4.1）

顶层根集合 `query_reports[]`。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | String | 查询 `QR-{DOMAIN}-{NNN}`；报表 `RPT-{DOMAIN}-{NNN}` |
| name / alias / description | String | alias 为 lowerCamelCase 稳定英文别名 |
| objectType | Enum | `DETAIL_QUERY / LIST_QUERY / STATISTICAL_QUERY / REPORT` |
| behaviorRef | BehaviorRef | **必填**，且必须指向 M2 `behaviorType=QUERY` 行为；双向严格一对一 |
| sourceObjects | QuerySource[] | |
| joins | QueryJoin[] | |
| parameters | QueryParameter[] | |
| conditions | QueryCondition[] | WHERE 语义 |
| resultColumns | ResultColumn[] | |
| groupBy | FieldExpression[] | |
| having | QueryCondition[] | 复用 QueryCondition，左侧通常为聚合表达式 |
| orderBy | OrderBy[] | `{expression, direction(ASC/DESC)}` |
| pagination | Pagination | `{enabled, defaultPageSize, maxPageSize}` |
| reportOptions | ReportOptions | 仅 `objectType=REPORT` 必填，其他类型应为空 |
| referenceSql | ReferenceSql | v6 必配；**v9 改为可选**（移除 MM 后物理表名在实现期确定，v9 §7.1） |
| version | String | |
| uiScreenRefs | ScreenRef[] | v5/v6 可选；触发预览/导出的 MU 屏幕（v6 §9.7.1） |

### 8.2 子结构

- **QuerySource**（v6 §9.4.2）：`objectRef`（M1 聚合根 ID）、`alias`（查询内唯一）、`entityPath`（可选，子实体路径）、`primary`（**有且仅有一个 true**）、`preAggregation`（可选：`groupBy[]` + `columns[]{name, sourceExpression, aggregateFunction}`）。
- **QueryJoin**（v6 §9.4.3）：`joinId`、`joinType`（`INNER/LEFT/RIGHT/FULL`）、`leftSource`/`rightSource`、`relationRef`（可选，引用 M1 `aggregate_associations.id`）、`conditionExpression`。
- **QueryParameter**（v6 §9.4.4）：`name`、`label`、`dataType`（String/Integer/Decimal/Boolean/Date/DateTime/Enum/DictionaryRef）、`required`、`defaultValue`、`allowedOperators`（v6：`EQ/NE/GT/GE/LT/LE/IN/NOT_IN/LIKE/BETWEEN/IS_NULL/IS_NOT_NULL` 共 12 个；v9 示例与前 10 个）、`sourceField`。
- **QueryCondition**（v6 §9.4.5）：`conditionId`、`leftExpression`、`operator`、`parameterRef`（与 fixedValue 二选一）、`fixedValue`、`logicalConnector`（`AND/OR`）、`group`（括号组合）、`skipWhenParameterEmpty`。
- **ResultColumn**（v6 §9.4.6）：`name`、`label`、`dataType`、`sourceExpression`、`aggregateFunction`（`NONE/COUNT/COUNT_DISTINCT/SUM/AVG/MIN/MAX`）、`format`、`nullable`、`visible`、`sortable`。
- **ReportOptions**（v6 §9.4.8）：`title`、`layout`（**仅支持 TABLE**）、`groupFields`、`subtotalFields`、`totalFields`、`exportFormats`（`XLSX/CSV/PDF`）、`emptyValueDisplay`。
- **ReferenceSql**（v6 §9.4.9）：`dialect`（PostgreSQL/MySQL/SQLServer/Oracle/SQLite 等）、`sql`（命名参数）、`parameterBindings[]{parameter, placeholder}`、`resultMappings[]{sqlColumn, resultColumn}`。

关键约束：M7 不是 BI 指标模型（无事实表/维度表/Cube/ETL，v6 §9.1）；**多个一对多来源同时聚合必须 preAggregation 预聚合，禁止 `SUM(DISTINCT amount)`**（v6 §9.6.17）；权限不进 M7，由 M2 requiredPermissions 承载（v6 §9.6.7）。

---

## 9. MU UI 模型（v6 与 v9 结构差异最大的模型）

### 9.1 v6 结构：屏幕为顶层 + callChain 调用链（v6 §10.2）

顶层：`screens[]` + `cross_cutting[]`。

**Screen**：`screenId`（建议 `frmXxx`）、`name`、`screenRef`（追溯证据，可选）、`layout`（ASCII，可选，§10.6）、`elements[]`、`navigation[]`、`events[]`。

**Element**：`id`、`type`（枚举 18 种：`TEXTBOX/COMBO/DATEPICKER/CHECKBOX/RADIO/BUTTON/TOOLBAR/MENU/LISTVIEW/GRID/TREEVIEW/TAB/TIMER/LABEL/IMAGE/FRAME/REPORT_VIEWER/OTHER`）、`label`、`io`（`I/O/I_O`，空=纯展示）、`required`（与 M1 对齐）、`enabled`、`dataBinding`（M1 聚合属性路径，如 `Contract.customerName`）、`dataSource`（M7 对象）、`permissionRef[]`（M5）、`refRules[]`（控件级，仅本元素内）。

**NavigationEdge**：`to`（目标 screenId，特殊值 `EXIT`）、`trigger`、`condition`。

**UIEvent**：`eventId`（建议 `{screenId}.{控件事件}`，如 `frmContract.tbrMenu_ButtonClick.SAVE`）、`name`、`source`（Click/KeyDown/快捷键等）、`permissions[]`、`preConditions[]`、`callChain[]`。

**CallChainStep**（v6 §10.2.5）：`step` 枚举 11 种：`VALIDATE / BEHAVIOR_CALL / EVENT_EMIT / SCENARIO_CALL / REPORT_CALL / QUERY_REPORT / NAVIGATE / CLOSE_MODAL / EXIT / DEVICE_SETUP / TOGGLE_INPUT`；配套字段 `rules[]`（VALIDATE→M3，必须无副作用）、`behaviorRef`、`eventRef`、`scenarioRef`、`reportRef`/`queryRef`、`to`、`targets[]`。

**CrossCuttingUI**：`id`（如 `UI.IDLE_MONITOR`）、`name`、`description`、`appliesTo[]`、`rules[]`、`target`、`shortcuts[]`。

### 9.2 v9 结构：层级导航 + 操作功能点（v9 §8.2）

顶层：`application{}` + `screens[]`。

**Application**：`name`、`menus[]`。
**Menu**：`menuId`、`name`、`children[]`（二级菜单**强制至少一个**）、`screenRef`（只有二级菜单挂屏幕，且与屏幕一对一，v9 §8.2.2）。
**Screen**：`screenId`、`name`、`screenType`（枚举 `SINGLE_FORM / LIST_MAINTENANCE / MASTER_DETAIL_FORM / QUERY_LIST`）、`layout`（ASCII，强制规则 §8.4）、`elements[]`、`actions[]`（替代 v6 的 events/callChain/navigation）。
**Element**：`id`、`type`（**收敛为 10 类**：`TEXTBOX/TEXTAREA/COMBO/DATEPICKER/POPUP_SELECT/NUMBER/CHECKBOX/BUTTON/GRID/LABEL`）、`label`、`io`、`required`、`dataBinding`、`dataSource`、`refRules[]`。
**ActionPoint**：`actionId`、`name`、`behaviorRef`（对应 M2 行为）、`actionType`（`BUTTON/SUBMIT/DRAFT/APPROVE/REJECT/RETURN`）、`permissionRef[]`。

**控件类型强制映射**（v9 §8.3）：`Date/DateTime→DATEPICKER`、`Enum→COMBO`、`DictionaryRef→COMBO`、`AggregateRootRef→POPUP_SELECT`（跳选框）、长文本 `String→TEXTAREA`、`Boolean→CHECKBOX`、其余标量 `→TEXTBOX/NUMBER`。

**布局强制规则**（v9 §8.4）：标签右对齐+控件左对齐；单表维护一行 2 控件（长文本占整行）；主从表主区一行 3 控件+从表表格内动态增删；查询列表条件区一行 3 控件+结果表格分页；**列表维护界面=工具栏+列表，新增/编辑弹 Modal，页面不直接展示表单**。

**审批双按钮规则**（v9 §8.5，强制）：带审批流的屏幕必须同时含 `actionType=DRAFT`（保存草稿，对应 `Contract_SaveAsDraft` 类行为）与 `actionType=SUBMIT`（提交，作为 M6 审批流 `trigger.behaviorRef` 启动入口）两个独立功能点；无审批流只需"保存"。

### 9.3 v6 的 callChain 顺序约束（v6 §10.2.5 / §10.4）

`VALIDATE` 必须在 `BEHAVIOR_CALL` 前；`EVENT_EMIT` 紧跟其生产者行为（= ME 事件 `producerBehaviorRef`）；`SCENARIO_CALL` 在触发事件之后；`REPORT_CALL/QUERY_REPORT` 在行为之后；`NAVIGATE` 收尾；查询类事件到 `QUERY_REPORT` 或 `BEHAVIOR_CALL(QUERY)` 即结束。

---

## 10. MM 对象-数据表映射模型（仅 v6，v9 移除）

顶层 `mappings[]`（v6 §11.3）。

**Mapping**：`id`（建议 `M-MAP-{对象代码}-{NNN}`）、`objectRef`（M1 对象）、`objectRole`（`AGGREGATE_ROOT/ENTITY/VALUE_OBJECT/ASSOCIATION`）、`objectName`（核对用中文名）、`tableMappings[]`、`mappingNote`。

**TableMapping**：`tableName`、`tableRole`（`MASTER/DETAIL/ASSOC/EXT/LOG/SNAPSHOT/VIEW`）、`primaryKey`（列引用）、`columnMappings[]`、`foreignKeys[]`、`tableNote`。

**ColumnMapping**：`attributeRef`（M1 属性路径，如 `Order.items[].itemId`）、`column`、`columnType`（方言类型如 VARCHAR2(32)）、`nullable`（与 M1 required 对齐）、`unique`、`defaultValue`、`isPrimaryKey`、`isForeignKey`、`fkTargetTable`、`fkTargetColumn`、`mappingNote`（冗余/派生/字典 code/前缀平铺说明）。

**ForeignKeyMapping**：`fkName`、`localColumn`、`targetTable`、`targetColumn`、`associationRef`（可选，引用 M1 聚合关联）。

约束（v6 §11.5）：复合对象一对象多表，DETAIL/EXT 表必须外键指向 MASTER；值对象二选一（前缀平铺或 JSON 列）不得混合；`AggregateRootRef` 映射为目标聚合根主表外键列；`DictionaryRef` 映射为存字典 code 的列；审计列/租户列/版本列可不反向映射到对象属性；索引/分区/迁移脚本不进 MM。

---

## 11. MI 接口模型（仅 v6，v9 移除）

顶层 `interfaces[]`（v6 §12.3.1）。

| 字段 | 类型 | 必填 | 说明/枚举 |
|---|---|---|---|
| interfaceId | String | ✓ | 建议 `INT-{NNN}`，全局唯一不重用 |
| name | String | ✓ | |
| interfaceType | Enum | ✓ | `PROVIDED`（本系统对外提供）/ `DEPENDENT`（本系统依赖） |
| providerSystem / consumerSystem | String | ✓ | |
| interfaceCategory | Enum | ✓ | `QUERY / COMMAND / NOTIFICATION` |
| businessPurpose / invokeScenario | String | ✓ | |
| inputParameters | FieldSpec[] | ✓ | |
| outputResult | FieldSpec[] | ✓ | 含嵌套对象/列表明细 |
| returnRule | String[] | ✓ | 无记录/参数错误/空结果集/失败处理 |
| relatedBehaviorRef | BehaviorRef[] | ✓ | PROVIDED 由 M2 `triggerType=EXTERNAL` 承接 |
| relatedEntityRef | EntityRef[] | 可选 | 字段口径来源（M1） |
| relatedReportRef | QueryReportRef[] | 可选 | 查询类接口口径来源（M7） |
| relatedEventRef | EventRef[] | 可选 | 事件型接口复用 ME 载荷，不得重复定义 |
| relatedExternalEntityRef | ExternalEntityRef[] | 可选 | M5 外部实体 |
| protocol | Enum | 可选 | `REST / SOAP / MQ / gRPC / SFTP / FILE` |
| dataFormat | Enum | 可选 | `JSON / XML / CSV / Binary` |
| authMethod | Enum | 可选 | `API_KEY / OAuth2 / mTLS / NONE` |
| timeoutMs | Integer | 可选 | |
| idempotency | Enum | 可选 | `IDEMPOTENT / NON_IDEMPOTENT` |
| contractNote | String | 可选 | |

**FieldSpec**（v6 §12.3.2）：`name`、`label`、`dataType`（String/Integer/Decimal/Boolean/Date/DateTime/Enum/ObjectRef/List）、`required`、`allowedValues[]`、`sourceField`（M1 属性路径）、`description`、`fields[]`（递归嵌套）。

约束（v6 §12.5）：`QUERY` 类接口不得改变状态；事件型接口载荷必须与 ME 一致；协议/格式/认证与 M5 externalContract 一致；变更保留编号并记 CHANGELOG.md。

---

## 12. 跨模型引用机制

### 12.1 ID 规范汇总（各模型元素规范"建议格式"条目）

| 模型元素 | ID 建议格式 | 来源 |
|---|---|---|
| M1 聚合根 | `AGG-XXX-001`（示例约定）；代码层 alias 英文驼峰 | v6 §2.4 示例 |
| M1 聚合关联 | `ASSOC-001` | v6 §2.4 示例 |
| M2 行为 | `{EntityAlias}_{ActionName}` | v6 §3.2.1 |
| M3 规则 | `RULE-{Domain}-{Seq}` | v6 §4.3.1 |
| ME 事件 | `{Entity}.{State}_{Past}` | v6 §5.4.1 |
| M4 场景 | `SCN-{DOMAIN}-{NNN}` | v6 §6.3.1 |
| M5 权限 | `PERM-{Domain}-{Action}` | v6 §7.3.3 |
| M6 流程 | `FLOW-{DOMAIN}-{NNN}` | v6 §8.3.1 |
| M7 查询/报表 | `QR-{DOMAIN}-{NNN}` / `RPT-{DOMAIN}-{NNN}` | v6 §9.4.1 |
| MU 屏幕 | `frmXxx`（与实现控件名一致）；元素=控件名 | v6 §10.2.1 |
| MU 事件 | `{screenId}.{控件事件}.{ACTION}` | v6 §10.2.4 |
| MM 映射 | `M-MAP-{对象代码}-{NNN}` | v6 §11.3.1 |
| MI 接口 | `INT-{NNN}` | v6 §12.3.1 |

### 12.2 ref 字段命名约定

- 跨模型引用一律**稳定 ID 引用**，字段名统一 `xxxRef` 后缀：`behaviorRef`、`ruleRef`、`eventRef`、`scenarioRef`、`subFlowRef`、`relationRef`、`queryReportRef`、`roleRef`、`targetAggregate`、`dataBinding`/`sourceField`（属性路径 `Aggregate.attribute` 或 `Aggregate.items[].attr`）。
- **双向一致**要求：M2 `producedEvents` ↔ ME `producerBehaviorRef`；M3 `subscribedEvents` ↔ ME `subscribers`；M3 `triggeredBehaviors` ↔ 下游行为；M2 `queryReportRef` ↔ M7 `behaviorRef`；M2 `requiredPermissions` ↔ M5 `permissions.targetRef`；M6 活动 `roleRef` ∈ 流程 `roleRefs`（各模型一致性约束节）。
- **反向追溯字段**（v5 起各模型新增，MU 侧权威声明、其他模型侧为可选一致性校验，v6 §1.4）：M1 `uiBindings`、M2 `uiEventRefs`、M3 `uiValidationRefs`、ME `uiEventPath`、M4 `uiTriggerScreen`、M5 `uiControlledElements`、M6 `screenRef`、M7 `uiScreenRefs`。
- 引用不得通过名称猜测；ID 变更必须展示影响范围并级联更新或阻止保存（v6 §8.6）。

---

## 13. 校验规则 / 门禁（规范声明的强制约束）

### 13.1 全局门禁

1. **可追溯门禁（两版都有，措辞不同）**：M2 中 `triggerType=USER_ACTION` 的行为必须能被至少一个 MU 事件（v6）/MU 操作功能点（v9）引用（反向可追溯、正向一致）；MU 引用的行为/规则/事件/场景/报表必须存在（v6 §1.3-7、§10.4-9；v9 §1.3-7、§8.7-5）。
2. **悬空引用（Dangling Reference）**由 CI 校验防止（v6 附录术语表）。
3. **原子性**：一个行为只操作一个对象；同聚合内变化不得用事件（v6 §5.1.2）或 syncTriggers（v9 §3.2.2）表达。
4. **语义边界**：事件只答事实、规则只答条件（且无副作用）、行为只答状态变更，三者不可合并表达（v6 §4.1、v9 §1.4）。
5. 每元文件自带 `version`；跨模型破坏性变更（实体删除、行为签名变更、事件载荷变更、接口口径变更）必须记 `CHANGELOG.md`（v6 §14.3、v9 §10.3）。

### 13.2 各模型要点（已在上文各节内标注，此处汇总高频门禁）

- M1：AggregateRootRef 必须填 targetAggregate；DictionaryRef 必须填 dictionaryRef 且不得与 enumValues 并存；字典 code/label/enabled 约束（v6 §2.3.4-2.3.5）。
- M2：EVENT 行为必须是某 ME 事件订阅者（v6 §3.4.2）；queryReportRef 只出现在 QUERY 行为且与 M7 严格一对一（v6 §3.3、v9 §3.4）。
- M3：被 MU 用作 VALIDATE 的规则必须无副作用（v6 §4.7.2）。
- ME：单一生产者；事件名过去时态；triggerCondition 仅事实描述；订阅者相互独立、无顺序假设；AT_LEAST_ONCE/EXACTLY_ONCE 订阅者须幂等（v6 §5.1.1、§5.9）。
- M4：仅三类步骤；EVENT_EMIT 前的行为=事件 producerBehaviorRef；EVENT_EMIT 后接的规则必须在 subscribedEvents 中且事件 subscribers 反向包含；RULE_EVALUATE 后的行为必须在规则 triggeredBehaviors 中（v6 §6.5）。
- M6：唯一 startActivity；USER_TASK/APPROVAL_TASK 只引用 M5 roleId 且角色∈流程 roleRefs；GATEWAY ≥2 分支、≤1 默认分支、非默认分支必须有判断条件；SUB_FLOW_CALL 调用图无环；审批必须显式覆盖 APPROVE/REJECT/RETURN，不得只有成功路径（v6 §8.5、v9 §6.5）。
- M7：有且仅有一个 primary=true 主对象；来源别名唯一；parameterBindings 必须覆盖 SQL 全部命名参数；resultMappings.resultColumn 必须引用已定义结果列；REPORT 必填 reportOptions、其他类型应为空；禁止外挂 M3 规则与权限字段（v6 §9.6）。
- MU：v6——callChain 顺序约束、layout 中 elementId 必须存在于 elements 且 io/required 对齐（v6 §10.4/§10.6.5）；v9——控件映射强制、布局规则强制、双按钮规则强制、二级菜单必挂屏幕（v9 §8.7）。
- MM：持久化对象至少一张表映射；attributeRef 可解析到 M1；DETAIL/EXT 外键指向 MASTER（v6 §11.5）。
- MI：interfaceId 全局唯一不重用；PROVIDED 必须有 M2 EXTERNAL 行为承接；QUERY 类不改状态（v6 §12.5）。

---

## 14. 版本演进要点（v1 → v9）

来源：README §二/§四/§六 + 各版本文件头。

| 版本 | 模型数 | 实质变化 |
|---|---|---|
| v1（2026-03） | 8 | 确立八模型 EDA 基线；ME 从行为模型独立为一等公民；**此时 M6=异常补偿模型（Saga/LIFO 补偿/重试退避），M7=质量约束模型（QoS/SLA 标注）** |
| v2（2026-03） | 8 | M1 升级为 DDD 聚合体系（聚合根/子实体/值对象/Invariant，替代 ReferentialConstraint）；M3 新增第 6 类 EVENT_DRIVEN 规则；ME Subscriber 升格为具名元素（可挂 priority/filterCondition） |
| v4（2026-07） | 8 | **M6/M7 换义**：M6 异常补偿→流程模型（COLLABORATION+APPROVAL）、M7 质量约束→查询统计与报表模型——理由：Saga/SLA 判为实现规格而非业务本体；M4 由"业务流程+业务用例双层"重构为"跨对象事件协同场景"（仅 BEHAVIOR_CALL/EVENT_EMIT/RULE_EVALUATE）；ME 增两条强制约束（事件事实性 §5.1.1、跨对象 CUD 识别 §5.1.2）；M3 增"局部规则 vs M3 规则"判定；M1 增数据字典；v4 直接承接 v2（v3 为未收录过程稿） |
| v5（2026-08） | 10 | 新增 MU UI 模型（入口层/追溯层，屏幕+元素+导航+事件+callChain）；新增 MM 映射模型；v4 划为"框架外"的 UI 与数据落地被收编；全部模型补 UI 反向追溯字段（§12.2 所列 8 个）；MU 补 ASCII 布局（§10.6，可选） |
| v6（2026-08） | 11 | 新增 MI 接口模型（系统边界契约层）；M5 externalContract 与 MI 对齐；最全版本 |
| v9（2026-08） | 7 | v6 的单体同步裁剪版：**移除 ME/M4/MM/MI 四模型**；M2 `syncTriggers` 替代 `producedEvents`（同步联动替代事件异步投递，SyncTrigger={ruleRef?, behaviorRef, description}）；M3 移除 EVENT_DRIVEN（规则一律被同步调用）；M5 移除 ExternalEntity（actorType 收敛 HUMAN/SYSTEM）；M6 移除事件触发/EVENT_WAIT/SCENARIO_CALL；M7 referenceSql 降为可选；**MU 完全重定义**为"总体界面→一级菜单→二级菜单→屏幕→操作功能点"层级，控件映射与 ASCII 布局从可选变强制，新增审批双按钮规则。编号不连续（缺 ME/M4/MM/MI）属有意保留（v9 §1.2 说明） |

**M6/M7 编号陷阱**：v1/v2 的 M6（异常补偿）、M7（质量约束）与 v4+ 的 M6（流程）、M7（查询报表）完全不同——引用他人"M6/M7"必须先确认版本（README §四）。

---

## 15. 文件与目录约定、建模顺序

### 15.1 目录约定（README §七；v6 §14.3；v9 §10.3）

```
v6: onto-cs/model/{projectId}/yaml/          v9: yaml/
  m1-object-model.yaml                        m1-object-model.yaml
  m2-behavior-model.yaml                      m2-behavior-model.yaml
  m3-rule-model.yaml                          m3-rule-model.yaml
  me-event-model.yaml                         m5-actor-model.yaml
  m4-scenario-model.yaml                      m6-flow-model.yaml
  m5-actor-model.yaml                         m7-report-model.yaml
  m6-flow-model.yaml                          mu-ui-model.yaml
  m7-report-model.yaml                        manifest.json（可选，路径必须相对）
  mu-ui-model.yaml
  m-mapping-model.yaml
  mi-interface-model.yaml
  manifest.json（可选）
```

- v1/v2 目录为 `models/{domain}/` + `models/shared/`（共享规则 `m3-shared-rules`、共享事件 `me-shared-events`、全局角色 `m5-global-roles`）；文件名在 v4 因 M6/M7 换义而改为 `m6-flow-model` / `m7-report-model`（README §七）。
- 通用约定：导入外部模型文件夹时复制进托管目录，不改外部源文件、不回写；manifest.json 缺失时按固定文件名识别，不得存绝对路径。

### 15.2 建模十二阶段（v6 §14.1；README §八）

v6 十二阶段（M5 分两次完善）：

1. M1 对象模型 → 2. M5（参与方和角色）→ 3. M3 规则 → 4. M2 行为 → 5. M7 查询报表 → 6. ME 事件 → 7. M5（权限）→ 8. M4 场景 → 9. M6 流程 → 10. MU UI（最后建，业务 ID 稳定后反向校验可追溯性）→ 11. MM 映射（DDL 稳定后）→ 12. MI 接口（接口需求明确后）。

v9 八阶段：M1 → M5（角色）→ M3 → M2（含 syncTriggers）→ M7 → M5（权限）→ M6 → MU。

---

## 16. 对我们的启示（All-agent 本体仓 Schema 设计）

1. **可直接抄的：元文件切分与命名**。一模型一 YAML、固定文件名（`m1-object-model.yaml` 式）、文件内 `model_type/version/domain` 三公共字段、`manifest.json` 可选且只存相对路径——与我们"Git+YAML、本体为唯一真源"完全同构，照搬可省设计成本（v6 §14.3）。
2. **可直接抄的：ID 前缀体系与 `xxxRef` 命名约定**（§12.1/§12.2）。前缀即类型标签，使 ref 字段无需 schema 外知识即可校验指向；双向一致对（producedEvents↔producer、queryReportRef↔behaviorRef 等）是现成的 lint 规则清单。
3. **可直接抄的：四层规则下沉判定**（M1 内置字段 → refRules → invariants → M3）。它解决"约束放哪"的 perennial 争论，建议原样写进我们的 Schema 设计文档（v6 §4.1.1）。
4. **可直接抄的： AggregateRootRef 必须显式 `targetAggregate`**——禁止"只在 description 写引用"，这让悬空引用校验可机械化（v6 §2.3.4）。
5. **要改的：MU 跟随 v9 而不是 v6**。v9 的"菜单树 + ActionPoint 直连行为"比 v6 的 callChain 简单一个量级，且控件类型强制映射（AggregateRootRef→POPUP_SELECT 等）可直接生成前端；All-agent 若面向 AI 生成，v9 MU 是更稳的蓝本（v9 §8）。
6. **要改的：ME/M4 的取舍要基于我们是否真有异步**。v9 证明了"无事件驱动"的裁剪是自洽的（syncTriggers 补位）；如果我们有多输入多输出的异步管线，保留 ME 但应采纳其两条硬约束（事件=过去时事实、triggerCondition 只许事实描述）来防止 LLM 生成时把规则塞进事件（v6 §5.1.1）。
7. **要改的：M7 的 referenceSql 放可选位**。v9 的处理正确——语义定义（source/conditions/resultColumns）是稳定层，SQL 是实现层；我们的本体仓不应让 SQL 成为真源（v9 §7.1）。
8. **要补的：本规范缺"多输入多输出"视角**。OMF 全部模型面向单一业务系统；我们作为"中台"需要为每个接入方（多输入）声明它消费哪些模型 slice——可借鉴 MI 的 PROVIDED/DEPENDENT 方向枚举（v6 §12.2）来表达"对外输出"与"依赖输入"，但接口粒度要换成数据契约粒度。
9. **要补的：字典与枚举治理**。v6 明确字典项"停用不删除、重命名须影响分析、参与生命周期的字典项修改须同步校验所有引用"——本体仓作为唯一真源时这条应升级为 Git 层面的 review 门禁（v6 §2.3.5）。
10. **要警惕的：版本语义断裂先例**。OMF 的 M6/M7 在 v4 换义造成沟通成本（README §四甚至专门写了一章）。我们给 schema 定版本时，字段换义宁可新增字段名（`flowType` 旧义保留 deprecated），不要复用字段名。
