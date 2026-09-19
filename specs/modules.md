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
- reads: `ontology/schema/**`（schema+模型注册表）、`ontology/patterns/**`（模式件库，二期）、域素材
- writes: `ontology/<域>/**` 草案（只产草案，进仓走 MR）
- 依赖:
  - script: `tools/schema_check.py`
  - data: `ontology/**`
- Seam 与出厂集: `fixtures/onto-modeler/`——固定 PRD 片段 → 断言产出的 profile 建议与骨架文件清单
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
  - data: `ontology/**`
- Seam 与出厂集: `fixtures/semantic-service/`——Golden Question 集：固定问题 → 断言命中的对象 ID 集与拒答行为
- 边界: 只读（写意图一律转提案池流程，二期）；不索引 build-contract 阵营模型

## skill: requirement-explorer

- 职责: 需求探索器——粗 PRD 反问收敛 → 细稿 + 本体草案（正向输入）
- 层: 工序（前端适配器）；触发面/reads/writes/依赖/Seam/边界：待二期立项时填充（格式同 db-reverse）

## skill: code-reverse

- 职责: 代码逆向器——存量源码 → 本体草案 + 调用链素材；细节二期

## skill: doc-extractor

- 职责: 文档萃取器——资料库 → 概念/术语/规则草案；细节二期

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

| 脚本 | 职责 | 状态 |
|---|---|---|
| `tools/schema_check.py` | 语义 CI 的 L1–L4 级（schema 合法/引用一致/依赖白名单/profile 合规+反向缺文件/逐元素结构性必填），断言表 specs/schema_check.md AC1–7 + GLS/CONS/REQ 套件 | 已建（票 03；票 10/11/13/16 演进，16=banned-term 禁用词拦截面——上票清单外发现，票 22 补账） |
| `tools/graph_index.py` | YAML → 内存图（多跳/闭包/影响链） | 已建（票 04） |
| `tools/check_citations.py` | ID 引用清单逐条比对检具：答案正文↔「本回答引用的元素 ID」清单节双向差异（正文有清单无/清单有正文无），退出码 0 一致/1 不一致/2 用法；通用大写前缀 token 不绑域；断言面 fixtures/semantic-service CIT-01–05（票 13，审查一 P2） | 已建（票 13） |
| `tools/proposal_check.py` | 提案池确定性检查：①proposal-schema 必备字段与枚举 ②proposal-target 靶存在性（modify/deprecate 在域、add 不在域，元素口径照图索引 id/*Id 定义键+已登记前缀，独立实现零耦合）③proposal-conflict 同靶 open 提案 change 矛盾 ④proposal-evidence 证据在档（仓根/提案目录相对+#锚点容许）；只解析 PROP-*.md；断言面 fixtures/proposal-pool AC1–6（票 18） | 已建（票 18） |
| `tools/semantic_service_core.py` | 语义服务四步瀑布可机判核心+CLI：显式锚定（前缀→模型→camp 面外判定在先，先阵营后存在性）、ID/名称解析（name/alias/属性标签/GLS term+alias 确定性分层匹配，不猜不模糊）、闭包/影响装配指令、拒答三分支（面外/仓内没有+缺件分层/禁用词+替代指路）与命中 ID 集——**自然语言成稿归 skill（提纯不重写）**；图消费经 `tools/graph_index.py` 子进程 `--json`（零耦合），禁用词表自实现（读域内 GLS status 含「禁用」，与 schema_check 是两个读者同真源）；CLI 退出码 0 answered/1 refused/2 配置错误；八问真域回归接 fixtures/semantic-service CORE-01–08（票 22） | 已建（票 22） |
| `tools/skill_deps_check.py` `tools/fixture_run.py` `tools/archive_check.py` 三闸 + `tools/ci.sh` | 从 sdd-flow2 实例化拷贝（含单测；fixture_run 新增 cmd-* 断言与占位 pending） | 已建（票 03 随迁） |
| `tools/install_skills.py` | 安装位同步与落闸：仓内 skills/ 正本 → ~/.agents/skills/ 安装位的 sync（先清后拷，只清本 skill 目录）、--check（漂移三型 missing/modified/extra + 孤儿检测）、--prune（孤儿清除，默认 dry-run，--yes 才删）、symlink 拒跑（退出 2）；注册表 `tools/install-registry.json` 由 sync 原子维护（孤儿三要素=登记过+安装位在+正本已删）；`tools/hooks/pre-commit`（core.hooksPath 启用）提交前跑 --check 拦漂移；断言表 tickets/12 AC1–4 + tickets/15 AC1–6；不进 ci.sh 四闸（安装位是仓外环境状态） | 已建（票 12；票 15 增强） |
