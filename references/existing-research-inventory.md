# All-agent · 既有调研稿盘点（可复用信源清单）

> 盘点日期：2026-09-17。范围：teach-petro-agent 仓库 `references/` 下 4 份调研报告 + 1 份演讲笔记 + 2 份背景稿（JD/公司），以及 `docs/ae-frontier-plan-v3.md` 第 1 节收录的六篇演讲产业叙事（Data4A Meetup / OceanBase ContextSeek / Datastrato-Gravitino / Datastrato 刘镔辉 / 腾讯云 TBDS DataBuddy / DataBuddy 公众号两篇 + 圆桌）。
> 用途：为 All-agent（企业语义中台：本体仓 + 多输入多输出 + 三循环）的 PRD 论证、本体 schema 设计、语义 CI、运行时检索、治理/元循环提供可引用的信源与数字。术语对齐 All-agent `CONTEXT.md`。
> 引用纪律：原始出处的外链见各报告末节"引用来源汇总"，本清单只登记报告路径与关键论点；数字均以原报告核实口径为准（"搜索摘要核实"的条目引用时注意降级表述）。

---

## 0. 最重要的 3 条信源（结论先行）

| # | 信源 | 为什么对 All-agent 最重要 |
|---|------|--------------------------|
| 1 | **腾讯云 TBDS《从业务本体到持续进化》（DataBuddy）**（ae-frontier-plan-v3.md §1.1⑤） | 与 All-agent 架构逐部件同构：本体先行映射后置、4+1 语义能力域（Glossary/Ontology/Metric/Playbook+Governance）、Semantic-as-Code（Git 权威源+五级语义 CI）、S0–S8 检索瀑布、强类型中间态五段、受控进化三源建议池+四条红线——几乎就是 All-agent 本体仓+语义 CI+业务语义循环的行业蓝本 |
| 2 | **Datastrato/Gravitino《开放语义层 AI 基础设施》（Apache Ossie/OSI）**（§1.1③） | 给出语义中台的治理对象划分（Domain/Glossary/Semantic view/Data asset × Governance Envelope）与开放交换格式（YAML/JSON import/export），是"本体仓作为唯一真源 + 派生物可重建"的标准层背书；金句"真正让 AI 理解的数据只占企业全量 5~10%"是 PRD 立论数字 |
| 3 | **《从元数据到 Data Agent》演讲笔记（Datastrato 刘镔辉）**（references/datastrato-trusted-dataagent-notes.md） | 唯一一份"乙方在真实企业把问数 agent 推到生产"的一线复盘：六轮收敛方法论（每轮收敛一种自由度）、可信资产评分卡 8 信号、verified metric 治理闭环、执行前校验链、Badcase 资产化+漂移五型——直接喂 All-agent 的治理循环（业务语义循环）与元循环设计 |

补充（PRD 数字弹药）：Data4A Meetup 的"Agent 自动生成语义可覆盖 70~80% 工作量" + 圆桌的"95% 生死线"（语义层 70-75% → +记忆反馈 80-90% → Loop Engineering 逼近 95%），与 5~10% 并列为本清单三大立论数字。

---

## 1. 总览表（9 份稿）

| # | 稿 | 路径 | 性质 | 与 All-agent 相关度 |
|---|----|------|------|--------------------|
| 1 | 报告一：OpenAI×Anthropic 官方文章调研 | references/data-agent-research.md | 官方一手文章精读（21 引用） | ★★★☆（Harness 工程化/评估/护栏方法论） |
| 2 | 报告二：Data Agent 开源项目调研 | references/data-agent-opensource.md | GitHub 逐仓核实（28 引用） | ★★★（语义层 MDL/M-Schema/底座轮子） |
| 3 | 报告三：Data Agent 前沿速览 | references/data-agent-frontier.md | 商业产品/协议/安全/评估（13 引用） | ★★★★（三产品 converged 打法+协议层+CaMeL） |
| 4 | 报告四：AE/语义层运动/Genie | references/analytics-agent-genie.md | dbt+OSI+Genie bp 验证（9 引用） | ★★★★（语义层=控制点的产业标准背书） |
| 5 | 演讲笔记：从元数据到 Data Agent | references/datastrato-trusted-dataagent-notes.md | 企业现场一线复盘（Datastrato 刘镔辉） | ★★★★★（治理循环落地方法论） |
| 6 | R23：石油行业调研 | references/petro-it-refs.md | 知网 12 篇精读（业务设定底稿） | ★★★（如 All-agent 需行业实证/试点叙事） |
| 7 | JD 拆解 | references/jd-breakdown.md | 岗位考点清单 | ★（仅作 PRD"需求约束"参考，非语义中台素材） |
| 8 | 公司调研：海能平台 | references/company-research.md | 公开网络调研 | ★★（PRD 目标客户语境/信任叙事） |
| 9 | v3 方案 §1.1：六篇演讲产业叙事 | docs/ae-frontier-plan-v3.md（§1.1） | 演讲知识稿提炼（含 DataBuddy 两篇+圆桌） | ★★★★★（本体仓/语义 CI/检索瀑布/受控进化全在这） |

另：`references/extracts/`（architecture-process / governance-quality / indicators-and-data 三份长提取件）为 R23 的深化素材，本清单不展开，需要业务指标口径时再查。

---

## 2. 分稿明细

### 2.1 报告一《OpenAI × Anthropic 官方一手文章调研：Data Agent》

| 项 | 内容 |
|----|------|
| 来源标识 | `references/data-agent-research.md`；调研 2026-09-14；21 条官方引用（openai.com / anthropic.com 全域名）。最重要一篇：OpenAI《Inside our in-house data agent》(2026-01-29) |
| 核心主张 | ① workflow vs agent 二分，"能用简单方案就别用 agent"——All-agent 的建造循环应显式编图而非放任自主循环；② OpenAI 内部数据 agent 的**六层上下文**（元数据血缘/历史查询/专家口径/产数代码/周边知识/运行时核对）= 给 Agent 喂语义的官方需求清单，直接对应本体仓"多输出"要供的上下文面；③ **golden SQL + 执行结果双重比对**（拒绝朴素字符串匹配）+ 持续单元测试/生产金丝雀 = 语义 CI L5 与出厂集的方法论母版；④ 权限穿透（pass-through permissions，表/行/列级）= "语义查询不扩权"的官方基准；⑤ 2026-06-03 OpenAI 关停低代码 Agent Builder/Evals 转 Agents SDK——"代码即语义/工作流"路线的官方背书（All-agent 本体 YAML+Git 路线的佐证） |
| 可引用数字/金句 | "6 层上下文"；3,500 内部用户 / 600+ petabyte / 70,000 数据集；MCP code execution "150,000→2,000 token，节省 98.7%"；多智能体 ≈ 15× 聊天 token；"agentic 系统常以延迟和成本换任务表现"；评估集"20-50 个真实失败任务起步"；三类 grader 口诀"能用确定性就用确定性，必要时用 LLM，审慎用人工" |
| 复用建议 | **PRD 论证**（六层上下文清单、评估方法论、金丝雀）；**语义 CI L5/出厂集**（golden 结果集双比对）；**运行时检索**（just-in-time / stored queries=轻量标识符）；**元循环**（"评产出不评路径"原则） |

### 2.2 报告二《Data Agent 开源项目调研》

| 项 | 内容 |
|----|------|
| 来源标识 | `references/data-agent-opensource.md`；调研 2026-09-14；GitHub API 逐仓核实（28 引用） |
| 核心主张 | ① **WrenAI 的 MDL 语义层**（声明 models/columns/relationships/metrics + instructions + queries.yml）是"本体仓声明式承载业务口径"的开源同构物；② **XiYan-SQL 的 M-Schema** 半结构化 schema 表示法是本体仓到"Agent 可消费上下文"的具体格式参照；③ **SuperSonic 的 Semantic Corrector**（规则+LLM 修复语义查询）与 Chat Memory（历史轨迹 few-shot）= 语义 CI 的 L3 侧与运行时缓存半边的成熟参照；④ 头部框架批量死亡（Vanna 归档/Dataherald 停摆/AgentKit 关停）——"教学和工程都不要绑框架，要绑底座"，支撑 All-agent"本体仓为唯一真源、派生物可重建"的架构论点；⑤ sqlglot/sqlfluff 34/28 方言均**无金仓/达梦**（近似方言+差异清单路线） |
| 可引用数字/金句 | BIRD 人类基线 92.96% vs 榜首 82.39%（华为 DataGallery-Text2SQL，2026-08）；Spider 2.0 发布时 o1-preview 仅 17.1%、GPT-4o 10.1%（Spider 1.0 为 86.6%）→ Lite 榜首 76.23%——"17.1%→76.23% 的差距主要被工程吃掉"；Vanna 23.8k star 归档（2026-03-29）；"凡以框架为底座的计划都应中止或改为历史案例" |
| 复用建议 | **本体 schema 设计**（抄 MDL/M-Schema 的字段组织）；**PRD 论证**（企业级难度数据点、不绑框架的架构论据）；**运行时检索**（SuperSonic 混合解析、历史查询 few-shot）；若 All-agent 输出物含 SQL 生成器，sqlglot 作 AST 闸依赖 |

### 2.3 报告三《Data Agent 前沿速览（2025H2~2026-09）》

| 项 | 内容 |
|----|------|
| 来源标识 | `references/data-agent-frontier.md`；调研 2026-09-14；13 条全部当日逐字抓取 |
| 核心主张 | ① **三大商业问数产品（Cortex Analyst / Genie / Fabric）已收敛到同一套打法**：语义层承载口径 + verified 问答对双用（引导生成+评估集）+ 权限穿透 + 强制只读 + 治理审计——"没有魔法，全是工程纪律的产品化"，是 All-agent"企业语义中台"需求的产业级需求证明；② **Fabric intent layers**（组织>角色>开发者>用户）= 指令层级的产品化，对应 All-agent 信号路由的优先级设计；③ **MCP 2026-07-28 版**（Elicitation=服务端反向澄清、Tasks=长任务断点续传）与 **A2A/Agent Card** ——All-agent"多输出"若含 MCP/A2A 形态，协议对应物现成；④ 安全三道防线：lethal trifecta（私数据×不可信内容×外发通道）→ instruction hierarchy（训练层）→ CaMeL（系统层，控制流/数据流抽取+工具边界执法）；⑤ BIRD-CRITIC 把评估从"生成准"推进到"修得好"——执行反馈+修复回路是主战场 |
| 可引用数字/金句 | "结果裁剪 25 行×25 列，为对话式洞察而非返回完整数据集"（Fabric）；CaMeL：77% 任务可证明安全 vs 无防御 84%；BIRD-CRITIC：o1-preview 35.5% vs 人类专家 ~80%；"lethal trifecta"判词"LLMs are unable to reliably distinguish the importance of instructions based on where they came from"；mem0 ADD-only 记忆（LoCoMo 92.5 为 README 自述数字） |
| 复用建议 | **PRD 论证**（三产品 converged = 需求收敛证据）；**语义 CI**（verified 问答对双用）；**元循环/治理**（intent layers 四层优先级、lethal trifecta 风险模型、CaMeL 边界执法）；**多输出**（MCP Elicitation/Tasks、A2A Agent Card 的输出形态映射） |

### 2.4 报告四《Analytics Engineer 转型、语义层运动、Analytics Agent 品类与 Genie》

| 项 | 内容 |
|----|------|
| 来源标识 | `references/analytics-agent-genie.md`；调研 2026-09-14；9 引用（dbt/OSI/Salesforce/ThoughtSpot/Genie bp） |
| 核心主张 | ① **OSI（Open Semantic Interchange）已定稿**：Snowflake 牵头、dbt/Salesforce/ThoughtSpot/Amazon/Google/DataHub 等参与，YAML 语义模型跨平台交换——语义层从"产品功能"变成"AI 时代数据基础设施标准"，All-agent 本体仓 YAML 格式的行业标准对位物；② "口径打架"的原始诊断（分析师 "knew just enough SQL to be dangerous"）与解法（把业务逻辑移进建模层，define once, reuse everywhere）——All-agent"业务定义优先"的出处级论证；③ Genie best practices：**问数 agent 的准确率大部分是数据侧准备出来的**——表要少（≤5 建议/50 上限）、metric view 预定义、注释是地基、**结构化 SQL 定义优先于文字指令**（文字是 last resort）、example SQL+benchmark 双用 |
| 可引用数字/金句 | "≤5 tables / 硬上限 50"；"Structured definitions through SQL are more reliable and maintainable than plain text guidance"；Salesforce："ending semantic drift"、"trustworthy agentic AI"；"You should be your agent's first user"；"If a metric definition changes in dbt, it's refreshed everywhere it's invoked" |
| 复用建议 | **PRD 论证**（OSI 标准+semantic drift 叙事）；**本体 schema 设计**（Glossary/Metric 域字段与"结构化优先"原则）；**语义 CI**（example SQL+benchmark 双用、"同一问题多问法"）；**元循环**（"自己当第一个用户"→审核流） |

### 2.5 演讲笔记《从元数据到 Data Agent》（Datastrato 刘镔辉，2026-09）

| 项 | 内容 |
|----|------|
| 来源标识 | `references/datastrato-trusted-dataagent-notes.md`；演讲截图 23 张 + SRT 转录 ~33 分钟；唯一"乙方企业现场生产化"一线复盘 |
| 核心主张 | ① 概念演进 Text-to-SQL→ChatBI→Data Agent，**问题边界越往后对数据上下文要求越高**；"SQL 能跑 ≠ 业务正确"，取数是生产化第一道门槛；② **六轮收敛方法论**：每轮不是加模块而是收敛一种自由度（自由搜索→可信资产评分卡；自由解释→Semantic Object IDs；自由生成→verified metric；自由执行→执行前校验链 policy→freshness→lineage→audit；自由修复→Badcase 资产化+回归套件+漂移五型）；③ **面向 Agent 的新型元数据**：业务含义/owner/生产废弃/字段级血缘/行列权限/工具边界/freshness-quality-usage-drift，暴露为 discover/describe/validate/audit 四 API——"Agent 时代元数据要变成执行前上下文"（= Metadata Control Plane 的一线版）；④ **责任链闭环**：Metric Owner/Data Owner/Security/Agent Owner/Review Board——"生产化的难点不只是模型和 harness，而是责任链是否能闭环"；⑤ 评测集方法论："一定不能自己写"——业务给 10-20 真实问题+AI 扩写到 ~100 题+**每题手算金标**；⑥ 指标歧义澄清：N 个候选指标各算一遍把差异摆给用户选 |
| 可引用数字/金句 | 上山模型：Base Camp→Camp4，山顶=高频任务 ~95% 准确，最后 5% 拼透明化；"专业用户不怕答案有问题，怕有问题还是黑盒"；"客户不是缺少数据，而是缺少一条 Agent 可以安全、准确、可审计调用的数据链路"；最小闭环：1 业务域+5-10 verified metrics+10-20 真实问题；可信资产评分卡 8 信号（owner/production-deprecated/domain-tier/lineage/freshness/policy-tag/usage/quality）；"大模型主要用在语义资产之前的链路"；裸 GPT-5 在 BIRD 只排第 31——"榜首和裸模型的差距就是上下文工程，不是模型代差" |
| 复用建议 | **治理循环（业务语义循环）**：六轮收敛=现成的方法论骨架；三源信号/建议池/owner 裁决的直接参照；**本体 schema 设计**：可信资产评分卡、Semantic Object IDs、drift 五型入本体元数据；**元循环**：Badcase 资产化+回归套件、评测集构建法；**PRD 论证**：上山模型、7 问清单、最小闭环=MVP 切分模板 |

### 2.6 R23《石油行业大数据/信息化方案调研》

| 项 | 内容 |
|----|------|
| 来源标识 | `references/petro-it-refs.md`；调研 2026-09-15；知网 12 篇核心精读 + Energistics/华为官网 |
| 核心主张 | ① 中海油数据治理体系总纲：组织/目录/标准/质量/安全/平台；原则含"采用分离、源头治理"；② 数据资产目录树形五层（L1 主题域分组→L5 属性级）、6 大业务域——**本体仓按业务域组织对象的行业先例**；③ 数据标准 6 专业 40 余册、9000+ 数据集、建模借鉴 POSC；④ 真实指标口径库：开发指标 21 项清单、措施评估公式（有效率 η=N_y/N_z、递减增油口径）、能效三级指标体系——本体仓 Metric 域的"真实业务粒度"样例；⑤ 首次实现行级数据加密和动态脱敏——语义查询不扩权的行业语境 |
| 可引用数字/金句 | 梦想云统一数据湖 1.7PB / 15 个专业 / 16 家油气田企业；"两统一、一通用"；L1→L5 五层目录；金仓"TPS 提升 35%、成本降低 50%"（vendor 数字，注意立场） |
| 复用建议 | 仅当 All-agent 需要行业实证/试点叙事时使用：**PRD 论证**（目标客户的治理现状=企业语义中台的"为什么是现在"）；**本体 schema 设计**（6 业务域+五层目录+真实 Metric 清单可作本体仓 seed 数据）；一般不进语义中台方法论主线 |

### 2.7 JD 拆解（相关性判断：低）

| 项 | 内容 |
|----|------|
| 来源标识 | `references/jd-breakdown.md`；用户提供的岗位 JD 拆解（2026-09） |
| 与 All-agent 的关系 | **基本不相关**。它是"考核什么"的清单（NL2SQL/RAG/工具调用/编排/网关/国产化），不含语义中台、本体、Metadata Control Plane 等素材。仅一处复用价值：All-agent PRD 写"目标用户/岗位能力约束"时可引用其 A/B/D/E 条目作为输入端形态（问数/问答/工具/编排）。不必入清单正文 |

### 2.8 公司调研《中海油"海能"平台》（相关性判断：低-中）

| 项 | 内容 |
|----|------|
| 来源标识 | `references/company-research.md`；调研 2026-09-12；公开网络（可信度已分级标注） |
| 与 All-agent 的关系 | **背景语境稿**，非方法论素材。可复用两点：① 目标客户画像与信任语境——"问数+问答"双轮是公开确认方向、"问智"未公开（引用需留余地）；② 央企私有化部署/国产底座/审计合规的语境，支撑"企业语义中台必须权限穿透+可审计"的 PRD 前提。仅进 PRD 的"背景与约束"一节 |

### 2.9 v3 方案 §1.1《六篇演讲的产业叙事》（含 DataBuddy 两篇 + 圆桌）

| 项 | 内容 |
|----|------|
| 来源标识 | `docs/ae-frontier-plan-v3.md` §1.1（六篇演讲知识稿 + 2 篇 DataBuddy 公众号文章 + 圆桌，2026 年中行业快照） |
| 核心主张 | 见下分演讲 |

**① Data4A Meetup《从人用数据，到 Agent 用数据》**

| 项 | 内容 |
|----|------|
| 核心主张 | 三代演进 NL2SQL（翻译）→ChatBI（交互）→**Data Agent（任务完成）**；生产化三维度：语义（Schema≠业务含义）、安全（权限≠任务授权，授权要 intent-focused）、效率（更多上下文≠更好答案）；架构判断 **Engine-Centric→Metadata-Centric**，Metadata Control Plane 成为控制平面；三步走 Connect（Gravitino/Unity Catalog 统一元数据）→Understand（OSI 语义标准）→Operate（Harness+Loop Engineering） |
| 数字/金句 | "Data Agent is not a chatbot over databases. It is a governed task execution system over enterprise data."；**"Agent 自动生成语义可覆盖 70~80% 工作量"**，业务方从定义者变确认方 |
| 复用建议 | **PRD 论证**（第一立论句+演进叙事）；**元循环/治理**（AI 出候选、人出裁决的三源思想源头）；"多输入"适配器的立项依据（语义可自动生成 70-80%） |

**② OceanBase ContextSeek《Agent 数据底座的进化论》**

| 项 | 内容 |
|----|------|
| 核心主张 | 两条自进化路径分歧：Agent 自进化（经验绑死框架）vs **上下文底座进化**（经验沉淀在数据层，跨框架复利）——All-agent"本体仓为唯一真源、派生物可重建"的进化论论证；ContextSeek"上下文的插座"：一切皆 ContextItem（source_type 定初始置信度，无 provenance 不入库）、四路召回+**L0/L1/L2 分层**（L2 抽象默认消费、L0 原文按需下钻）、Scope 隔离（tenant→project→subject，防串味）、Provenance 置信度表+Link 证据链 DAG（Noisy-OR 综合）、raw→extracted→knowledge→skill 显式管道+梦境机制 |
| 数字/金句 | Provenance：human_input 1.0 → document 0.8 → agent_inference 0.6 → dream 0.3；行业坐标 Prompt Engineering(2022-23)→Context Engineering(2025)→**Harness Engineering(2026)**："我该如何闭环，它才可靠？" |
| 复用建议 | **本体 schema 设计**（provenance/置信度/证据链字段、来源类型枚举入本体元模型）；**运行时检索**（L0/L1/L2 分层+Scope 边界=检索瀑布的分层先例）；**元循环**（梦境机制=跨层探针与"发现模式，非事实"的灵感提权）；仓库：github.com/ob-labs/contextseek |

**③ Datastrato/Gravitino《开放语义层 AI 基础设施》（Apache Ossie / OSI）**

| 项 | 内容 |
|----|------|
| 核心主张 | 数据接口 **from SQL to intent**："Agents assemble a plan before a query reaches an engine. The quality of that plan depends on governed business meaning."——语义层从"提升一致性"升级为**控制点**；**Apache Ossie**（OSI 2026-06 进 Apache 后改名）：YAML/JSON 可移植语义模型，每平台一条 import+一条 export；**interchange ≠ production service**——标准之外四件生产的事：metric execution / semantic service（registry/versioning/ACL）/ concept alignment（domain/glossary/**ontology graph**）/ agent safety（verified context+policy checks）；**四个治理对象**（Domain/Glossary term/Semantic view/Data asset）× Governance Envelope（Stable ID·Owner·Role·Version·Certification·Audit）；Agent 取数五步 **Scope→Resolve→Plan→Execute→Explain**；落地四 Gate：Align→Register→Resolve→Federate；企业建议自底向上 |
| 数字/金句 | **"Semantic lookup never expands the caller's authority"**（语义查询永不扩大调用方权限）；**"真正让 AI 理解的数据只占企业全量 5~10%"**（冷启动现状判断）；"每个平台一条 import + 一条 export" |
| 复用建议 | **本体 schema 设计**（四个治理对象+Governance Envelope 字段=本体对象的最小元数据集；Ossie YAML=本体仓格式兼容目标）；**多输入多输出**（"一条 import+一条 export"=前后端适配器的交换格式依据）；**治理循环**（Envelope 六件套、四 Gate=本体仓冷启动路线）；**PRD 论证**（5~10% 数字、from SQL to intent） |

**⑤ 腾讯云 TBDS DataBuddy《从业务本体到持续进化》（全场信息密度最高）**

| 项 | 内容 |
|----|------|
| 核心主张 | 产品定位 **Agent 原生私域数据工作台**：五段式架构 数据底座→语义控制面→Agent Runtime→受控执行→持续进化（"在现有数仓之上补足业务，而不是重建"）；一个 AUM 问题隐藏六类业务决定；**4+1 语义能力域**：Glossary（术语/同义词/缩写/禁用词+Owner+有效期）/ Operational **Ontology**（对象/属性/关系/约束/有效时间/Action）/ Metric（公式/粒度/时间/单位/维度/过滤/零分母/SQL）/ Playbook（触发意图/步骤/工具/缺参/HITL/输出合同）+ Governance 横切（Owner/权限/状态/版本/质量/影响分析/审批/审计/发布/回滚）；**本体先行，映射后置**（"Schema 与历史 SQL 是证据，不是最终业务权威"）；六阶段冷启动 Pipeline（本体草稿→确认发布 Git MR→范围过滤→候选生成→精评决策→激活治理）；**Semantic-as-Code**：Git 是语义权威源（"被治理的是版本化业务契约，不是在线业务状态"），权威性=Commit 快照+受控合并+CI 验证+Owner 审批+可验证发布物；**五级语义 CI**（L1 Schema→L2 引用与本体一致→L3 指标/SQL/安全→L4 治理/权限/兼容→L5 行为与检索回归：Golden Question/SQL/Result+负样本+ACL+拒答）+ Shadow Build；**S0–S8 检索瀑布**（S0 固定边界 Identity/Commit/ACL→S1 显式锚定 @Entity/@Metric/Stable ID→S2 对象装配引用闭包→S3 确定性检索→S4 混合召回→S5 受限图扩展 1-2 跳→S6 资格与歧义/拒答→S7 回读权威源校验 ID/Hash→S8 发布与评测）；**强类型中间态五段** IntentSpec→SemanticContext→SemanticPlan→ExecutionPlan→EvidencePack（"模型：理解与提出计划；语义编译器+Harness：验证、授权、执行、审计与失败关闭"）；**受控进化**：三源信号统一建议池（监督源 Benchmark/自检源 实体体检/交互源 Runtime）+四条红线（不直接改主干、只提 MR 不自行合并、不手改派生物、高影响人工审批）+"一次反馈=一处根因=一个 MR"+EA/EX/ESM 三评测指标（执行对了≠理解对了）；运营：5 角色×5 节奏，**自动化止于提案，责任归于 Owner** |
| 数字/金句 | "本体先行，映射后置"；"被治理的是版本化业务契约"；"一次反馈 = 一处根因 = 一个 MR"；"自动化止于提案，责任归于 Owner"；S0-S8 全链可早停 |
| 复用建议 | **全部件对照物**：本体仓=4+1 能力域+Semantic-as-Code；语义 CI=五级 CI 直接对齐 All-agent CONTEXT.md 的 L1-L5；运行时检索=S0-S8 瀑布；治理循环=三源建议池+四条红线（即 All-agent 业务语义循环的行业母版）；本体 schema 设计=强类型中间态五段（前后端接口契约的参照） |

**⑥ DataBuddy 公众号两篇（产品视角补充）**

| 项 | 内容 |
|----|------|
| 核心主张 | **动作四级风险分级**（回答出错→查询出错→生产 DDL/DML/发布→外联；"Agent 从生成内容走向改变状态"，应对原则"风险越高，确定性控制越前移"）；任务托管三标准（产物可定位/动作可回放/结果可核验）；分层封装"**把确定性交给程序，把判断留给模型**"（原子能力→程序化 Tool→业务 SOP Skill→主 Agent）；语义四要素+**SemQL** 编译（语义召回→SemQL→SQL）+覆盖度分级策略（完整命中 SemQL/部分命中受约束 NL2SQL/未命中加严）；**信任低谷**死循环（语义资产少→准确率低→不敢用→没反馈）破局靠双输入；**记忆四层作用域**（Session→Personal→Team→Enterprise，晋升过两道关，"不能因为一条经验用得多就自动当企业真相"）；双引擎护栏（规则+HITL 同步阻断 + LLM 审计异步复核）；SQL 三阶段（生成前限域/执行前收敛/执行后留证）；评测三层判分（确定性校验+多模型盲判+人工标注） |
| 数字/金句 | "风险越高，确定性控制越前移"；"把确定性交给程序，把判断留给模型"；"不能因为一条经验用得多，就自动当企业真相"；四级风险分档 |
| 复用建议 | **治理循环/元循环**（四级风险分档=信号路由表的风险维度；记忆四层=Enterprise 层晋升两道关即本体仓入仓闸门的话术）；**运行时检索**（SemQL+覆盖度分级=多输出的确定性/生成性双路）；**PRD 论证**（信任低谷=冷启动难题的产业表述） |

**⑦ 圆桌《Agent 时代，开源数据栈的未来》（Doris/Gravitino/SeaTunnel/顾问）**

| 项 | 内容 |
|----|------|
| 核心主张 | **95% 生死线**：客户普遍要求 95% 才上线；无 memory/context 只有语义层 ≈70-75%，+memory/feedback loop→80-90%，逼近 95% 靠 Loop Engineering（self-healing）；**Context Layer ≠ Semantic Layer**（硅谷开始弃用"语义层"一词）；YAML vs Markdown 之争（落地障碍是"用户不想定义语义层"，但"独立的层存在+决定生死线"方向确定）；MCP 不适合数据分析的争论（一来一回 1-2MB 塞上下文）；知识提供三流派（文件派/结构化派/参数派）未收敛；**Tools vs 语义层是连续函数**（"让模型做选择题而不是问答题，准确率立刻上 90%"）；FDE 角色之争；语义层建设=把 Data Governance 从事后变事前 |
| 数字/金句 | 70-75% → 80-90% → 95%（生死线阶梯）；"让模型做选择题而不是问答题，准确率立刻上 90%"；"语义层=把治理从'事后'变'事前'" |
| 复用建议 | **PRD 论证**（95% 生死线阶梯=三循环自迭代必要性的数字论证：语义层只能到 70-75%，闭环才到 95%）；**风险与反方观点登记**（YAML vs 自然语言、MCP 边界之争——All-agent 答辩时要能应对） |

---

## 3. 交叉印证矩阵（同一主张的多源背书）

| 主张 | 互证来源 | 强度 |
|------|---------|------|
| 语义层是 Agent 时代的控制点（Metadata/Semantic Control Plane） | ①Data4A、③Datastrato/Ossie、⑤DataBuddy、报告三三产品 converged、报告四 OSI | 五源，最强 |
| 本体先行、AI 出候选人出裁决 | ①Data4A（70-80%）、③Datastrato（concept alignment）、⑤DataBuddy（本体先行映射后置）、演讲四笔记（语义映射=AI 辅助+人工定稿） | 四源 |
| Semantic-as-Code：Git 权威源+分级 CI+可验证发布物 | ⑤DataBuddy 五级 CI（唯一完整版）、报告一 OpenAI Agents SDK 代码优先、演讲四笔记 verified metric 治理闭环 | 三源 |
| 强类型中间态/计划先于执行 | ⑤DataBuddy 五段、③Datastrato（Agents assemble a plan before a query reaches an engine）、报告一 SchemaFlow（Pydantic 阶段契约） | 三源 |
| 语义查询不扩权/权限穿透 | ③Datastrato、报告一（pass-through×3 篇）、报告三（Fabric intent layers）、R23（行级加密动态脱敏语境） | 四源 |
| 受控进化：三源信号+自动化止于提案 | ⑤DataBuddy、演讲四笔记（Badcase 资产化+回归）、报告三（mem0 ADD-only 旁证） | 三源 |
| 检索是协议不是搜索（分层瀑布、显式锚定优先） | ②ContextSeek（L0/L1/L2）、⑤DataBuddy（S0-S8）、报告一（just-in-time/stored queries） | 三源 |

## 4. 使用注意

1. **搜索摘要核实降级**：报告四的 OSI 四条来源、报告一 [13][17][20][21] 未逐字抓取，正式引用时避免逐字引号。
2. **vendor 数字标注立场**：金仓"TPS+35%/成本-50%"为厂商博客；mem0 基准为 README 自述；引用时注明"厂商口径"。
3. **时效**：全部为 2026-09-14/15 核实快照；star 数、榜单、产品名（OSI→Ossie→？）仍在变动，PRD 引用时带日期。
4. **与 All-agent 术语对齐**：本清单的"本体仓/语义 CI 五级/信号路由表/出厂集/三循环"按 All-agent `CONTEXT.md` 口径书写；DataBuddy 的"语义控制面"≈All-agent 的"本体仓+语义 CI"，"持续进化"≈"业务语义循环"。
