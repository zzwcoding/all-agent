# 票 43：Golden 扩编 + rubric 内容（6→12 问）

Status: done

> 注（L0 拆票时点）：依赖票 42（rubric 格式与校验器以其为准）。**先清单后施工**：新增 6 问的具体问句清单先报 L0 过目，过目后再动笔（照票 41 先例）。
> 注（L0 验收时点）：12 问机判断言接线 fixtures/semantic-service/assertions.json 不在本票 Touches，显式移交票 44 接线（L0 裁决，冻结值以 lessons/43 对照表承载）。
Belongs to: docs/第三期C线拆票方案.md 批次一；docs/design-l5-scoring.md §3 + §8 票 B
Touches: fixtures/semantic-service/questions/、fixtures/semantic-service/expected-answers/、fixtures/semantic-service/rubrics/（新建）、lessons/43

## What to build

Golden 评分集从 6 问扩编到 12 问：

1. **存量 6 问补 rubric**（Q1/Q3/Q4/Q7/Q8 等现存问，参照答案已有，不换问题只补 rubric）。
2. **新增 6 问 + 参照答案**，按 design §3.2 四维配额：口径正答 +2（多义候选问 / 闭包叙述完整度问）、拒答话术 +2（缺件分层说明问 / 近邻指路恰当性问）、禁用词处置 +1（替代口径引导话术问）、面外拒答 +1（面外说明话术问）。
3. **12 份 rubric** 落 `fixtures/semantic-service/rubrics/`：格式照 design §3.3（question/reference/dimensions+weight+anchors{5,3,1}/disqualifiers），每维锚 5 例引参照答案原文；rubric 必须过票 42 的 `l5_score.py` 格式校验。
4. 新增参照答案继续手工按 skill 工序产出 + 带引用 ID 清单，接 `check_citations` 闸（票 13/17 既有纪律）。

## 设计裁决（L0 已定）

- 每问的 status/命中 ID 仍由 core 机判面先钉（机判绿才进评分）——本票需给出"每问机判先绿再进评分"的流水断言或实跑留痕。
- 新增问取材复用票 17 先例（真域取材、问答本体不扩文件）。
- rubric 的 disqualifiers 只列语义级一票否决项，与机判面（check_citations/guard_corpus）零重复（design §1.3 红线）。

## 验收（注源）

- [x] AC1 新增 6 问问句清单 L0 过目留痕（源：本票 AC 表 + lessons/43 记录）
- [x] AC2 12 份 rubric 全过 l5_score 格式校验（锚定例齐/权重合法/reference 真实）（源：本票 AC 表）
- [x] AC3 新增参照答案过 check_citations（引用 ID 全真）（源：CI/实跑）
- [x] AC4 每问机判先绿留痕（status/命中 ID 与 core 断言一致）（源：本票 AC 表）
- [x] AC5 `bash tools/ci.sh` 四闸绿（源：CI）

## 交接包（L2 自主档）

任务: 6 问清单→L0 过目→新增问答+rubric×12+存量补 rubric。
先读: docs/design-l5-scoring.md §3（扩编维度/配额/rubric 格式）；fixtures/semantic-service/questions/golden-questions.md 与 expected-answers/（现存 6 问形态）；fixtures/semantic-service/rubrics/（票 42 样例，若票 42 已落地）；tools/l5_score.py（rubric 校验口径）；tools/check_citations.py（引用闸）；lessons/17（真域取材先例）。
框架红线: **新增 6 问问句清单先报 L0 过目，未过目不动笔**；参照答案手工按工序产出（不编造 ID）；出厂集纪律（新增内容全进 fixtures，归档闸可登记）。
边界红线: 只动 Touches 清单；不动 ontology/ 真域；不改 core 机判断言。
产出: 6 问清单（过目版）+新增问答+rubric×12+check_citations 接入+lessons/43（含 L0 过目记录）。
验收: AC1–5 全过；`bash tools/ci.sh` 四闸绿。
回报: 产物路径+五项 AC 实证+L0 过目记录摘要+ci.sh 摘要+偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | 新增 6 问清单 | L0 过目留痕在场（lessons/43） |
| AC2 | rubrics/ 12 份 | l5_score 格式校验全绿 |
| AC3 | 新增 expected-answers | check_citations 全绿 |
| AC4 | 12 问逐问 | 机判（status/命中 ID）先绿留痕 |
| AC5 | CI | 四闸全绿 |
