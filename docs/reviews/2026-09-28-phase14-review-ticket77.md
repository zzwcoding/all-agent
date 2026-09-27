# 第十四轮外部审查 · 票 77 多域扩展防呆四件（commit 59ca813）

## §1 元信息

- 被审提交：59ca813（HEAD，票 77 收官 · 多域防呆四件），前置 87b676c（lessons/0019 误删清理）
- 审查人：外部审查子代理（ZCode）
- 审查日期：2026-09-28
- 审查方式：只读——四工具实跑（onboard_check / meta_probe --list-domains / review_gate verify --all / report_numbers）、ci.sh 最终树原样实跑、`git show 59ca813` 全量 diff 精读、667 测试 discover 现跑（26.4s OK，skipped=3）、AGENTS/PRD/lessons/快照逐处比对；临时夹具一律落 /tmp 并清除，仓内零写入（本文档除外）
- 结论速览：**AC 8/8 PASS；P1=0，P2=0，P3=6；判定：可收货**

## §2 AC1–AC8 逐条核验表

| # | 断言 | 判定 | 证据 |
|---|---|---|---|
| AC1 | onboard_check 对 bohai/his 实跑硬项全绿；pkb skillpkg 缺席仅警告不红 | **PASS** | 实跑 `python3 tools/onboard_check.py`：bohai 硬项 3/3 ✔（manifest/语义闸/devkit）、his 硬项 3/3 ✔（审记双 pending 为 ⚠ soft 如实报）、pkb `⚠ [soft] skillpkg 导出 — 缺 exports/skillpkg/pkb/SKILL.md（豁免域…）`；总结「硬缺口 0，软警告 5」，退出码 0。单测 test_bohai_hard_green / test_his_hard_green / test_pkb_skillpkg_absent_warn_not_fail（tools/test_onboard_check.py:91–106）套件绿 |
| AC2 | 临时夹具缺 manifest / 缺 devkit → exit 1 且逐项报缺 | **PASS** | /tmp 夹具实跑 `onboard_check ghost --root <tmp>`：`✘ [hard] manifest 在场`、`✘ [hard] 语义闸单域绿`、`✘ [hard] devkit 导出` 逐项列出，裸退出码 1（先管道后裸跑两次核码，未掩码）。单测 test_missing_manifest_is_hard_fail_exit_1 / test_missing_devkit_hard_and_skillpkg_warn_only（test_onboard_check.py:53–72）绿 |
| AC3 | meta_probe --list-domains 实跑出 bohai/pkb/his 三域 | **PASS** | 实跑输出 `bohai\nhis\npkb`，退出码 0；与 onboard_check.list_domains 同源一致性有专测钉死（test_enumeration_same_source_as_meta_probe，test_onboard_check.py:108–117） |
| AC4 | verify --all 逐件报状态（pkb 无 skillpkg 不在面）；夹具一 pass 一缺失 → exit 1 | **PASS** | 实跑 5 件（3 devkit + 2 skillpkg，pkb skillpkg 自然不在枚举面）逐行 `[pass]/[pending]`，his 双 pending 如实报，小结「最差退出码 1」，退出码 1；夹具单测 test_all_one_pass_one_pending_exit_1（test_review_gate.py VerifyAllMode）绿；空 exports → exit 2 有专测（test_all_empty_exports_exit_2） |
| AC5 | report_numbers 夹具计数正确、git 缺席降级「未知」；实跑落盘快照 | **PASS** | 夹具单测（unitTests=1、gitHead=「未知」、md+json 双件落盘、空根全零）绿；实跑 stdout 与已提交 docs/meta/指标快照-2026-09-27.md{,.json} 内容一致；667 与 `unittest.TestLoader().discover('tools','test_*.py').countTestCases()`=667 现核相符 |
| AC6 | archive_check 未跟踪项被报出且 exit 0；非 git 目录静默 | **PASS** | WarnUntracked 四测全绿（未跟踪列出/已跟踪不列/净仓空表/非 git 静默/报告带出不阻退出码，test_archive_check.py:190–237）；本次审查实跑 ci.sh 时警告线实弹触发（`[⚠ 未跟踪] docs/meta/owner-delegation-2026-09-28.md`）且归档闸仍 pass——只警不拦实证 |
| AC7 | AGENTS 协议①⑥无三域硬编码命令名单；目录地图含两新工具 | **PASS** | `grep "verify exports/" AGENTS.md` 零命中（exit 1）；AGENTS.md:47 协议①「域清单以 `meta_probe --list-domains` 现跑为准，新域接入面用 `onboard_check.py`」、⑥「`review_gate.py verify --all`——自动枚举…逐行报状态…任一非 pass exit 1」、新增⑧指标快照条；AGENTS.md:30 目录地图 tools 行含 onboard_check+report_numbers 两件；docs/prd.md:66 F14 行含票 77 四件注记 |
| AC8 | `bash tools/ci.sh` 最终树原样全绿（协议⑩） | **PASS** | 审查窗对当前树（=59ca813+未跟踪授权文件）原样实跑：`出厂集 17/17 通过`→`边界闸 无违规`→`归档闸: 全部文件对得上`→`CI: 全绿`，`CI_EXIT=0` |

测试诚实度抽核：无同义反复。关键断言均验真实行为——test_verify_record_returns_tuple_without_printing 断言 stdout 严格为空（核「核心函数不打印」契约）、test_enumeration_same_source_as_meta_probe 跨工具互核、test_report_carries_untracked_and_does_not_block_exit 同时断言 status=pass 与 untracked 含新件（真验「只警不拦」而非只验其一）、test_tmp_root_sorted_enumeration 验排序与非目录项排除。

## §3 发现清单

### P1（必须修）

无。

### P2（应修）

无。

### P3（小疵，不阻塞收货）

1. **提交信息测试计数与实况不符（恰与本票「数字现跑现取」主题相讽）**：commit 59ca813 信息称「新增 24：onboard 9+快照 4+verify-all 6+list-domains 4+untracked 5」——分量自相加为 28，实际实数为 27（`grep -c "def test_"` 前后差：onboard 9 / 快照 4〔grep 计 5 系 seed_fixture 字符串字面量里的 `def test_ok` 干扰〕/ verify-all 6 / list-domains 4 / untracked 4，非 5）；「tools 140 测试」=五 touched 测试文件实数之和（9+4+44+62+21=140）无误。错误数字未进任何落盘文档（`grep "新增 24"` 于 docs/AGENTS/lessons 零命中），快照 667 本数正确。建议：不动（commit message 不可改），留痕即可；后续收官数字一律走 report_numbers 口径。
2. **AGENTS.md ⑥ 未提 verify --all 的配置错 exit 2 边**：`tools/review_gate.py` cmd_verify_all 以 `worst=max(worst, code)` 收敛，审记非法（invalid）时退出码为 2 非 1；票面写全了「（配置错 exit 2）」，AGENTS ⑥ 只写「任一非 pass exit 1」。建议下次文档对齐顺带补「（配置错 exit 2）」四字。
3. **verify --all --json 为 JSONL 而非单一 JSON 文档**：实测 stdout 为逐行 JSON（每行一对象，小结行已正确抑制）；`--json` 帮助文本只说「stdout 只含 JSON」，消费方若整体 `json.loads` 会炸。建议帮助文本注明「逐行 JSON（JSONL）」或下次票改包数组。
4. **onboard_check._grep_glob 对目录条目无 is_file 防护（潜伏）**：`p.read_text(...)` 未过滤目录，若 fixtures/semantic-service/expected-answers 或 fixtures/l5-scoring/expected 未来出现子目录，`**/*` 会把目录喂给 read_text 抛 IsADirectoryError 使工具崩。现两目录均无子目录（实测 NONE），不可达。建议补 `if p.is_file()` 一行。
5. **「逐域十项」名实微差（超交付非缺陷）**：票面/帮助文本称十项，实现实际 11 类（另含 devkit.json 伴生软项），双审记目标域输出 12 行。属多不属少，建议下次措辞改「十项+」或实数。
6. **词面示例硬编码（非逻辑硬编码，记录备查）**：tools/onboard_check.py:4/12/117 详情文案以「pkb」作豁免域示例——枚举逻辑全动态（list_domains 唯一源），不属本票根治的「声明面写死单域」问题；meta_probe 的 CORE_QUESTION_SETS/GRAPH_BASELINE_ANCHORS 按域冻结问集为票 64/69 既有设计且本票未触碰。均不判缺陷，记录防误读。

### 多域隔离回归专项（本票主题的正向确认）

- 四工具逻辑面零域名词面硬编码：onboard_check/report_numbers 经 list_domains 全域动态枚举；review_gate verify --all 用通配 `VERIFY_ALL_GLOBS = ("exports/devkit/*/devkit.md", "exports/skillpkg/*/SKILL.md")`（tools/review_gate.py:357）且被 report_numbers.export_rows 复用为唯一枚举源；meta_probe --list-domains 现跑枚举。加第四域零改代码、零改 AGENTS ①⑥⑧（grep 断言在位）。
- verify_record 提炼干净：单件 verify 与 --all/onboard_check/report_numbers 四方共用同一状态机（tools/review_gate.py:296–349），无逻辑复制；配置错仍走 stderr（单件与 --all 人工模式均 `file=sys.stderr`），票 45 契约保持（lessons/63 坑 1 自录的四条红测试即其证据）。
- 归档闸 quotepath=false、`line[3:]` 剥前缀、git 缺席/超时静默、不入退出码、JSON 报告带出——边界齐。

## §4 结论

票 77 四件全部按票面交付且实跑属实：onboard_check 三域实跑硬面齐、软项如实警告（his 双 pending、L5 面未建均不洗白）；meta_probe --list-domains 与 review_gate verify --all 把 AGENTS 协议①⑥从「手抄三域名单」改为「现跑枚举」，verify_record 提炼为四工具共用状态机且未复制逻辑、stderr 契约保持；report_numbers 快照六项数字（667 测试/三域 7·8·4 模型文件/豁免 1·2·0/五生成物审记态/15 篇体检留痕）与当前树逐一相符，gitHead 记 87b676c 属提交前快照正常现象；归档闸未跟踪警告在本审查实跑 CI 时即实弹触发且不阻闸；ci.sh 最终树原样复跑 CI_EXIT=0（AC8 独立复核通过）。八条 AC 全过、零 P1/P2；六条 P3 均为措辞/潜伏/记录性小疵，无一条涉及行为错误或闸完整性，其中两条（AGENTS ⑥ exit 2 补字、_grep_glob is_file 防护）建议随下一张文档/工具票顺带清偿。**判定：可收货。**
