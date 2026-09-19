# 本体仓 Schema · 七模型精简版 + GLS 术语扩展（v9 蓝本 + 运行期字段预留）

> 本文是本体 YAML 的 schema 文档（人读）；机读消费方两份：
> `model-registry.json`（模型注册表：camp/consumers/profiles/dependsOn）、`model-deps.json`（类型层依赖白名单 + ID 前缀表）。
> 执行闸：`tools/schema_check.py`（语义 CI L1–L4，断言表 `specs/schema_check.md` AC1–7 + 票 10 GLS-AC1–4）。
> 蓝本：OMF v9 七模型（references/omf-spec-digest.md §0/§16，下注 `v9 §x`）；裁剪决定均注明出处。
> GLS 术语模型为本仓自定义扩展（OMF v6/v9 均无，票 10 走"元模型错→框架版本演进"路由进 schema，演进账见 CHANGELOG.md）。

## 0. 定位与裁剪总则

- 一模型一 YAML、固定文件名、文件内 `model_type/version/domain` 三公共字段——照搬 OMF 文件约定（digest §16.1）。
- 一期不做 ME 事件/M4 场景/MM 映射/MI 接口（v9 同款裁剪：先同步世界，异步需求实证后回加，PRD F1；digest §16.6）。
- 字段换义宁可新增字段不复用旧名（digest §16.10）；被换义退役的字段名进 `model-registry.json` 各模型的 `lockedFields`，闸在 L4 强制（AC7）。
- 字典项停用不删除（digest §16.9）：`enabled: false` 保留行，删除走影响分析。

## 1. 公共字段与文件约定

每个模型元文件第一层必须有：

| 字段 | 必填 | 说明 |
|---|---|---|
| `model_type` | ✓ | 模型类型标签，取值见 model-registry.json 各模型 `modelType`（OBJECT/BEHAVIOR/RULE/ACTOR/FLOW/REPORT/UI/GLOSSARY） |
| `version` | ✓ | 模型元文件版本（语义化三段，引号包裹） |
| `domain` | ✓ | 所属域标识，与域 manifest.json 的 `domain` 一致 |

文件命名固定：`m1-object-model.yaml` / `m2-behavior-model.yaml` / `m3-rule-model.yaml` / `m5-actor-model.yaml` / `m6-flow-model.yaml` / `m7-report-model.yaml` / `mu-ui-model.yaml` / `glossary-model.yaml`（v9 §10.3；GLS 照 `mu-ui-model.yaml` 非数字先例，票 10）。文件名与 `model_type` 的对应真源 = model-registry.json 各模型 `yamlFile`，错挂 = L1 违规（票 10 AC4）。

每个域一个目录（`ontology/<域>/`），目录内必须有 `manifest.json`：

```json
{"domain": "bohai", "label": "渤海油田产量域", "profile": "v9-full", "schemaVersion": "1.0.0"}
```

`profile` 引用 model-registry.json 的 profile 组合名；未启用的模型文件出现 = L4 违规（AC6）。

**元素级运行期预留字段（全模型可选，一期只定义不消费，PRD F1「运行期四外衣」）**：
- 元素级 `version`（String）：元素独立版本，供运行期消费方做兼容判断。
- 元素级 `validFrom`（ISO 日期）：有效期起点，供运行期判断"当前可消费版本"。
- 预留字段闸只做"存在即放行"，不做语义消费——防止 schema 二次断裂（R7、digest §16.10）。

## 2. ID 前缀与 ref 命名约定

**前缀即类型标签**：所有元素 ID 必须带模型前缀，使 ref 无需 schema 外知识即可机械校验指向（digest §16.2）。前缀→模型映射的真源在 `model-deps.json` 的 `idPrefixes`：

| 模型 | ID 前缀 | 元素 |
|---|---|---|
| M1 | `AGG-` / `ASSOC-` / `DICT-` | 聚合根 / 聚合关联 / 数据字典 |
| M2 | `BH-` | 行为（本仓约定 `BH-{域}-{动宾}`；OMF 的 `{EntityAlias}_{ActionName}` 无前缀不可机械校验，此为本仓对 OMF 的显式偏差） |
| M3 | `RULE-` | 规则（`RULE-{域}-{Seq}`） |
| M5 | `ACTOR-` / `ROLE-` / `PERM-` | 参与者 / 角色 / 权限（`PERM-{域}-{Action}`） |
| M6 | `FLOW-` | 流程 |
| M7 | `QR-` / `RPT-` | 查询 / 报表 |
| MU | `SCR-` | 屏幕（OMF 建议 `frmXxx`；同理改用可校验前缀，此为第二处显式偏差） |
| GLS | `GLS-` | 术语（`GLS-{域}-{Seq}`，票 10） |

**ref 字段约定**：
- 跨模型引用一律稳定 ID 引用，字段名统一 `xxxRef` / `xxxRefs` 后缀；少数沿用 OMF 原名（`targetAggregate`、`sourceAggregate`、`ownerEntity`、`appliedRules`、`requiredPermissions`、`inheritsFrom`、`roles`、`permissions`、`dictionaryId`、`dataSource`）——全集见 `model-deps.json` 的 `refKeys`。
- 禁止"只在 description 里写引用"：`AggregateRootRef` 类型属性必须显式 `targetAggregate`（digest §16.4）。
- 引用不得通过名称猜测；ID 变更必须过影响分析（v6 §8.6）。
- **依赖方向单向登记**：M7 与 M2 的严格一对一，依赖边只登记 M7→M2（M7.behaviorRef），M2 侧不设 `queryReportRef` 依赖边——本仓 M2 元素不写 `queryReportRef`，写了即 L2 依赖白名单违规（AC5 的判定依据）。一对一的双向一致性核验属 L2 一致性对清单，随图索引（票 04）落地。

## 3. 四层规则下沉判定（照搬，digest §16.3）

约束放哪，按判定逐级下沉，不许上跳：

1. 内置字段约束（`required`/`unique`）→ 2. 只依赖当前属性值 → `Attribute.refRules` → 3. 只依赖同聚合内部 → `Aggregate.invariants` → 4. 跨对象/跨行为/复用 → M3 规则。

## 4. M1 对象模型（OBJECT）

顶层：`aggregates[]`、`data_dictionaries[]`、`aggregate_associations[]`（v9 §2.4）。

**聚合根 AggregateRoot**：

| 字段 | 必填 | 说明 |
|---|---|---|
| id | ✓ | `AGG-{域}-{NNN}` |
| name / alias | ✓ | 中文名 / 英文标识符（代码映射用） |
| aggregateType | ✓ | 固定 `AGGREGATE_ROOT` |
| description | 可选 | |
| lifecycle | 可选 | 生命周期状态列表 |
| attributes | ✓ | 属性表（见下） |
| entities / valueObjects | 可选 | 子实体 / 值对象（组合） |
| invariants | 可选 | 聚合不变性：`name/expression/violationMessage/enforcedAt(ON_CREATE/ON_UPDATE/ON_DELETE/ALWAYS)` |
| version / validFrom | 可选 | 运行期预留 |

**属性 Attribute**（v9 §2.3.4）：

| 字段 | 必填 | 说明 |
|---|---|---|
| name / label | ✓ | 英文 camelCase / 中文展示名 |
| type | ✓ | `String/Integer/Decimal/Date/DateTime/Boolean/Enum/Money/ValueObject/AggregateRootRef/DictionaryRef` |
| required / unique / defaultValue | 可选 | `unique` 仅聚合根属性有效 |
| enumValues | type=Enum 时 | 不得与 dictionaryRef 并存 |
| valueObjectRef | type=ValueObject 时 | 引用值对象名称（对象内，不走全局 ID） |
| targetAggregate | type=AggregateRootRef 时**必填** | 指向目标聚合根 ID |
| dictionaryRef | type=DictionaryRef 时**必填** | `{dictionaryId, typeCode}`；dictionaryId 指向 DICT- |
| refRules | 可选 | 局部规则：`name/expression(用 value 指当前属性值)/violationMessage/enforcedAt` |

**数据字典**：`id(DICT-)/name/types[]`；DictionaryType `typeCode/typeName/items[]`；DictionaryItem `code(稳定存储值)/label(可改)/enabled(停用置 false，不删除)/sortOrder`。平级结构不定义 parentCode（v6 §2.3.5）。

**聚合关联 AggregateAssociation**：`id(ASSOC-)/sourceAggregate/targetAggregate(M1)/associationType(REFERENCE/DEPENDENCY)/sourceRole/targetRole/cardinality(ONE_TO_ONE/ONE_TO_MANY/MANY_TO_ONE/MANY_TO_MANY)/referenceField`。

## 5. M2 行为模型（BEHAVIOR）

顶层：`behaviors[]`（v9 §3.2）。

| 字段 | 必填 | 说明 |
|---|---|---|
| id | ✓ | `BH-{域}-{动宾}`（本仓前缀约定，见 §2） |
| name | ✓ | 中文动宾短语 |
| ownerEntity | ✓ | 所属 M1 聚合根 ID |
| behaviorType | ✓ | `COMMAND / QUERY`（v9 收敛） |
| triggerType | ✓ | `USER_ACTION / SYSTEM`（v9 收敛） |
| preconditions | ✓ | 谓词表达式列表，全部满足才可执行 |
| postconditions | ✓ | `{field, setValue}` 状态变更 |
| appliedRules | ✓ | 调用的 M3 规则 ID 列表（可为空列表） |
| requiredPermissions | ✓ | 引用 M5 权限 ID 列表（可为空列表） |
| syncTriggers | 可选 | v9 跨对象同步联动载体（见下） |
| **contract** | 可选 | **运行期预留**：行为对外契约描述（一期不消费） |
| **riskLevel** | 可选 | **运行期预留**：风险级（一期不消费） |
| **idempotent** | 可选 | **运行期预留**：幂等标记（一期不消费） |
| version / validFrom | 可选 | 运行期预留 |

**SyncTrigger**（v9 §3.2.2）：`ruleRef`（可选，规则只判断不改状态）、`behaviorRef`（**必填**，同步调用的下游行为）、`description`。硬约束：下游行为必须作用于**另一个独立聚合**（禁止同聚合自我联动）；查询行为 `syncTriggers` 必须为空；联动失败语义必须在 postconditions 或 M6 明确，禁止隐含吞异常。

语义边界：**规则只答条件是否满足、行为只答改变什么状态**，不可合并表达（v9 §1.4）。

## 6. M3 规则模型（RULE）

顶层：`rules[]`（v9 §4.3）。

| 字段 | 必填 | 说明 |
|---|---|---|
| id | ✓ | `RULE-{域}-{Seq}` |
| name | ✓ | |
| ruleType | ✓ | `VALIDATION / CALCULATION / DERIVATION / TRANSFORMATION / RISK`（v9 移除 EVENT_DRIVEN） |
| description | 可选 | |
| inputParams | 可选 | Param：`name/type/sourceField(如 dailyProduction.outputVolume)/required/description` |
| outputType | ✓ | DataType，校验类通常 Boolean |
| **expression** | 二选一 | 伪代码/DSL，不限定语言 |
| **narrative** | 二选一 | **运行期预留**：叙述式写法（自然语言规则文本）——与 expression 双写法，为运行期 Agent 消费预留"人话口径"（PRD F1） |
| reusedBy | 可选 | 引用本规则的行为 ID 列表（反向追踪） |
| externalEngine | 可选 | 外部规则引擎名 |
| version / validFrom | 可选 | 运行期预留 |

规则无副作用（只判断），被 MU 用作校验的规则必须无副作用（v6 §4.7.2 残余约束）。

## 7. M5 主体模型（ACTOR）

顶层：`actors[]`、`roles[]`、`permissions[]`（v9 §5.3）。

**参与者 Actor**：`actorId(ACTOR-)/name/actorType(HUMAN|SYSTEM，v9 移除 EXTERNAL)/roles(ROLE- 列表)/attributes(ABAC 条件用 Map)/version/validFrom(预留)`。

**角色 Role**：`roleId(ROLE-)/name/inheritsFrom(ROLE- 列表，多继承)/permissions(PERM- 列表)`。角色是 M6 人工任务的唯一参与人类型；删除/重命名前必须分析 M6 的 roleRefs。

**权限 Permission**：`permissionId(PERM-{域}-{Action})/targetType(BEHAVIOR|ENTITY)/targetRef(行为或实体 ID)/dataScope(ALL/OWN/DEPT/CUSTOM)/abacCondition(可选)`。权限不进 M7，由 M2 requiredPermissions 承载（v6 §9.6.7）。

## 8. M6 流程模型（FLOW）

顶层：`flows[]`（v9 §6.3，同步编排）。

| 字段 | 必填 | 说明 |
|---|---|---|
| id | ✓ | `FLOW-{域}-{NNN}` |
| name / description | ✓ / 可选 | |
| flowType | ✓ | `COLLABORATION / APPROVAL` |
| businessObjectRefs | ✓ | 涉及的 M1 聚合根 |
| roleRefs | ✓ | 流程允许承担人工活动的角色集合 |
| trigger | ✓ | `triggerType(MANUAL/BEHAVIOR/SCHEDULE/SUB_FLOW)` + 配套字段（v9 移除 EVENT） |
| startActivity | ✓ | **有且仅有一个**（活动 ID） |
| endActivities | ✓ | ≥1，必须指向 END 活动 |
| activities | ✓ | 活动列表 |
| version / validFrom | 可选 | 运行期预留 |

**活动 FlowActivity**：`activityId/name/activityType(START/END/USER_TASK/APPROVAL_TASK/SYSTEM_TASK/BEHAVIOR_CALL/SUB_FLOW_CALL/GATEWAY)/roleRef(USER_TASK/APPROVAL_TASK 必填，只能引用 ROLE- 且 ∈ 流程 roleRefs)/behaviorRef(BEHAVIOR_CALL)/subFlowRef(禁止成环)/ruleRef(可选，进入/完成/网关判断)/conditionExpression(流程局部条件)/approvalOutcomes(APPROVE/REJECT/RETURN)/nextActivities`。

## 9. M7 查询统计与报表模型（REPORT）

顶层：`query_reports[]`（v9 §7.4）。

| 字段 | 必填 | 说明 |
|---|---|---|
| id | ✓ | `QR-{域}-{NNN}` / `RPT-{域}-{NNN}` |
| name / alias / description | ✓ / ✓ / 可选 | alias 为 lowerCamelCase 稳定英文别名 |
| objectType | ✓ | `DETAIL_QUERY/LIST_QUERY/STATISTICAL_QUERY/REPORT` |
| behaviorRef | ✓ | 必须指向 M2 `behaviorType=QUERY` 行为；严格一对一（依赖边单向 M7→M2，见 §2） |
| sourceObjects | ✓ | `{objectRef(M1), alias(查询内唯一), primary(有且仅有一个 true), entityPath?, preAggregation?}` |
| joins / parameters / conditions | 可选 | QueryJoin/QueryParameter/QueryCondition 同 v9 §7.4 |
| resultColumns | ✓ | `{name/label/dataType/sourceExpression/aggregateFunction(NONE/COUNT/COUNT_DISTINCT/SUM/AVG/MIN/MAX)/...}` |
| groupBy / having / orderBy / pagination | 可选 | 同 v9 §7.4 |
| reportOptions | objectType=REPORT 必填 | 其他类型应为空；layout 仅 TABLE |
| referenceSql | 可选 | **v9 降为可选**：语义定义是稳定层，SQL 是实现层，不进真源（digest §16.7） |
| version / validFrom | 可选 | 运行期预留 |

M7 不是 BI 指标模型（无事实表/维度/Cube/ETL）；多个一对多来源同时聚合必须 preAggregation，禁止 `SUM(DISTINCT amount)`。

## 10. MU UI 模型（UI，v9 重定义版）

顶层：`application{}` + `screens[]`（v9 §8.2）。

**Application**：`name/menus[]`；Menu：`menuId/name/children[]（二级菜单强制至少一个）/screenRef(只有二级菜单挂屏幕，与屏幕一对一)`。

**Screen**：`screenId(SCR-)/name/screenType(SINGLE_FORM/LIST_MAINTENANCE/MASTER_DETAIL_FORM/QUERY_LIST)/layout(ASCII)/elements[]/actions[]`。

**Element**：`id/type(10 类：TEXTBOX/TEXTAREA/COMBO/DATEPICKER/POPUP_SELECT/NUMBER/CHECKBOX/BUTTON/GRID/LABEL)/label/io/required/dataBinding(M1 属性路径)/dataSource(M7 对象)/refRules[]`。控件映射强制：Date→DATEPICKER、Enum/DictionaryRef→COMBO、AggregateRootRef→POPUP_SELECT、长文本→TEXTAREA、Boolean→CHECKBOX（v9 §8.3）。

**ActionPoint**：`actionId/name/behaviorRef(对应 M2 行为)/actionType(BUTTON/SUBMIT/DRAFT/APPROVE/REJECT/RETURN)/permissionRef[](M5)`。审批双按钮规则：带审批流的屏幕必须同时含 DRAFT 与 SUBMIT 两个独立功能点（v9 §8.5）。

## 11. GLS 术语模型（GLOSSARY，本仓自定义扩展，票 10）

OMF v6/v9 均无术语模型（digest §0/§16）。术语 = 业务概念的定义/别名/解释，与 M1 的 DICT（值域字典，承载枚举值域）不是一回事——本仓自定义扩展，走"元模型错→框架版本演进"路由进 schema（CHANGELOG.md + 机读表 version 1→1.1.0，本节即迁移票正文）。

顶层：`terms[]`。

| 字段 | 必填 | 说明 |
|---|---|---|
| id | ✓ | `GLS-{域}-{Seq}` |
| term | ✓ | 术语词面（业务真源原文，不改动） |
| aliases | 可选 | 同指异名（全称/标准名/别称），可空列表 |
| termType | 可选 | 术语分类，沿业务真源原文（如 禁用词/别名/一词两译/黑话/缩写/术语/治理热词），不做枚举收敛——真源说什么是什么 |
| definition | ✓ | 定义/解释；口径争议、禁用替代等注记逐字保真 |
| relatedObjectRefs | 可选 | 关联 M1 聚合根 ID 列表。**只挂真实存在的对象，可空留空不硬挂**；依赖边 GLS→M1 单向登记（model-deps.json edges），指向悬空 = L2 红（GLS-AC3） |
| status | 可选 | 状态/有效期（沿业务真源原文，如 `禁用（替代：×）`/`有效`/`有效（待联席裁决）`） |
| owner | 可选 | 术语 Owner（业务部门） |
| source | ✓ | 注源（如 `R5·设定书 §6`）——术语必须可溯源，无源不落仓 |
| notes | 可选 | 补充注记（承载落点/未建原因等，人读追溯用，机器不检） |

- camp=business-core、consumers=[runtime, build]：自动进 semantic-service 检索面（划界只看 camp）与生成器在场校验，无需改任何消费方。
- **profile 组合：入 v9-full 与 headless，不入 v9-core**（v9-core = M1/M2/M3/M5 四模型最小核保持原样，术语属增强件；"未启用"因此可测——GLS-AC2 负变体）。
- 旧域无 glossary-model.yaml 不红：缺在场不校验是既定行为（AC6 同款语义），旧域零改动兼容。
- GLS→GLS（术语见术语）**不设专用依赖边**：当前业务面无此需求（最小够用）。若模型里出现指 GLS- 的 `xxxRef(s)` 形态字段，会落"未登记 edges 字段按 dependsOn 兜底"的判定路径（兜底集含自身，不白名单红；悬空检查仍然生效）——真要规模化再用时再显式登记边。

## 12. 换义锁定字段（lockedFields，AC7 的机读真源）

OMF 的 M6/M7 在 v4 换义造成过沟通成本（digest §14/§16.10）。本仓把"退役字段名"登记在 model-registry.json 各模型 `lockedFields`，schema_check 在 L4 强制：**模型文件内出现锁定字段名 = 兼容性违规**（新义必须新增字段名）。现行锁定表：

| 模型 | 锁定字段 | 旧义（禁止复用的理由） |
|---|---|---|
| M2 | `producedEvents` | v6 事件异步引用（ME 载体）；v9 由 syncTriggers 承载 |
| M3 | `subscribedEvents` / `triggeredBehaviors` | v6 事件驱动规则专属；v9 移除 EVENT_DRIVEN |
| M5 | `externalContract` | v6 外部实体契约；v9 移除 EXTERNAL |
| M6 | `eventRef` | v6 EVENT_WAIT/事件触发残留；v9 流程为同步编排 |
| MU | `callChain` | v6 屏幕调用链；v9 以 actions 操作功能点替代 |

## 13. 模型注册表与依赖白名单（机读）

- `model-registry.json`：每模型 `camp`（business-core/integration/build-contract；一期 integration 空，MI 未引入）、`consumers`（runtime/build）、`profiles`（可用组合：v9-full/v9-core/headless）、`dependsOn`（类型层依赖白名单摘要）。消费方：profile 裁剪、检索面划界（semantic-service 只索引 business-core）、生成器在场校验三件事共用（PRD F1）。
- `model-deps.json`：`idPrefixes`（ID 前缀→模型）+ `refKeys`（ref 字段名全集）+ `edges`（from 模型 × ref 字段 → 允许目标模型集）。AC4/AC5 的判定真源；与 registry 的 dependsOn 做一致性核对，冲突 = L1 违规。
- 依赖白名单要点：M2 不得依赖 M7（AC5 例证，见 §2）；M1 零依赖；M6 依赖 M1/M2/M3/M5；MU 依赖 M1/M2/M3/M5/M7；GLS 只依赖 M1（relatedObjectRefs 单向边，票 10）。
