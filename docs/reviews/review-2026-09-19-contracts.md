# 接口契约对账报告 · 卡（specs/modules.md）↔ 实现（skill/脚本/出厂集/本体仓）

> 日期：2026-09-19 · 对账范围：specs/modules.md 全部卡 × 磁盘实际（skills/、~/.agents/skills/、tools/、fixtures/、ontology/）
> 方法：逐卡比对 + 双位置 diff + install_skills --check + fixture assertions 逐条读 + ci.sh 实跑复验（四闸全绿复现）
> 结论速览：**整体一致性很高，5 张已建卡全部账实相符；仅 2 个脚本卡上未登记（L3 清单漏账）+ 1 处命名易误读。幽灵 skill 0，幽灵断言 0。**

---

## 1. 已建 skill 卡 ↔ 磁盘目录：一致（幽灵 0 / 未声明 0）

modules.md 中已建卡（非二期占位）共 **5 张**：onto-modeler / db-reverse / impact-analyzer / semantic-service / proposal-pool。

| 卡 | 仓内 skills/ | 安装位 ~/.agents/skills/ | 双位置内容 | install-registry.json |
|---|---|---|---|---|
| onto-modeler | 有 | 有 | `diff -rq` 一致 | 已登记 |
| db-reverse | 有 | 有 | 一致 | 已登记 |
| impact-analyzer | 有 | 有 | 一致 | 已登记 |
| semantic-service | 有 | 有 | 一致 | 已登记 |
| proposal-pool | 有 | 有 | 一致 | 已登记 |

- **幽灵（卡上有、磁盘没有）：0**。二期占位卡 7 张（requirement-explorer / code-reverse / doc-extractor / app-generator / skill-publisher / mcp-publisher / meta-doctor）磁盘两侧均无实体——占位卡未偷跑，符合卡名纪律。
- **未声明（磁盘有、卡上没有）：0**。仓内 `skills/` 恰好 5 个目录；`tools/install-registry.json` 恰好登记同 5 名；`python3 tools/install_skills.py --check` 实跑输出 5 个 skill 全一致、无孤儿（孤儿三要素检测未见异常）。
- 备注：`~/.agents/skills/` 下另有约 30 个目录（sdd-flow2、tdd、grilling 等），属用户全局其他 skill，不在本仓登记职责内，且 install_skills 未将其判孤儿——不算未声明。

## 2. 触发面 ↔ SKILL.md frontmatter description：5/5 语义一致

| 卡 | 卡面触发面 | SKILL.md description 开头 | 判定 |
|---|---|---|---|
| onto-modeler | "给某域建本体/修整本体草案/加模型元素" | "本体建模工序——给某域建本体/修整本体草案/加模型元素。…" | 一致（几乎逐字） |
| db-reverse | "把这个库/这份 DDL 逆向成本体" | "数据库逆向器——把这个库/这份 DDL 逆向成本体。…" | 一致 |
| impact-analyzer | "改 X 会影响什么/评估这个变更" | "变更影响分析器——改 X 会影响什么/评估这个变更。…" | 一致 |
| semantic-service | "查口径/问业务对象/解析指标含义" | "运行时语义服务——查口径/问业务对象/解析指标含义。…" | 一致 |
| proposal-pool | "把这条信号起草成提案/过一遍提案池/查提案池状态" | "提案池处理——把这条信号起草成提案/过一遍提案池/查提案池状态。…" | 一致 |

每个 description 还额外承载了卡面的"边界"要点（只产草案走 MR / 只读仓 / 写意图转提案池 / 自动化止于提案），无脱节、无越界扩权表述。

## 3. reads/writes 契约 ↔ SKILL.md 实际声明（抽查 3 张）：一致，1 处无害出入

**onto-modeler**
- reads：卡=`ontology/schema/**`+`ontology/patterns/**`（二期）+域素材；SKILL.md=schema 文档+两份机读表（模型注册表、依赖白名单）+用户域素材。patterns 件库 SKILL.md 未提——与卡上"二期"标注自洽，非脱节。
- writes：卡=`ontology/<域>/**` 草案；SKILL.md=同 + 两份工序产物（profile 建议、骨架文件清单）——这两份正是卡 Seam 段"断言产出的 profile 建议与骨架文件清单"所指，账实相符。
- 依赖：`tools/schema_check.py` 双侧一致。

**semantic-service**
- reads：卡=`ontology/**`（经 graph_index）+模型注册表（只索引 business-core）；SKILL.md=同，且划界依据明确指向 model-registry.json 的 camp 字段（references/retrieval-waterfall.md §5）。
- writes：卡=无（只读服务）；SKILL.md=无——双侧都是"写意图一律转提案池"。
- 依赖：`tools/graph_index.py`（--query/--closure/--impact/--json 四面）双侧一致。

**proposal-pool**
- reads：卡=`docs/proposals/**`+`ontology/**`+`references/proposal-format.md`+信号素材；SKILL.md 四项全对齐，proposal-format.md 还明确了"仓级共享件不入私件目录"的理由（与边界规则"任何 skill 读另一 skill 私件=禁止"自洽）。
- writes：卡=PROP-<域>-<NNN>.md + 裁决落痕（只动 status 与裁决注记）；SKILL.md 同，且重申"不直改 ontology/**、不起 git 分支"。
- 依赖：`tools/proposal_check.py` 双侧一致。

**结论**：三张抽查卡的输入输出契约与实际声明无实质出入；唯一"出入"是 onto-modeler 卡面保留了二期 patterns 读面而 SKILL.md 未实现——卡已自我标注二期，属预留而非漂移。

## 4. fixtures/ 覆盖：5/5 已建 skill 均有非空出厂集，断言是真闸不是摆设

| skill | 出厂集 | 断言数 | 核心行为验证方式（抽样证据） |
|---|---|---|---|
| onto-modeler | fixtures/onto-modeler/（输入+参照产物+负变体） | 19 | AC3 cmd 实跑 `schema_check.py {fixture}/expected-output/bohai` 须"语义闸: 全过"；AC4 负变体 cmd-fails 须报 dangling-ref+AGG-BOHAI-999 |
| db-reverse | fixtures/db-reverse/（8 表 SQL+expected-output） | 9 | AC3 实跑语义闸全过；断言钉"证据非权威，待 Owner 确认"头部声明与 dirty-signs 在档 |
| impact-analyzer | fixtures/impact-analyzer/（三变更场景） | 17 | 三条机读佐证实跑 graph_index --impact --json（全链/字典/空集）；正则守卫"hops= 行必须同行含 via="、"无影响场景禁入其他 ID" |
| semantic-service | fixtures/semantic-service/（Golden Question+expected-answers+guard-corpus） | 41 | 八问实弹 `semantic_service_core.py --ask` 回归（CORE-01–08，ci.sh 尾部实跑可见）；拒答态正则禁编造 ID；CIT-01–05 引用清单比对；guard-corpus good/bad 例集压真答案 |
| proposal-pool | fixtures/proposal-pool/（正例 2+负变体 6） | 15 | 正例实跑 proposal_check exit 0（"解析提案 2 份"）；六负变体各自 cmd-fails 且 outputContains 钉死违规码（proposal-schema/target/conflict/evidence） |

判定：**非摆设**。每套出厂集都有"cmd 实跑真闸 + 负变体反证"双层，纯 file-contains 的参照产物断言也都被 cmd 断言锚定。另：`fixtures/graph_index`、`fixtures/schema_check` 属 L2/L3 规约与脚本自己的出厂集（非 skill 级），`fixtures/mcp-publisher` 实测的是 L3 脚本 `mcp_manifest_gen.py`（--check 防陈旧等 4 断言）——**注意**：mcp-publisher 作为 skill 仍是二期占位卡，出厂集目录先于 skill 实体存在（服务的是票 23 脚本），命名上易误读为"skill 已有出厂集"，建议在该卡或目录 README 注一句归属。ci.sh 实跑复验：**出厂集 8/8 通过**。

## 5. 脚本清单（modules.md 末尾）↔ tools/ 实际：**1 项出入（两张脚本卡上未登记）**

| tools/ 实际（非 test） | 脚本清单有行？ |
|---|---|
| schema_check.py / graph_index.py / check_citations.py / proposal_check.py / semantic_service_core.py / mcp_manifest_gen.py / semantic_mcp_server.py | 有（含演进账与断言面注记，详实） |
| skill_deps_check.py / fixture_run.py / archive_check.py / ci.sh | 有（三闸+ci.sh 合并行） |
| install_skills.py（含 install-registry.json、hooks/pre-commit） | 有（票 12/15 行） |
| **guard_corpus_check.py** | **无行——卡上未登记** |
| **mcp_smoke_client.py** | **无行——卡上未登记** |

- `guard_corpus_check.py`：票 20（Status: done）建造的守卫例集回归检具，有单测 test_guard_corpus_check.py、真源 fixtures/semantic-service/guard-corpus/regex.txt，且其断言已替换进 semantic-service 出厂集——**实际已在四闸生效链上**，但 L3 脚本清单漏账（AGENTS.md 目录地图反而提了它，说明是 modules.md 漏更而非黑户）。
- `mcp_smoke_client.py`：票 24（Status: done）的实弹 smoke 客户端，有单测，票面/lessons/24 齐全——同样漏登 L3 清单。
- 反向（清单有、磁盘无）：无。test_*.py 13 件属"含单测"约定覆盖；__pycache__ 非产物。

**判定**：modules.md 自称"卡是唯一真源"，而 L3 清单落后于票 20/24 两个 commit 的实际产出——属文档级漏账（不影响闸，但违反自家真源纪律），建议补两行。

## 6. model-registry.json ↔ ontology/ 实际模型：一致

- 注册表声明 8 模型：M1/M2/M3/M5/M6/M7/MU/GLS（version 1.2.0，票 03 立七模型+票 10 增 GLS，与账目一致）。
- `ontology/bohai/` 实际 7 个模型文件：m1-object / m2-behavior / m3-rule / m5-actor / m6-flow / m7-report / glossary。
- 逐项核对：**文件名与注册表 yamlFile 一一相符**；**各文件 `model_type` 字段（OBJECT/BEHAVIOR/RULE/ACTOR/FLOW/REPORT/GLOSSARY）与注册表 modelType 逐一相符**。
- 唯一缺口 MU（UI 模型）未建文件——**已按规约豁免登记**：bohai/manifest.json `omittedModels` 记录 MU 缺席理由（R5 无界面素材证据）+ 裁决记录指针，即 schema_check AC6 反向缺文件检查的合法豁免路径；profile=v9-full 因 M6 仅该组合覆盖而保留，逻辑自洽。
- 配套白名单 `model-deps.json` 的 idPrefixes（AGG-/BH-/RULE-/ACTOR-/FLOW-/QR-/RPT-/SCR-/GLS- 等 13 前缀）覆盖注册表 8 模型全部 ID 面；闸侧一致性核对由 schema_check 承担，本次 ci.sh 实跑语义闸全绿旁证无漂移。

---

## 总评

**账实相符度：5 项完全一致，1 项局部出入。** 五张已建 skill 卡在"卡名=目录名、双位置同内容、注册表登记、触发面=description、reads/writes/依赖=SKILL.md 契约、出厂集非空且真测核心行为"六个面上全部对上；二期占位卡没有偷跑实体；本体注册表与渤海域模型文件逐字段相符且 MU 缺席走的是合法豁免登记。本次实跑复验：`install_skills --check` 5/5 一致无孤儿，`ci.sh` 四闸全绿（出厂集 8/8、边界闸无违规、归档闸 384 文件全对上）。

**Top 3 出入（均为轻量、可一次性清账）：**

1. **L3 脚本清单漏登两张脚本**（唯一实质出入）：`tools/guard_corpus_check.py`（票 20 已建、有单测、已接入 semantic-service 出厂集断言链）与 `tools/mcp_smoke_client.py`（票 24 已建、有单测）均不在 modules.md 脚本清单——"卡是唯一真源"纪律下的文档漏账，建议补两行（连同 test_* 归属注记）。
2. **fixtures/mcp-publisher 目录先于 skill 存在**：mcp-publisher 卡是二期占位（无 SKILL.md），但同名出厂集目录已在测票 23 的 L3 脚本 `mcp_manifest_gen.py`——不是幽灵，但命名易让人误判"该 skill 已建成"，建议在卡或 fixtures/mcp-publisher 加一句归属注记。
3. **onto-modeler 卡面 reads 保留 `ontology/patterns/**`（二期）而 SKILL.md 未提**：卡已自我标注二期、属预留读面，非漂移；待二期立项时 SKILL.md 需同步补读面，届时记得对账。
