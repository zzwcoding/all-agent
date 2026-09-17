# 票 08：skill impact-analyzer

Status: todo
Belongs to: specs/impact-analyzer.md；PRD F12
Touches: ~/.agents/skills/impact-analyzer/、fixtures/impact-analyzer/、docs/impact/

## What to build

- skill 本体（变更 → 影响链 + 落地顺序；报告落 docs/impact/）
- fixtures/impact-analyzer/ 出厂集（AC1–4）

## 验收（注源）

- [ ] AC1–4 全过（源：specs/impact-analyzer.md）
- [ ] 每条影响项带传播依据 ref（源：spec 行为约定）

Blocked by: 票 04

## 交接包（L2 自主档）

任务: 建 skill impact-analyzer + fixtures/impact-analyzer/ 出厂集。
先读: specs/impact-analyzer.md（AC1–4）；specs/modules.md 卡；tools/graph_index.py（--impact 能力，票 04）；ontology/schema/model-deps.json（传播依据）。
框架红线: 出厂集先行；每条影响项必须带传播依据（哪条 ref）；无下游引用时明确报"无影响"，不硬凑。
边界红线: 只读仓；报告落 docs/impact/NN-*.md。
产出: ~/.agents/skills/impact-analyzer/ + fixtures/impact-analyzer/ + lessons/08-*.md。
验收: AC1–4 全绿；ci.sh 四闸绿。
回报: 产物路径 + ci.sh 摘要 + 偏差。不 commit。
