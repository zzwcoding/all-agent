# spec · schema_check（语义 CI L1–L4；票 41 增 L3 确定性子集）

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

缺 id 盲区套件（票 27，真源 = tickets/27-缺id盲区演进票.md AC 表；元素枚举去 id 锚定，空壳守卫收窄为「主集合键缺失或集合为空」）：

| 断言 | 给定 | 期望 |
|---|---|---|
| MID-AC1 | 合法元素+无 id 元素混入且引用全有效（mid-ac1-mixed-missing-id：BH-MID-001 + 无 id 行为） | 报 L1 required-field 缺必填字段「id」红，红因可指认到无 id 元素（修前此形态整域静默全绿=唯一逃逸形态）；合法元素零扰动 |
| MID-AC2 | 纯无 id 域（mid-ac2-pure-missing-id：M1/M2 主集合字典全无 id 键） | 逐元素报 L1 required-field 缺 id 红（修前每文件被空壳守卫一条吞掉），不再是空壳一条 |
| MID-AC3 | bohai / valid-domain / 全部出厂集域副本（attributes 等嵌套字典无 id 是合法形态） | 全绿零扰动（由既有 AC1/GLS-AC1/REQ-AC4/BAN-AC3/AC4 等绿断言承载） |
| MID-AC4 | `terms: []` 纯空集合（=REQ-AC3b） | 仍报空壳红——空壳语义不回退（断言 REQ-AC3b 承载，零改动） |

重复 id 套件（票 38，真源 = tickets/38-重复id检测.md AC 表；同域元素 id 唯一，违规码 `duplicate-id`，L1 身份族）：

| 断言 | 给定 | 期望 |
|---|---|---|
| DUP-AC1 | 同域两元素同 id（dup-ac1-same-domain-duplicate-id：AGG-DUP-001 在同一主集合出现两次，两元素必填字段齐全、ownerEntity 引用照常解析） | 报 L1 duplicate-id 红，报文含双位置（先出现 m1-object-model.yaml:5 + 后出现 m1-object-model.yaml:10）与双元素名（井甲/井乙）；重复≠悬空，无杂音红因 |
| DUP-AC2 | bohai / valid-domain / 全部出厂集域副本（各域合法复用同形 ID——唯一性判定键 = manifest 域值，跨域不判） | 全绿零误报（由既有绿断言 + 全量回归承载）；跨键同值（M5 actorId/roleId 式）/跨文件同域两形态由单测面（DuplicateId 类）钉死 |

L3 确定性闸套件（票 41，真源 = tickets/41-L3确定性闸.md 可机判子集清单（L0 裁决）+ AC 表；L3=语义 CI 五级的指标/SQL/安全，本套件只收确定性可判子集四项，违规码 `l3-*`；明示不收 SQL 语义正确性/指标公式数学正确性/安全敏感度分级/任何需 LLM 判断的项——归 L5 设计案）：

| 断言 | 给定 | 期望 |
|---|---|---|
| L3-AC1a | M3 sourceField 指向不存在字段（l3-ac1a-source-field-missing：RULE-BOHAI-001 sourceField 字段段 nonExistentField 不在所指聚合 attributes） | 报 L3 l3-source-field 红，报文含规则 ID 与字段段；对象段按匹配序（id→alias→name→别名驼峰词唯一包含）解析成功，红因钉在字段 |
| L3-AC1b | M7 sourceExpression 引用未声明别名（l3-ac1b-expression-ref：QR-BOHAI-001 列引用 x.wellCode，x 不在 sourceObjects） | 报 L3 l3-expression-ref 红，报文含报表 ID、表达式与「未在 sourceObjects 声明」 |
| L3-AC1c | referenceSql 含 UPDATE（l3-ac1c-sql-readonly：QR-BOHAI-001 增 referenceSql UPDATE 语句） | 报 L3 l3-sql-readonly 红（DML/DDL 黑名单词大小写不敏感 + \b 词边界；updated_at 式列名不误伤由单测钉死） |
| L3-AC1d | EXPRESSION 型规则缺 expression（l3-ac1d-rule-form：RULE-BOHAI-002 ruleType=EXPRESSION 且无 expression/narrative） | 报 L3 l3-rule-form 红（schema.md §6 二选一形态；ruleType 值集实读无 EXPRESSION/NARRATIVE 型，EXPRESSION 特判 + 其余型至少一者在场；ruleType 缺失归 L1 required-field 不叠红） |
| L3-AC2a/2b | bohai / ontology 仓根全量 | exit 0 全绿且计数行 `L1: 0 \| L2: 0 \| L3: 0 \| L4: 0`——存量零误报红线（首跑两处红经裁决=真缺陷已修域 RULE-BOHAI-003，裁决记录 lessons/41） |
| L3-AC3 | valid-domain 正例副本 | 零倒（全绿零扰动，负变体注入即红互为印证） |
| L3-AC4 | --json 机读输出 | levels 含 `"L3": 0`（计数与人类输出行同步进报告） |

## 违规码总表

| 级别 | kind | 判定真源 |
|---|---|---|
| L1 | yaml-syntax / missing-common-field / unknown-model-type / filename-mismatch / missing-manifest / missing-manifest-field / unknown-profile / deps-registry-conflict | schema.md §1 + model-registry.json |
| L1 | required-field（票 13：缺结构性必填字段；票 27：主集合逐字典枚举——无 id 元素报缺必填身份字段，空壳判定收窄为「主集合键缺失或集合为空」；文件名错挂的文件跳过本闸） | model-registry.json 各模型 requiredElementFields |
| L1 | duplicate-id（票 38：同一 manifest 域值之下元素 id（id/*Id 定义键，非 ref 键、带注册前缀）不得重复——挂票 27 元素枚举建域值→id 索引，报文含双位置与元素名；M5 actorId/roleId/permissionId 跨键同值同判；跨域不判；文件名错挂的文件跳过本闸） | manifest.json domain + model-deps.json idPrefixes |
| L1 | unknown-omitted-model / bad-omitted-model（票 13：omittedModels 引用未注册模型/条目缺 model） | model-registry.json models |
| L2 | dangling-ref / dep-whitelist | model-deps.json（refKeys ∪ *Ref/Refs ∪ edges） |
| L2 | consistency-redirection / consistency-not-one-to-one / consistency-permission / consistency-flow-role | schema.md §14（票 11） |
| L4 | profile-disabled / field-redefinition | model-registry.json profiles / lockedFields |
| L4 | missing-model-file（票 13：profile 启用却缺文件且 omittedModels 无带理由豁免；豁免条目缺 reason 视为无效） | manifest.json omittedModels + model-registry.json profiles |
| L4 | banned-term（票 16：域内 GLS 术语 status 含「禁用」条目的 term+aliases 进禁用词表，全域元素 name/alias 键子串命中即红；description/notes 不扫=文档自由；GLS 以 term 承载词面不自匹配；文件名错挂的文件跳过本闸） | 域内 glossary-model.yaml 术语 status |
| L3 | l3-source-field / l3-expression-ref / l3-sql-readonly / l3-rule-form（票 41：L3 确定性闸四项——sourceField 双段字段存在性（对象段匹配序 id→alias→name→别名驼峰词唯一包含，中文注记后缀剥离，非双段形态不判）；resultColumns sourceExpression 的 别名.字段 token 别名须声明、字段须在所指聚合 attributes（objectRef 悬空归 dangling-ref 红因不混）；referenceSql 可选字段在场才扫，DML/DDL 黑名单词大小写不敏感+词边界；规则形态二选一（EXPRESSION 特判，ruleType 缺失归 required-field）；文件名错挂的文件跳过 L3 闸） | tickets/41 可机判子集清单（L0 裁决）+ schema.md §6/§9/§15 |

## 行为约定

- 只读不写 YAML；失败输出含文件+行级定位；--json 供 CI 消费
- 依赖白名单、模型注册表与逐元素必填表来自 `ontology/schema/model-registry.json` + `model-deps.json`，不硬编码
- 域 manifest 可选 `omittedModels: [{model, reason}]`（票 13）：登记 profile 启用但有意不建文件的模型及理由（bohai 的 MU 即此形态）；reason 缺失/空串 = 无效豁免
- 结构性必填口径与逐模型推导表见 lessons/13；schema.md 全字段集（preconditions 等）不在必填闸内（缺口清单留后续演进票）
- 禁用词拦截面（票 16）按域生效：禁用词表=本域 GLS 术语 status 含「禁用」条目的 term+aliases（宽进严出，不枚举状态值）；匹配面=递归收集所有字典中键恰为 `name`/`alias` 的字符串值（通用口径，不逐模型硬列挂点）；GLS 无文件的域表为空、闸静默
- L3 确定性闸（票 41）按域生效：域内聚合目录（M1 aggregates）为 L3-1/L3-2 的解析基准；对象段匹配序 `L3_OBJECT_MATCH_ORDER`（模块常量，可配置演进=改元组不改判定逻辑）——直配层 id/alias（不区分大小写）+ name（原文精确），末层「别名驼峰词唯一包含」兼容 schema.md §6 示例的自造短名形态（dailyProduction），多命中=不解析报本码；报告计数行与 --json levels 含 L3；剩余非确定性子集归 L5 评分框架设计案（第三期 B 线批次三方案 1）
