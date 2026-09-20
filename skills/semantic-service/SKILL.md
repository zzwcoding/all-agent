---
name: semantic-service
description: 运行时语义服务——查口径/问业务对象/解析指标含义。受控检索瀑布：显式锚定→ID 解析→闭包装配→可拒答，仓内没有就说明缺什么，绝不编造；回答必带元素 ID 引用可追溯；只读——写意图一律回「走提案流程」。
---

# semantic-service · 运行时语义服务（工序，运行时面）

给对话中的业务问题提供**只读、可追溯、可拒答**的语义答复：答案一律锚定本体元素 ID，检索面外或仓内没有的概念明确拒答并说明缺什么，绝不编造。本 skill 机器通用：正文不含任何具体业务域知识，域知识只存在于本体仓。

## 触发面 / 何时用

- 用户要「查口径」「问业务对象」「解析指标含义」时使用。
- 不适用：修改本体（写意图一律回「走提案流程」，写入必经 MR + 语义 CI）；建本体或逆向草案（建造工序的事）；评估变更影响（治理工序的事）。

## 输入输出契约

- reads：`ontology/**`——经 `tools/graph_index.py` 建图检索；检索面划界依据 `ontology/schema/model-registry.json` 的 camp 字段（操作法见 references/retrieval-waterfall.md §5）。
- writes：无——回答即产出，只读服务，不产文件、不改仓。
- 依赖脚本：`tools/graph_index.py`（`--query` 存在性确认 / `--closure` 正向闭包 / `--impact` 反向引用集 / `--json` 机读）。
- 可机判判定已提纯于 `tools/semantic_service_core.py`（MCP 服务器与出厂集共用同一核心），本 skill 工序语义与其保持一致，改判定先改 core 再对齐正文。

## 检索面（先划界，再检索）

- 检索面 = **camp=business-core** 的模型（逐 ID 判定：前缀 → 模型 → camp，对照 `ontology/schema/model-registry.json`）。
- camp=build-contract 的模型**不在检索面**：命中其元素不返回任何细节，只说明阵营归属并指路（话术见 references/refusal-guide.md R1）。
- **划界只看 camp，不看 consumers**：consumers 只有 build 但 camp=business-core 的模型（如流程类）仍在检索面内。
- **图索引没有阵营概念**：`tools/graph_index.py` 全量建图（含 build-contract 模型的节点与边），阵营裁剪是本 skill 的工序职责——凡引用检索面外元素细节的答案都是事故，先裁后答。

## 工序（检索瀑布，顺序固定，逐级降级）

1. **显式锚定**：问题带 @元素ID → 直达该节点，不走模糊检索；`--query` 确认存在即进入装配（步骤 3）；锚定不存在**不猜**，降步骤 2 或步骤 4。
2. **ID/名称解析**：无 @ID 时从问题抽概念候选词，通读候选域模型文件的 id/name/alias 产生候选 ID，逐个 `--query` 确认；全部未命中 → 「仓内没有该概念」，不做模糊匹配、不凭名称相似度造 ID。
3. **闭包装配**：命中后装配子图上下文——`--closure N` 正向（它引用谁）+ `--impact` 反向（谁引用它：行为/流程/查询出口），配齐口径四件套：承载字段、校验规则、执行行为、查询出口；答案只引用装配集内的元素。
4. **可拒答**：检索面外 → 说明阵营归属并指路，不返回细节；仓内没有 → 按层说明缺什么（查询层/对象字段层/行为规则层），给最接近的真实概念作近邻指路（带 ID、注明非所问），绝不编造。

## 行为约定

- **回答必须带 ID 引用**：每个业务论断标注承载它的元素 ID，答案末尾固定「本回答引用的元素 ID」清单（格式见 references/id-citation-format.md）；无 ID 支撑的论断不出口。
- **只读**：写意图（改口径/补概念/修模型）一律回「走提案流程」，本 skill 不直改仓、不产草案文件。
- **可拒答优先于可回答**：宁可拒答并说明缺口，不给无锚定的泛泛之答。
- 多义命中时列候选带 ID 请用户锚定，不擅自合并作答。

## 细则索引（进入对应步骤时读）

- references/retrieval-waterfall.md——检索瀑布判定细则（四级判定与边界、闭包深度策略、检索面划界操作法）
- references/refusal-guide.md——拒答话术与缺件说明规范（R1 面外 / R2 仓内没有 / R3 解析失败 / R4 写意图）
- references/id-citation-format.md——ID 引用格式（行内引用、闭包轨迹记法、引用清单规则）
- references/l5-dispatch.md——L5 评分子 agent 派发契约（离线评分面，票 44：批收官软闸/发布前硬闸触发时逐问派 3 个全新子 agent、请求/结果 JSON 照 specs/l5_score.md 协议、评分无效重派与仲裁升级；运行时问答不触发）

## 出厂集（Seam）

`fixtures/semantic-service/`——Golden Question 集：四问各压瀑布一级（口径解析/显式锚定/仓内没有/检索面外）→ 断言命中 ID 集、显式锚定直达、拒答不编造 ID、阵营不越界不返 UI 细节，另附 `--impact`/未找到两条机读佐证。改本 skill 工序描述前，先确认出厂集仍绿。
