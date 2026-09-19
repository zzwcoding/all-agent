# modules.md · All-agent skill 卡集合

> 卡是唯一真源，格式真源见 sdd-flow2 `references/skill-module-format.md`。
> 划分依据：PRD F1–F14 聚类（docs/prd.md）；分层纪律见 docs/design-sdd-flow2.md §1。
> 一期范围（PRD 决策 3）：onto-modeler / db-reverse / impact-analyzer / semantic-service + L3 两脚本；其余二期（骨架卡先立）。
> （2026-09-19：+proposal-pool 转正（票 18）；skill 双位置与安装位机制（票 05/12/15））
> 卡名纪律：卡名 = skill 目录名（边界闸按名精确匹配，（一期）/（二期）标注不入名字槽）；skill 正本落仓内 skills/<名>/，安装位 ~/.agents/skills/<名>/（双位置同内容，票 05 起）。

## skill: onto-modeler

- 职责: 本体建模工序——按 PRD/素材推荐 profile、脚手架出模型文件骨架、把草案修整到可过语义 CI
- 层: L1 工序
- 目录: 仓内 skills/onto-modeler/（正本，边界闸+归档闸治理）+ ~/.agents/skills/onto-modeler/（安装位，Kimi Code 路由）；两份内容必须一致
- 触发面: "给某域建本体/修整本体草案/加模型元素"
- reads: `ontology/schema/**`（schema+模型注册表）、`ontology/patterns/**`（模式件库，票 33 首批五件，工序步骤 2.5 消费）、域素材
- writes: `ontology/<域>/**` 草案（只产草案，进仓走 MR）
- 依赖:
  - script: `tools/schema_check.py`
  - data: `ontology/**`
- Seam 与出厂集: `fixtures/onto-modeler/`——固定 PRD 片段 → 断言产出的 profile 建议与骨架文件清单；`fixtures/pattern-library/`——模式件结构探针（首批五件+负变体）与组合示例域过语义闸（票 33）
- 边界: 不读生成器 skill 私件；不直改仓内已定稿本体（只产草案）

## skill: db-reverse

- 职责: 数据库逆向器——DDL/库表 → 本体草案（对象/属性/映射证据），自下而上供业务 Owner 裁决
- 层: 工序（前端适配器）
- 目录: 仓内 skills/db-reverse/（正本，边界闸+归档闸治理）+ ~/.agents/skills/db-reverse/（安装位，Kimi Code 路由）；两份内容必须一致
- 触发面: "把这个库/这份 DDL 逆向成本体"
- reads: DDL 文件或库连接描述、`ontology/schema/**`
- writes: `ontology/<域>/**` 草案 + 映射证据文件
- 依赖:
  - script: `tools/schema_check.py`
  - data: `ontology/**`
- Seam 与出厂集: `fixtures/db-reverse/`——渤海域 8 表 DDL 子集 → 断言逆向出的对象清单与属性覆盖
- 边界: 同 onto-modeler；草案必须标注"证据非权威，待 Owner 确认"

## skill: impact-analyzer

- 职责: 变更影响分析器——本体变更 → 影响链路（哪些对象/规则/报表/映射受波及）+ 建议落地顺序
- 层: 工序（治理/输出两用）
- 目录: 仓内 skills/impact-analyzer/（正本，边界闸+归档闸治理）+ ~/.agents/skills/impact-analyzer/（安装位，Kimi Code 路由）；两份内容必须一致
- 触发面: "改 X 会影响什么/评估这个变更"
- reads: `ontology/**`、`tools/graph_index.py` 产出的图
- writes: 影响分析报告（落 `docs/impact/` 或对话附盘文件）
- 依赖:
  - script: `tools/graph_index.py`
  - data: `ontology/**`
- Seam 与出厂集: `fixtures/impact-analyzer/`——固定本体+固定变更 → 断言影响链节点集
- 边界: 只读仓；不修改任何本体文件

## skill: semantic-service

- 职责: 运行时语义服务——受控检索瀑布（显式锚定优先、逐级升级、可拒答）+ 口径解析 + 子图装配，供 Agent 只读消费
- 层: 工序（运行时面）
- 目录: 仓内 skills/semantic-service/（正本，边界闸+归档闸治理）+ ~/.agents/skills/semantic-service/（安装位，Kimi Code 路由）；两份内容必须一致
- 触发面: "查口径/问业务对象/解析指标含义"
- reads: `ontology/**`（经 graph_index）、模型注册表（只索引 business-core 阵营）
- writes: 无（只读服务；回答即产出）
- 依赖:
  - script: `tools/graph_index.py`
  - script: `tools/semantic_service_core.py`（可机判判定核心，票 22 提纯；票 25 单源声明双向化）
  - data: `ontology/**`
- Seam 与出厂集: `fixtures/semantic-service/`——Golden Question 集：固定问题 → 断言命中的对象 ID 集与拒答行为
- 边界: 只读（写意图一律转提案池流程，二期）；不索引 build-contract 阵营模型

## skill: requirement-explorer

- 职责: 需求探索器——粗 PRD 反问收敛 → 细稿 + 本体草案（正向输入）
- 层: 工序（前端适配器）
- 目录: 仓内 skills/requirement-explorer/（正本，边界闸+归档闸治理）+ ~/.agents/skills/requirement-explorer/（安装位，Kimi Code 路由）；两份内容必须一致
- 触发面: "从粗需求/粗 PRD 反问收敛出细稿与本体草案"
- reads: 域素材（粗需求/粗 PRD，含标记关键词清单）、`ontology/schema/**`
- writes: `docs/requirements/*.md`（细稿：收敛结论+开放问题清单+明示不建模清单，三节缺一不可，末节附关键词×三落点对照表）、`ontology/<域>/**` 草案（只产草案，进仓走 MR）
- 依赖:
  - script: `tools/schema_check.py`
  - data: `ontology/**`
- Seam 与出厂集: `fixtures/requirement-explorer/`——固定粗 PRD 片段（中性域，【】标记关键词，含故意含糊表述）→ 断言细稿三节齐、问题三字段结构完备、草案过语义闸、草案头部声明（AC1）+ 覆盖不变量探针：关键词×（草案 YAML+细稿两节）双向核对，正例 exit 0、漏覆盖负变体 exit 1（AC2，真源=票 30 AC 表）
- 边界: 同 onto-modeler；草案头部必须标注"AI 只做格式转换，业务必须人确认"；含糊表述只进开放问题不硬建模——未覆盖必须变成问题

## skill: code-reverse

- 职责: 代码逆向器——存量源码 → 本体草案 + 调用链素材（类→聚合根候选/字段→属性/常量约束→规则候选/字面量集→字典候选，调用图→调用链素材；方法级行为默认挂起）
- 层: 工序（前端适配器）
- 目录: 仓内 skills/code-reverse/（正本，边界闸+归档闸治理）+ ~/.agents/skills/code-reverse/（安装位，Kimi Code 路由）；两份内容必须一致
- 触发面: "把这份源码/这个代码库逆向成本体草案与调用链素材"
- reads: 用户提供的源码/代码库（含随输入落盘的符号覆盖清单）、`ontology/schema/**`
- writes: `ontology/<域>/**` 草案（只产草案，进仓走 MR）、`docs/code-reverse/*.md`（调用链素材：代码符号→草案元素逐条映射+源码 file:line 证据+调用链+疑点清单+明示不逆向清单，末节符号覆盖对照表=覆盖探针判定面）
- 依赖:
  - script: `tools/schema_check.py`
  - data: `ontology/**`
- Seam 与出厂集: `fixtures/code-reverse/`——合成迷你代码库两文件（中性域，类与字段/方法调用链/常量约束/字面量集四类素材齐，另埋两处真实脏特征供疑点清单）→ 断言草案过语义闸+符号覆盖探针正例 exit 0（AC1）、草案头部声明与 file:line 注源（AC2）、映射缺一个符号覆盖的负变体 exit 1（AC3，真源=票 31 AC 表）
- 边界: 同 onto-modeler；草案头部必须标注"证据非权威，待 Owner 确认"；不发明源码里不存在的语义——调用链不产生关联推断，引用只从字段引用推导，推断性关联进疑点清单；方法无可复述业务语义挂起不产行为文件（omittedModels 带理由）

## skill: doc-extractor

- 职责: 文档萃取器——成文文档/资料库 → 概念/术语/规则草案（定义句→GLS 术语候选/可条件化条款→M3 规则候选，文档的本体形态就是术语与规则）+ 证据索引（每条候选→文档 file#锚点 逐条证据）
- 层: 工序（前端适配器）
- 目录: 仓内 skills/doc-extractor/（正本，边界闸+归档闸治理）+ ~/.agents/skills/doc-extractor/（安装位，Kimi Code 路由）；两份内容必须一致
- 触发面: "从这些文档萃取概念/术语/规则草案"
- reads: 用户提供的成文文档/资料库（含随输入落盘的标记条目清单：编号+类型+锚点）、`ontology/schema/**`
- writes: `ontology/<域>/**` 草案（GLS 术语 + M3 规则为主，零证据的整模型挂 omittedModels 带理由豁免；只产草案，进仓走 MR）、`docs/doc-extractor/*.md`（证据索引：候选清单逐条注源+状态判定+疑点清单+状态标注留痕，末节覆盖对照表=覆盖探针判定面）
- 依赖:
  - script: `tools/schema_check.py`
  - data: `ontology/**`
- Seam 与出厂集: `fixtures/doc-extractor/`——合成制度文档两份（中性域：术语定义 6 条含 1 明示废弃+1 明示限语境，可条件化条款 5 条+纯叙述性条款 2 条）→ 断言草案过语义闸+萃取覆盖探针正例 exit 0（AC1）、草案头部声明与 file#锚点 注源+证据索引 ≥7 条且逐条含锚点（AC2）、覆盖对照表缺一条的负变体 exit 1（AC3，真源=票 32 AC 表）
- 边界: 同 onto-modeler；草案头部必须标注"证据非权威，待 Owner 确认"；状态不洗白——文档明示废弃/仅限某语境的条目照 GLS status 纪律如实标注不丢弃；规则必须条件化——纯叙述性条款进疑点清单不硬转；每条候选注源 `文档 file#锚点`；零对象/行为/主体/界面证据不产 M1/M2 文件（omittedModels 带理由），relatedObjectRefs 无承载不硬挂

## skill: app-generator

- 职责: 应用生成器——本体+技术架构+开发指导书 → 导出开发包；发布前过人审闸（PRD 决策 2）；细节二期

## skill: skill-publisher

- 职责: Skill 发布器——本体切片 → 可对话技能包；人审闸同 F9；细节二期

## skill: mcp-publisher

- 职责: MCP 发布器——本体能力 → MCP Server（stdio 先行）；人审闸同 F9；细节二期

## skill: proposal-pool

- 职责: 提案池处理——三源信号（监督/自检/交互）归一成标准提案文件、确定性冲突预检、状态流转落痕（自动化止于提案）；真提案进仓的 MR 由人直接在 Git 完成
- 层: L1 工序（业务语义循环闸口）
- 目录: 仓内 skills/proposal-pool/（正本，边界闸+归档闸治理）+ ~/.agents/skills/proposal-pool/（安装位，Kimi Code 路由）；两份内容必须一致
- 触发面: "把这条信号起草成提案/过一遍提案池/查提案池状态"
- reads: `docs/proposals/**`（提案池现状与池内冲突面）、`ontology/**`（真域，target 存在性与 change 定型的判定依据）、`references/proposal-format.md`（提案文件格式规范，仓级共享件）+ 用户提交的信号素材
- writes: `docs/proposals/PROP-<域>-<NNN>.md` 提案 + 既有提案的裁决落痕（只动 status 与正文裁决注记）
- 依赖:
  - script: `tools/proposal_check.py`
  - data: `ontology/**`
- Seam 与出厂集: `fixtures/proposal-pool/`——正例提案两份（add 渤海新规则 + modify 真实元素）+ 负变体（字段缺失/modify 不存在/add 已存在/同靶冲突/证据路径不存在，另加枚举非法）→ 断言 proposal_check 四类检查（AC1–6，真源=票 18 AC 表）
- 边界: 自动化止于提案——不起 git 分支、不直改 ontology/** 已定稿本体；open→accepted/rejected 只由 Owner 裁决，skill 只代执行翻转并留痕

## skill: meta-doctor

- 职责: 元循环体检——跨层探针度量 + 信号路由表分流（业务错→MR/工程错→票/元模型错→schema 演进票）

## 边界规则

| 禁止 | 例外 | 理由 |
|---|---|---|
| 前端适配器（requirement-explorer/db-reverse/code-reverse/doc-extractor）直连后端生成器（app-generator/skill-publisher/mcp-publisher） | 无 | 一切经本体仓——多输入多输出的铁律 |
| 任何 skill 直改 `ontology/**` 已定稿本体 | 无 | 写入必经 MR + 语义 CI；skill 只产草案 |
| semantic-service 写 `ontology/**` | 无 | 运行面只读；写意图转提案流程 |
| 任何 skill 读另一 skill 的私有 references | 无 | 逻辑包含靠显式依赖行 |
| 生成器读取 build-contract 之外缺少声明的模型 | 无 | 生成器声明所需模型，缺了报错不硬编 |

## 规约清单（L2）

| 规约 | 状态 |
|---|---|
| ontology/schema/（YAML schema + 模型注册表 model-registry.json + model-deps.json） | 已建（票 03）；票 10 增 GLS 术语模型 |
| references/omf-spec-digest.md 等调研三件 | 已落盘 |

## 脚本清单（L3）

> （2026-09-19 注记）mcp-publisher 本体 = PRD F11 发布物：`tools/mcp_manifest_gen.py` 生成器 + `tools/semantic_mcp_server.py` stdio 服务器（消费文档 docs/mcp-server.md）；L3 工具群不立 skill 卡，卡面维持二期占位。

| 脚本 | 职责 | 状态 |
|---|---|---|
| `tools/schema_check.py` | 语义 CI 的 L1–L4 级（schema 合法/引用一致/依赖白名单/profile 合规+反向缺文件/逐元素结构性必填），断言表 specs/schema_check.md AC1–7 + GLS/CONS/REQ 套件 | 已建（票 03；票 10/11/13/16 演进，16=banned-term 禁用词拦截面——上票清单外发现，票 22 补账） |
| `tools/graph_index.py` | YAML → 内存图（多跳/闭包/影响链） | 已建（票 04） |
| `tools/check_citations.py` | ID 引用清单逐条比对检具：答案正文↔「本回答引用的元素 ID」清单节双向差异（正文有清单无/清单有正文无），退出码 0 一致/1 不一致/2 用法；通用大写前缀 token 不绑域；断言面 fixtures/semantic-service CIT-01–05（票 13，审查一 P2） | 已建（票 13） |
| `tools/proposal_check.py` | 提案池确定性检查：①proposal-schema 必备字段与枚举 ②proposal-target 靶存在性（modify/deprecate 在域、add 不在域，元素口径照图索引 id/*Id 定义键+已登记前缀，独立实现零耦合）③proposal-conflict 同靶 open 提案 change 矛盾 ④proposal-evidence 证据在档（仓根/提案目录相对+#锚点容许）；只解析 PROP-*.md；断言面 fixtures/proposal-pool AC1–6（票 18） | 已建（票 18） |
| `tools/guard_corpus_check.py` | 守卫例集回归检具（票 20 守卫单源化）：守卫正则唯一真源=fixtures/semantic-service/guard-corpus/regex.txt，manifest.txt 逐行登记 match/nomatch 预期，对 root 逐文件施 regex——好例必不命中、坏例必命中、文件缺失/空套件=违规（禁空套件亮绿灯）；真答案（expected-answers）持续受守卫；退出码 0/1/2 对齐仓内约定；断言面 fixtures/semantic-service ac3 cmd 条目 | 已建（票 20） |
| `tools/semantic_service_core.py` | 语义服务四步瀑布可机判核心+CLI：显式锚定（前缀→模型→camp 面外判定在先，先阵营后存在性）、ID/名称解析（name/alias/属性标签/GLS term+alias 确定性分层匹配，不猜不模糊）、闭包/影响装配指令、拒答三分支（面外/仓内没有+缺件分层/禁用词+替代指路）与命中 ID 集——**自然语言成稿归 skill（提纯不重写）**；图消费经 `tools/graph_index.py` 子进程 `--json`（零耦合），禁用词表自实现（读域内 GLS status 含「禁用」，与 schema_check 是两个读者同真源）；CLI 退出码 0 answered/1 refused/2 配置错误；八问真域回归接 fixtures/semantic-service CORE-01–08（票 22） | 已建（票 22） |
| `tools/mcp_manifest_gen.py` | MCP capability manifest 生成器（票 23）：域发现（扫 */manifest.json）+每域 profile/camp 概览（读 model-registry.json，按 profile 圈定+omittedModels 剔除）+四工具契约模板常量 TOOL_CONTRACTS（描述真源，semantic_mcp_server import 同源复用防漂移）；**零时间戳确定性派生物**（同本体仓重生成字节一致），三模式 stdout/--out/--check（--check=与入库副本逐字节比对，防陈旧断言载体，fixtures/mcp-publisher AC2）；发布物 exports/mcp/capability-manifest.json 禁手改；stdlib 零第三方 | 已建（票 23） |
| `tools/semantic_mcp_server.py` | 语义服务 MCP stdio 服务器（票 23）：四工具（ask→票 22 core 子进程；query/closure/impact→graph_index 子进程）+回答骨架组装（**必含 ID token 与「本回答引用的元素 ID」清单**，拒答态列禁用词/替代/近邻真实 ID）；**CI 免疫红线**——mcp SDK 缺席时模块可 import、起服打指引 exit 2（本仓 CI 不装 mcp，协议面测试 skipUnless 留票 24 venv 实弹）；API 面=v2 `mcp.server.MCPServer`（v1 FastMCP 兼容回退，lessons/23）；描述真源=生成器模板（起服装载入库 manifest 逐项核对，漂移回退模板） | 已建（票 23；协议面待票 24 实弹） |
| `tools/mcp_smoke_client.py` | MCP 端到端实弹 smoke 客户端（票 24）：官方 mcp SDK stdio 客户端拉起 semantic_mcp_server，顺序实调四工具并逐调用打印请求/响应摘要（走查证据）；内置出厂集同源断言（期望值抄自 fixtures/semantic-service CORE-01/03/04/05 + fixtures/mcp-publisher/cases U1–U8 对照单）——经 MCP 协议实调结果必须与出厂集行为一致；引用清单节与 ID token 在场为内置断言；协议面测试 skipUnless mcp（本仓 CI 不装 mcp，实弹走 .venv-mcp，票 24 实测 mcp 2.2.0 + Python 3.11） | 已建（票 24） |
| `tools/meta_probe.py` | 元循环探针（票 28 建九项，票 29 增第 10 项与豁免复核并入，F14）：十项确定性体检零 LLM——①出厂集（fixture_run 子进程逐套 PASS/PENDING/FAIL）②语义闸（schema_check 子进程 L1/L2/L4）③CORE 分布（八问逐条 semantic_service_core --json，status 分布+与 fixtures CORE-01–08 冻结期望对照；八问常量表内置、与断言 fixture 同步维护）④边界闸豁免 .skill-deps-allow 逐条+人工复核栏（复核结论由 --review 或缺省 docs/meta/exemption-reviews.json 并入留痕，票 29）⑤归档豁免 .archive-allow 同上 ⑥安装位（install_skills --check 子进程，漂移/孤儿/注册表规模）⑦skill↔卡同步（modules.md 卡名集合 vs skills/*/SKILL.md 双向差集；有 skill 无卡=违规，占位卡不判违规）⑧提案池（PROP-*.md status 计数+proposal_check 子进程退出码）⑨图基线（graph_index 节点/边快照）⑩信号路由表自检（policies/signal-routing.json：合法 JSON+routes 恰三类 业务错/工程错/元模型错+每类 instances ≥2 条且指针逐个真实——commit 逐个 git log 验存、PROP 逐个查 docs/proposals/ 在池；路由表坏=硬闸红，票 29）；判定归各闸、探针只采集呈现不复制判定逻辑；MD 十节+结论行+机读 JSON（--out 同名双落盘，缺省 stdout，留痕带时间戳非 golden）；退出码 0 硬闸全绿/1 硬闸红/2 用法，硬闸=1/2/6/7/10，3/4/5/8/9 信息项不判死；子进程工具缺席/坏输出→该项 SKIPPED 降级不崩（硬闸全绿+硬闸缺→结论 DEGRADED 仍退出 0）；留痕落 docs/meta/（布局表 docs 条目 meta/*.md+meta/*.json，票 28） | 已建（票 28 九项；票 29 增第 10 项路由表自检+豁免复核并入 --review/缺省 exemption-reviews.json+体检节奏入协议第 9 条） |
| `tools/skill_deps_check.py` `tools/fixture_run.py` `tools/archive_check.py` 三闸 + `tools/ci.sh` | 从 sdd-flow2 实例化拷贝（含单测；fixture_run 新增 cmd-* 断言与占位 pending） | 已建（票 03 随迁） |
| `tools/install_skills.py` | 安装位同步与落闸：仓内 skills/ 正本 → ~/.agents/skills/ 安装位的 sync（先清后拷，只清本 skill 目录）、--check（漂移三型 missing/modified/extra + 孤儿检测）、--prune（孤儿清除，默认 dry-run，--yes 才删）、symlink 拒跑（退出 2）；注册表 `tools/install-registry.json` 由 sync 原子维护（孤儿三要素=登记过+安装位在+正本已删）；`tools/hooks/pre-commit`（core.hooksPath 启用）提交前跑 --check 拦漂移；断言表 tickets/12 AC1–4 + tickets/15 AC1–6；不进 ci.sh 四闸（安装位是仓外环境状态） | 已建（票 12；票 15 增强） |
