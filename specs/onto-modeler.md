# spec · onto-modeler（本体建模 skill）

触及: skill `onto-modeler`（~/.agents/skills/onto-modeler/）

## 出厂集断言表

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | 固定 PRD 片段（渤海域口径） | 产出含 profile 建议（启用模型清单+理由） |
| AC2 | 同上 | 产出骨架文件清单符合一模型一文件命名约定 |
| AC3 | 同上 | 产出的草案 YAML 能过 schema_check L1 |
| AC4 | 草案含跨模型引用 | 引用用 ID+xxxRef 形式，无裸文本指代 |

## 行为约定

- 只产草案，进仓走 MR；业务判断标"待 Owner 确认"，不替人下业务结论
- 规则放置按四层下沉判定（内置字段→refRules→invariants→M3）
