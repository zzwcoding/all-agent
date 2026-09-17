# 票 05：skill onto-modeler

Status: done
Belongs to: specs/onto-modeler.md；specs/modules.md 卡；PRD F1 配套
Touches: ~/.agents/skills/onto-modeler/、fixtures/onto-modeler/

## What to build

- skill 本体（SKILL.md 薄壳 + references：schema 摘要引用、profile 推荐规则、四层下沉判定）
- fixtures/onto-modeler/ 出厂集（AC1–4：固定 PRD 片段 + 断言）

## 验收（注源）

- [x] 出厂集断言全绿（源：specs/onto-modeler.md AC1–4）
- [x] 触发面与卡一致（源：modules.md 卡字段纪律 1）
- [x] 边界闸过（源：边界铁律 4）

Blocked by: 票 03

## 交接包（L2 自主档）

任务: 建 skill onto-modeler（~/.agents/skills/onto-modeler/）+ fixtures/onto-modeler/ 出厂集。
先读: specs/onto-modeler.md（AC1–4）；specs/modules.md 卡（触发面/reads/writes/边界）；ontology/schema/schema.md + model-registry.json；~/.agents/skills/sdd-flow2/references/skill-module-format.md。
框架红线: 出厂集先行——先写 fixtures（固定 PRD 片段 + assertions.json）确认红，再写 SKILL.md 正文到绿；SKILL.md 薄壳（触发面+路由+契约），细则下沉 references/。
边界红线: skill 正文不许出现具体业务域内容（机器通用，域知识只在 fixtures）；不读其他 skill 私件。
产出: ~/.agents/skills/onto-modeler/{SKILL.md,references/} + fixtures/onto-modeler/ + lessons/05-*.md。
验收: AC1–4 断言全绿；触发面与卡一致；ci.sh 四闸绿。
回报: 产物路径 + ci.sh 摘要 + 偏差。不 commit。
