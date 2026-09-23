# 票 63：pkb 本体定稿残留修复（GLS 三处 + M5 引用错位）

Status: done

> 来源：第九轮后第二域专项审查 P3-1/2/3/4（docs/reviews/2026-09-23-phase9-review-pkb-domain.md）。票 58 Owner 全签收后定稿文件内的待裁/待确认残留与引用错位——语义闸不查内容语气，属审查面实锤。
Belongs to: 第九轮后 pkb 域审查整改（票 63–65，无批方案，三票并列小整改）
Touches: ontology/pkb/glossary-model.yaml、ontology/pkb/m5-actor-model.yaml

## What to build

1. **GLS-PKB-003**：definition 主文删除「——个人版主从关系待细稿 Q6 裁决」残留，按已裁口径改写（Wiki=本体下游派生页，口径/定义类人工编辑走提案池回流本体——与同条 notes 一致，措辞从简）。
2. **GLS-PKB-005**：notes「个人版 Local/Global 分档取舍挂细稿 Q5」改为已裁口径注记（Q5 已裁=通用清单起步+三接入点预留，开关就位不开）。
3. **GLS-PKB-004**：notes 删除「（待 Owner 确认）」，relatedObjectRefs 挂接语义转正式注记（图谱节点由条目内容抽取而来的描述注记，票 58 定稿）。
4. **M5 header**：「Q9 已裁单 Owner（『我的知识库』），无多角色/多主体」改挂真实素材出处——Owner 原话「我的知识库」（docs/requirements/personal-weknora-细稿.md §一 Owner 关键词）+ 拍板清单 Q9 行仅作隐私边界旁注或不再引用；单 Owner 建模判断保持，只修注源。
5. 四文件外的 pkb 其余件零扰动；bohai 域零扰动。

## 验收（注源）

- [x] AC1 四处残留/错位全修，grep 复核：`grep -n "待 Owner 确认\|待细稿 Q6\|挂细稿 Q5" ontology/pkb/` 零命中（「待」类待裁语气清零；允许保留「待 Owner 确认」于草案位 docs/，定稿位 ontology/ 不允许）
- [x] AC2 语义闸：`python3 tools/schema_check.py ontology`（仓根）与 `python3 tools/schema_check.py ontology/pkb` 全绿，L1–L4 零（修后跑）
- [x] AC3 拍板清单一致性复核：修后 GLS/M5 表述与 docs/requirements/pkb-拍板清单-Q2-Q10.md 已裁九问零矛盾
- [x] AC4 `bash tools/ci.sh` 四闸全绿（最终树原样跑，协议⑩）

## 交接包（L0 自执行）

任务: 四处小修，不改模型结构/ID/任何机判字段。
产出: ontology/pkb 两件措辞修订。
验收: AC1–4 全过后翻 done 一票一提交；commit message 引审查报告路径。
