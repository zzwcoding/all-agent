# 骨架文件清单 · 渤海油田产量域（onto-modeler 参照产物）

- 输入: ../input/prd-fragment.md（固定出厂输入 v1）；profile 结论见 profile-recommendation.md（v9-full）
- 本文件是 skill 工序第 2 步（脚手架骨架）对该固定输入的标准产出样本
- 草案落盘位置（进仓走 MR）: ontology/bohai/；出厂集内参照位置: expected-output/bohai/

## 文件清单（一模型一文件，固定文件名）

| # | 文件 | 说明 |
|---|---|---|
| 0 | bohai/manifest.json | 域声明：domain / label / profile / schemaVersion（profile 必须取自模型注册表的组合名） |
| 1 | bohai/m1-object-model.yaml | 对象模型（OBJECT） |
| 2 | bohai/m2-behavior-model.yaml | 行为模型（BEHAVIOR） |
| 3 | bohai/m3-rule-model.yaml | 规则模型（RULE） |
| 4 | bohai/m5-actor-model.yaml | 主体模型（ACTOR） |
| 5 | bohai/m6-flow-model.yaml | 流程模型（FLOW） |
| 6 | bohai/m7-report-model.yaml | 查询统计与报表模型（REPORT） |
| 7 | bohai/mu-ui-model.yaml | UI 模型（UI） |

## 骨架约定

- 每个模型文件第一层必带公共字段：model_type（与注册表 modelType 一致）/ version（三段语义化，引号包裹）/ domain（与 manifest 的 domain 一致）。
- 文件名固定、不可自造；一模型一文件；profile 未启用的模型不得出现在清单与目录内。
- 骨架先空表后填草案：顶层数据为空集合也必须保持合法映射（公共字段在场），保证每一步都可过语义闸。
