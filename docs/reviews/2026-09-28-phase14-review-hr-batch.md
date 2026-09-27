# 第十四轮外部审查 · 第四域 hr 接入批（票 78–80，commits e6adf63 / bda7e5a / 39aaaf2）

## §1 元信息

- 被审提交：三提交全链——e6adf63（票 78 立项）→ bda7e5a（票 79 建模）→ 39aaaf2（票 80 导出与批收官，HEAD）
- 审查人：外部审查子代理（ZCode）
- 审查日期：2026-09-28
- 审查方式：只读。逐件精读 `git show` 三提交全量 diff 与 ontology/hr 八件对 references/hr-source/employees.sql（127 行 DDL）人工对照；实跑 schema_check（单域+仓根）、app_pack_gen/skill_pack_gen/mcp_manifest_gen 三 `--check` 再制、review_gate verify --all、graph_index --json、semantic_service_core 两问 --json、report_numbers、`bash tools/ci.sh` 最终树原样（退出码 0「CI: 全绿」）；锚点 grep 断言现跑；/tmp 中转件用后即删，仓内零写入（本文档除外）
- 授权链核对基准：docs/meta/owner-delegation-2026-09-28.md（协议⑪承载件）
- 结论速览：**六面全 PASS；P1=0，P2=0，P3=6；判定：可收货**

## §2 六项审查面逐项判定

### 面 1 · 建模保真度（核心）——PASS（附 P3×3）

**① 列/PK/FK/ENUM/UNIQUE/可空/级联覆盖：24/24 列零漏零改义。** 逐表对照（m1-object-model.yaml 行号为证据位）：

| 表 | DDL 列 | M1 覆盖 | 结构件 |
|---|---|---|---|
| employees（employees.sql:41-49） | emp_no/birth_date/first_name/last_name/gender/hire_date 六列全 NOT NULL | AGG-HR-001 六属性，empNo unique:true（m1:31-42） | RULE-HR-001（ENUM 值域，m3:19-33） |
| departments（:51-56） | dept_no PK + dept_name UNIQUE | AGG-HR-002 双 unique:true（m1:55-62） | RULE-HR-004（UNIQUE，m3:73-87） |
| dept_emp（:68-76） | emp_no/dept_no/from_date/to_date，PK(emp_no,dept_no)，双 FK CASCADE | AGG-HR-003 四属性全 required（m1:77-80），PK 记于描述（m1:70-71） | ASSOC-001/002 + RULE-HR-003（视图现行判定） |
| dept_manager（:58-66） | 同构四列 | AGG-HR-004（m1:94-97） | ASSOC-003/004 |
| titles（:78-86） | emp_no/title/from_date/**to_date 可空**（:82 无 NOT NULL，六表唯一可空列） | AGG-HR-005 toDate **无 required 键**=如实可空（m1:114），RULE-HR-005 inputParams required:false + 表达式空值放行（m3:96-102） | ASSOC-005 |
| salaries（:88-96） | emp_no/salary/from_date/to_date，PK(emp_no,from_date) | AGG-HR-006（m1:128-136） | RULE-HR-002 一期一条（m3:35-50） |

- **六处 ON DELETE CASCADE（employees.sql:63,64,73,74,83,93）全部升 ASSOC 一行不丢**：ASSOC-HR-001…006（m1:148-200），六 FK→六关联一一对应；级联语义登记 RULE-HR-006（narrative 形态，schema.md §6 两形态机判面首个实战用例）——narrative 有 P3-3 小疵见 §3。
- **ENUM**：gender ENUM('M','F') → M1 enumValues [M,F]（m1:39）+ DICT-HR-001（m1:139-145，且注明中文释义为通识注记非新增证据）+ RULE-HR-001，三处一致。
- **2 视图**：dept_emp_latest_date/current_dept_emp（employees.sql:98-108）→ 未硬造对象，语义落 RULE-HR-003（INNER JOIN+MAX(from_date) 条件逐句转写，m3:56-60）+ Q7 结构证据，处理正确。

**② 「发明」检查：零硬发明，哨兵一处越线（P3-1）。** 9999-01-01 在 DDL 内零出现——RULE-HR-003 明注「哨兵为数据惯例（Q3 已裁注记，非本判定依据）」（m3:59-60）、GLS-HR-006 同口径（glossary:67），规则登记面守住了 Q3 裁决；但 QR-HR-001 isCurrent 列的 sourceExpression **实际用了哨兵等值测试**（m7:66 `s.toDate == DATE '9999-01-01'`），且 M2 BH-QuerySalary 注释称该列语义来自 RULE-HR-003（m2:22）——RULE-HR-003 的逻辑是视图 max(from_date) 判定，与哨兵测试不同源，交叉引用失真（细则见 §3 P3-1）。职级值集确实未字典化（Q2，DDL 无 ENUM/CHECK 证据，title 为 String 自由文本 m1:112）✓；salary 未标单位（Q1，「期间薪档」，m1:130-132/GLS-HR-004:52 注明「DDL 无单位证据」）✓；数据量级（九行部门/30 万员工）一律注记不入本体（m1:50、细稿 §五）✓。实体六表直映、属性名=列名驼峰化（emp_no→empNo 头注声明 m1:8），CHAR(4)/VARCHAR 长度信息全域一致不建模，无改义。

**③ M7 alias.field 一致 + QR↔BH 双射：机判+人核双过。** 五出口全部 sourceExpression/conditions 左值逐个对照 M1 属性名——QR-001 s.fromDate/s.salary/s.toDate/e.empNo/e.lastName/e.firstName、QR-002 a.fromDate/a.empNo/d.deptNo/d.deptName、QR-003 t.title/t.toDate 等、QR-004 m.empNo/m.fromDate/m.toDate、QR-005 e.hireDate/e.gender/e.empNo——全部命中 M1 定义，零拼错；五 QR behaviorRef ↔ 五 BH（QuerySalary/Headcount/Title/Manager/Tenure）严格一对一双射，M2→M7 零反向引用（单向 M7→M2）。schema_check L3-1/L3-2 单域 0 违规机判背书（实跑输出「L1: 0 | L2: 0 | L3: 0 | L4: 0」）。

### 面 2 · 拍板链合规（协议⑪）——PASS

- **授权记录独立落盘且原文转录**：docs/meta/owner-delegation-2026-09-28.md §一逐字引 Owner 会话原文（「…需要拍板的按你推荐的拍板」），§二授权范围四项、§三 L0 自设边界（**devkit/skillpkg 审记 approve 不代行**——by= 机械取 git user.name 会留「Owner 已审」假痕）、§四拍板留痕 D1–D3；「一次性、限当批」明示（:27-29）。细稿头部引授权记录 §二2（细稿:6-8），逐问表头标「按授权逐问落定：推荐+依据=拍板」（细稿:53）。
- **Q1–Q8 每问「推荐+依据」齐备**（细稿 §四表 55-64 行）：Q1 期间薪档不标单位/Q2 职级不字典化/Q3 现行判定以视图语义为准+哨兵注记/Q4 级联如实登记+业务面只读/Q5 照 DDL 拆分+出口拼接/Q6 ÷365.25 一位小数/Q7 五出口不越权/Q8 四主体推荐档待转正——推荐与依据两列俱全，且 M1/M2/M3/M5/M7/GLS 行内注记可反查（如 m1:9-10、m3:6-7、m5:4-5、m7:4-8）。M5 全件标「推荐档待 Owner 转正」✓。
- **核验边界执行（关键项）：PASS，零违规。** `grep -c '"hr"' exports/reviews/devkit-review.json exports/reviews/SKILL-review.json` → **0/0**；`review_gate.py verify --all` 实跑 7 件：pass 3（bohai devkit/skillpkg+pkb devkit）/ **pending 4（his×2+hr×2）**，hr 两件均报「无本目标审记…按待人审处理」；devkit.md 状态行「待Owner人审」（exports/devkit/hr/devkit.md:3）。L0 未代审，授权 §三边界如实执行——**不存在 P1 代审违规**。

### 面 3 · 闸与导出面——PASS

- `python3 tools/schema_check.py ontology/hr` → hr(profile=v9-full,7文件)，L1:0 L2:0 L3:0 L4:0，exit 0；`schema_check.py ontology` → **四域（bohai/his/hr/pkb）26 模型文件 L1–L4 全零**，exit 0。
- `app_pack_gen.py ontology/hr --check exports/devkit/hr` → 「再制一致…逐字节一致」exit 0；`skill_pack_gen.py ontology/hr --models M1,M3,GLS --check exports/skillpkg/hr` → 逐字节一致 exit 0；`mcp_manifest_gen.py ontology --check exports/mcp/capability-manifest.json` → 逐字节一致 exit 0（票 79 声明的 mcp-publisher 出厂集红灯再制清偿，实证复现）。
- verify --all：7 件（pass 3/pending 4），最差退出码 1——与协议⑥「审记缺失=挂账不阻塞四闸」口径一致，挂账面（his×2+hr×2）与票 80 AC1/走查 §四记载一致。
- `bash tools/ci.sh` 最终树原样实跑（协议⑩）：单测 667 → 出厂集 17/17 → 边界闸无违规（豁免 10 条）→ 归档闸全对 → **「CI: 全绿」**。三提交信息均称 CI_EXIT=0，审查窗独立复跑证实。

### 面 4 · 多域隔离——PASS

- `git diff e6adf63^..39aaaf2 --name-only`（三提交全量）：**ontology/bohai、ontology/his、ontology/pkb 下零文件改动**（--stat 空输出，exit 0）；批内唯一共享件改动=exports/mcp/capability-manifest.json（全域再制件，预期内）与 tools/test_meta_probe.py / test_onboard_check.py / test_report_numbers.py（域数字面量动态化，属审查任务明示允许项）。
- 四域体检 json 实读：体检-2026-09-28-{bohai,pkb,his,hr}.json 全部 conclusion=PASS、exitCode=0。
- 票 79 边界声明「不动既有三域文件」与实际一致；票 76 分桶回归（跨域借 ID 双红）未被本批扰动（仓根全绿+单域全绿双态实证）。

### 面 5 · 文档与账实一致——PASS

- **图索引 248 节点/400 边可复现**：`graph_index.py ontology --query "AGG-HR-001" --json` → `stats: {nodes: 248, edges: 400}`，与 hr-walkthrough.md:20 一字不差；hr 元素六点抽核（AGG-HR-001/006、RULE-HR-003、FLOW-HR-001、QR-HR-002、GLS-HR-006）全命中。
- **语义服务两问复现**：问「人司年限口径是什么？」→ answered（GLS 术语二级解析），**引用 14 条**；问「部门在职人数怎么算？」→ answered，**引用 18 条**；命中链成员与走查 §三记载一致（GLS-HR-008→RULE-HR-008→BH-HR-QueryTenure→QR-HR-005；AGG-HR-002/GLS-HR-002→BH-HR-QueryHeadcount→QR-HR-002→RULE-HR-007）。两问引用 ID 全集对 ontology/hr 定义集机扫：**悬空引用零**（审查窗独立脚本复核 31 个引用 ID 全可解析）。
- **快照账实一致**：report_numbers 现跑（HEAD=39aaaf2）与 docs/meta/指标快照-2026-09-28.md 逐项相同——667 单测/域 4/模型文件 26（hr 7+豁免 1）/生成物 7/审记态 pending×4；快照生成时点 2026-09-28 01:11:24（bda7e5a）与票 80「本批数字引自快照」声明一致。
- **三期报告 §2 dated 注记守纪律**：git show 39aaaf2 核对——「现值：638 单测」批收官指标行**未回改** ✓；域面更新（hr 域循环行+「三域 19」→「四域 26」命令注释）在 dated 注记（「域面更新（2026-09-28，票 80，dated 注记……数字以当期快照为准）」，三期报告 §2 顶部）辖域内且 26 有快照背书——判定为域面更新非计数回改（措辞张力见 §3 观察项 b）。
- **票 Touches 对账**：票 79（12 件列 12 件实改，缺省票自身=房规）与票 80（19 件列 19 件实改）**逐件一致**；票 78 缺列 owner-delegation 记录一件（P3-5），其余 9 件一致。
- **lessons/64 三节齐**：做了什么/坑（五坑，与提交信息「五坑台账」对表）/取舍（审记不代审、COMMAND×0/MU/不字典化、narrative 首实战）三节俱全。
- 豁免复核④：hr 仅 MU omittedModels 登记（manifest.json:7-12，bohai 票 13 先例式），非审记豁免不入 docs/meta/exemption-reviews.json 辖域（该文件复核对象=.skill-deps-allow 10 条边界闸豁免，本批零变化）——「无新增豁免」结论成立。

### 面 6 · 提交信息声明抽验——PASS

| 声明（出处） | 复跑结果 |
|---|---|
| 「锚点推进 grep 断言 4/4」（39aaaf2） | 现树四 grep 全命中：AGENTS.md「第四域 hr 接入批收官」×1、目录地图「第四域 hr 人力资本已进仓」（AGENTS.md:29）、三期报告 dated 注记 ×1、三期报告 ontology/hr ×2 |
| 「capability-manifest 再制后逐字节一致」（bda7e5a） | `--check` exit 0 逐字节一致（面 3） |
| 「图索引 248 节点/400 边」（39aaaf2） | --json stats 精确复现（面 5） |
| 「verify --all 7 件 pass3/pending4」（39aaaf2） | 实跑 7 件 3 pass/4 pending（面 2） |
| 「四域 26 文件全绿」（bda7e5a/39aaaf2） | 仓根 schema_check 26 文件 L1–L4 零（面 3） |
| 「CI_EXIT=0」（三提交） | 审查窗最终树原样复跑「CI: 全绿」（面 3） |
| 「smoke 文案补 hr 行（断言面如实注未建）」（39aaaf2） | tools/mcp_smoke_client.py:2-6/epilog 增 hr 行且明注「ID 断言正则仍为 bohai 词面未建」——如实 |
| 「三处实跑测试域数字面量动态化」（bda7e5a） | 三 test_* 文件 diff 属实（域清单改文件系统动态枚举+>=4 下限）；667 测试 ci.sh 全绿 |

## §3 发现分级清单

### P1（必须修）

无。

### P2（应修）

无。

### P3（小疵，不阻塞收货）

1. **QR-HR-001 isCurrent 列以哨兵为实际判定式，且 M2 注释交叉引用失真**：m7-report-model.yaml:66 `sourceExpression: s.toDate == DATE '9999-01-01'` 使哨兵成为该出口列的判定依据（超出 Q3「采纳为数据惯例**注记**」的字面辖域）；m2-behavior-model.yaml:22 注释「RULE-HR-003 # 现行判定（『是否现行』列语义）」与 m7:66 注释「现行判定语义 RULE-HR-003」均指向 RULE-HR-003，但该规则逻辑是视图 max(from_date) 判定（DepartmentAssignment 域），与哨兵等值测试不同源——薪酬出口并无视图背书，注释把两套语义混为一谈。缓解事实：RULE 登记面本身守 Q3（视图语义）、哨兵用法有「数据惯例」透明注记、无任何闸/VALIDATION 依赖哨兵。建议：下次票二选一——isCurrent 改按 RULE-HR-003 同构语义（s.fromDate == MAX(s.fromDate) OVER s.empNo）或把 m2:22/m7:66 注释改为「出口哨兵惯例标记，非 RULE-HR-003 语义」。
2. **细稿 §六 与实建 M3 规则数漂移**：docs/requirements/hr-人力资本-细稿.md:78 写「M3（七规则）」，实建八规则（RULE-HR-001…008，manifest/ticket 79/commit message 均按「八规则」口径）——细稿自称「口径以本细稿为进仓真源」（细稿:7），规划件与建成件差一处未回注。建议：细稿 §六 补一行 dated 勘误（建模时 RULE-HR-007 在职人数口径单列），不改历史只加注。
3. **RULE-HR-006 narrative 级联计数错位+部门侧级联缺记**：m3-rule-model.yaml:109-123 叙事只讲「删除 employees 行将级联清除四轨迹表……（六处 ON DELETE CASCADE）」，但六处 FK 中两处是 dept_emp.dept_no/dept_manager.dept_no → departments（employees.sql:64,74），**删除 departments 行的级联路径（部门删→任职/管理行清）全件未叙述**，且「六处」挂在被叙述的员工删除路径下属计数错置（该路径仅涉四处）。规则自述目的即「登记源库语义供集成方知悉」，缺部门侧叙事是实义缺格。建议：narrative 补一句部门侧级联并拆分计数（4 处→employees、2 处→departments）。
4. **授权记录 D1 理由句「8 表 6 实体」与素材实况差**：docs/meta/owner-delegation-2026-09-28.md:35 写「8 表 6 实体」，素材实为 **6 表+2 视图**（employees.sql 六个 CREATE TABLE+两个 CREATE OR REPLACE VIEW；细稿 §二、RESOURCES.md R14、README-素材溯源全按 6 表口径）——授权记录正文（引文）无误，仅 L0 解读栏理由句数字失真，不影响授权效力与选型结论。建议：随下次文档对齐加一句 dated 勘误注（记录不重录）。
5. **票 78 Touches 漏列授权记录**：tickets/78-hr域立项.md:5 未列 docs/meta/owner-delegation-2026-09-28.md——该记录是本票最核心产物（票面批次行/AC4 有引用，不属漏做，属 Touches 面漏记）；对账纪律（AGENTS ⑧「票面引用必须真实存在」的姊妹面）宜含授权承载件。建议：留痕即可，后续立项票 Touches 恒列授权记录。
6. **第六期拆票方案草案滞留未跟踪态**：docs/第六期端到端实弹拆票方案-草案.md 未入 git（本次 ci.sh 归档闸警告线实弹报出「[⚠ 未跟踪]」）——按授权 §三「仅落盘备晨拍板」属半故意态（票 77 审查同款先例：授权文件当时也未跟踪、次票入仓），但「落盘」不进版本库即距 lessons/0019 误删实证一线之遥，且票 80 边界只说「另落盘」未记路径，换窗口即不可发现。建议：晨拍板后随票入仓；若长期待裁则把路径记入走查/残项查询面。

### 观察项（不计级，记录备查）

a. **departments lifecycle [设立,撤销] 为弱证据词汇**（m1:51-53）：DDL 无部门时间列，「设立/撤销」是 schema lifecycle 字段的注记性填充而非结构事实（员工 lifecycle 有「不由本表字段承载」的免责注记，部门无同类注记）——与既有三域同款做法，不判缺陷；db-reverse 域后续可考虑 lifecycle 词表注「推定」两级。
b. **三期报告 §2 「计数行照旧不回改」措辞张力**：dated 注记称计数行不回改，同票却把命令注释行「三域 19 模型文件」改为「四域 26」——按「批收官指标行（638 单测行）不动+域面更新有 dated 注记+数字有快照背书」读法为自洽，建议后续把「计数行」措辞限定为「批收官指标行」以免歧义。
c. **salaries PK 有 RULE 而其余三复合 PK 仅描述注记**：titles PK(emp_no,title,from_date)/dept_emp、dept_manager PK(emp_no,dept_no) 只在 M1 描述行+细稿表落账，M3 未立对应唯一性规则——M3 头注「不凑数」自洽（三个 PK 语义被时态行结构自然承载，唯薪酬 PK 有出口去重用途故单列），判定为有意取舍非覆盖缺口。

## §4 结论

- 六项审查面**全 PASS**：建模保真度（24 列/6 FK/ENUM/UNIQUE/可空/级联全覆盖，QR↔BH 双射，alias.field 零错）、拍板链（授权记录独立落盘原文转录、Q1–Q8 推荐+依据齐、**审记 pending 边界零违规**）、闸与导出（单域+仓根 26 文件全绿、三再制逐字节一致、verify --all 7 件 3pass/4pending、ci.sh 复跑全绿）、多域隔离（三域模型文件零改动、四域体检全 PASS）、文档账实（248/400、14/18 引用、悬空零、快照全部现跑复现）、提交声明（8 项抽验全对得上，含锚点 grep 4/4）。
- **P1=0，P2=0，P3=6**：六条 P3 均为注记/叙事/账面层小疵，无一影响闸绿、结构覆盖或拍板链效力；其中 P3-1（哨兵注释混指）与 P3-3（级联部门侧缺记）是仅有的两处「模型文字与证据源有出入」，透明注记均在、修复成本低。
- **最终判定：可收货。** 建议将 P3-1/P3-3 合开一张小整改票（或随第五域接入票顺带清偿），P3-2/4/5/6 留痕随下次文档对齐处理；审记挂账 his×2+hr×2 维持待人审，第五域/第六期开工前按授权边界候 Owner 晨拍板。
