---
name: onto-modeler
description: 本体建模工序——给某域建本体/修整本体草案/加模型元素。按 PRD/素材推荐 profile、脚手架出模型文件骨架、把草案修整到过语义 CI；只产草案（进仓走 MR），业务判断标「待 Owner 确认」。
---

# onto-modeler · 本体建模（L1 工序）

把 PRD/域素材变成结构完备、能过语义闸的本体**草案**。本 skill 机器通用：正文不含任何具体业务域知识，域素材只存在于出厂集与用户提供的输入里。

## 触发面 / 何时用

- 用户要「给某域建本体」「修整本体草案」「给本体加模型元素」时使用。
- 不适用：从数据库/源码/文档逆向草案（各有专门的前端适配器工序）；改已定稿本体（写入必经 MR，本 skill 只产草案不进仓）。

## 输入输出契约

- reads：`ontology/schema/**`（schema 文档与两份机读表：模型注册表、依赖白名单）；`ontology/patterns/`（模式件库，工序 2.5 消费）；用户提供的域素材（PRD 片段/文档/口述要点）。
- writes：`ontology/<域>/**` 草案——域 manifest.json、一模型一文件的模型 YAML，以及两份工序产物文档：profile 建议、骨架文件清单。只产草案，进仓走 MR。
- 依赖脚本：`tools/schema_check.py`（语义闸，修整步的判定器）。

## 工序（按序执行，每步产物落盘）

1. **推荐 profile**：通读域素材，按 references/profile-selection.md 的「信号 → 模型」规则列出应启用模型集，对照 `ontology/schema/model-registry.json` 的 profiles 组合选最小覆盖组合；产出《profile 建议》文档：启用模型清单 + 每模型一条理由（引素材原文信号）+ 待 Owner 确认项。
2. **脚手架骨架**：按建议的 profile 生成域目录骨架——manifest.json（domain / label / profile / schemaVersion，profile 必须取注册表组合名）+ 一模型一文件（固定文件名与公共字段约定见 `ontology/schema/schema.md` §1）；产出《骨架文件清单》文档。未启用的模型不得建文件。
2.5. **查模式件库**：若 `ontology/patterns/` 存在，逐件对照其 applies_when 与域素材信号；匹配的模式件按其 fragment 组合进草案——占位符全部替换为域实例、按 compose_notes 落实改名与对齐注意、元素 description 注记「组合自 patterns/<pattern_id>」；组合产物仍是草案，业务语义须人审（AI 只做格式转换，业务必须人确认）。无匹配则跳过本步，不硬凑。格式与组合纪律见 references/pattern-usage.md。
3. **填草案**：逐模型填充元素。铁律：
   - 公共字段 model_type / version / domain 必填（version 三段语义化、引号包裹）；
   - 元素 ID 一律带模型前缀——「前缀即类型标签」，前缀表见 `ontology/schema/model-deps.json`；
   - 跨模型引用一律「稳定 ID + xxxRef 字段」，禁止只在 description 里用名字指代（ref 字段名全集同在 model-deps.json）；
   - 约束放置按 references/rule-placement.md 四层下沉判定，原则上不双层登记，确需双层时两处语义一致并标注待 Owner 确认。
4. **修整到过闸**：跑 `python3 tools/schema_check.py <域目录>`，按报告逐条修复（L1 公共字段与 manifest、L2 悬空引用与依赖白名单、L4 profile 合规与锁定字段），直到全过；然后把草案交人走 MR。本 skill 不做 git 提交、不直改已定稿本体。

## 行为约定

- **AI 只做格式转换与结构完备性**：业务语义（对象划分、口径、阈值、状态机）必须人确认；证据不足处标「待 Owner 确认」，不替人下业务结论。
- 规则只答「条件是否满足」，行为只答「改变什么状态」，不合并表达。
- 字典项停用置 enabled: false 保留行，不删除。
- 换义锁定字段（注册表 lockedFields）禁止复用——新义必须新增字段名。
- 引用不得靠名称猜测；ID 变更须过影响分析。

## 细则索引（进入对应步骤时读）

- references/profile-selection.md——profile 推荐规则（信号→模型→最小覆盖组合）
- references/rule-placement.md——四层规则下沉判定与硬约束
- references/pattern-usage.md——模式件格式与组合纪律（模式件是素材不是域；占位符替换/注记/人审三纪律）
- references/schema-pointer.md——schema 真源索引（只指路，不复制内容，防双真源）

## 出厂集（Seam）

`fixtures/onto-modeler/`——固定 PRD 片段 → 断言 profile 建议内容（AC1）、骨架清单命名（AC2）、草案过语义闸（AC3）、引用纪律含指空负变体（AC4）；`fixtures/pattern-library/`——模式件结构探针（首批五件 + 负变体）与组合示例域过语义闸（票 33）。改本 skill 工序描述前，先确认出厂集仍绿。
