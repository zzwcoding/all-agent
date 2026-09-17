# 票 07：skill semantic-service

Status: done
Belongs to: specs/semantic-service.md；PRD F4
Touches: ~/.agents/skills/semantic-service/、fixtures/semantic-service/

## What to build

- skill 本体（检索瀑布：显式锚定→ID 解析→闭包装配→可拒答；只读）
- fixtures/semantic-service/ Golden Question 集（AC1–4）

## 验收（注源）

- [x] AC1–4 全过（源：specs/semantic-service.md）
- [x] 回答带 ID 引用（源：spec 行为约定）
- [x] 不索引 build-contract 阵营（源：卡边界）

Blocked by: 票 03、票 04

## 交接包（L2 自主档）

任务: 建 skill semantic-service + fixtures/semantic-service/ Golden Question 集。
先读: specs/semantic-service.md（AC1–4）；specs/modules.md 卡（只读边界、不索引 build-contract 阵营）；ontology/schema/model-registry.json（camp 字段是检索面划界依据）；tools/graph_index.py（票 04 产物，检索后端）。
框架红线: 出厂集先行（Golden Q 集先写）；检索瀑布顺序固定：显式锚定→ID 解析→闭包装配→可拒答；回答必须带 ID 引用；只读——写意图一律回"走提案流程"。
边界红线: 不索引 camp=build-contract 的模型；不直改仓。
产出: ~/.agents/skills/semantic-service/ + fixtures/semantic-service/（Golden Q + 断言 AC1–4）+ lessons/07-*.md。
验收: AC1–4 全绿；ci.sh 四闸绿。
回报: 产物路径 + ci.sh 摘要 + 偏差。不 commit。
