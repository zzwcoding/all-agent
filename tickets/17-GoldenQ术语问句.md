# 票 17：Golden Q 术语问句（semantic-service 扩展）

Status: done
Belongs to: 第二批拆票方案（2026-09-19 用户批准）；票 10 遗留
Touches: skills/semantic-service/、fixtures/semantic-service/、lessons/17

## What to build

- Golden Q 集增两问（术语类）：剔检产量命中、禁用词处置
- 检索瀑布细则补「术语词先落 GLS」步；新答案接 check_citations

## 设计裁决（L0 已定）

- 两问定稿：
  - Q7「剔检产量是什么口径？」→ 一/二级解析落 `GLS-BOHAI-002`（剔检产量，别名净产量）→ 闭包装配关联对象（AGG-BOHAI-001/002）与承载规则（RULE-BOHAI-019）指路；
  - Q8「老完成率还能用吗？」→ GLS 命中禁用术语 → 回答=禁用说明（禁用、替代=产量完成率）+ 替代口径真实 ID 指路（RULE-BOHAI-009 / QR-BOHAI-002），**不得**把禁用词当作可用口径作答。
- 检索瀑布步（写进 references/retrieval-waterfall.md，SKILL.md 薄壳不动、卡触发面不动——字段纪律 1）：名称解析遇术语词（GLS 命中）时，术语条目本身是答案的一部分（定义/别名/状态），并沿 relatedObjectRefs 指路实体。
- 新答案必须过票 13 的 check_citations（正文↔清单双向一致）——接入 assertions 的 cmd 断言。
- **skill 正文改动 → 必须 sync 安装位**（票 15 钩子会拦漂移提交，sync 是提交前动作）。

## 验收（注源）

- [x] AC1–4 全过（源：本票 AC 表）
- [x] 卡触发面/薄壳未变，改动只在 references 与 fixtures（源：字段纪律 1）
- [x] 安装位与正本零漂移（源：票 15 --check）

## 交接包（L2 自主档）

任务: semantic-service 术语问句扩展（出厂集先行红→绿）。
先读: skills/semantic-service/{SKILL.md, references/retrieval-waterfall.md, references/refusal-guide.md}；fixtures/semantic-service/（四问格式与断言格局）；tools/check_citations.py 用法；ontology/bohai/glossary-model.yaml（GLS-BOHAI-001/002 现状）；skills/semantic-service 出厂集既有参照答案的瀑布级标注风格。
框架红线: 出厂集先行（新问先入 questions 文件+断言，参照答案未建时红→按工序手工产出→绿）；参照答案风格与既有四份一致（瀑布级标注+ID 引用清单）；check_citations 过；全部既有 18 断言不许倒。
边界红线: 只动 skills/semantic-service/references/retrieval-waterfall.md（如需）、fixtures/semantic-service/、lessons/17；SKILL.md/卡/其他 references 不动；执行面含安装位 sync（不动仓内正本以外的东西）。
产出: questions 增两问 + expected-answers 两份 + assertions.json 增断言（含 check_citations cmd 条）+ retrieval-waterfall.md 补 GLS 步（如工序确需）+ lessons/17 + 安装位 sync 执行与 --check 零漂移证明。
验收: AC1–4 全过；`bash tools/ci.sh` 四闸绿；`python3 tools/install_skills.py --check` 零漂移。
回报: 产物路径 + AC 实证 + ci.sh 摘要 + 偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | Q7 剔检产量答案 | file-contains `GLS-BOHAI-002` + 关联 AGG/RULE 指路 + check_citations exit 0 |
| AC2 | Q8 老完成率答案 | file-contains 禁用说明与替代指路（RULE-BOHAI-009/QR-BOHAI-002）+ check_citations exit 0 |
| AC3 | Q8 答案 | 不含"老完成率是有效口径"类表述（守卫正则：禁用词不得被答成可用口径） |
| AC4 | 全出厂集 | 既有断言零破坏，四闸绿，安装位零漂移 |
