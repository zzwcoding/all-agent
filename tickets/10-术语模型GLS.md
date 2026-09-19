# 票 10：术语模型 GLS（元模型演进）

Status: done
Belongs to: 一期收官报告 §7 第一批 / §6 缺口 8；PRD F1 配套
Touches: ontology/schema/、ontology/bohai/、fixtures/schema_check/、tools/schema_check.py、CONTEXT.md

## What to build

- Glossary 模型进 schema：独立模型类型 GLOSSARY（GLS- 前缀），非 M1 扩展
- 渤海域 glossary 落仓：R5·§6 术语 10 条全覆盖（关闭对账表第三节缺口）
- schema_check 相应扩展（若文件名清单等硬编码处需同步）+ 出厂集新 AC

## 设计裁决（L0 已定，写入票防漂移）

- **独立模型而非 M1 扩展**：术语是业务概念的定义/别名/解释，与 M1 的 DICT（值域字典）不是一回事；OMF v6/v9 均无此模型，属本仓自定义扩展——正因如此走"元模型错→框架版本演进"路由：CHANGELOG + 版本号 + 本票即迁移票。
- 文件命名 `glossary-model.yaml`（照 `mu-ui-model.yaml` 非数字先例）；ID `GLS-{域}-{Seq}`；camp=business-core、consumers=[runtime, build]；**profile 组合：入 v9-full 与 headless，不入 v9-core**（v9-core=四模型最小核保持原样，术语属增强件；这样"未启用"才有可测负变体——AC2 依赖此裁决）。旧域无 GLS 文件不红——缺在场不校验是既定行为。

## 验收（注源）

- [x] AC1–4 出厂集全绿（源：本票交接包 AC 表）
- [x] 渤海域术语 10 条进仓且语义闸全绿（源：docs/walkthrough/step5-fidelity.md 第三节）
- [x] schema.md/注册表/依赖表/CHANGELOG 四件一致，版本号已演进（源：信号路由表"元模型错"行）

## 交接包（L2 自主档）

任务: Glossary 模型进 schema（元模型演进票）+ 渤海域术语落仓 + 出厂集扩展。
先读: ontology/schema/schema.md 全文 + model-registry.json + model-deps.json；tools/schema_check.py（模型类型/文件名的判定方式，确认哪些清单需同步）；docs/walkthrough/step5-fidelity.md 第三节（术语缺口清单）；/Users/divh/Downloads/teach-petro-agent/docs/business-setting.md §6（术语真源）；references/omf-spec-digest.md §16（版本演进纪律）。
框架红线: 出厂集先行——新 AC 断言先红后绿；schema 三件（schema.md 人读 + 两份机读表）必须一致，机读表是判定真源；CHANGELOG 落 ontology/schema/CHANGELOG.md（仓根布局表不收 CHANGELOG，勿放根目录）+ registry/依赖表版本号演进（1.0.0→1.1.0，语义化）；旧域零破坏（fixture valid-domain 不加 GLS 仍须全绿）。
边界红线: 只动 ontology/schema/、ontology/bohai/、fixtures/schema_check/、tools/schema_check.py 及其单测、CONTEXT.md 本体仓词条（模型列表括号补 GLS）、specs/modules.md 规约清单状态、lessons/10；不动四个 skill 与其出厂集。
产出: ontology/schema/{schema.md 增章+两机读表增条目+CHANGELOG.md} + fixtures/schema_check/（GLS 正变体+负变体+assertions 增 AC）+ ontology/bohai/glossary-model.yaml（每条术语注源 R5·§6，含 aliases/definition/relatedObjectRefs）+ lessons/10-*.md + specs/modules.md 规约清单状态更新。
验收: `bash tools/ci.sh` 四闸绿；`python3 tools/schema_check.py ontology/bohai` 全绿；AC1–4 全过。
回报: 产物路径 + ci.sh 摘要 + AC 清单 + 偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | fixtures 最小域 + 合法 glossary-model.yaml（2–3 条术语） | 语义闸全过 |
| AC2 | GLS 文件出现在 profile=v9-core 的域（GLS 不入该组合） | L4 profile 违规，红 |
| AC3 | 术语 relatedObjectRefs 指向不存在对象（GLS-xxx 悬空指 AGG- 不存在 ID） | L2 dangling-ref，红 |
| AC4 | glossary 文件 model_type 写错（如 OBJECT）或 GLS 文件名错挂 | L1 违规，红 |
