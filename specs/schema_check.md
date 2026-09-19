# spec · schema_check（语义 CI L1–L4）

触及: tools/schema_check.py（L3 脚本）；契约: CLI `schema_check <ontology目录> [--json]`

## 出厂集断言表（真源 = fixtures/schema_check/assertions.json，逐条对齐）

基础套件（票 03，七模型最小域 + 非法变体）：

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | 合法本体（fixtures 最小域） | exit 0，报"全过" |
| AC2 | YAML 语法错误文件 | 报 L1 失败+文件名，非零退出 |
| AC3 | 缺 model_type/version/domain 公共字段 | 报 L1 失败并指名字段 |
| AC4 | ref 指向不存在的 ID | 报 L2 失败+悬空引用位置 |
| AC5 | ref 类型越白名单（M2 引 M7） | 报 L2 失败+违反的依赖规则 |
| AC6 | profile 未启用的模型文件出现 | 报 L4 失败 |
| AC7 | 字段换义式变更（同名不同义） | 报 L4 兼容性失败 |

GLS 套件（票 10，真源 = tickets/10-术语模型GLS.md AC 表）：

| 断言 | 给定 | 期望 |
|---|---|---|
| GLS-AC1 | 合法 glossary 最小域（术语 relatedObjectRefs 指向真实 M1 对象） | exit 0，报"全过" |
| GLS-AC2 | GLS 文件出现在不入该模型的 profile（v9-core） | 报 L4 profile-disabled + 未启用模型 GLS |
| GLS-AC3 | 术语 relatedObjectRefs 指向不存在的 AGG- | 报 L2 dangling-ref + 悬空 ID |
| GLS-AC4 | GLS 文件名/model_type 错挂两型 | 报 L1 filename-mismatch + 双方文件名 |

一致性对套件（票 11，真源 = tickets/11-一致性对核验.md AC 表）：

| 断言 | 给定 | 期望 |
|---|---|---|
| CONS-AC1 | QR 错绑 COMMAND 行为 + 两 QR 共绑同一 QUERY 行为 | 报 L2 consistency-redirection + consistency-not-one-to-one（含涉事 ID） |
| CONS-AC2 | PERM 存在但 targetRef 未回指要求它的行为 | 报 L2 consistency-permission（含行为/权限双方 ID） |
| CONS-AC3 | M6 活动 roleRef 不在流程 roleRefs 内 | 报 L2 consistency-flow-role（含流程/活动/角色 ID） |

必填闸套件（票 13，真源 = tickets/13-机读必填字段闸.md AC 表）：

| 断言 | 给定 | 期望 |
|---|---|---|
| REQ-AC1 | M2 行为缺 behaviorType（一致性锚点字段） | 报 L1 required-field 红（不再静默跳过），含元素 ID 与字段名 |
| REQ-AC2 | M7 报表缺 behaviorRef | 报 L1 required-field 红 |
| REQ-AC3a | GLS 术语缺 definition | 报 L1 required-field 红 |
| REQ-AC3b | GLS `terms: []`（空壳文件） | 报 L1 required-field 红 |
| REQ-AC4 | 元素带四外衣预留字段（元素级 version/validFrom、M2 contract/riskLevel/idempotent、M3 narrative 写法） | exit 0，报"全过"（存在即放行） |
| REQ-AC5 | v9-full 域缺 MU 文件、manifest 无豁免 | 报 L4 missing-model-file 红 |
| REQ-AC6 | 同 REQ-AC5 但 omittedModels 带理由豁免 | exit 0，报"全过" |

禁用词拦截面套件（票 16，真源 = tickets/16-禁用词拦截面.md AC 表）：

| 断言 | 给定 | 期望 |
|---|---|---|
| BAN-AC1 | 元素 name 含禁用词（ban-ac1-name-hit：GLS status=禁用 的 term=老完成率） | 报 L4 banned-term 红，含 GLS 条目 ID 与命中词 |
| BAN-AC2 | 元素 alias 含禁用词（ban-ac2-alias-hit：撞禁用条目的 aliases 成员） | 报 L4 banned-term 红 |
| BAN-AC3 | bohai 全量（RULE-BOHAI-009 description 提及禁用词「老完成率」） | exit 0 全绿——description 不扫（文档提及合法） |
| BAN-AC4 | 元素 name 撞 status=有效术语 + description 提及禁用词 + GLS 自身 term 承载禁用词（ban-ac4-valid-term-in-name 防误报对照） | exit 0 全绿——只拦禁用 status；匹配面=name/alias；GLS 不自匹配 |

## 违规码总表

| 级别 | kind | 判定真源 |
|---|---|---|
| L1 | yaml-syntax / missing-common-field / unknown-model-type / filename-mismatch / missing-manifest / missing-manifest-field / unknown-profile / deps-registry-conflict | schema.md §1 + model-registry.json |
| L1 | required-field（票 13：缺结构性必填字段/空壳文件；文件名错挂的文件跳过本闸） | model-registry.json 各模型 requiredElementFields |
| L1 | unknown-omitted-model / bad-omitted-model（票 13：omittedModels 引用未注册模型/条目缺 model） | model-registry.json models |
| L2 | dangling-ref / dep-whitelist | model-deps.json（refKeys ∪ *Ref/Refs ∪ edges） |
| L2 | consistency-redirection / consistency-not-one-to-one / consistency-permission / consistency-flow-role | schema.md §14（票 11） |
| L4 | profile-disabled / field-redefinition | model-registry.json profiles / lockedFields |
| L4 | missing-model-file（票 13：profile 启用却缺文件且 omittedModels 无带理由豁免；豁免条目缺 reason 视为无效） | manifest.json omittedModels + model-registry.json profiles |
| L4 | banned-term（票 16：域内 GLS 术语 status 含「禁用」条目的 term+aliases 进禁用词表，全域元素 name/alias 键子串命中即红；description/notes 不扫=文档自由；GLS 以 term 承载词面不自匹配；文件名错挂的文件跳过本闸） | 域内 glossary-model.yaml 术语 status |

## 行为约定

- 只读不写 YAML；失败输出含文件+行级定位；--json 供 CI 消费
- 依赖白名单、模型注册表与逐元素必填表来自 `ontology/schema/model-registry.json` + `model-deps.json`，不硬编码
- 域 manifest 可选 `omittedModels: [{model, reason}]`（票 13）：登记 profile 启用但有意不建文件的模型及理由（bohai 的 MU 即此形态）；reason 缺失/空串 = 无效豁免
- 结构性必填口径与逐模型推导表见 lessons/13；schema.md 全字段集（preconditions 等）不在必填闸内（缺口清单留后续演进票）
- 禁用词拦截面（票 16）按域生效：禁用词表=本域 GLS 术语 status 含「禁用」条目的 term+aliases（宽进严出，不枚举状态值）；匹配面=递归收集所有字典中键恰为 `name`/`alias` 的字符串值（通用口径，不逐模型硬列挂点）；GLS 无文件的域表为空、闸静默
