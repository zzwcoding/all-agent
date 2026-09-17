# 施工日志 08 · skill impact-analyzer + 影响分析出厂集

日期: 2026-09-17
角色: L2 编码（自主档）
票: tickets/08-skill影响分析.md（spec: specs/impact-analyzer.md AC1–4；PRD F12）

## 做了什么

1. **出厂集先行（红→绿）**：先写 fixtures/impact-analyzer/ 固定变更输入 changes/change-list.md（三场景：C1 改 AGG-BOHAI-001 字段 / C2 停用 DICT-BOHAI-01 字典项 PRODUCING / C3 改无下游对象 ACTOR-BOHAI-001）+ assertions.json（18 条断言承载 AC1–4+传播依据总断言+四条 cmd 机读佐证）→ 实跑全红（三份参照报告不存在，13 条 NG）→ 按 skill 工序对最小域 fixtures/graph_index/ontology-base（票 04 产物，只读复用，同票 07 手法）手工产出 expected-output/ 三份参照报告，转绿。参照报告即 docs/impact/NN-*.md 的规范样例：影响链每行=受影响 ID/模型/跳数/传播依据（via=<ref字段名>）/落地顺序位次。
2. **AC4 对象先实测后选定**：--impact 对候选逐一实测——AGG-BOHAI-001 影响 14 节点（hops=1 直接引用者 6 个：经 targetAggregate/sourceAggregate/ownerEntity×2/businessObjectRefs/objectRef）、DICT-BOHAI-01 影响 15 节点（直接引用方 AGG-BOHAI-001 经 dictionaryId）、ACTOR-BOHAI-001 零命中、SCR-BOHAI-01 也零命中。AC4 选 ACTOR-BOHAI-001（SCR-BOHAI-01 是 MU 面外元素，阵营叙事归语义服务，不混用）。
3. **两条守卫正则先正反例验证再落断言**（票 07 的坑位纪律）：①「每条影响项带传播依据」（spec 行为约定）= 01/02 报告全扫描守卫 `\A(?:(?!^- .*hops=(?![^\n]*via=))[\s\S])*\Z`——凡「- 」行含 hops= 必须同行含 via=（正例过/无依据行不过/无影响行文件不受误伤）；②AC4 不硬凑 = 03 报告注册前缀 12 枚举禁入、仅放行 ACTOR-BOHAI-001（ACTOR-(?!BOHAI-001\b) 先排除合法值），全文出现任何其他受影响 ID 列表即红。四条 cmd 佐证：--impact 对三场景机读可复现（14/15/0），零命中在 `\"impact\": []`（机读）与「0 个受影响节点」（人类读）两形态均可判。
4. **skill 本体**：仓内 skills/impact-analyzer/ 正本（SKILL.md 薄壳：frontmatter 触发面原文「改 X 会影响什么/评估这个变更」+ 六步固定工序 固定变更→机械取证→影响链→落地顺序→特例纪律→报告落盘 + 行为约定 + 细则索引；细则下沉 references/ 三件：report-template.md 报告模板与填写规则、rollout-order.md 落地顺序判定（跳数主序+依赖方向微调+字典先行/消费末端收尾，层序是启发式不许推翻跳数）、special-cases.md 字典停用不删除+无下游引用特例处置——全文域无关，grep 渤海/bohai/油田/井/产量/采油 零命中）。写完原样安装到 ~/.agents/skills/impact-analyzer/（先删后装 + ditto + diff -r 校验一致）。
5. **modules.md impact-analyzer 卡补「目录」字段**（照票 05 措辞双位置说明，本票唯一 modules.md 改动）；.skill-deps-allow 增 `fixtures/impact-analyzer/**` 豁免一条（同票 05/06/07 格式带理由）。

## 取舍

- **传播依据=via 记法，机械来源唯一**：--impact 输出每项自带 via=<ref字段名> 与 path=传播链，报告照抄不加工——「哪条 ref」的票面红线由此变成命令输出的转录纪律，不引入第二套依据体系。
- **AC4 守卫做成全文件前缀禁入而非节内检查**：fixture_run 的 file-matches-regex 只对全文，无法圈节；把 03 场景单独成文（一份分析一份报告本就是落盘规则），整文件只许出现变更对象一个 ID，比脆弱的节切分断言强得多。
- **报告一场景一份**：三份参照报告而非一份合订——合订本里 AC4 节必然混入 C1 的受影响 ID，守卫正则无从下手；同时示范了 NN 序号递增的落盘规则本身。
- **字典特例的诚实分层**：code 级引用不进图（图只走元素 ID ref）是图索引的事实边界，报告把它写成「机械面 + 人工补充扫描（前置条件文字语义依赖 PRODUCING，待 Owner 确认）」双层——既守住「每条影响项带传播依据」（机器行全带 via），又不停留在假完备。
- **落地顺序主序=跳数、层序只做同跳数微调**：依赖白名单存在权限↔行为类型级互指（targetRef/requiredPermissions 双向），层序严格化必出环；写明「冲突以跳数为准，层序是启发式」避免工序给出不可执行的伪精确顺序。
- **机读佐证四条而非两条**：除三场景 --impact --json 复现外，加一条人类读形态的「0 个受影响节点」——无影响结论的核验方式在报告里教人跑的就是人类读命令，佐证与工序同形。

## 坑

- **--impact 的 BFS 序≠落地顺序**：命令输出顺序是反向 BFS 首达序（发现序），直接抄成落地顺序会把 hops=2 的行为排在 hops=1 的流程后面又对不上位次——报告的顺序列必须按 rollout-order 规则重排（跳数主序+同跳数层序微调），且影响链行位次与顺序节列表逐一对齐（report-template 填写规则明文要求）。
- **守卫正则的裸前缀陷阱**：AC4 白名单放行 ACTOR-BOHAI-001 时，若正文出现「ACTOR- 前缀表示参与者」这类裸前缀写法会误触禁入（ACTOR- 后不接 BOHAI-001\b）——03 报告写作时通篇避免裸前缀枚举，验证脚本四组正反例（合法 ID/他 ID/裸前缀/编造后缀）先跑通。
- **description 字段的长文本易夹带笔误**：assertions.json description 首写出现 actOR 大小写错位，JSON 合法但难看；长 description 写完应自查域词一致性（本票已修）。
- **边界闸对 skill 正文扫描不分节**：SKILL.md 出厂集节引用 `fixtures/impact-analyzer/` 与其他正文引用同等对待，豁免行必须先行——本次先加豁免再跑闸一次过；同理正文不得出现 `fixtures/graph_index/...`（分析本体路径只活在出厂集自己的文件里，skill 正文只说「票 04 最小域」不带反引号路径）。
- **~/.agents 安装位先删后装**：沿用票 07 结论，ditto 前先 rm -rf 防旧版残留。

## 验收（对照票面）

- [x] AC1–4 全过：fixture_run 对 fixtures/impact-analyzer/ 18 条断言 PASS（AC1 影响链含全部 6 个直接引用者+全链 14 节点 / AC2 建议落地顺序章节+先改被依赖者后改依赖者+方向依据 / AC3 停用不删除纪律+字典引用扫描 DICT-BOHAI-01 及其引用方 AGG-BOHAI-001 经 dictionaryId / AC4 无影响明确语+核验方式+不硬凑守卫）（源：specs/impact-analyzer.md AC1–4）
- [x] 每条影响项带传播依据：01/02 参照报告守卫正则断言「含 hops= 的行必须同行含 via=」，影响链全部行带 via=<ref字段名>（源：spec 行为约定）
- [x] 无下游引用明确报无影响不硬凑：AC4 场景实测 --impact 零命中（ACTOR-BOHAI-001），参照报告「无影响」+核验方式+零行影响链，守卫正则禁任何受影响 ID 列表（源：票面框架红线）
- [x] 只读仓、报告落 docs/impact/NN-*.md：卡 writes=docs/impact/，正文与模板只写报告目录、不改本体（源：边界红线）
- [x] ci.sh 四闸绿：`bash tools/ci.sh` 退出码 0（详见收尾实跑输出；出厂集 impact-analyzer 转 PASS 后 6/6 全过、无 pending；边界闸无违规（豁免清单 4 条））

## 遗留与移交

- 票 09 端到端走查：渤海域真域模型进仓后（ontology/bohai/ 票 05 起可用），可用本 skill 对真域对象跑一次真实影响分析落 docs/impact/01-*.md 作端到端样本；出厂集参照报告继续锚定最小域不变。
- 报告模板与 ontology-base 的 ID 集耦合（同票 07 结论）：最小域演进时 fixtures/impact-analyzer/assertions.json 的守卫与参照报告需同步复核。
- 「安装位同步是手工纪律」沿用票 05 结论；本票不 commit，产物待主窗口验收后统一提交。
