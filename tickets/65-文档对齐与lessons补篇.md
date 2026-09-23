# 票 65：文档对齐（AGENTS.md 锚点+目录地图）+ lessons 58/59 补篇

Status: done

> 来源：第九轮后第二域专项审查 P2-2/P3-5 与观察项 2（docs/reviews/2026-09-23-phase9-review-pkb-domain.md）。AGENTS.md 是「新窗口入口协议」第一站，锚点停在票 57 会让下一个窗口对第五期/pkb 域零感知；lessons 每票一篇惯例自票 03 起，58/59 缺篇。
Belongs to: 第九轮后 pkb 域审查整改（票 63–65）
Touches: AGENTS.md、lessons/、（观察项 2 定夺）docs/prd.md

## What to build

1. **AGENTS.md 状态锚点推进**：在第九轮整改（票 57）之后续接第五期记录——54e4e76（pkb 立项进仓：R10–R12+细稿+ontology/pkb 草案+capability-manifest 再制）/ 7b6591b（第五期拆票方案：DDD 不路由+personal-weknora 选址）/ d9b1894（拍板清单落盘）/ 590b0e2（票 58–62 拆票落盘）/ a7fa7bb（票 58 pkb 域定稿=M1 定稿+M2 五行为+M5 三件套+GLS 翻版，Owner Q2–Q10 签收）/ de7bb50（票 59 devkit 导出+审记 pending+实弹修两缝隙：app_pack_gen 豁免域感知/review_gate verify 按 target 过滤）；锚点尾注当前下一张=票 60（新仓开工交接），并提一句本轮审查（报告路径+票 63–65 整改中）。
2. **AGENTS.md 目录地图 ontology/ 行**：补第二域 pkb（个人知识库 WeKnora，第五期端到端实弹素材域：M1/M2/M5/GLS+manifest，M3/M7 豁免态，bohai 7+pkb 5 文件语义闸全绿）；渤海域描述保持「首个业务域」不变。
3. **lessons 补篇两篇**：lessons/59-pkb域定稿.md（票 58：九问拍板→定稿翻版的工序与坑）与 lessons/60-pkb-devkit导出与审记.md（票 59：两平台缝隙实弹发现与修复记录）——卷号按 lessons 目录实际顺延（现最大卷号 58，补篇为 59/60，票面 Touches 卷号与实际不一致处按各票惯例留痕）。每篇至少含：做了什么/实弹发现/教训三条结构（对齐 lessons/ 现有体例，施工窗可读 ticket 58/59 票面+git log 复原）。
4. **观察项 2 定夺**：PRD 是否补第二域登记行——按 F15 入账同款风格在 docs/prd.md 决策日志区补一行（pkb 域=第五期端到端实弹素材域，需求真源=细稿+拍板清单），或显式记「不补，域素材归 requirements 层」——二选一成文于 lessons/60 或本票 AC。

## 验收（注源）

- [x] AC1 AGENTS.md 锚点含第五期六提交（短哈希逐个 grep 在位）且尾注下一张=票 60；字符串替换带断言复核（协议第 6 条：替换后 grep 复核）
- [x] AC2 目录地图 ontology/ 行同时出现 bohai 与 pkb，「首个业务域」措辞未误删
- [x] AC3 lessons/59、lessons/60 在位且三结构齐（做了什么/实弹发现/教训）
- [x] AC4 PRD 定夺成文（补行或不补的理由，落 lessons/60 或票面）
- [x] AC5 `bash tools/ci.sh` 四闸全绿（最终树原样跑，协议⑩）

## 交接包（L0 自执行）

任务: 纯文档票——锚点续接+目录地图+两篇 lessons+PRD 一行定夺。
产出: AGENTS.md 两处修订+lessons×2+（可能）prd.md 一行。
验收: AC1–5 全过后翻 done 一票一提交；commit message 引审查报告路径。
