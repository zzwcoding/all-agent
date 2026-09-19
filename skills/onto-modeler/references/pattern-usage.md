# pattern-usage · 模式件库使用与组合纪律（票 33）

模式件库在 `ontology/patterns/`：可复用建模片段仓，一个文件一件通用建模模式（域无关）。本页是工序步骤 2.5 的细则：模式件的格式约定、匹配判定、组合三纪律。组合示例的活样板见出厂集 `fixtures/pattern-library/compose-example/`（state-machine-lifecycle + coded-dictionary 两件组合的迷你草案域）。

## 模式件是什么、不是什么

- **是素材，不是域**：patterns/ 目录没有 manifest.json，不进 schema_check 域校验（无域可校验）；结构纪律由出厂集 `fixtures/pattern-library/` 的结构探针承载（YAML 可解析 + 七头字段齐 + fragment 可解析 + 占位符形如 {{xxx}}）；归档闸以 ontology-pattern 产物类登记。
- **域无关**：模式件正文零业务域词；域词只允许出现在组合产物（草案域）里。给 patterns/ 增补新件不是建模工序的事——走 L0 裁决沉淀，本工序只消费不新增。
- **组合产物只是草案**：PRD 原文纪律——模式件组合出来的东西必须走人审进仓；本 skill 只产草案，进仓走 MR。

## 文件约定

`ontology/patterns/<pattern-id>.yaml`，七个头字段：

| 字段 | 说明 |
|---|---|
| pattern_id | 模式件标识（=文件名去后缀），组合注记引用它 |
| name | 模式件中文名 |
| description | 模式解决什么建模问题 |
| applies_when | 适用信号——素材出现什么信号就考虑组合本件 |
| fragment | 可组合 YAML 片段，元素带 {{占位符}}；占位符必须双引号包裹（裸 {{ 会落 YAML 流解析，负变体出厂集实证） |
| compose_notes | 组合与改名列注意，含「组合后按域素材证据决定」的补件清单 |
| source | 出处（首批五件 = L0 授权自创，票 33） |

fragment 的元素形态与 schema.md 的真实域元素结构一致——正常组合（替换占位符、并入对应模型文件）即可过 schema_check L1。

## 工序步骤 2.5 的组合三纪律

1. **占位符全部替换**：fragment 里每个 {{占位符}} 替换为域实例；compose_notes 点名的对齐关系逐条核对（如状态值集与字典 label 一一对齐、外键引用字段名与关联 referenceField 同名、dictionaryId/typeCode 与字典条目精确一致）——对不上即组合错误。
2. **pattern_id 入 description 注记**：被组合的元素 description 注记「组合自 patterns/<pattern_id>」；多件组合进同一元素时注记并列（「组合自 patterns/A；组合自 patterns/B」）。
3. **产物仍是草案走人审**：组合产物过 schema_check 只是结构合格；业务语义（状态值集、主从归属、码表内容、审批角色）必须 Owner 确认。compose_notes 点名的「按域素材证据决定」补件（如状态迁移合法性规则、拒绝分支回退路径）没有素材证据就不建、挂「待 Owner 确认」，不硬凑。

## 匹配判定（applies_when → 组不组合）

- 逐件读 applies_when 的信号清单，对照域素材；命中任一信号即候选。
- 候选不等于必组：组合以素材证据为界——模式件给的是「形态」，值集/归属/角色等业务内容一律取自素材；素材没有就挂待 Owner 确认。
- 无任何匹配件：跳过步骤 2.5，直接进填草案步；不为凑用而回头造模式件。

## 组合后自查（进修整步前）

- 占位符零残留：草案域 YAML 全文无 {{ 。
- 注记在位：被组合元素 description 含「组合自 patterns/<pattern_id>」。
- 结构过闸：草案跑 `python3 tools/schema_check.py <域目录>`（步骤 4），组合产物与手工草案同一标准。
