# 施工日志 17 · Golden Q 术语问句（semantic-service 扩展）

日期: 2026-09-19
角色: L2 编码（自主档）
票: tickets/17-GoldenQ术语问句.md（AC 真源=票面 AC 表；两问定稿与瀑布步均为 L0 设计裁决，照办）
交接包注记: 主窗口防踩坑清单（既有出厂集格局先吃透、graph_index 断言是否锁数字先查、AC3 守卫禁肯定表述不禁词面、check_citations 清单节照既有格式、skill 正文改动最小化、出厂集先行）均已照办，下文逐条留证。

## 做了什么

1. **路线裁决（防踩坑 1）**：先查 `fixtures/graph_index/assertions.json`——AC1 锁「图统计: 节点=16 边=29」、AC4 锁「影响集: 14 个受影响节点」，即**精确数字断言**，给 ontology-base 补 glossary 副本必红。取推荐路线：问答本体（ontology-base）不动，Q7/Q8 解析证据直接引 `ontology/bohai` 真域（GLS-BOHAI-001/002 在彼；questions 文件头注记此裁决及理由）。
2. **出厂集先行（红→绿）**：questions/golden-questions.md 增 Q7/Q8 两行（问号沿票 17 设计裁决定稿编号）+ 证据域注记；assertions.json 增 10 条断言（23→33，既有 23 条零改动）。红相实测：恰好 8 条 NG 且全是「两份参照答案缺位」及其 check_citations 依赖，既有 23 条全绿、两条新机读佐证（GLS `--query`/`--closure` 打真域）即绿——红因纯净。
3. **两份参照答案**（按 SKILL.md 工序对 bohai 真域手工产出，瀑布级标注+「本回答引用的元素 ID」清单风格照既有四份）：
   - `expected-answers/ac7-term-caliber.md`（Q7 剔检产量）：二级解析落 `GLS-BOHAI-002`（别名净产量，术语条目即答案一部分）→ 三级 `--closure 1` 沿 relatedObjectRefs 指路 `AGG-BOHAI-001/002` → 承载规则 `RULE-BOHAI-019`（剔检支 expression+两支并列/跨月归属待 Owner 的注记如实转达）→ 行为 `BH-BOHAI-QueryBlockMonthlyCompletion` + 出口 `QR-BOHAI-002`（effectiveOutputSum 列）——口径四件套配齐。
   - `expected-answers/ac8-banned-term-disposal.md`（Q8 老完成率）：二级解析落 `GLS-BOHAI-001`（termType=禁用词，status=禁用（替代：产量完成率））→ 回答=禁用说明（含「强制拦截面未建」缺口如实说明+提案流程指路）+ 替代口径真实 ID 指路（`RULE-BOHAI-009` / `QR-BOHAI-002`），全程不把禁用词当作可用口径。
   - 两份各接 check_citations cmd 断言（CIT-06/07，票 13 闸）：6/6、5/5 token 双向一致。
4. **AC3 守卫正则（防踩坑 2，本票灵魂断言）**：票17 AC3 = ac8 文件上的全扫描 tempered 正则（同 AC3/AC4 守卫式），八组禁式：
   - G1 `老完成率…[是为属]…有效/可用/现行/合法/标准/正式…(口径|做法|指标|算法|标准)`（copula 前单字负断言排「不/未/没/无/非/别/莫/再/作」——「不是/不再是/作为」不误伤；copula 不收「算」，防「算法」词干误切）；
   - G2/G3 `老完成率口径仍/为|是|即|=…`（裁决点名的「口径为…」形态）；G4/G5 直接/被动认定式（作为/视为/当作/被当作…）；
   - G6 仍可/可继续/继续使用/照常/沿用…；G7 「还能用」陈述形态拦、疑问形态（还能用吗？）放行——问题原文必须出现；
   - G8 (使用|采用|沿用|改用|换用|用回|按|用)老完成率，use-动词前置负断言排否定语境（不得再用/禁止使用/停止使用），裸「用」加排 (使|采|沿|改|换|回) 防「禁止**使用**老完成率」被裸用分支误伤。
   - **双向自测**：24 好（禁用话术/问句形态/否定形态全过）× 23 坏（是有效口径/口径为可用/仍可使用/沿用/还能用。…全拦）全过；再对真文件做**变异测试**——把「请改以产量完成率作答」换成「老完成率仍是有效口径，可继续使用…」，守卫翻红。
5. **瀑布步（防踩坑 4，最小改动）**：references/retrieval-waterfall.md §2 增「术语词先落 GLS」一条（术语条目即答案一部分：定义/别名/termType/状态照登；沿 relatedObjectRefs 指路实体进 §3；禁用词=禁用说明+替代指路）+ §6 速查表增一行。SKILL.md/卡/其他 references 零改动；改动处零反引号路径 token，边界闸扫描面不变。
6. **安装位**：`python3 tools/install_skills.py sync semantic-service`（modified 1=retrieval-waterfall.md）+ `--check` 零漂移（4 个 skill 全一致）。

## 取舍（口径账）

- **问答本体为何不扩**：graph_index 出厂集锁精确图统计（16/29/14），ontology-base 加文件必连锁红；GLS 命中的机械佐证改挂真域（`python3 tools/graph_index.py ontology/bohai --query GLS-BOHAI-002 --closure 1`，fixture_run cmd cwd=仓根，沿票 16 BAN-AC3 挂真仓先例）。
- **守卫禁的是肯定表述不是词面**：「老完成率」词面在问题、条目 term、替代注记里必然出现，全部放行；拦的是「把它答成可用口径」的谓语形态（系表/沿用/仍可/口径为）。已知取舍：按/使用类动词的否定前置只排单字负语境，「按照老完成率」类深度否定嵌套（如「不再按照」）不在守卫面——按与照两个语素嵌套组合的穷举成本高于收益，且 G6 已拦「继续按照」前缀形态；此为防漏报优先的取舍（宁可偶发误伤逼人改写，不可放行肯定表述）。
- **check_citations 面外的措辞自由**：答案里「GLS- 前缀」「D4/D10」「CALCULATION」等非 ID token 不入清单（检具只收段式 ID）；两份答案正文↔清单 token 集合实测一致。
- **票面 AC1 的「关联 AGG/RULE 指路」落法**：AGG 走 GLS relatedObjectRefs 正向闭包（机械佐证 cmd 可复现），RULE 走 §3 口径四件套装配（承载规则 RULE-BOHAI-019）——两步都在答案里显式标注瀑布级。

## 坑

- **「禁止使用老完成率」会踩自己的守卫**：裸「用」分支不看前动词，「禁止使**用老完成率**」被拆出「用老完成率」命中 G8——补 (?<!使)(?<!采)(?<!沿)(?<!改)(?<!换)(?<!回) 链后放行。守卫正则必须拿**完整答案文本**（含问题引用、条目转写、清单节）自测，单测好例句不够。
- **「作为可用口径」是伪装的否定**：「不把它**作为**可用口径作答」里的「为」会被 G1 的 copula 分支吃进去（「为可用口径」子串）——copula 前负断言加「作」+ G4 只收「老完成率」后**紧邻**「作为/视为/当作」的肯定形态，两侧合围。
- **fixture 断言的问句形态放行是双向的**：G7 用 `(?![吗?？])` 而不是禁「还能用」全词——否则 questions 文件里的 Golden Question 原文进 ac8 头部就把守卫自己点红。

## 验收（对照票面 AC 表，逐条实证）

- [x] AC1：`python3 tools/fixture_run.py` → `票17 AC1` 三条全 ok（file-contains GLS-BOHAI-002/净产量/relatedObjectRefs/AGG-BOHAI-001/002/RULE-BOHAI-019/闭包装配/引用清单/解析自 bohai 真域；`--closure 1` 机读佐证 ok；CIT-06 check_citations exit 0「结论: 一致」）（源：AC 表 AC1）
- [x] AC2：`票17 AC2` 三条全 ok（file-contains GLS-BOHAI-001/禁用/产量完成率/RULE-BOHAI-009/QR-BOHAI-002/引用清单/解析自 bohai 真域；`--query GLS-BOHAI-001` 输出含「禁用词」「禁用（替代：产量完成率）」；CIT-07 exit 0）（源：AC 表 AC2）
- [x] AC3：`票17 AC3` 守卫正则 ok（对真实 ac8 文件全扫描匹配）；变异测试注入肯定表述→翻红（源：AC 表 AC3）
- [x] AC4：既有 23 条断言全 ok 零破坏；`bash tools/ci.sh` 四闸绿；`python3 tools/install_skills.py --check` 零漂移（源：AC 表 AC4）
- [x] 卡触发面/薄壳未变：`git diff --stat` 仅 retrieval-waterfall.md + fixtures/semantic-service/ 三文件 + lessons/17（源：字段纪律 1）

## 偏差与注记

1. questions 文件头两行措辞微调（「四问各压」→「前四问各压」+ 证据域注记）——出厂集固定输入的自述文件，属票面 Touches 的 fixtures/semantic-service/ 面；既有断言「输入（四问齐）」原文四串全保留、零倒。
2. assertions.json description 追加票 17 段落（沿票 13 先例：description 随票增注），既有描述零改动。
3. 机读佐证挂 `ontology/bohai` 真域路径（无 {fixture_dir}）——真域若改 GLS 条目措辞（如 status 原文）会红，属「真源改动须过出厂集」的预期闸效，不是脆断言。
4. 本票不 commit，票面 Status 留 todo 待主窗口验收（沿流水线协议）。
