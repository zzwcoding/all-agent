# 51 · 票 50：DDD 设计件规范 + ddd-modeler 开卡（第四期 DDD 线起步）

- 日期：2026-09-20
- 依据：tickets/50-DDD设计件规范与开卡.md（六项 What to build 与 AC 表 L0 定稿照办）+ docs/ddd-modeler-建造交接包.md §2/§3（共识与三件套）+ references/ddd-as-code-digest.md §1/§4（字段骨架来源）+ docs/第四期DDD线拆票方案.md 票 50 节
- 触发：第四期 DDD 线批次一票 50 施工（L2 自主档串行一票）
- 卷号说明：票号 50 但施工日志顺延落 lessons/51（lessons/50 已被票 49 占用——延续票 48→lessons/49、票 49→lessons/50 同款顺延惯例）

## 做了什么

1. **设计件格式真源（AC1）**：新建 `design/ddd/README.md`——四类设计件（聚合卡 aggregate-card / 领域事件表 domain-events / 聚合↔表映射 table-mapping / 仓储边界声明 repository-boundaries）逐类给字段 schema 表 + 语义说明 + 最小合法样例（样例内嵌 README 代码块，`design/ddd/` 下不放 .yaml 样例文件）。通用约定七条：status 恰一处行首（草案/已审，归档闸机判面）、domain 必填、`- 词条ID` 引用即类型、跨聚合仅 ID 引用不内嵌属性、kind 判别字段、草案头声明。聚合卡的**不变量三元组（trigger 触发操作→expect_fail 期望失败→method 指向聚合方法）**、corrective_policies、ways_to_access 必含（字段骨架抄 references/ddd-as-code-digest.md §1/§4，README 正文不点名外部框架）。
2. **开卡（AC2）**：specs/modules.md 增 `## skill: ddd-modeler` 卡，九槽齐（职责/层/目录/触发面/reads/writes/依赖/Seam 与出厂集/边界）；触发面=选配路由，判据表照交接包 §5 写入卡面（状态机→路由/规则多且长寿→路由/多团队边界痛→路由/读多写少薄规则→传统分层/一次性脚本→不上，核心判据="改一条规则要动几个地方"）。reads=`ontology/<域>/**`+`ontology/schema/**`+格式真源；writes=`design/ddd/<域>/**` 草案走 MR。skill 正文不写（票 52）。
3. **ddd_check 提前声明实跑裁决**：modules.md 脚本清单先登记 `tools/ddd_check.py`（状态列注明票 51 建、planned-script），卡依赖行即可声明双 script（schema_check + ddd_check）。实跑 `python3 tools/skill_deps_check.py` 证实：`[警告][planned-script]` + `边界闸: 无违规` + exit 0——票 03 先例照实成立，交接包预案一（提前声明）成立，无需回退到预案二（先只写 schema_check）。
4. **边界规则增两行（AC3）**：①非 ddd-modeler 工序写 `design/ddd/**`（设计件只由 ddd-modeler 工序写入，草案制）；②ddd-modeler 读生成器 skill 私件。实跑边界闸绿。
5. **登记（AC4）**：repo-layout.json 增 **design 顶层条目**（patterns `ddd/*.md`+`ddd/*.yaml`，purpose 写明被建域产物/草案走 MR/非派生物不走 --check）；archive-registry.json 增 design-card 类（requiredFields=["status"]，合法值 草案/已审，flippedBy=Owner MR 人审；pathPatterns 收窄到 yaml）。归档闸实跑全绿（749 文件）。
6. **功能规格**：specs/ddd-modeler.md 照 specs/onto-modeler.md 形态（触及行+出厂集断言表+行为约定）+ 真源指针行照票 26 五 spec 先例（断言真源=票 51/52 票面 AC 表+出厂集，本表骨架占位）；AC1–7 编号占位（AC1–6 对应票 51 五查负变体+绿灯样本，AC7 对应票 52 skill 出厂集）。
7. **架构图（AC5）**：diagrams/all-agent.html bounded 插入 DDD 节点（流水线位置 本体仓→ddd-modeler→BE1/F9，选配路由标注）+ 两棱（CORE→DDD「本体模型就位，无词条不建模」/ DDD→BE1「聚合卡等设计件，草案走MR」）+ 节点明细表一行；只增内容不动版式/配色/结构（照票 26 三图刷新手法），html.parser 机械校验标签闭合 OK。**节点段摘录随票回报 L0 转 Owner 过目（票面 AC5 红线：过目留痕后方可关票；本票不翻 Status 不 commit）**。

## 取舍

- **lessons 卷号顺延 vs 票面 Touches 写 lessons/50**：lessons/50 已被票 49 施工日志占用（「日志只增不改」），照票 48/49 两次先例顺延 lessons/51 并在卷号说明留痕——已报偏差，不抢占编号。
- **布局登记形态：design 顶层条目而非 design/ddd 条目**：票面写「repo-layout.json 增 design/ddd/ 条目」，但归档闸 check_layout 按顶层目录匹配（票 28 已实证「子目录独立条目是死配置」）——落地为顶层 design 条目+patterns 加 ddd/ 前缀，语义与票面一致（design/ddd/ 下 md+yaml），机检面成立。
- **design-card pathPatterns 收窄到 yaml**：防踩坑 7 预案二选一，收窄比「收 md 再豁免 README」简单且不造豁免账——README.md 是格式文档不是设计件，受布局表位置管、不受产物类字段检查。design/ddd/ 下无 .yaml 样例文件（真设计件票 51 起），AC4 的「样例文件过归档闸」以「登记在场+归档闸全绿+样例内嵌 README」实证。
- **卡上 Seam 槽写 fixtures/ddd-modeler/ 占位**：本票不建出厂集（票 51 建），fixture_run 对不存在的出厂集目录不判死（fixtures/ 根已有 14 套，--require-fixtures 仍绿）——卡面如实注「票 51 建并落断言，本票占位 pending」。
- **AC4「design/ddd/ 条目」按闸的实语义落地为 design 条目**：不照票面字面造死配置（造了=登记在场但闸永远看不见，比不登记更糟）；偏差已在 lesson 与布局表 description 双留痕。

## 坑

- **归档闸 status 机判按文件内首个 `status:` 行取值、无行首锚**：`xxx_status:` 这类含 status 子串的键会被误命中——README 通用约定 2 已写死「恰一处行首 status 行 + 不得用含 status 子串的键名」，票 51 的 ddd_naming 设计时留意同款陷阱。
- **fnmatch 的 `*` 跨路径分隔符**：patterns `ddd/*.yaml` 天然覆盖 `ddd/<域>/任意深度.yaml`，不必写 `**`；写了 `ddd/**/*.yaml` 冗余但无害（归档闸与登记表 pathPatterns 同语义）。
- **skill_deps_check 的 planned-script 豁免只认「脚本清单」节**：parse_planned_scripts 只扫 modules.md `## 脚本清单` 节内的 tools/ token——卡上声明未落盘脚本必须先在该节登记，否则是 missing-script 红不是警告。
- **票面 AC4 措辞「design/ddd/ 下样例文件过归档闸」与防踩坑 7「不放 .yaml 样例」表面冲突**：以防踩坑为准（样例 yaml 会触发 design-card 必备字段检查，那是票 51 真设计件的事）——AC4 实证改为登记在场+归档闸全绿，lesson 留痕免复查疑。

## Owner 过目记录（AC5，2026-09-20）

架构图变更（DDD 节点+两棱+明细表行）经 L0 转 Owner 过目：**批准，按此关票**。节点语义（本体仓→ddd-modeler 选配→F9）与明细表描述落定。
