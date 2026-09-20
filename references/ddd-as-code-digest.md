# 调研落盘 · DDD-as-code 方法论（ddd-modeler 设计输入）

> 日期：2026-09-20。用途：第四期 DDD 线拆票方案（docs/第四期DDD线拆票方案.md）的外部依据。
> 委托调研（explore 子代理，五题框架），本文件为结论蒸馏；来源 URL 逐条在案。

## 1. Context Mapper（CML，contextmapper.org）——最该抄的字段骨架

- CML 分两层 DSL：战略层 ContextMap（Partnership/SharedKernel/Upstream-Downstream+OHS/PL/ACL），战术层 BoundedContext 内嵌 Aggregate → Entity/ValueObject/DomainEvent/Command。值得抄进聚合卡 YAML 的字段：`aggregate_root` 布尔标记、属性用 `- TypeName` 引用语法（引用即类型）、DomainEvent/Command 带属性表、`domainVisionStatement`。（[Tactic DDD Syntax](https://contextmapper.org/docs/tactic-ddd/)）
- 内置校验证明的可行边界：**结构校验（重名、类型合法、关系方向）可全自动；聚合切分合理性只能靠 refactoring 提案+人审**——机器给建议，人做裁决。（[JUG 演讲](https://www.jug.ch/events/slides/190910_ContextMapperDDD_Slides.pdf)、[ozimmer 实践](https://ozimmer.ch/modeling/2022/11/23/ContextMapperInsights.html)）
- 生成器面：PlantUML/Mermaid 图、MDSL 契约、FreeMarker 任意模板——"设计件→图"成本极低，人审靠图。（[Generators](https://contextmapper.org/docs/generators/)）

## 2. Event Storming / Event Modeling——引导工序的机器化拆法

- Event Modeling 把产出物压成四积木：Command/Event/Aggregator/Read Model，按时间轴铺，天然结构化卡片非散文；工序 = 事件时间轴→命令→读模型→按"垂直切片"逐条补全，每步产出形状固定，适合 LLM 逐轮填表。（[eventmodeling.org](https://eventmodeling.org/posts/event-modeling-cheatsheet/)）
- Context Mapper 官方有"Event Storming 结果录入 CML"教程——引导产物→设计件是可形式化的一跳。（[Model Event Storming Results](https://contextmapper.org/docs/event-storming/)）
- **TUM 2026 论文的关键教训**：五步 LLM 框架（词汇表→模拟事件风暴→限界上下文→聚合→技术映射）中，步 1–3 产出可用，**步 4–5（聚合设计/技术映射）误差累积后不可用，修复比重来更贵**；对策 = 每步新鲜上下文、只喂上一步**定稿**中间件、加一致性保护环。LLM 已知偏差：聚合切得比人类专家**偏碎**。（[arXiv 2603.26244](https://arxiv.org/html/2603.26244v1)）

## 3. DDD 纪律的静态可判子集（决定 ddd_check 闸什么）

- 可静态判（有 jMolecules+ArchUnit/jQAssistant/Spring Modulith 三套现成验证器佐证）：跨聚合/跨上下文引用方向、Repository 只返回本聚合、事件发布归属。（[jMolecules](https://xmolecules.org/aea-paper.pdf)）
- 2026 愿景论文主张把聚合边界完整性检查前移到**建模期**元模型级——正是我们"设计件 YAML + ddd_check"的位置。（[arXiv 2603.26987](https://arxiv.org/abs/2603.26987)）
- 只能靠评审：聚合粒度、不变量完备性、事件是否该跨边界。**结论：ddd_check 第一版闸图结构规则，粒度/完备性输出"待人审清单"不硬闸。**

## 4. 不变量 → 测试的机器化

- Codely "Aggregate Design Blueprint"：聚合卡 = Name/Properties/**Enforced Invariants**/**Corrective Policies**/Domain Events/Ways to access，每个不变量生成一个 DomainError、每个用例一个测试，强制 TDD——与我们聚合卡形态几乎同构，直接抄。（[Codely](https://codely.com/en/blog/how-to-implement-ddd-code-using-ai)）
- 无代码仓的落法：不变量字段机读化（描述+指向聚合方法+触发条件），ddd_check 先闸"红灯声明三元组"（触发操作→期望失败→指向方法）齐备性，测试生成留接口后置。

## 5. DDD + LLM 近期实践

- **context-mapper-mcp**（npm，2026-02）：把 CML 全套操作做成 MCP 工具，LLM 经工具层产 DDD 设计件+即时校验（批量收集全部错误 failFast=false）——"LLM 产设计件+确定性闸"路线已有人走通，**最有参考价值的开源先例**。（[npmx](https://npmx.dev/package/context-mapper-mcp)）
- codecentric 五原则：AI 产物必须有懂上游的人验，人保持在环。（[codecentric](https://www.codecentric.de/en/knowledge-hub/blog/five-principles-for-ai-assisted-ddd-keeping-the-human-at-the-center)）
- "聚合卡作为 AI 上下文包"无直接开源先例——Codely Blueprint 是最接近形态，属空白+机会。

## 6. 对 ddd-modeler 的直接建议（已吸收入拆票方案）

1. 聚合卡字段骨架抄 CML+Codely：aggregate_root 标记 / 属性 `- 词条ID` 引用 / 事件带载荷词条表 / 不变量三元组 / Corrective Policies / Ways to access。
2. ddd_check 第一版只闸图结构规则（跨聚合仅 ID 引用、载荷→词条解析、不变量三元组齐备、表映射无断链、重名），粒度合理性出"人审清单"。
3. 校验一次收集全部错误批量返回（failFast=false），不逐条打回。
4. 引导工序按 Event Modeling 切片拆，每轮产结构化 YAML 中间件落盘；新鲜上下文只喂定稿（TUM 教训）。
5. skill 内置"合并候选上下文"显式追问步，对冲 LLM 切碎偏差。
6. 设计件→Mermaid 图作副产物，人审靠图（CML 证明成本极低）。
