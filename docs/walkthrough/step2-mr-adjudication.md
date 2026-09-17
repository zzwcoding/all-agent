# 模拟 MR 裁决记录 · 草案 → ontology/bohai/ 进仓（票 09 端到端走查 · 工序②）

> 本仓一期为单人使用（PRD 决策 1：MR 人审由仓主在 Git 完成），本票按票面「模拟 MR 流程」执行：**Owner 裁决以 R5 设定书原文为裁决依据**——设定书是业务 Owner 意图的书面记录，凡设定书有明文的按明文落仓，设定书没有的一律不建并标「待 Owner 确认」。真实人审由 L0 在 commit 前完成（本票不 commit）。
> 进仓闸：`python3 tools/schema_check.py ontology/bohai` 全绿（模拟 MR 的闸；CI 不自动跑，L0 验收复跑）。

## 一、profile 裁决：维持 v9-full，但 MU 不建文件

- 走查草案（工序①）profile=v9-core：DDL 证据只够 M1。
- 进仓裁决：R5 有 M2–M7 的业务证据——§2 采集/补录行为（M2）、§4 规则库+§3 指标口径（M3）、§1 角色卡（M5）、§7 两剧本+§1/§4 问题单闭环（M6）、§3 指标查询出口（M7）。
- **M6 只有 v9-full 组合覆盖**（注册表 profiles：v9-full=M1/M2/M3/M5/M6/M7/MU；v9-core 无 M6；headless 无 M6）——降配 headless 会丢 §7 剧本证据，故 profile 维持 v9-full（不改 manifest 的 profile 字段）。
- **MU 不建文件**：R5 全文无界面/屏幕/菜单/控件证据（§1 的「消费票」是 teach-petro-agent 的票号，非 UI 证据）——按「设定书没有的一律不建」不产 mu-ui-model.yaml。v9-full 下启用模型不出文件不违规（schema_check AC6 只禁「未启用却出文件」的反向）。
- 结论：**进仓 manifest profile=v9-full、模型文件 6 个（缺 MU）**；MU 待 UI 素材/Owner 确认后补。

## 二、D1–D15 脏特征裁决（逐条：草案疑点 → 进仓处置）

| # | 疑点 | 进仓处置（落点） | 仍待 Owner |
|---|---|---|---|
| D1 | 吨方混写 | oilOutput 保持 Decimal，label 注「吨」；单位一致性校验落 M3 `RULE-BOHAI-001`（§4 规则 3，折算密度域）；区块密度换算系数随描述注记（§2.2） | 存量误录行的数据修复（语义层不吞） |
| D2 | A/B 班重复行 | reportShift 保留 Enum [A,B,C]（班次行按业务事实保留）；键冲突不改（主键声明照字典） | 去重规则与键约束是否强化 |
| D3 | 化验/折算打架 | 两属性并存（waterCut / waterCutLab）；一致性检测落 `RULE-BOHAI-002`（偏差≤5pp，§4 规则 4） | 权威源归属 |
| D4 | 配产双值行 | planOutput 保留；完成率口径（`RULE-BOHAI-009`）描述注记争议 | 双值行的版本语义 |
| D5 | openDays 矛盾行 | 值域 [0,24] 下沉 M1 refRules（§4 规则 5，四层下沉第 2 层——只依赖当前属性值） | 矛盾行清洗规则 |
| D6 | 井号旧写法 | 归一化落 `RULE-BOHAI-005`（TRANSFORMATION，§4 规则 7）；同名键列关联经 §5 关系草案落 AggregateRootRef（见三） | 归一表全集 |
| D7 | 状态滞后 | currentStatus 保留 Enum 四值 + 井 lifecycle 登记同值集（§5「状态机」）；不增设时间戳属性（字典无此列） | 状态时效责任方 |
| D8 | field_name 冗余 | 保留属性，不提升对象（一表一对象维持；提升=业务判断无证据） | 是否提升「油田」为独立对象 |
| D9 | layerSplit 口径不一 | 保持 String 不结构化；配注合格率术语（§6）无配注目标承载字段，未建（见对账表） | 分层格式规范 |
| D10 | 跨月切割 | 检泵周期（`RULE-BOHAI-016`）与剔检口径（`RULE-BOHAI-019`）描述注记争议 | 归属期规则 |
| D11 | 批次补录 | 补录行为 `BH-BOHAI-RecordOverhaul` 前置条件要求批次号带补录标记；状态迁移校验 `RULE-BOHAI-007`（§4 规则 9）挂该行为 | 补录窗口阈值（T-3 之外） |
| D12 | 有效期 30% 缺失 | effectiveFrom/To 不设 required；措施有效期（`RULE-BOHAI-015`）描述注记缺失处理 | 缺失行是否计入统计分母 |
| D13 | 年增油算法不一 | `RULE-BOHAI-018`（递减增油）描述保留事故 7 注记 | 统一口径前的使用边界 |
| D14 | 新旧停机码 | `RULE-BOHAI-006`（TRANSFORMATION，§4 规则 8）narrative 承载映射方向；属性保持 String 不建枚举 | 映射表全集（字典只示例 R3↔BELT 一对） |
| D15 | 净重口径 | `QR-BOHAI-003`/AGG-BOHAI-008 描述保留「与井口口径天然不等」注记 | 商品量 vs 井口口径的仲裁（§8 事故 13 同源） |

## 三、进仓新增结构清单（全部注源 R5·§x，DDL 草案之外的增量）

| 增量 | 注源 | 说明 |
|---|---|---|
| 5 个 wellRef（AGG-002/003/004/005/006 → AGG-001，AggregateRootRef） | R5·§5 关系（「措施—作用于→井；化验样—取样自→井」）+ §5 Join 白名单（oil_production_daily ⋈ well_info ✓）+ 各表 well_id 键列（A.x） | DDL 无外键，关联语义按 §5 关系草案落引用；「引用 vs 依赖」的取舍待 Owner 确认 |
| AGG-BOHAI-009 受效关系（injectorWellRef/producerWellRef/splitCoefficient/responseStartDate + Σ=1 invariant） | R5·§5「受效关系（注水井→受效油井，多对多，属性=劈分系数 Σ=1、响应起始日）」 | **无源表**（8 表之外的业务实体）：物理落表待 Owner 确认；不建它则 §5「oil ⋈ water_injection 直连 ✗ 须经受效关系实体」无承载 |
| ASSOC-BOHAI-001~007 | R5·§5 关系草案 + A.x 键列 | 与 wellRef 同源；方向/基数按 §5（受效关系多对多经关系实体展开为两条一对多） |
| M2 行为 8 个（4 COMMAND + 4 QUERY） | R5·§2.1（采集/15 分钟级调度）、A.2/A.4/A.6（录入/补录）、§3 指标查询出口（M7 须配 QUERY 行为） | 行为划分按素材证据最小集；行为颗粒度待 Owner 确认 |
| M3 规则 19 个 | §4 规则 2/3/4/7/8/9/10/12（8 条质量类）+ §3 指标 1/2/3/4/5/6/7/9/10/13/14（11 条指标类） | 未建：§4 规则 1（键结构已承载）/5（refRules 承载）/6（well_completion 不在 8 表）/11（实时域）/13–20（判据在提取件二，不在素材面）；§3 指标 8/12/15 公式或判据不全 |
| M5 角色 8 + 参与者 3 + 权限 8 | R5·§1 角色卡八行 + §2.1 系统调度（SYSTEM 参与者） | Owner 角色权限面留空（裁决权在治理面/MR，不在行为权限）；小李兼岗=一 actor 两 role |
| M6 流程 3 个 | R5·§7 剧本 1/2 + §1/§4 问题单闭环（分发→认领→整改→复核→关闭） | 剧本未指名执行角色，roleRef 按口径 Owner 归位——待 Owner 确认 |
| M7 查询 4 个 | §3 指标 1/5/11 的查询出口 + §3 指标口径抽查面（Golden Q 用） | M7 与 M2 QUERY 行为严格一对一（schema §2） |

## 四、进仓闸记录

- 命令：`python3 tools/schema_check.py ontology/bohai` → 全绿（L1: 0 | L2: 0 | L4: 0，输出摘录见施工日志 lessons/09）。
- 裁决遗留（待 Owner / 待二期）：上表「仍待 Owner」列 15 项 + MU 素材 + AGG-BOHAI-009 物理落表 + 提取件二 8 条规则 + 指标 8/12/15 公式。
