# CONTEXT.md · All-agent 术语表

> 共享语言：代码命名、文档、对话都用这里的词。新术语先入表再使用。

## 产品

- **All-agent**：本项目——企业语义中台 + 建造/运行一体化平台。本体仓为唯一真源，多输入多输出，三循环自迭代。
- **本体仓（ontology repo）**：Git + YAML 承载的业务语义唯一真源（对象/行为/规则/事件/场景/主体/流程/报表/UI/映射/接口/术语模型）。
- **派生物（derived artifact）**：图谱索引、运行时语义缓存、导出开发包——全部可从本体仓重建，禁手改。

## 架构

- **前端（frontend/适配器）**：把输入（需求/数据库/源代码/文档）转成本体 YAML 草案的部件；只产草案，进仓必过 MR + 语义 CI。
- **后端（backend/生成器）**：把本体 YAML 变成输出（应用包/Skill/MCP/报告）的部件；只读仓，禁直连前端。
- **语义 CI（semantic CI）**：五级检查——L1 语法合法 / L2 引用与本体一致 / L3 指标·SQL·安全 / L4 权限·兼容 / L5 行为与检索回归（Golden Question + 出厂集）。L5 现状（票 44）：结构断言级已建（core 机判十二问 + 出厂集断言）；LLM 评分级=离线批评分器（12 问评分集 + rubric 锚定例 + l5_score.py 三采样中位聚合），按 design-l5-scoring 节奏触发——批收官软闸 / 发布前硬闸，不进每提交 CI，红灯走信号路由三分道。
- **出厂集（factory corpus）**：每个生成器/适配器的固定输入→确定性断言集，平台改版的回归闸（双门槛：全过 + 负样本不误报）。
- **信号路由表（signal routing）**：元循环的核心纪律——业务错→本体 MR；工程错→sdd-flow 票；元模型错→框架版本演进（CHANGELOG+版本号+迁移票伴随实现票）。
- **正本/安装位**：skill 的双位置——正本 `skills/<名>/`（仓内，受边界闸+归档闸治理）、安装位 `~/.agents/skills/<名>/`（Kimi Code 路由用）；`install_skills sync/--check` 维护两处一致，pre-commit 钩子（core.hooksPath 启用）拦提交时漂移。
- **人审闸（human review gate）**：生成物发布前的人确认承载机制（PRD 决策 2，ADR 0003）——审记旁档（`exports/reviews/`，逐版本追加不覆盖）+ 哈希锚定（`review_gate.py verify` 现算 sha256，本体再生即已审自动失效回落待人审，零宽限）+ 三档分级（manifest 免审 / skillpkg 首审+变更审 / devkit 全审，判档规则见 design-human-review-gate §3.3）；打回强制开单走信号路由表；published 态只预留字段不实现。

## 三循环

- **业务语义循环**：本体 → Agent 消费 → 三源信号（监督/自检/交互）→ 提案池 → MR（自动化止于提案）。
- **提案池/提案（PROP）**：三源信号归一成的标准化提案文件（`docs/proposals/PROP-<域>-NNN.md`），状态机 draft/open/accepted/rejected；自动化止于提案（`proposal_check` 做确定性冲突预检），进仓 MR 由人完成。
- **建造循环**：sdd-flow 四拍（讨论→约定→开发→检查）。
- **元循环**：跨层探针度量 → 信号路由 → 分道修复 → 定期体检；治理对象 = 平台自身与元模型。
