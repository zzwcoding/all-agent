# WeKnora × 个人知识库 × 本体 · 调研落盘（2026-09-22）

> 用途：**个人版本体 WeKnora**（个人知识库管理）PRD 前置调研。Owner 原始诉求："使用 all-agent 生产一个端到端项目——个人版本体 WeKnora，作为知识库管理，管理日常开发资料、想法、文档、书籍、技术感悟、工作业务；关键词：知识库、RAG、本体、建模、wiki、graphrag、知识图谱。"
> 方法：本机全盘检索（mdfind + 逐文件精读）× 网上一手信源核实。引用纪律照 RESOURCES.md：写论断回查原文，不凭记忆。

---

## 〇 一分钟结论

1. **All-agent 仓内 weknora 零命中**；但**本机其他仓有全套一手资料**：源码级深度调研 1 份（R10）、完整复刻学习仓 1 个（R11）、Neo4j GraphRAG 实操仓 1 个（R11）、本体×GraphRAG 课程底稿 7 篇（R11）、概念词条库 1 份（R11）。"个人版本体 WeKnora"不是从零起步，是站在已有的调研+复刻+方法论上做产品化。
2. **WeKnora 本体（腾讯，R10）**：企业级 RAG 知识库 + ReAct Agent + Wiki 三合一框架，Go 主服务约 47 万行，v0.8.0（2026-09-03），约 2.2 万 star（2026-09-10 实测 21,967）。默认 ParadeDB（PostgreSQL）一个库扛 BM25+pgvector；GraphRAG 走 Neo4j profile（每 chunk 一次 LLM 抽取实体关系）；Wiki Mode=LLM 从文档自治生成互链 Markdown+版本回滚；Lite 模式=sqlite-vec 单机零外部依赖——**个人版的直接形态参照**。
3. **概念对号已有定稿词条（all-agent-ex TERMS.md，R11）**：知识库=仓库（原文+切块+元数据）；Wiki=LLM 蒸馏的人读页面层；知识图谱=LLM 抽的实体关系网（无模式层，类型漂移）；RAG=消费技术不是存储物。这一族产品**没有本体**——"本体 WeKnora"的差异化正在这里：把 WeKnora 的"弱模式层（通用、无规则、改 prompt 无审）"换成**领域本体登记+闸**，即 **ontology-guided GraphRAG**。
4. **本体×GraphRAG 三接入点已定稿（teach-petro-agent 底稿 69，R11）**：A 建图段=抽取对号表（类型清单换成领域本体，治类型漂移）；B 图上=约束层（抽取结果过闸再入库，治幻觉边）；C 查询段=确定性前哨（语义瀑布先行精确入图，模糊降兜底，面外先拒）。**"本体不动引擎只接管说法"**——这是"个人版本体 WeKnora"区别于"再装一个 WeKnora"的核心设计资产。
5. **两条可走的工程路线待 Owner 拍板**（PRD 头号开放问题）：(a) 作为 All-agent 本体仓**第二业务域**（bohai 同款，skill+脚本形态，语义服务/MCP 消费）；(b) 走**第五期端到端实弹**（本体→聚合卡→devkit→sdd-flow 建真系统）——Owner 说的"生产一个端到端项目"与 (b) 吻合，但须拍板。
6. **Owner 已有真实知识资产**（/Users/divh/Documents/）：书籍资产（书籍全文 txt）、概念资产（书摘 txt+思维导图 png）、author-compiler/wiki（概念 wiki 页）——个人库首批素材的**真实形态**，PRD 的对象建模须对着它们校准，不是凭空设对象。

---

## 一 本机资料地图（全盘检索命中，逐份精读）

| # | 资产 | 路径 | 是什么 | 对本项目价值 |
|---|---|---|---|---|
| 1 | WeKnora 源码级调研报告（**R10**） | `/Users/divh/Downloads/agent-security-learning/WeKnora调研.md`（同文副本 `/Users/divh/Downloads/安全评估agent/WeKnora调研.md`） | 2026-09-10 浅克隆 Tencent/WeKnora@1c16db3（v0.8.0）逐文件阅读，三进程架构/文档管线/10 种检索引擎/混合检索 RRF/ReAct Agent/沙箱/Wiki/27 厂商模型接入/攻击面，全部论断附源码路径 | **产品蓝本事实底座**：功能面、架构选型、Lite 单机形态、"README 与代码不一致点"全部现成 |
| 2 | weknora复刻 学习仓（**R11**） | `/Users/divh/Downloads/agent-security-learning/weknora复刻/`（副本 `/Users/divh/Downloads/安全评估agent/weknora复刻/`） | Python 复刻 WeKnora 核心管线：SQLite+numpy 手写 BM25/余弦/图存储/Wiki，**四开关**（vector/keyword/wiki/graph）+**四维投影**（chunk 唯一事实源，向量/倒排/图谱/Wiki 全是派生物）；PRD+架构图 v1+lessons 已成套 | **管线机制的教学版实现**：四维投影/父子分块/RRF/ExtractConfig 抽取/Wiki 回滚全部有可运行参照 |
| 3 | neo4j-graphrag-ex 实操仓（**R11**） | `/Users/divh/Downloads/neo4j-graphrag-ex/` | 复刻 neo4j-partners/sample-graphrag：Cypher 建图/vector/fulltext 索引/三种 Retriever/SimpleKGPipeline 建图/GraphRAG 问答链/LLM 替你建图/MiniMax 供应商替换 | **工业版 GraphRAG 栈的一手实操经验**（向量检索找到门+图遍历进屋拿东西+LLM 答题） |
| 4 | teach-petro-agent 本体×GraphRAG 课程（**R11**） | `/Users/divh/Downloads/teach-petro-agent/lessons/`：53-治理本体仓 / 54-抽取式图谱 / 55-五流派速览BCE / 56-五流派擂台对账 / 67-Palantir落地链路 / 68-FDE与垂直模板 / 69-本体与GraphRAG三接入点 | 本体治理仓机制/逐 chunk LLM 抽取+类型闸/GraphRAG 五流派/Palantir Ontology/**三接入点缝合设计**（A 对号表/B 过闸/C 前哨，含完整伪代码与走查推演） | **"本体 WeKnora"的核心方法论已设计完**——底稿 69 可直接作为本项目的缝合设计输入 |
| 5 | all-agent-ex 概念词条库（**R11**） | `/Users/divh/Downloads/all-agent-ex/lessons/TERMS.md`（§RAG/知识库/Wiki 节 ：127-134、§GraphRAG vs 向量 RAG ：159-165） | 知识库/Wiki/知识图谱/RAG 与本体的对号表；隐含本体与类型漂移；WeKnora 与 GraphRAG 关系；三接入点定稿词条；灌图=取证+过闸；图的存储三层；Neo4j 定位 | **术语口径真源**：PRD 的 GLS 术语候选直接从这里取定义，不必新造 |
| 6 | all-agent-ex 深潜课图谱与 RAG 篇（**R11**） | `/Users/divh/Downloads/all-agent-ex/lessons/all-agent-deep-dive/04-组织与消费-图谱与RAG.md` | 图谱组织与消费的教学讲解 | 背景教材 |
| 7 | 本体论字幕稿（**R7 既有**） | `/Users/divh/Downloads/资料/本体论/`（Frank Coyle《为什么 Agentic 系统需要本体论》srt×2） | "Pydantic at the door, ontology at the ledger"；Agent 无副作用先行 | 本体必要性的立论弹药（已在用） |
| 8 | Palantir Ontology 演讲资料（**R11**） | `/Users/divh/Downloads/资料/data - AI - 演讲/本体/FDE必看 Ontology落地技术细节….知识.md`、`/Users/divh/Downloads/14分钟揭秘Palantir一堆文件如何变成Ontology.知识.md` | Palantir Ontology 落地细节与五层消费面 | 企业级本体先例（参照系，个人版按需裁剪） |
| 9 | WeKnora 安全工程对照与接入先例（**R11**） | `/Users/divh/Downloads/安全评估agent/agentjiaotu/docs/接入指南-weknora.md`、`docs/research/2026-09-10-WeKnora安全工程对照.md`、`docs/adr/0005-weknora-不拆件与防御分工.md` | 把 WeKnora 当外部知识源接入安全 agent 的实战：MCP 代理/沙箱策略/防御分工 | **已有"消费 WeKnora"的工程先例**；个人版若做安全边界可回查 |
| 10 | Langchain-Chatchat 上游源码（相关度低） | `/Users/divh/Documents/agent-learn/upstream/Langchain-Chatchat/` | 开源 RAG 框架源码 | 备查，不入主线 |
| 11 | **Owner 既有知识资产（PRD 对象建模的现实锚）** | `/Users/divh/Documents/书籍资产/`（书籍全文 txt）、`/Users/divh/Documents/概念资产/`（书摘 txt+思维导图 png）、`/Users/divh/Documents/author-compiler/wiki/`（概念 wiki 页+assets/concepts 结构） | 个人已积累的书/概念/ wiki 资料 | 首批入库素材的**真实形态**：全文 txt、书摘、图片、wiki 页——对象与属性设计必须装得下它们 |

---

## 二 WeKnora 是什么（R10 摘要 + 官方核实）

- **定位**：腾讯微信团队开源的企业级 LLM 知识管理框架（微信对话开放平台技术底座），三大能力：① RAG 快速问答；② ReAct Agent 智能推理（编排检索/MCP 工具/技能目录/沙箱/联网搜索）；③ Wiki 模式（Agent 从原始文档自治生成互链 Markdown 知识库+可视化知识图谱，支持人工编辑、版本历史、一键回滚）。另有跨会话长期记忆（v0.8.0）、多源同步（飞书/GitLab/Notion/语雀/RSS）、10 IM 渠道。
- **架构要点**（默认部署）：frontend(Vue3) + app(Go 主服务) + docreader(Python gRPC 解析微服务) + **ParadeDB(PostgreSQL：业务数据+BM25+pgvector 三合一，默认无需独立向量库)** + redis；可选 profile：neo4j（GraphRAG）/minio/searxng/qdrant/milvus 等。
- **文档管线**：25+ 解析器、OCR、自适应分层分块（父子块：子块进索引，父块只入库供回捞）、**分块可手工编辑且带版本历史**；入库后异步扇出：摘要+问题生成+**图谱抽取（每 chunk 一次 LLM 抽取）**+Wiki 生成。
- **检索**：10 种检索引擎适配；向量+关键词加权 RRF 融合；RAG 流水线=事件驱动插件链（查询理解/意图分类→并行检索（chunk+Neo4j 实体图并发）→重排（复合分+MMR）→合并→引用别名 fail-closed→流式生成）。
- **GraphRAG 的模式层=提示词里的通用 11 类清单**（R10/R11 双重核实）——弱模式：通用、无规则、改 prompt 无审。**这正是"本体 WeKnora"要换掉的部件**。
- **个人版最短路径参照**：Lite 模式=`DB_DRIVER=sqlite`（内置 sqlite-vec）+ 不配 Redis，零外部依赖单二进制。
- **成熟度**：v0.8.0（2026-09-03），一年破 2.2 万 star，约每 2-4 周一个版本；MIT（LICENSE 内嵌第三方声明）；官方建议内网部署。

## 三 概念对号（TERMS.md 词条精要，R11——PRD 术语候选的定义来源）

- **知识库**=仓库（原文+切块+元数据）；**Wiki**=LLM 蒸馏出的人读页面层（有版本历史、无语义治理）；**知识图谱**=LLM 从文档抽的实体关系网（广义 KG，无模式层）；**RAG**=消费技术不是存储物（相似度检索→塞上下文→LLM 生成带引用答案）；**本体**= ought/means 的登记（什么算什么：定义+规矩，图是模子压出来的边）。
- **向量 RAG vs GraphRAG 一句话**：普通 RAG 答"答案在某一段里"的问题；GraphRAG 答"答案散布在所有文档之间"的问题（全局综合/多跳跨文档）。代价：建图每份文档过 LLM，贵几个量级+更新要重建——先普通 RAG，"全局/多跳真的疼了"才升级。
- **隐含本体病根**：无本体系统里实体分类/关系命名由 LLM 预训练知识即席裁决——一本平均化、概率性、无主的本体；模型升级=无 changelog 的宪法换版。对策=分层：通用让隐含兜底，领域特殊必须显式登记过闸。
- **三接入点（缝合立场："本体不动引擎只接管说法"）**：A 建图段=抽取对号表（治类型漂移）；B 图上=约束层（过闸才立边，"图库对不上=图在执法"，治幻觉边）；C 查询段=确定性前哨（黑话归一→锚定直达→精确入图→模糊降兜底→面外先拒，治问法漂移）。投入判据：**语义错误代价越高的域越值得接**。
- **宪法先行 vs 人口先行**：WeKnora=人口先行宪法即兴（快、说法不保证一致）；All-agent=宪法先行人口后进（慢、可追溯可拒答）。合体形态=确定性检索（瀑布）+LLM 成稿；GraphRAG 的进化方向（ontology-guided 抽取）正是补宪法。

## 四 网上一手信源

1. WeKnora 官方仓：https://github.com/Tencent/WeKnora （README：三大核心能力；官网 https://weknora.weixin.qq.com ）
2. 微软 GraphRAG 官方文档：https://microsoft.github.io/graphrag/ （基于语料建知识图谱+社区摘要执行查询）
3. IBM: What is GraphRAG：https://www.ibm.com/think/topics/graphrag （2025-05，GraphRAG=RAG 高级版定义）
4. Microsoft Learn: Graph-Augmented RAG Patterns：https://learn.microsoft.com （向量搜索+图遍历的关系感知检索）
5. GraphRAG 完全指南（2025-08，第三方综述）：https://www.meta-intelligence.tech

## 五 综合判断："个人版本体 WeKnora"＝三样东西的合体

```
WeKnora 的管线（RAG/图谱/Wiki 四维投影，R10/R11 已吃透并复刻过）
× All-agent 的本体治理（宪法先行：本体仓唯一真源/语义 CI/GLS 术语闸/三接入点/提案池）
× 个人规模约束（单用户、本地优先、低摩擦捕获、素材=书籍全文/书摘/想法/开发资料/工作资料）
```

- 差异化主张（PRD 一句话的原料）：**知识库答"有什么"，Wiki 答"怎么读"，图谱答"和什么有关系"，本体答"什么算什么"——个人版本体 WeKnora = 四格齐备、且"什么算什么"有登记有闸的个人知识平台。**
- 核心张力（PRD 必答题）：**低摩擦捕获 vs 治理纪律**。想法/灵感要随手记（人口先行，先入库后治理），工作业务/开发资料要口径可靠（宪法先行，登记过闸）——个人版两头都要，分层治理是自然解：通用概念让隐含兜底，领域特殊（项目名/黑话/口径）显式登记。
- 与 All-agent 平台的关系：本项目天然是 **All-agent 端到端实弹的第一发**（AGENTS.md 第五期候选：本体→聚合卡→devkit→sdd-flow 建真系统），也是 F8 文档萃取器→本体→F3 图索引→F4 语义服务→F11 MCP 全链路的首个个人域实战。

## 六 对 PRD 的直接输入

- **对象候选族**（证据=Owner 原词）：知识条目（含来源类型）、文档、书籍、想法/感悟、开发资料、工作业务资料；参照物=Owner 既有资产形态（txt 全文/书摘/png/wiki 页）。
- **功能候选族**（证据=Owner 关键词）：入库/采集、检索问答（RAG）、图谱构建与检索（GraphRAG，本体对号表+过闸）、Wiki 生成与版本、语义服务/MCP 消费。
- **规则候选挂起**：Owner 输入零约束条款——不硬建，等开放问题收敛。
- **技术选型已有底**：检索栈可循 weknora复刻（sqlite+手写）或 WeKnora Lite（sqlite-vec）或 Neo4j 系（neo4j-graphrag-ex 实操过）三档；LLM 接入可循 agent-key/Keychain 纪律（R11 两仓同款）。
