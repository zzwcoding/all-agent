# 个人知识库域（个人版本体 WeKnora） 开发包（devkit · pkb）

status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）

- 生成器: tools/app_pack_gen.py（确定性装配：YAML 机读 + 提案 frontmatter 扫描，零 LLM 零时间戳）
- 本体来源: ontology/pkb（profile=headless）
- 声明模型: M1 对象模型 / M2 行为模型 / M3 规则模型（豁免未建） / M7 查询统计与报表模型（豁免未建）
- 固定输入: fixtures/app-pack-gen/inputs/tech-constraints.md（出厂集固定输入（合成））、fixtures/app-pack-gen/inputs/dev-guide.md（出厂集固定输入（合成））
- 开放提案开关: 启用（docs/proposals）
- 防陈旧: python3 tools/app_pack_gen.py ontology/pkb --check exports/devkit/pkb/devkit.md

## 技术架构约束（固定输入，原样装配）

出厂集固定输入（合成）——中性示例文本，非任何真实项目规约；生成器按原样装配进开发包头部约束节，文件内容不参与判定。

## 技术架构约束

- 服务端形态：Python 服务端 + 关系库，三层架构（接入 / 领域 / 数据）。
- 数据访问：一切业务数据经语义层数据字典取数，禁直连物理表名。
- 集成边界：对外只暴露查询出口与行为接口，不出裸表。

（以上为合成中性约束，仅作开发包装配通路的固定输入。）

## 开发指导书（固定输入，原样装配）

出厂集固定输入（合成）——中性示例文本，非任何真实项目规约；生成器按原样装配进开发包头部约束节，文件内容不参与判定。

## 开发指导书

- 装配顺序：先数据字典后接口——数据字典是接口签名的唯一依据。
- 口径实现：统计口径以规则清单（M3）的 expression/narrative 为准，查询出口（M7）只是实现形态，两处不一致时以规则为准并回提案流程。
- 疑点处置：开发包第④节开放疑点逐条过目，命中疑点的实现先挂起待 Owner 裁决，不自行拍板。

（以上为合成中性指导，仅作开发包装配通路的固定输入。）

---

## 一、数据字典（M1 对象模型）

### AGG-PKB-001 知识条目（KnowledgeItem）

- AGGREGATE_ROOT；描述: 个人知识库的被管理单元（Owner 原话「管理我日常的开发资料、想法、文档、书籍、 技术感悟、工作业务等等」）。粒度已裁=单一聚合+sourceType 区分来源（Q2 签收 2026-09-22；某类内容长出独立属性面时走提案拆分）。载体形态参照 Owner 既有 资产：书籍全文 txt/书摘 txt/思维导图 png/概念 wiki 页（调研 §一#11）。
- lifecycle: 暂存/入册

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| title | 标题 | String |  |
| sourceType | 来源类型 | String |  |
| contentRef | 内容载体引用 | String |  |
| status | 状态 | Enum | 字典值集: 暂存/入册 |
| collectedAt | 采集时间 | DateTime |  |

## 二、口径四件套（M7 查询出口 × M2 行为 × M3 规则 × M1 承载）

（M7 豁免未建：无查询/报表/统计口径素材证据——「以后可能会要」不算证据（profile-selection §1）。——口径节空）

## 三、行为与规则清单（M2/M3 全量，注源=模型文件 [R<n>·…] 注释标签）

### 行为（M2 · 5 条）

- BH-PKB-CaptureItem 捕获条目 [COMMAND/USER_ACTION] ownerEntity=AGG-PKB-001 appliedRules=—
- BH-PKB-PromoteItem 整理入册 [COMMAND/USER_ACTION] ownerEntity=AGG-PKB-001 appliedRules=—
- BH-PKB-AskKnowledge 检索问答 [QUERY/] ownerEntity=AGG-PKB-001 appliedRules=—
- BH-PKB-QueryGraph 图谱查询 [QUERY/] ownerEntity=AGG-PKB-001 appliedRules=—
- BH-PKB-RegenWiki 再生Wiki页 [COMMAND/USER_ACTION] ownerEntity=AGG-PKB-001 appliedRules=—

（M3 豁免未建：Q5 已裁（2026-09-22）：图谱通用清单起步+三接入点结构预留（开关就位不开），规则闸未启用且 Owner 输入零约束条款——切本体对号表档时再立规则候选。——规则清单空）

## 四、开放疑点（docs/proposals 扫描）

无开放提案。
