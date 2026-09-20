# 施工日志 43 · Golden 扩编与 rubric（6→12 问，L5 评分面内容）

日期: 2026-09-20
角色: L2 编码（自主档）
票: tickets/43-Golden扩编与rubric.md（AC 真源=票面 AC 表；设计=docs/design-l5-scoring.md §3 + §9 裁决②）
交接包注记: 红线「新增 6 问问句清单先报 L0 过目，未过目不动笔」已照办——先清单提案（含逐问 core 实跑验证，淘汰两候选）后动笔。

## 做了什么

1. **L0 过目记录（AC1）**：6 问清单提案（Q9–Q14，按 design §3.2 四维配额：口径正答-多义 Q9 / 口径正答-闭包 Q10 / 拒答-缺件分层 Q11 / 拒答-近邻指路 Q12 / 禁用-替代引导 Q13 / 面外-说明 Q14）先报 L0，提案时逐问附 core 实跑证据（含两候选「检修影响产量」「跨月检修的产量归属」实跑形态不符被淘汰的记录）。**L0 结论（2026-09-20）：批准，按此动笔**；L0 抽验 Q9（ambiguous 5 命中）与 Q13（refused_banned GLS-BOHAI-001）与提案一致；槽 5/6「域内唯一禁用词/唯一面外前缀，与存量 Q8/Q4 必然共享命中对象，差异化落在问句形态与话术考点」的声明获认可。问句原文逐字见 golden-questions.md 表（Q9–Q14 行）。
2. **6 份新增参照答案**（按 SKILL.md 工序对 bohai 真域手工产出，瀑布级标注+「本回答引用的元素 ID」清单风格照既有六份）：
   - `expected-answers/ac9-multi-sense-candidates.md`（Q9）：5 候选分组（计量 waterCut / 化验 waterCutLab / 综合含水率指标链）+ 请锚定修饰词 + 不代 Owner 仲裁（D3；RULE-BOHAI-002 容差是检出不是仲裁）。
   - `expected-answers/ac10-closure-narrative.md`（Q10）：RULE-BOHAI-009 全等主命中 → 公式/粒度 → 分子分母 sourceField → 行为（封账前置注记照登）→ 出口 completionPct；并列列（RULE-BOHAI-019）与 t4 限定变体（FLOW-BOHAI-001）单列「非本答」；D4 注记照登。
   - `expected-answers/ac11-refusal-missing-rule.md`（Q11）：R2 四件齐；缺件分层=查询层有出口近邻（QR-BOHAI-002/004 标非所问）、对象/行为规则层未建，「出口存在≠规则存在」；全文 ID={QR-BOHAI-002, QR-BOHAI-004} 零编造。
   - `expected-answers/ac12-refusal-nearby-guidance.md`（Q12）：近邻指路可行动——「数据有承载、命名口径未立项」辨析（AGG-BOHAI-002 事实载体 vs 命名口径），AGG-BOHAI-004 字面交集如实标；全文 ID={AGG-BOHAI-002, AGG-BOHAI-004} 零编造。
   - `expected-answers/ac13-banned-algorithm-trap.md`（Q13）：算法陷阱不落——v1 公式仓内无承载，不复现不反推（未找到不猜在禁用分支的延伸）；禁用说明→替代口径→真实 ID 指路三步连贯（GLS-BOHAI-001 / RULE-BOHAI-009 / BH-BOHAI-QueryBlockMonthlyCompletion / QR-BOHAI-002）。
   - `expected-answers/ac14-out-of-surface-write-intent.md`（Q14）：写意图形态面外拒答——R1 四件（结论先行/camp=build-contract 阵营归属/保留锚定/分道指路：建造链路与提案流程分道）+ 零细节零补猜；全文仅复述用户锚定 SCR-BOHAI-01。
   - **逐份过 check_citations（AC3）**：6/6 exit 0「结论: 一致」；另以 guard-corpus/regex.txt 对 6 份全文自检 6/6 nomatch（守卫干净，为后续若入 manifest 预留绿）。
3. **12 份 rubric（AC2）**：`rubrics/` 下 Q1 样板转正（q1-sample-rubric.yaml 正文 rubric 未改，仅头注释更新为正式 rubric+留痕指针）+ 新写 11 份（q2/q3/q4/q7/q8 存量补 + q9–q14 新增），每份 dimensions 带 weight+anchors{5,3,1}（锚 5 例引参照答案原文）+disqualifiers（语义级一票否决，与机判面零重复——词面/细节形态泄漏与禁词形态显式让给守卫正则，rubric 注释行声明）。**校验实跑**：`l5_score.py --rubrics fixtures/semantic-service/rubrics --results <36 份 mock 采样>` → 结论 PASS、exit 0（12 问格式全过+聚合链路走通；mock 在 /tmp 不入仓）；负变体（拷贝 Q9 rubric 删 5 档锚定例）→ exit 2「维度 candidate_coverage 缺锚定例（缺档: 5）」，证明校验器非空洞绿。
4. **逐问机判先绿对照表（AC4）**：12 问对 `ontology/bohai` 全量实跑 `semantic_service_core.py --json`（2026-09-20 冻结），status/命中集与既有 CORE 探针一致性如下：

   | 问 | core status | 关键 hits（sorted） | 关键 citations | 对应既有探针 |
   |---|---|---|---|---|
   | Q1 日产量口径是什么？ | answered | AGG-BOHAI-002, BH-BOHAI-QueryWellDailyOutput, QR-BOHAI-001, RULE-BOHAI-003, RULE-BOHAI-004 | 含 AGG-BOHAI-002/RULE-BOHAI-002 | CORE-01 一致 |
   | Q2 @AGG-BOHAI-001 有哪些行为？ | answered（一级·显式锚定） | AGG-BOHAI-001 + 7×BH（集合同 CORE-02 冻结值） | — | CORE-02 一致 |
   | Q3 月度产量汇总口径是什么？ | refused_missing | [] | near=[AGG-BOHAI-002, AGG-BOHAI-004] | 无 CORE 探针（票 04 AC3 断言面在其答案文件） |
   | Q4 @SCR-BOHAI-01 的页面长什么样？ | refused_out_of_surface | [] | []（零泄漏） | CORE-04 同分支（探针串为「界面细节」变体） |
   | Q7 剔检产量是什么口径？ | answered | GLS-BOHAI-002 | 含 AGG-BOHAI-001/002、RULE-BOHAI-019 | CORE-06 一致 |
   | Q8 老完成率还能用吗？ | refused_banned | GLS-BOHAI-001 | RULE-BOHAI-009/QR-BOHAI-002 在 citations | CORE-05 一致 |
   | Q9 含水率的口径是什么？ | answered（ambiguous，5 hits） | AGG-BOHAI-002, AGG-BOHAI-006, BH-BOHAI-QueryBlockWaterCut, QR-BOHAI-004, RULE-BOHAI-010 | 含 RULE-BOHAI-002（容差检出） | 新钉（本表即冻结值） |
   | Q10 产量完成率的口径是什么？ | answered（ambiguous） | BH-BOHAI-QueryBlockMonthlyCompletion, FLOW-BOHAI-001, QR-BOHAI-002, RULE-BOHAI-009 | RULE-BOHAI-009/019, BH, QR-BOHAI-002 | 新钉 |
   | Q11 统计月封账的规则是什么？ | refused_missing | [] | =near=[QR-BOHAI-002, QR-BOHAI-004] | 新钉 |
   | Q12 井口产量的口径是什么？ | refused_missing | [] | =near=[AGG-BOHAI-002, AGG-BOHAI-004] | 新钉 |
   | Q13 老完成率具体是怎么算的？ | refused_banned | GLS-BOHAI-001 | RULE-BOHAI-009/BH/QR-BOHAI-002+GLS-BOHAI-001 | 新钉（同 CORE-05 分支） |
   | Q14 把 @SCR-BOHAI-01 的提交按钮改成必填校验要怎么改？ | refused_out_of_surface | [] | []（零泄漏；camp 展开 build-contract，anchor_exists=false） | 新钉（同 CORE-05/04 先阵营后存在性分支） |

   退出码契约核对：answered 问 exit 0、拒答问 exit 1（CLI 契约 0/1/2，逐问实测）。
5. **golden-questions.md 登记**：追加 Q9–Q14 五列表行 + 头部扩编注记（真域取材/四维配额/L0 过目指针 lessons/43/rubrics 位置）+ 尾注更新（Q9–Q14 连续编号）；存量问零改动（「输入（四问齐）」四断言串原样在位）。
6. **AC5**：`bash tools/ci.sh` 四闸绿（末节实测记录）。

## 取舍（口径账）

- **assertions.json 本票未动**：票 42 样板注释曾说「票 43 落真 rubric 时在本出厂集 assertions.json 接入校验断言」，但票 43 Touches 未含该文件、边界红线「只动 Touches 清单」、AC 表五项均不要求改断言（AC2/AC3/AC4 均为实跑留痕）——故 12 问机判断言与 rubric 校验断言的接线留待票 44（L5 接线）或后续小票，本票以 lessons/43 本表承载冻结值。这是对「样板注释预告」与「票面边界红线」冲突的显式裁决，非遗漏。
- **Q10 分子分母不引 AGG-BOHAI-002**：实测 `graph_index --query RULE-BOHAI-009 --impact` hops≤2 集为 {BH, FLOW-BOHAI-001, PERM-BOHAI-QueryBlockMonthlyCompletion, QR-BOHAI-002, RULE-BOHAI-019}，AGG-BOHAI-002 不可达——参照答案遵守「答案只引用装配集内元素」，分子/分母以规则 inputParams 的 sourceField 路径（dailyProduction.oilOutput/planOutput，非 ID token）点名，答案 ID 集保持 ⊆ core citations ∪ hits。rubric 锚例同步按此措辞。
- **Q13 措辞避自己的守卫**：初稿「不能按老完成率算」实测**命中守卫 G8**（「按老完成率」分支的单字否定 lookbehind 不含「能」字）——改写为不含「按/用+老完成率」的表述（「这个问题没有『怎么算』的现行答案」「不把它当可用口径作答」），终稿 6 份答案守卫全 nomatch。教训：写禁用词相关答案必须拿完整文本对 regex.txt 实测，不能凭语感。
- **槽 5/6 共享命中对象**：bohai 真域禁用词仅 GLS-BOHAI-001 一条、面外前缀仅 SCR- 一个，Q13/Q14 与 Q8/Q4（及 core 探针）必然同命中对象——差异化落在问句形态（算法陷阱 vs 可用性判断；写意图 vs 查看）与 rubric 维度，L0 过目已认可；如实记录，不硬凑新命中对象。
- **rubric 维度与机判零重复的落法**：Q4/Q14 的「零细节泄漏」、Q8/Q13 的「禁词词面」均不设 LLM 维（守卫正则与机判断言所有），LLM 维只评语义级（臆测/暗示/软化/补猜）——rubric 文件头注释行显式声明此分工。
- **Q1–Q4 存量问的双机判面**：这四问原文按票 04 对 ontology-base（最小域）产出，其出厂断言在答案文件上；票 22 起 core 八问对 bohai 另有机判面。本表记录的是 bohai core 面（评分集的机判入口），两套面并存不冲突，各自断言均绿。
- **新问编号 Q9 起**：Q5/Q6 沿票 17 裁决保持 retired 不复活。

## 坑

- **「的」分词陷阱（差点造出假拒答问）**：extract_concepts 对「的」做替换时插入空格导致概念分段——「跨月检修的产量归属口径是什么？」分出「产量归属」后 t4 头部共缀误命中 RULE-BOHAI-009/FLOW-BOHAI-001（实跑 answered 而非预期 refused_missing），该候选问被淘汰。同型候选「检修影响产量…」亦因 t4 命中「检修类型」标签 answered。**造拒答问必须实跑 core 验形态，词面推演不可靠**（tier4 头部共缀+分词规则双重意外）。
- **「X的Y口径」类问句的分词副作用是双向的**：Q11「统计月封账的规则是什么？」分出游离 token「规则」，实测未引入杂音（全量无命中）——但换一个域词就可能撞候选面，新问句定稿前一律实跑。
- **YAML 数字键**：rubric anchors 的 `5:` 经 yaml.safe_load 解析为 int 5，程序化删档做负变体时用 `del anchors[5]` 不是 `del anchors['5']`（第一次负变体因此 KeyError，修正后红因精确=缺锚定例）。
- **管道里取 exit code**：`core --json | python3 -c 格式化` 的 `$?` 是格式化器的退出码不是 core 的——留痕时退出码必须单独跑或用 PIPESTATUS，本票对照表的退出码以逐问独立实跑为准。
- **「这是禁用词」句式看着安全也可能踩 G1**：G1 要求系词后 0–4 字内跟正面形容词，「已是禁用词」「登记为禁用词」因形容词是「禁用」不在正面词表而放行——但「已是有效/可用口径」必红；守卫正则的排他表与正面词表都要逐字核对，不能只看「有没有否定词」。

## 验收（对照票面 AC 表，逐条实证）

- [x] AC1：L0 过目留痕=本日志「做了什么」第 1 条（提案→抽验 Q9/Q13→批准，2026-09-20）；问句原文在 golden-questions.md Q9–Q14 行（源：票面 AC 表 AC1）
- [x] AC2：rubrics/ 12 份（Q1 样板转正+11 新），`l5_score.py --rubrics … --results <mock36>` PASS exit 0；负变体删 5 档锚 exit 2「缺锚定例」（源：票面 AC 表 AC2）
- [x] AC3：6 份新增 expected-answers 逐份 `check_citations.py` exit 0「结论: 一致」（6/6）；守卫正则自检 6/6 nomatch（源：CI/实跑）
- [x] AC4：12 问逐问机判先绿留痕=本日志对照表（status/hits/citations 冻结值+CORE 探针一致性；退出码 0/1 契约逐问实测）（源：票面 AC 表 AC4）
- [x] AC5：`bash tools/ci.sh` 四闸全绿（末节实测）（源：CI）

## 偏差与注记

1. assertions.json 未接入新断言（取舍第 1 条，显式裁决非遗漏）；q1-sample-rubric.yaml 仅头注释更新、rubric 正文与票 42 版零差异。
2. 本票不 commit，票面 Status 留 todo 待主窗口验收（沿流水线协议）。
3. mock 评分结果仅存在于 /tmp（校验留痕为本日志文字记录），未入仓——正式评分采样归票 44 子 agent 派发协议。
4. 参照答案中「请锚定」后接的后续口径承诺（Q9「补修饰词后本服务按闭包装配给出该支完整口径」）为话术表述，不构成机判面。
