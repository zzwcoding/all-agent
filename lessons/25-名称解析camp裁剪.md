# 施工日志 25 · core 名称解析补 camp 裁剪（P1 功能正确性尾款）

日期: 2026-09-19
角色: L2 编码（自主档）
票: tickets/25-名称解析camp裁剪.md（AC 真源=票面 AC 表；设计裁决 L0 已定，照办）
因由: docs/reviews/2026-09-19-phase3-review-tickets20-24-and-sddflow2-audit.md P1——票 22 的 R1 检索面纪律在名称解析路径失守（L0 已亲自复现）。
交接包注记: 主窗口防踩坑八条（红相先落袋/裁剪点位在候选产生处/复用同一 camp 判定/集相等探针/负变体断言/合成域专测/单源声明/TDD+全量绿灯）逐条照办，下文留证。

## 做了什么

1. **修前红相落袋**：`python3 tools/semantic_service_core.py fixtures/graph_index/ontology-base --ask "单井日产量录入" --json` → answered，hits 首位即 SCR-BOHAI-01（MU，t1 全等），且 scaffold_commands 第一条就是它的 `--impact` 指令；同域 registry 里 M5(ACTOR)/M6(FLOW) camp=business-core，故本案例唯一面外元素=SCR-BOHAI-01。
2. **TDD 红先**：`test_semantic_service_core.py` 增 3 测（16 测/域类）——名称解析裁剪（红：SCR-DEMO-01 在 hits）、禁用词替代指路裁剪（红：SCR-DEMO-01 在 citations；合成域 GLS 禁用词条目 definition 增第二替代名「对象甲管理屏」恰为 MU 屏名，使该路径可测）、@锚定路径回归（修前即绿，符合"锚定路径本就合规"）。出厂集 CORE-01–08 换 python -c 集相等探针（修前修后全过——bohai 无 MU 文件）+ 新增 CORE-09 负变体（修前出厂集唯一红，如实打印 SCR 泄漏清单）。
3. **修复**（`tools/semantic_service_core.py`，净增约 15 行）：新增 `Surface.in_surface()`（前缀→模型→camp，R1 唯一判定链），裁剪点位=候选产生处——`resolve_names` 节点循环入口裁面外（面外 ID 从源头不进候选 dict，hits/citations/scaffold_commands 三出口天然干净）；`scan_layers`（缺件/近邻汇入 citations/scaffold 的出口）与 `replacement_pointers`（禁用词替代指路直达 citations）同点位补齐；`_citation_ok` 与 @锚定面外判定表达式收敛到同一函数（语义等价：有前缀但 registry 无 camp 时 in_surface=False，同样拒面外）。
4. **status 语义零改动**：命中集全为面外 → hits 空 → 走既有「四级·可拒答」R2 缺件分支如实拒答；有 business-core 命中 → answered 不变。不设第五种 status、不报面外计数。
5. **CORE 探针升级**：八问从 outputContains 单向包含改为集相等探针（子进程跑 core --json，钉 status+core 退出码+hits ID 集 sorted list 精确相等+关键 citations 在集，不等打印差异退出 1）；期望集修前采集基线、修后复测一致后冻结。断言总数 41→42（CORE-09 净增 1）。
6. **单源声明双向化**：specs/modules.md semantic-service 卡依赖增 `script: tools/semantic_service_core.py` 独立行（skill_deps_check 每行只取第一个反引号路径，必须独立成行）；SKILL.md 输入输出契约节补声明句（措辞照票面）；`install_skills.py sync semantic-service` 重写 1 文件，`--check` 零漂移，边界闸无违规（core 路径反引号引用被卡依赖放行）。
7. **边界**：只动 Touches 清单（core+单测+fixtures/semantic-service/assertions.json+SKILL.md+modules.md+lessons/25）；tools/ 其他脚本、ontology/、expected-answers/ 参照答案零改动；不 commit。

## 复现用例前后对照（AC1）

| | 修前 | 修后 |
|---|---|---|
| 命令 | `python3 tools/semantic_service_core.py fixtures/graph_index/ontology-base --ask "单井日产量录入" --json` | 同左 |
| status | answered | answered（不变） |
| hits | **SCR-BOHAI-01**, AGG-BOHAI-001, FLOW-BOHAI-001, AGG-BOHAI-002, QR-BOHAI-001, ROLE-BOHAI-001 | AGG-BOHAI-001, FLOW-BOHAI-001, AGG-BOHAI-002, QR-BOHAI-001, ROLE-BOHAI-001 |
| citations | 9 ID（本就无 SCR——_citation_ok 旧判定已拦） | 同修前（零变化） |
| scaffold_commands | **首条=SCR-BOHAI-01 --impact** | 首条=AGG-BOHAI-001 --impact，SCR 零泄漏 |
| 退出码 | 0 | 0 |

## 九问冻结期望集（修后实测冻结，探针逐日值守）

| # | 问（域） | status/退出码 | hits 冻结集 | citations 关键钉 |
|---|---|---|---|---|
| CORE-01 | 日产量口径是什么？（bohai） | answered/0 | AGG-BOHAI-002, BH-BOHAI-QueryWellDailyOutput, QR-BOHAI-001, RULE-BOHAI-003, RULE-BOHAI-004 | ⊇ AGG-BOHAI-002, RULE-BOHAI-002 |
| CORE-02 | @AGG-BOHAI-001 有哪些行为？（bohai） | answered/0，一级·显式锚定 | AGG-BOHAI-001 + 7×BH-BOHAI-*（反向） | —— |
| CORE-03 | 桶油增产成本的口径是什么？（bohai） | refused_missing/1 | [] | []（未建+待 Owner） |
| CORE-04 | @SCR-BOHAI-01 的界面细节（bohai） | refused_out_of_surface/1 | [] | []，scaffold 亦空 |
| CORE-05 | 老完成率还能用吗？（bohai） | refused_banned/1 | GLS-BOHAI-001 | ⊇ RULE-BOHAI-009, QR-BOHAI-002 |
| CORE-06 | 剔检产量是什么口径？（bohai） | answered/0 | GLS-BOHAI-002 | ⊇ AGG-BOHAI-001, AGG-BOHAI-002, RULE-BOHAI-019 |
| CORE-07 | 月度结算的口径是什么？（bohai） | answered/0 | AGG-BOHAI-008 | ⊇ BH-BOHAI-QueryMonthlySettlement, QR-BOHAI-003 |
| CORE-08 | 有效产量的口径是什么？（bohai） | answered/0 | AGG-BOHAI-005, GLS-BOHAI-003, RULE-BOHAI-019 | —— |
| CORE-09 | 单井日产量录入（最小域） | answered/0 | AGG-BOHAI-001, AGG-BOHAI-002, FLOW-BOHAI-001, QR-BOHAI-001, ROLE-BOHAI-001 | SCR-BOHAI-01 不在 hits∪citations∪scaffold |

## hits 集与参照答案 ID 清单交叉核对（答案差异记账，不硬凑）

以 hits 集为准冻结（集相等钉的是 core 的词面候选集口径）；成稿引用面由 citations 钉关键承载 + check_citations 闸管答案侧。既知差异：

- **Q1**（ac1 答案引用 {AGG-BOHAI-001, AGG-BOHAI-002, RULE-BOHAI-001, BH-BOHAI-RecordDailyOutput, QR-BOHAI-001, DICT-BOHAI-01}）：AGG-BOHAI-001（闭包起点）/RULE-BOHAI-001（校验）/DICT-BOHAI-01（dictionaryRef 下钻）是 skill 成稿按瀑布 §3 人工装配的引用，core 词面候选集不含（「日产量」t2 命中的是标签宿主 AGG-BOHAI-002）；反向 hits 里 RULE-BOHAI-003/004 与 BH-BOHAI-QueryWellDailyOutput 是 t3/t4 词面候选的诚实登记（lesson 22 t4 噪声账）。
- **Q7**（ac7）：hits={GLS-BOHAI-002}，答案其余引用（指路对象/承载规则/行为/出口）全部由 citations 装配集承载——装配集 ⊇ 答案引用集，无缺口。
- **Q8**（ac8）：hits={GLS-BOHAI-001}=答案首项；答案里的 AGG-BOHAI-002（分子分母承载）不在 core citations（禁用词分支 citations=禁用条目+替代指路，替代链只到 RULE/QR/BH）——成稿补充承载属 skill 装配职责，非 core 缺口。
- **Q4**（ac3）：core 机械面 citations=[]（桶油增产成本对全域零 2-gram 交集，近邻不硬凑）；答案给的两条近邻指路（QR-BOHAI-001/AGG-BOHAI-002）是 skill 语义判断——lesson 22「缺件分层是机械面」的既知分工，不是本票回归。
- **Q3**（ac2）：core hits=锚点+7×BH 反向；答案引用另有 PERM/QR/ASSOC/FLOW/AGG-002 等装配面 ID（在 citations），且答案只列 3 个 BH（成稿择要）——两侧口径不同层，锚定路径行为零变化（单测回归钉死）。

## 取舍（口径账）

- **正向闭包只对 GLS 命中跑（票 22 偏差 5 的账，本票补记）**：`assemble()` 里 `--closure 1` 只对 GLS 命中执行（沿 relatedObjectRefs 指路实体，再对其扫 impact 取承载规则）；非 GLS 命中只跑 `--impact` 反向。理由：口径四件套的反向面（行为 ownerEntity/出口/规则经 reusedBy）`--impact` 已覆盖，对对象命中再跑正向只会带出 DICT/ASSOC——不入 citations 模型面，多跑只添子进程开销与噪声；GLS 是例外，术语条目的承载链只在正向 relatedObjectRefs 上，不跑正向则 ac7 的指路对象不可达。代价：对象命中的正向承载（如字典下钻链）不在 core 装配集，由 skill 成稿按瀑布 §3 人工 `--closure` 补齐——ac1 答案的 DICT-BOHAI-01 即此口径（既知差异，见上）。
- **裁剪点位=候选产生处，不在三个出口各打补丁**：面外 ID 从源头不进候选集，hits/citations/scaffold_commands 三出口天然干净；近邻与替代指路虽不是"名称解析命中集"，但其出口同样汇入 citations/scaffold_commands（R2 分支与禁用词分支），故同点位补齐——R1「任何候选 ID 先过阵营检查」的完整落地。@锚定路径维持先阵营后存在性，仅把判定表达式收敛到 `in_surface`（票面"维持现状（已合规）"：行为不变，单测回归钉死）。
- **命中集全为面外=既有 R2 语义**：检索面外本来就是"不在服务面"，如实走"仓内没有"拒答（面外细节一个字不漏），不设第五种 status、不另行报错（票面裁决原文）。
- **期望集冻结口径**：bohai 域无 MU 模型文件，CORE-01–08 修前修后实测一致——修前采集基线、修后复测相等后冻结；面外压力全部由 CORE-09 在最小域（含 MU 屏）承担，负变体断言钉死审查复现用例不回归。
- **拒答三问的 cmd-fails 语义收进探针**：升级后 CORE-03/04/05 探针本体是 cmd-succeeds（探针退出 0=断言成立），core 退出码 1 的 CLI 契约钉在探针内（p.returncode==1）。对 lesson 22 的 cmd-fails 记录是演进不是推翻：status+退出码+集相等三重钉，断言力只增不减。

## 坑

- **复用重构漏局部变量引用点**：把锚定路径判定收敛到 `in_surface` 时删了 `camp` 局部变量，拒绝载荷 Struct 改了就地取值、`reason` f-string 漏改——4 测 ERROR（NameError）。教训：收敛复用前先 grep 该局部变量全部引用点。
- **fixture_run 是 shlex.split 非 shell**：python -c 探针代码必须双引号整体包裹（内部全用单引号）、单行分号写法——换行符会被 shlex 切碎；中文问句在单引号内安全。票 23 先例同款。
- **replacement_pointers 的红相可在合成域造出**：给 GLS 禁用词条目 definition 写第二个「替代口径=<MU 屏名>」即让替代指路带出面外 ID（_REPL_PATTERNS 逐名捕获后对全索引做名称匹配）——不必动 fixtures 即可让该路径 TDD 红→绿。

## 验收（对照票面 AC 表，逐条实证）

- [x] AC1：复现用例翻绿——上表前后对照；CORE-09 修前出厂集唯一红、修后 ok；status=answered、SCR-BOHAI-01 不在 hits/citations/scaffold_commands、AGG-BOHAI-001 在 hits（源：AC 表 AC1）
- [x] AC2：CORE-01–08 集相等探针全过——期望集与 expected-answers/ 逐集交叉核对（差异如上记账，答案侧无面外 ID；四份旧答案 ID 白名单正则断言持续在守）（源：AC 表 AC2）
- [x] AC3：单源声明双向——卡依赖行含 core（specs/modules.md semantic-service 卡独立 script 行）、SKILL.md 契约节含声明句、`install_skills.py sync semantic-service` 后 `--check` 零漂移、边界闸无违规（源：AC 表 AC3）
- [x] AC4：全厂 8/8 出厂集通过；单测 319=316 既有+3 新，零倒；`bash tools/ci.sh` 四闸绿（源：AC 表 AC4）
