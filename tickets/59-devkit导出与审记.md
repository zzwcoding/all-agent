# 票 59：pkb 域 devkit 导出 + 审记

Status: todo

Belongs to: docs/第五期端到端实弹拆票方案.md §4（前置：票 58 done）
Touches: exports/devkit/pkb/、exports/reviews/（审记旁档）、repo-layout 归档登记（如需）

## What to build

F9 应用生成器对 pkb 域出开发包（交接给编码 agent 的轻形态）：

1. `python3 tools/app_pack_gen.py ontology/pkb --out exports/devkit/pkb/`（生成器名以 tools/ 实际为准；四节：对象/行为/规则清单/口径卡）。
2. 审记：`python3 tools/review_gate.py verify exports/devkit/pkb/devkit.md`——devkit 全审档（ADR 0003 判档），审记旁档 exports/reviews/ 追加不覆盖。
3. capability-manifest 如受影响再制（--check 复核）。

## 验收（注源）

- [ ] AC1 devkit 四节齐且内容可指认到 pkb 元素 ID（AGG-PKB-001 / BH-PKB-* / GLS-PKB-*）（源：票面）
- [ ] AC2 review_gate verify 过、审记旁档在场（源：AGENTS.md 批收官清单⑥）
- [ ] AC3 归档闸认 exports/devkit/pkb/ 布局（不匹配即登记 repo-layout）（源：归档闸）
- [ ] AC4 `bash tools/ci.sh` 四闸全绿（源：CI）

## 交接包

任务: devkit 导出+审记+归档对账。
产出: exports/devkit/pkb/ 全件 + 审记旁档。
验收: AC1–4 全过后翻 done 一票一提交。
