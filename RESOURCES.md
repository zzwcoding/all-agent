# RESOURCES.md · All-agent 信源清单

> 规则：写论断回查原文，不凭记忆。R 编号在 PRD/spec/底稿中引用。

| 编号 | 信源 | 内容 | 位置 |
|---|---|---|---|
| R1 | OMF 规范精读摘要（v6 全文 144k + v9 全文 64k 一手提取） | 11 模型字段级 schema、ID/ref 约定、校验门禁、版本演进、建模顺序 | `references/omf-spec-digest.md`；源仓 github.com/sharptoolbox/ontology_modeling_framework |
| R2 | 既有调研资产盘点（9 份稿） | DataBuddy/Ossie/ContextSeek/Data4A/刘镔辉笔记的核心主张与复用建议，含交叉印证矩阵 | `references/existing-research-inventory.md` |
| R3 | 技术选型调研 | YAML 解析=PyYAML、图索引=纯 Python 内存图、MCP=官方 SDK 轻量可行 | `references/tech-selection.md` |
| R4 | DataBuddy《从业务本体到持续进化》 | 4+1 语义能力域、五级语义 CI、S0–S8 检索瀑布、强类型中间态、三源建议池+四条红线 | 经 R2 索引；原文笔记 teach-petro-agent/references/data-agent-research.md |
| R5 | 渤海油田业务设定书 v3 | 首个业务域素材：8 表 DDL、指标口径库、治理角色链 | teach-petro-agent/docs/business-setting.md |
| R6 | sdd-flow2 设计案 | skill=深模块、四层半、两条验收主线 | docs/design-sdd-flow2.md |
| R7 | Frank Coyle《为什么 Agentic 系统需要本体论》 | 神经符号护栏："Pydantic at the door, ontology at the ledger"；Agent 无副作用先行 | /Users/divh/Downloads/资料/本体论/ 字幕稿 |
| R8 | 《Fundamentals of Analytics Engineering》 | 数据底座生命周期、语义层落地条件、治理三支柱 | /Users/divh/Downloads/资料/技术书籍/…/原书提取/ |
| R9 | DDD-as-code 方法论调研摘要（ContextMapper/EventModeling/jMolecules/Codely Blueprint/TUM 论文五源） | 四类设计件字段骨架与切片法、新鲜上下文纪律、ddd_check 静态可判子集依据，第四期 DDD 线全链注源 | `references/ddd-as-code-digest.md` |
| R10 | WeKnora 源码级深度调研（Tencent/WeKnora @ v0.8.0/1c16db3，2026-09-10 逐文件核实） | 三进程架构/ParadeDB 单库 BM25+pgvector/文档管线父子分块/加权 RRF/GraphRAG（Neo4j+逐 chunk LLM 抽取+通用 11 类弱模式）/Wiki Mode/ReAct Agent/Lite 单机模式 | `/Users/divh/Downloads/agent-security-learning/WeKnora调研.md`；上游 github.com/Tencent/WeKnora；索引 `references/weknora-personal-kb-digest.md` |
| R11 | 本体×GraphRAG 教学资产群（weknora复刻仓 + neo4j-graphrag-ex 仓 + teach-petro-agent lessons 53–69 + all-agent-ex TERMS.md） | 四维投影四开关教学实现/Neo4j GraphRAG 全流水线实操/本体×GraphRAG 三接入点定稿（A 对号表/B 过闸/C 前哨）/知识库·Wiki·图谱·RAG×本体概念对号 | 各仓本机路径见 `references/weknora-personal-kb-digest.md` §1 |
| R12 | 微软 GraphRAG 官方文档 + IBM GraphRAG 定义（2025） | GraphRAG 方法定位：语料→知识图谱→社区摘要→全局查询；与向量 RAG 的分工（段内问题 vs 跨文档问题） | https://microsoft.github.io/graphrag/ ；https://www.ibm.com/think/topics/graphrag |
| R13 | HIS 医院数据报表平台实训文档群（GitHub `luzai02/his-`，2026-09-25 经 gh API 落盘五件） | 第三域 his 素材真源：PRD 960 行（8 业务域/15 源表/7 ADS 指标表/6 报表模块 18 API/页面交互）+详细设计 1215 行（ADS 表字段级 schema/双数据源/API 设计）+前后端与 Kafka 设计；八模型素材全齐 | `references/his-source/` 五件；上游 github.com/luzai02/his-（公开仓无 License 文件=仅文本素材引用，细稿为本仓改写，第六批方案 §4.3 证据边界） |

数字弹药（引用时注 R2/R4）：语义自动覆盖 70~80%；企业可被 AI 理解的数据仅 5~10%；95% 生死线阶梯（语义层 70-75% → +记忆反馈 80-90% → +Loop Engineering 逼近 95%）。
