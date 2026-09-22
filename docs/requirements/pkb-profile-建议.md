# profile 建议 · 个人知识库域（pkb）——onto-modeler 工序产物（2026-09-22）

> **AI 只做格式转换，业务必须人确认**。素材：Owner 口述粗需求（细稿 docs/requirements/personal-weknora-细稿.md）+ 调研 references/weknora-personal-kb-digest.md（R10–R12）。

## 结论

**建议 profile = headless**（M1/M2/M3/M5/M7/GLS）——覆盖证据模型集 {M1, GLS} 的最小注册表组合；M2/M3/M5/M7 依 manifest omittedModels 带理由豁免。

## 启用清单

| 模型 | 骨架文件 | 启用理由（引素材原文） |
|---|---|---|
| M1 对象 | m1-object-model.yaml | Owner 原话「**管理**我日常的开发资料、想法、文档、书籍、技术感悟、工作业务」——被管理实体及其属性信号 |
| GLS 术语 | glossary-model.yaml | Owner 关键词原词「知识库、rag、本体、建模、wiki、graphrag、知识图谱」——七词中六词口径可复述（R11·TERMS.md 定稿词条），立六条术语候选 |

## 组合核对

- 需要集 N = {M1, GLS}（唯一有素材证据的两模型）。
- v9-core = {M1,M2,M3,M5}：不含 GLS，不覆盖 N——否。
- headless = {M1,M2,M3,M5,M7,GLS}：覆盖 N，多余 4 模型——**取**（最小）。
- v9-full = 8 模型：覆盖 N，多余 6 模型（含 MU/M6）——多余更多，不取。

## 未启用说明（omittedModels 豁免，理由入 manifest）

| 模型 | 不启用原因 |
|---|---|
| M2 | 行为素材只有「管理/检索问答/wiki 生成」短语级证据，无触发/前置/状态变更语义（细稿 Q10 未裁）——行为候选挂起，不产文件 |
| M3 | Owner 输入零约束/校验/计算条款；图谱抽取过闸类规则待 Q5 裁决后另立 |
| M5 | 「我的知识库」单 Owner 自述，无角色/权限/数据范围素材（Q9 未裁） |
| M7 | 无查询/报表/统计口径素材——「以后可能会要」不算证据（profile-selection §1） |
| MU/M6 | headless 组合本就不含；亦无界面/流程素材证据 |

## 模式件库查对（工序 2.5）

`ontology/patterns/` 五件逐一对照，**无匹配，不硬凑**：

| 模式件 | 判定 |
|---|---|
| coded-dictionary | 不匹配——来源类型值集未完（细稿 Q3），值集纪律不建枚举/字典 |
| state-machine-lifecycle | 不匹配——条目状态生命周期待 Q10 裁决，暂无状态集证据 |
| master-detail-aggregate | 不匹配——Q2 推荐档为单一聚合；书籍↔书摘主从结构待 Q8 裁决 |
| approval-flow | 不匹配——零审批素材 |
| validity-versioning | 不匹配——零版本/有效期素材（Wiki 版本历史是页面层机制非本体元素） |

## 待 Owner 确认段

1. Q2 粒度推荐档（单聚合+sourceType）是否认可；2. Q3 值集全集；3. Q10 双链捕获与 status 占位转枚举时机；4. 域名/ID 前缀 `pkb` 是否认可（MR 前改名零成本，进仓后 ID 变更须过影响分析）。
