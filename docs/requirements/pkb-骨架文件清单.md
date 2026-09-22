# 骨架文件清单 · 个人知识库域（pkb）——onto-modeler 工序产物（2026-09-22）

草案域目录：`ontology/pkb/`（**未进仓，进仓走 MR**；headless profile，M2/M3/M5/M7 豁免见 manifest omittedModels）。

| # | 文件 | 状态 | 内容 |
|---|---|---|---|
| 1 | `ontology/pkb/manifest.json` | ✅ 已产 | domain=pkb / profile=headless / schemaVersion=1.2.0 / omittedModels×4 带理由 |
| 2 | `ontology/pkb/m1-object-model.yaml` | ✅ 已产 | AGG-PKB-001 知识条目（5 属性候选：title/sourceType/contentRef/status/collectedAt，全带待确认注记） |
| 3 | `ontology/pkb/glossary-model.yaml` | ✅ 已产 | GLS-PKB-001~006 六术语（知识条目/RAG/Wiki/知识图谱/GraphRAG/本体，定义逐条注源 R11/R12） |
| 4 | m2-behavior-model.yaml | ⛔ 豁免 | 行为候选挂起（Q10） |
| 5 | m3-rule-model.yaml | ⛔ 豁免 | 零约束条款素材（Q5 后另立） |
| 6 | m5-actor-model.yaml | ⛔ 豁免 | 主体粒度未裁（Q9） |
| 7 | m7-report-model.yaml | ⛔ 豁免 | 无报表素材 |
| 8 | mu-ui-model.yaml / m6-flow-model.yaml | ⛔ 组合外 | headless 不含，且无素材证据 |

配套工序文档：《profile 建议》= docs/requirements/pkb-profile-建议.md；需求面真源 = docs/requirements/personal-weknora-细稿.md（含 Q1–Q10 裁决记录）。

验收：`python3 tools/schema_check.py ontology/pkb` 全绿（语义闸 L1–L4；草案态不进 ci.sh 全仓扫——进仓 MR 时随全仓四闸走）。
