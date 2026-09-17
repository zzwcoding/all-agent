# Golden Q 抽查 · semantic-service 对 ontology/bohai 真域（票 09 端到端走查 · 工序③）

> 工序依据：`skills/semantic-service/SKILL.md` 四步检索瀑布 + references 三件（waterfall/refusal-guide/id-citation-format）。
> 问答本体：`ontology/bohai/`（票 09 工序②进仓版；图统计：**节点=69 边=109**，`tools/graph_index.py` 全量建图）。
> 检索面划界：检索面 = camp=business-core。本域六模型（M1/M2/M3/M5/M6/M7）全在面内；**MU 未建文件（R5 无界面素材），本域面外集合为空**——「检索面外拒答」在真域不可按 R1 原样实测，Q5 以「锚定失败 + 注册表阵营推演」替代并如实记为走查缺口。
> 六问覆盖票面要求五类：指标口径解析（Q1 日产量 / Q2 月度结算 / Q6 有效产量）、对象问答（Q3）、显式 @ID 锚定（Q3）、仓内没有的拒答（Q4）、检索面外拒答（Q5，替代形态）。
> 每问命令均可复现；命令输出以「取证」块摘录。

---

## Q1 · 日产量的口径是什么？（指标口径解析）

- 走到的瀑布级：二级 ID/名称解析（无 @ID；候选词「日产量/日产」通读六模型 id/name/alias，唯一命中）→ 三级闭包装配（口径四件套）
- 取证：
  - `python3 tools/graph_index.py ontology/bohai --query AGG-BOHAI-002 --closure 2` → 1 个下游节点：AGG-BOHAI-001（hops=1 via=targetAggregate）
  - `python3 tools/graph_index.py ontology/bohai --query AGG-BOHAI-002 --impact` → 27 个受影响节点（四件套经此反向收集）

### 答案

「日产量」在本域的承载落点是 **`AGG-BOHAI-002`（日产计量）**（二级名称解析唯一命中；正向闭包确认其经 wellRef 挂到 `AGG-BOHAI-001`（井））。口径四件套装配如下：

1. **承载字段**：`AGG-BOHAI-002` 的属性 oilOutput（日产油量（吨），Decimal）——源列 oil_output（R5·附录 A.2，★核心事实源）。**口径含糊处如实说明**：该列存在「吨方混写」脏特征（个别行误录为方，疑点 D1），存量数据的单位语义未经 Owner 裁决，本口径按「吨」理解。
2. **校验规则**：执行行为引用的规则为 `RULE-BOHAI-005`（井号归一化，TRANSFORMATION，录入时归一 N2/N-2→N-02）；质检侧挂 `BH-BOHAI-RunDailyQualityCheck`，经 appliedRules 引用 `RULE-BOHAI-002`（计量/化验含水偏差 ≤5pp）、`RULE-BOHAI-003`（日产油非空率 ≥99.5%）、`RULE-BOHAI-004`（连续 30 日恒值检测）、`RULE-BOHAI-008`（区块物质平衡偏差 ≤3%）；单位一致性的检出面是 `RULE-BOHAI-001`（化验折算密度域 [0.82,0.98] t/m³）。行级值域直接下沉在属性上：waterCut refRules [0,100]、openDays refRules [0,24]（R5·§4 规则 5）。
3. **执行行为**：`BH-BOHAI-RecordDailyOutput`（录入日产计量，COMMAND/USER_ACTION，班次手抄录入——R5·§2.1 手工录入环节是脏数据主要来源）与 `BH-BOHAI-RunDailyQualityCheck`（执行日产质检，COMMAND/SYSTEM，15 分钟级 ETL 闭环调度触发）。
4. **查询出口**：`QR-BOHAI-001`（单井日产量明细查询）——结果列 oilOutput（日产油量（吨））直接取 d.oilOutput；注意明细行含 reportShift（报表班次），同井同日 A/B 班重复行（疑点 D2）**未去重**，去重口径待 Owner。

反向闭包（--impact 27 节点）同时提示：`AGG-BOHAI-002` 是 `RULE-BOHAI-009`（产量完成率）、`RULE-BOHAI-019`（有效产量·剔检口径）、`RULE-BOHAI-010`（综合含水率）等口径的承载事实源——改日产计量口径属于高影响变更，须走提案流程（本服务只读，不代改）。

**一句话口径**：日产量 = `AGG-BOHAI-002.oilOutput`（日产油量（吨）），经 `BH-BOHAI-RecordDailyOutput` 班次录入、`BH-BOHAI-RunDailyQualityCheck` 质检把关，经 `QR-BOHAI-001` 查询出口消费；单位混写与班次重复行两处疑点使该口径在 Owner 裁决前保留保留意见。

### 本回答引用的元素 ID

- AGG-BOHAI-002（日产计量——口径承载对象，二级解析命中）
- AGG-BOHAI-001（井——正向闭包下游，wellRef 挂靠）
- RULE-BOHAI-005（井号归一化——录入行为 appliedRules 引用）
- RULE-BOHAI-002 / RULE-BOHAI-003 / RULE-BOHAI-004 / RULE-BOHAI-008（质检行为 appliedRules 引用的四条规则）
- RULE-BOHAI-001（化验折算密度值域——单位一致性检出面）
- BH-BOHAI-RecordDailyOutput（录入日产计量——执行行为）
- BH-BOHAI-RunDailyQualityCheck（执行日产质检——执行行为）
- QR-BOHAI-001（单井日产量明细查询——查询出口）
- RULE-BOHAI-009 / RULE-BOHAI-019 / RULE-BOHAI-010（反向闭包提示的下游口径规则）

---

## Q2 · 月度结算的口径是什么？（指标口径解析）

- 走到的瀑布级：二级 ID/名称解析（候选词「月度结算/商品量/结算」命中 AGG-BOHAI-008）→ 三级闭包装配
- 取证：
  - `python3 tools/graph_index.py ontology/bohai --query AGG-BOHAI-008 --closure 1` → 0 个下游节点（该对象无正向引用）
  - `python3 tools/graph_index.py ontology/bohai --query AGG-BOHAI-008 --impact` → 4 个受影响节点：BH-BOHAI-QueryMonthlySettlement（hops=1 via=ownerEntity）、QR-BOHAI-003（hops=1 via=objectRef）、PERM-BOHAI-QueryMonthlySettlement（hops=2 via=targetRef）、ROLE-BOHAI-005（hops=3 via=permissions）

### 答案

「月度结算」承载于 **`AGG-BOHAI-008`（区块月度结算）**，键=区块+结算月（复合主键 blockName+settleDate，settleDate 粒度=月）：

1. **承载字段**：netWeight（商品量净重（吨））——口径即字段定义：**脱水稳定后净重，扣自用油与输差**（R5·§3 指标 11「商品量」，Owner=销售计量站）。
2. **校验规则**：无计算规则——商品量在仓内是**直接取数字段**而非公式算出，故无 M3 口径规则（这不是缺件，是该指标在 8 表素材面的形态）。
3. **执行行为**：`BH-BOHAI-QueryMonthlySettlement`（查询区块月度商品量结算，QUERY）。
4. **查询出口**：`QR-BOHAI-003`（区块月度商品量结算查询），结果列 netWeight（商品量净重（吨））。

**口径冲突注记（重要）**：结算口径与井口口径**天然不等**（扣自用油与输差；疑点 D15，同源 R5·§8 事故 7/事故 13「一数四源」）。两口径在本域并列存在、不互替：井口侧是 `AGG-BOHAI-002`（日产计量），结算侧是本对象。哪个作为对外权威数，仓内**没有仲裁规则**——这是真实缺口，请走提案流程补口径仲裁定义（本服务只读）。

### 本回答引用的元素 ID

- AGG-BOHAI-008（区块月度结算——二级解析命中）
- BH-BOHAI-QueryMonthlySettlement（查询行为，--impact hops=1）
- QR-BOHAI-003（查询出口，--impact hops=1）
- PERM-BOHAI-QueryMonthlySettlement（查询权限，--impact hops=2）
- ROLE-BOHAI-005（业务 Owner 经营口径（销售计量站），--impact hops=3）
- AGG-BOHAI-002（日产计量——井口口径对照物，非所问主链，仅作口径区分）

---

## Q3 · @AGG-BOHAI-001 有哪些行为？（显式锚定 + 对象问答）

- 走到的瀑布级：一级显式锚定（@ID 直达，未走名称模糊检索）→ 三级闭包装配（--impact 反向收集「谁引用了我」）
- 取证：`python3 tools/graph_index.py ontology/bohai --query AGG-BOHAI-001 --impact` → 48 个受影响节点；检索面检查：AGG- 前缀 → M1 → camp=business-core，在面内

### 答案

问题带 @AGG-BOHAI-001，**显式锚定直接命中**：`AGG-BOHAI-001`（井，AGGREGATE_ROOT，源表 well_info，生命周期 [生产中, 停产, 检修, 待弃置]）。

**名下行为（ownerEntity 直挂，--impact hops=1 反向收集，可复现）**：

- `BH-BOHAI-QueryWellDailyOutput`（查询单井日产量，QUERY/USER_ACTION）——需权限 `PERM-BOHAI-QueryWellDailyOutput`；查询出口 `QR-BOHAI-001`（behaviorRef 回指该行为）。

**经子对象挂靠的行为（ownerEntity 指向井的子记录对象，--impact hops=2，单列防误答）**：

- `BH-BOHAI-RecordDailyOutput`（录入日产计量，ownerEntity=`AGG-BOHAI-002`，经 targetAggregate 挂井）
- `BH-BOHAI-RunDailyQualityCheck`（执行日产质检，ownerEntity=`AGG-BOHAI-002`）
- `BH-BOHAI-RecordOverhaul`（补录井检修台账，ownerEntity=`AGG-BOHAI-004`）
- `BH-BOHAI-RecordFluidTest`（录入流体化验结果，ownerEntity=`AGG-BOHAI-006`）

**关联结构（非行为，闭包轨迹供下钻）**：子记录对象 6 个（`AGG-BOHAI-002`/`AGG-BOHAI-003`/`AGG-BOHAI-004`/`AGG-BOHAI-005`/`AGG-BOHAI-006`/`AGG-BOHAI-009`，均经 targetAggregate 指向本对象）；聚合关联 7 条（`ASSOC-BOHAI-001`…`ASSOC-BOHAI-007`，经 sourceAggregate）；流程 3 条（`FLOW-BOHAI-001` 产量下滑归因、`FLOW-BOHAI-002` 注水井措施评估、`FLOW-BOHAI-003` 质量问题单闭环，经 businessObjectRefs）；查询出口 3 个（`QR-BOHAI-001`/`QR-BOHAI-002`/`QR-BOHAI-004`，经 objectRef）。

### 本回答引用的元素 ID

- AGG-BOHAI-001（井——显式锚定对象，一级直达）
- BH-BOHAI-QueryWellDailyOutput（锚定对象名下行为，ownerEntity 直挂）
- PERM-BOHAI-QueryWellDailyOutput（上述行为所需权限）
- QR-BOHAI-001（上述行为的查询出口）
- BH-BOHAI-RecordDailyOutput / BH-BOHAI-RunDailyQualityCheck / BH-BOHAI-RecordOverhaul / BH-BOHAI-RecordFluidTest（经子对象挂靠的行为，非井名下，单列防误答）
- AGG-BOHAI-002 / AGG-BOHAI-003 / AGG-BOHAI-004 / AGG-BOHAI-005 / AGG-BOHAI-006 / AGG-BOHAI-009（井的子记录对象）
- ASSOC-BOHAI-001 / ASSOC-BOHAI-002 / ASSOC-BOHAI-003 / ASSOC-BOHAI-004 / ASSOC-BOHAI-005 / ASSOC-BOHAI-006 / ASSOC-BOHAI-007（聚合关联）
- FLOW-BOHAI-001 / FLOW-BOHAI-002 / FLOW-BOHAI-003（触达本对象的流程）
- QR-BOHAI-002 / QR-BOHAI-004（触达本对象的其余查询出口）

---

## Q4 · 桶油增产成本的口径是什么？（仓内没有 → R2 拒答）

- 走到的瀑布级：二级 ID/名称解析（穷尽未命中）→ 四级可拒答（R2 仓内没有）
- 取证：`python3 tools/graph_index.py ontology/bohai --query RULE-BOHAI-020` → `未找到: RULE-BOHAI-020（图内共 69 节点；不做名称猜测）`（退出码 1）——按命名规律推想的 ID 经图索引复核明确不存在

### 答案

**拒答：仓内没有「桶油增产成本」这一概念。** 本服务不回答无锚定的口径问题，以下说明缺什么。

**检索轨迹（未找到，不猜）**：名称候选「桶油/成本/投入/增产成本」在六模型文件的 id、name、alias 中均无命中；按命名规律推想的 ID（RULE-BOHAI-020）经图索引复核报「未找到」——没有就是没有，不编造。

**缺什么（缺件分层说明）**：

- **查询层**：缺成本类统计查询（M7 现有四出口均为产量/含水/结算，无成本列）。
- **对象/字段层**：缺「措施总投入」承载字段——R5·§3 指标 15 的数据源是「2.5+ERP」，ERP 侧投入数据不在本域 8 表内，台账对象 `AGG-BOHAI-005`（井措施记录）只有产出面字段（incrOilAnnual），无投入面字段。
- **行为/规则层**：缺桶油成本计算规则（分子无源，规则无从建）。

**下一步**：业务口径缺口，请走提案流程补「措施投入」字段与「桶油增产成本」规则/查询定义（进仓走 MR + 语义 CI）。本服务只读，不代填口径、不产文件。

**近邻指路（真实存在、非所问）**：`RULE-BOHAI-018`（递减增油）——桶油成本的**分母**（折算增油量）在仓内有口径承载（含 6.29 桶/m³ 换算注记），但那只覆盖分母；分子（投入）仓内没有。

### 本回答引用的元素 ID

- RULE-BOHAI-020（用户外推形态的复核对象：图索引明确「未找到」，非仓内元素）
- RULE-BOHAI-018（近邻指路，非所问：仅覆盖分母口径）
- AGG-BOHAI-005（近邻指路，非所问：措施台账，缺投入字段）

---

## Q5 · @SCR-BOHAI-01 的页面长什么样？有哪些按钮？（检索面外·替代形态）

- 走到的瀑布级：一级显式锚定（锚定失败）→ 检索面阵营推演 → 四级可拒答（R3 话术并入 R2；R1 面外场景在真域不可原样实测，见下方「走查缺口」）
- 取证：`python3 tools/graph_index.py ontology/bohai --query SCR-BOHAI-01` → `未找到: SCR-BOHAI-01（图内共 69 节点；不做名称猜测）`（退出码 1）

### 答案

问题带 @SCR-BOHAI-01。**锚定失败：该 ID 在本域不存在**（图索引明确「未找到」，不做近似拼写猜测）——本域没有建任何界面模型：R5 设定书全文无界面/屏幕/菜单证据，按「设定书没有的一律不建」，`mu-ui-model.yaml` 未进仓（裁决见 docs/walkthrough/step2-mr-adjudication.md）。

**阵营归属说明（推演，非检索产出）**：SCR- 前缀按 `ontology/schema/model-deps.json` → 界面模型（MU），按 `model-registry.json` camp=build-contract——**不在本服务检索面**。即使该 ID 存在，本服务也只说明阵营归属并指路建造链路，不返回布局/控件/动作任何细节。

**走查缺口（如实记录）**：因本域 MU 集合为空，「锚定可解析但 camp 裁剪不过」的 R1 原样场景不可达；本问降级为「锚定失败 + 注册表阵营推演」。R1 话术的完整实测样本见出厂集 `fixtures/semantic-service/expected-answers/ac4-refusal-out-of-face.md`（对 fixtures/graph_index/ontology-base 最小域）。

**你要的如果在业务面**（业务面等价概念，不是页面映射关系）：日产计量的录入行为是 `BH-BOHAI-RecordDailyOutput`（需权限 `PERM-BOHAI-RecordDailyOutput`，角色 `ROLE-BOHAI-001` 采集管理员）；录入界面的建造契约属 build 侧消费方。若认为缺业务概念（如新行为/新口径），走提案流程。

### 本回答引用的元素 ID

- SCR-BOHAI-01（用户锚定 ID，仅复述并说明「未找到」与阵营推演，未展开任何细节）
- BH-BOHAI-RecordDailyOutput（业务面等价概念：录入行为）
- PERM-BOHAI-RecordDailyOutput（上述行为所需权限）
- ROLE-BOHAI-001（采集管理员——权限角色）

---

## Q6 · 有效产量的口径是什么？（多义/修饰词消歧）

- 走到的瀑布级：二级 ID/名称解析（命中唯一 ID 但语义两支）→ 三级闭包装配 → 按多义纪律列候选请用户锚定，不擅自合并
- 取证：`python3 tools/graph_index.py ontology/bohai --query RULE-BOHAI-019 --closure 1` → 1 个下游节点：BH-BOHAI-QueryBlockMonthlyCompletion（hops=1 via=reusedBy）

### 答案

「有效产量」二级解析命中 **`RULE-BOHAI-019`（有效产量（剔检口径），CALCULATION）**——这是 R5·§3 指标 2 的口径落点。该指标原文就是**一词两译**（R5·§6 术语表：「有效产量，一词两译，需修饰词消歧（开井日历/剔检）」），仓内两支口径并列、未合并：

1. **检修剔除支（已译，别名「剔检产量」）**：把当前状态为「检修」的井从日产量统计合计中剔除后求和（expression：`SUM(dailyProduction.oilOutput WHERE well.currentStatus <> '检修')`）——即票 09 影响分析变更「产量口径剔除检修井」的口径落点。跨月检修（如检泵 8-28→9-06）的当月归属是未决争议（疑点 D10），待 Owner。
2. **开井日历折算支（未译）**：R5 原文给出支名但公式细节未给全，仓内未建该支表达式——narrative 已保留占位并标待 Owner，不编造公式。

**消费面**（闭包轨迹）：`RULE-BOHAI-019` →(reusedBy)→ `BH-BOHAI-QueryBlockMonthlyCompletion`（查询区块月度产量完成率）→(behaviorRef)→ `QR-BOHAI-002`（区块月度产量完成率统计，结果列 effectiveOutputSum「有效产量·剔检（吨）」）。

**请你锚定修饰词**：你要问的是「剔检产量」还是「开井日历折算」？前者仓内可答（本回答即）；后者公式待 Owner 补齐前，仓内只有占位注记。

### 本回答引用的元素 ID

- RULE-BOHAI-019（有效产量（剔检口径）——二级解析命中，两支口径并列）
- BH-BOHAI-QueryBlockMonthlyCompletion（消费该口径的查询行为，--closure hops=1）
- QR-BOHAI-002（查询出口，结果列 effectiveOutputSum）
- AGG-BOHAI-001（井——剔检判据字段 currentStatus 的宿主，经 wellStatus 入参引用）

---

## 抽查小结

| # | 问题 | 覆盖类别 | 走到级 | 命中/拒答 | 引用 ID 数 |
|---|---|---|---|---|---|
| Q1 | 日产量的口径是什么 | 指标口径解析 | 二级→三级 | 命中（四件套齐） | 13 |
| Q2 | 月度结算的口径是什么 | 指标口径解析（月度结算） | 二级→三级 | 命中（四件套：无规则件=如实说明） | 6 |
| Q3 | @AGG-BOHAI-001 有哪些行为 | 显式锚定+对象问答 | 一级→三级 | 命中（48 节点反向集） | 21 |
| Q4 | 桶油增产成本的口径是什么 | 仓内没有的拒答 | 二级→四级 R2 | 拒答（缺件三层+近邻 2） | 3 |
| Q5 | @SCR-BOHAI-01 页面长什么样 | 检索面外拒答（替代形态） | 一级（锚定失败）→四级 R3+阵营推演 | 拒答（真域无 MU，缺口如实记） | 4 |
| Q6 | 有效产量的口径是什么 | 多义消歧 | 二级→三级 | 命中（两支并列，请用户锚定） | 4 |

未编造 ID 自查：以上全部 ID 经 `grep` 于 ontology/bohai/ 六文件真实存在（验收自查项，见施工日志 lessons/09）。
