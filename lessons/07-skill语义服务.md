# 施工日志 07 · skill semantic-service + Golden Question 集

日期: 2026-09-17
角色: L2 编码（自主档）
票: tickets/07-skill语义服务.md（spec: specs/semantic-service.md AC1–4；PRD F4）

## 做了什么

1. **出厂集先行（红→绿）**：先写 fixtures/semantic-service/ 固定输入 questions/golden-questions.md（四问各压瀑布一级）+ assertions.json（18 条断言承载 AC1–4+ID 引用+两条机读佐证）→ 实跑全红（四份参照答案不存在，14 条 NG）；再按 SKILL.md 工序对问答本体 fixtures/graph_index/ontology-base（票 04 最小域，只读复用）手工产出 expected-answers/ 四份参照答案，断言转绿。参照答案每份带头部元信息（Golden Question 原文/走到的瀑布级/断言面）+ 答案正文 + 「本回答引用的元素 ID」清单——清单节本身就是 id-citation-format.md 定的格式规范的第一份实物。
2. **四问压四级**：Q1「日产量口径是什么」（二级名称解析+三级闭包：口径四件套 AGG-BOHAI-001.dailyOutput / 载体 AGG-BOHAI-002 / RULE-BOHAI-001 / 出口 QR-BOHAI-001，外加 dictionaryRef→DICT-BOHAI-01 下链示范）；Q2「@AGG-BOHAI-001 有哪些行为」（一级显式锚定直达+--impact 反向收集 BH-BOHAI-UpdateWellStatus/BH-BOHAI-QueryWellDailyOutput，关联行为 BH-BOHAI-RecordDailyOutput 单列防误答）；Q3「月度产量汇总口径是什么」（四级 R2 仓内没有：拒答+检索轨迹+缺件三层说明+近邻指路 QR-BOHAI-001/AGG-BOHAI-002）；Q4「@SCR-BOHAI-01 的页面长什么样」（一级锚定可解析→camp 裁剪不过→四级 R1 面外拒答，不返回任何 UI 细节，只给业务面等价概念并注明"不是映射关系"）。
3. **「未编造 ID」「不含 MU 细节」的机读断言面**：fixture_run 只有正向 file-matches-regex，两条负向约束都用全扫描守卫正则实现——`\A(?:(?!X)[\s\S])*\Z` 在每个位置断言"编造形态从此处不出现"。AC3 守卫=注册表 12 个 ID 前缀逐一禁入、仅放行白名单 {AGG-BOHAI-002, QR-BOHAI-001}（前缀级负向先行排除合法值，如 AGG-(?!BOHAI-002\b)）；AC4 守卫=MU 文件十类特征 token 全禁（MENU-/gridDaily/ACT-SCR/LIST_MAINTENANCE/screenType/GRID/日产量列表/单井日产量录入/产量管理/保存）。两条守规写断言前先用 python 正反例各验一遍（正例必过、负例必不过）才进 assertions.json。
4. **skill 本体**：仓内 skills/semantic-service/ 正本（SKILL.md 薄壳：frontmatter 触发面原文「查口径/问业务对象/解析指标含义」+ 检索面划界节 + 四步瀑布工序 + 行为约定 + 细则索引；细则下沉 references/ 三件：retrieval-waterfall.md 瀑布判定细则与判定速查表、refusal-guide.md R1–R4 话术与缺件分层规范、id-citation-format.md 引用记法与引用清单规则——全文域无关，grep 渤海/bohai/油田/井/CEP 等十一词零命中）。写完原样安装到 ~/.agents/skills/semantic-service/（ditto + diff -r 校验一致）。
5. **检索面划界写法**：正文明确三条——检索面=camp=business-core（逐 ID：前缀→模型→camp，对照 model-registry.json）；**划界只看 camp 不看 consumers**（consumers 仅 build 的流程类模型仍在面内）；**图索引无阵营概念（全量建图含 build-contract），阵营裁剪是本 skill 的工序职责**。Q4 的最小域 MU 屏就是这条的实测样本。
6. modules.md semantic-service 卡补「目录」字段（照票 05 措辞的双位置说明，本票唯一 modules.md 改动）；.skill-deps-allow 增 `fixtures/semantic-service/**` 豁免一条（同票 05/06 格式带理由）。

## 取舍

- **AC3 的拒答答案是"会指路"的拒答**：近邻指路（QR-BOHAI-001 明细查询、AGG-BOHAI-002 明细载体）既示范"拒答也要带 ID"（refusal-guide 通用禁则），又让"未编造 ID"断言有东西可钉——守卫白名单恰好等于近邻指路集，编造任何白名单外 ID 即红。指路与编造的界线（真实存在+标「非所问」+不暗示已有答案）写进 refusal-guide R2。
- **AC4 的"不代答映射"是本票最细的一条线**：面外拒答时给业务面等价概念（录入行为/查询口径）是加分项，但不得说"该页面的行为是 X"——页面→行为的映射本身就在 MU 模型里，说了就是泄露面外细节。refusal-guide R1 把这条写成显式规则，Q4 参照答案照做。
- **AC2 的反向收集用 --impact 不用 --closure**：「对象有哪些行为」在图上是反向边（ownerEntity 指向对象），--closure 正向查不到；工序正文明确"正向 --closure（它引用谁）+ 反向 --impact（谁引用它）"双向装配，references/retrieval-waterfall.md §3 定深度策略（N 从 1 起，最多 3）。
- **名称解析不走检索脚本**：图索引 --query 是存在性确认器不是搜索引擎；候选 ID 靠通读域模型文件 id/name/alias 人工对齐——不私拉检索工具，这是边界闸纪律下的诚实写法，写进 waterfall §2。
- **机读佐证两条**：cmd-succeeds 跑 --impact 断言锚定对象的引用集含全部行为/规则/权限 ID（Q2 答案的命令级可复现面）；cmd-fails 断言图索引对不存在 ID 明确报「未找到/不做名称猜测」（Q3「未找到不猜」的机械面）。图索引会全量索引含 MU——正因如此它只能当佐证，阵营裁剪留在工序。
- **expected-answers 头部带"走到的瀑布级"**：四份答案各自示范停在哪一级，既是答案也是 skill 工序的对照样本——改工序描述时先看出厂集是否还绿的抓手。

## 坑

- **fixture_run 的正则只有正向**：「不得出现 X」要写成「全文每个位置都匹配 (?!X)」的全扫描守卫式；直接写负向 lookahead 作 pattern 会反向亮灯（re.search 在干净位置命中 lookahead 自己）。动手前先想清楚 match 语义再落断言。
- **守卫正则的字面量陷阱**：候选词「保存」「GRID」这类短 token 极易误伤未来答案的合理用词；取 token 时从 MU 文件实际内容反推（菜单名/控件 id/action id/屏类型/页面与菜单名），并用正反例单测验证边界（「录入单井日产量」≠「单井日产量录入」，靠词序区分才敢禁后者）。
- **--impact 的输出天然含面外元素**：实测 impact(AGG-BOHAI-001) 集合里有 SCR-BOHAI-01（MU 屏经 behaviorRef→行为→对象反向可达）——这正是"图索引无阵营概念"的活例证；若把命令输出直接当答案就越界了，工序必须先裁后答。
- **-c 后缀与 \b**：AC3 白名单放行 AGG-BOHAI-002 时必须带 \b，否则 AGG-BOHAI-0023 这类编造会借前缀溜过去；同理 QR-(?!BOHAI-001\b) 只放行整串。
- **~/.agents 安装位先删后装**：ditto 覆盖前确认目标不存在旧版残留（本票首装无此问题，记给后续改版）。

## 验收（对照票面）

- [x] AC1–4 全过：fixture_run 对 fixtures/semantic-service/ 18 条断言 PASS（AC1 口径四件套+dictionaryRef 链 / AC2 显式锚定直接命中+未走模糊检索+行为 ID / AC3 拒答+缺什么+未编造 ID 守卫 / AC4 面外语+不含 MU 细节守卫）（源：specs/semantic-service.md AC1–4）
- [x] 回答带 ID 引用：四份参照答案逐一含「本回答引用的元素 ID」清单节，四条断言承载（源：spec 行为约定）
- [x] 不索引 build-contract 阵营：SKILL.md 检索面节明确 camp=business-core 划界、图索引全量与工序裁剪职责；AC4 守卫正则断言参照答案零 MU 细节；Q4 以最小域 SCR-BOHAI-01 实测（源：卡边界）
- [x] 检索瀑布顺序固定：工序四步 显式锚定→ID 解析→闭包装配→可拒答，正文与 waterfall §0/§6 一致
- [x] 只读：writes=无，写意图一律回「走提案流程」（正文行为约定+refusal-guide R4）
- [x] ci.sh 四闸绿：`bash tools/ci.sh` 退出码 0（单测 97 条 OK；出厂集 5/6 过、impact-analyzer 占位 pending；边界闸无违规（豁免清单 3 条）；归档闸 153 个受管文件全合规）

## 遗留与移交

- 票 08 impact-analyzer 照本票+票 05/06 定例：正本双落、Seam 豁免行、AC 断言机械面+纪律面双层；其出厂集目录已占位 pending。
- 问答本体暂用 fixtures/graph_index/ontology-base（票 04 产物，只读）；票 09 真域 ontology/bohai/ 模型进仓后，Golden Q 集是否迁真域再跑一遍作端到端走查样本，留票 09 议。
- 守卫正则白名单与最小域 ID 集耦合：ontology-base 若演进（加对象/改 ID），fixtures/semantic-service/assertions.json 的两条守卫与参照答案需同步复核——耦合已写进出厂集 description。
- 「安装位同步是手工纪律」沿用票 05 结论；本票不 commit，产物待主窗口验收后统一提交。
