# 票 58：pkb 域定稿（Q2–Q10 落定 + M2/M5 补全）

Status: done

Belongs to: docs/第五期端到端实弹拆票方案.md §4；docs/requirements/pkb-拍板清单-Q2-Q10.md（签收记录载体）
Touches: ontology/pkb/（m1/m2/m5/glossary/manifest）、exports/mcp/capability-manifest.json（再制）、docs/requirements/pkb-拍板清单-Q2-Q10.md（签收表）

## What to build

Owner 已签收 Q2–Q10 全按推荐档（2026-09-22 会话「都按你推荐的就行」，Q3 按推荐档 fallback=六值起步 String 占位、新增走提案转 DICT）。本票把签收落进本体：

1. M1 定稿：status 转 Enum [暂存,入册]（Q10 双链）；contentRef 注 Q8 口径（书摘优先、全文挂载可选）；sourceType 注 Q3 口径；description 去「待确认」翻「已裁（票 58）」；version 0.1.0→1.0.0。
2. 新建 M2 行为模型（Q10/Q7/Q6 口径）：BH-PKB-CaptureItem 捕获条目（COMMAND，postcondition status=暂存）/ BH-PKB-PromoteItem 整理入册（COMMAND，暂存→入册）/ BH-PKB-AskKnowledge 检索问答（QUERY，带引用）/ BH-PKB-QueryGraph 图谱查询（QUERY）/ BH-PKB-RegenWiki 再生Wiki页（COMMAND，注 Q6 派生页+提案回流口径）。
3. 新建 M5 主体模型（Q9 单 Owner）：ACTOR-PKB-001（HUMAN）+ ROLE-PKB-001（知识库管理员）+ PERM×5（targetType BEHAVIOR 对准五个行为，dataScope ALL）。
4. glossary 定稿翻版：version 1.0.0；GLS-PKB-001 status 去「待 Owner 确认」；GLS-PKB-003 Wiki 注 Q6 已裁口径。
5. manifest：omittedModels 收敛为 M3（Q5 已裁通用清单起步+三接入点预留，规则闸未启用无素材）+M7（不变）；description 翻「票 58 定稿」。
6. 派生物再制：mcp_manifest_gen ontology --out exports/mcp/capability-manifest.json。

## 验收（注源）

- [x] AC1 `python3 tools/schema_check.py ontology/` 全仓绿（含 pkb 4 文件）（源：CI 语义闸）
- [x] AC2 capability-manifest 再制一致（--check exit 0）（源：mcp-publisher 出厂集）
- [x] AC3 签收记录九问齐（拍板清单签收表 Q2–Q10 全有结论+日期+方式）（源：docs/requirements/pkb-拍板清单-Q2-Q10.md）
- [x] AC4 `bash tools/ci.sh` 四闸全绿（源：CI）

## 交接包

任务: 上述 6 件改/建，草案翻定稿（version 1.0.0）。
产出: ontology/pkb 5 文件 + 再制 manifest + 签收表回填。
验收: AC1–4 全过后翻 Status: done 一票一提交。
