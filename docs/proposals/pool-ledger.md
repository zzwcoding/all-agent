# 提案池对账表（pool-ledger · 票 19）

> 对账基准：票 19 素材清单（三真源合并去重 33 条 A1–A33 + 清单外核验 8 项 B1–B8，草表见 `lessons/19-裁决队列实弹落池.md` §一）。
> 本表三列起步：素材条目 → PROP ID（或"不立提案+理由"）→ 状态/证据/备注。素材条目全覆盖，零遗漏零凭空。
> accepted 条目 commit 号均经 git log 核实（票 10=0474bc8 / 票 16=bad916c / 票 17=29f890b）。
> 本文件不受 proposal_check 机检（工具只解析 PROP-*.md——设计如此，README 同）。

## 一、素材条目 → 提案映射（A1–A33）

| 草表号 | 素材条目（来源） | PROP ID | 状态 | 证据与备注 |
|---|---|---|---|---|
| A1 | D1 吨方混写——存量误录行修复（step2§二） | PROP-BOHAI-006 | **accepted** | 裁决 判据两级+处置A（确诊=油>液/疑似=密度越界，出清单交业务修复）；RULE-BOHAI-020 落地；commit `50da7f3`（提案闸盲区实弹发现→票 56 清偿） |
| A2 | D2 A/B 班重复行——去重/键约束（step2§二） | PROP-BOHAI-007 | **rejected** | 裁 A 班次行=业务事实（提案预设路径）：RULE-021 不建；AGG-002 主键声明修正为班次粒度（commit `9b606f5`） |
| A3 | D3 权威源归属（step2§二） | PROP-BOHAI-008 | **accepted** | 裁决 C 并存分场景（日度=计量折算/月度正式指标=化验/>5pp 化验校正），m1 三处注记落定；commit `203d7fa`；RULE-BOHAI-010 取数方向→PROP-031 联动未闭 |
| A4 | D4 配产双值行版本语义（step2§二） | PROP-BOHAI-009 | **accepted** | 裁 A 版本事实：RULE-022 检出+取版（当日最后班次非空值）；RULE-009 分母净化；commit `a001af7` |
| A5 | D5 openDays 矛盾行清洗（step2§二） | PROP-BOHAI-010 | **accepted** | 裁 标注出清单交业务核实（不归零——归属未定，联动 D7）；RULE-023 落地；commit `4f793e1` |
| A6 | D6 归一表全集+归一位置（step2§二） | PROP-BOHAI-011 | **accepted** | (a) 全集到齐关箱：四类变体+幂等算法落 RULE-005（commit `b059e8d`）；(b) 位置裁决见 `4b0b5e6` |
| A7 | D7 状态时效责任方（step2§二） | PROP-BOHAI-012 | **accepted** | 裁 责任方=作业区录入+治理稽核检出（SLA 时限值入问题清单）；commit `9e2286d`；剔检口径时效获解释 |
| A8 | D8 是否提升「油田」对象（step2§二） | PROP-BOHAI-013 | **accepted** | 裁不提升（无业务驱动，fieldName 保持行内冗余）；随 A28 族一并关（commit `9d0b0c4`） |
| A9 | D9 分层格式规范（step2§二） | PROP-BOHAI-014 | open（部分裁决） | (a) 方向已裁：保持 String 不发明格式（commit `bfbeca0`）；格式规范+配注目标承载缺素材待 Owner，入问题清单 |
| A10 | D10 跨月归属期规则（step2§二） | PROP-BOHAI-015 | **accepted** | 裁 按日历天数劈分（当月只承担当月天数）；RULE-024 落地、016/019 注记升级引用；commit `cea7095` |
| A11 | D11 补录窗口阈值（step2§二） | PROP-BOHAI-016 | **accepted** | T-5 到齐关箱：RULE-025 表达式+挂接落定（commit `043613f`） |
| A12 | D12 缺失行计入分母（step2§二） | PROP-BOHAI-017 | **accepted** | 裁 缺失行不入分母+缺失率单列+入清单核实性质；RULE-015 定案；commit `fc21fb8` |
| A13 | D13 统一前使用边界（step2§二） | PROP-BOHAI-018 | open（部分裁决） | (b) 使用边界已裁：统一前限井组年尺度内部评估不入对外报表（commit `69ce96c`） |
| A14 | D14 停机码映射表全集（step2§二） | PROP-BOHAI-019 | **accepted** | 全集 12 对到齐落 RULE-006（R11 不折减差异保留）；commit `db6a517` |
| A15 | D15 商品量 vs 井口仲裁（step2§二） | PROP-BOHAI-020 | **accepted** | 裁决 ①+②+③（并存披露+使用边界+输差率折算关系，阈值挂后续提案）；AGG-008+QR-003 同步落定；commit `048aa32`；事故 7/13 同源问题有标准答案 |
| A16 | MU 全模型无素材（step2§一/§四） | PROP-BOHAI-022 | **rejected** | 裁维持不建（R5 无 UI 证据+产物形态无界面面；素材到另立提案）；commit `881b041` |
| A17 | AGG-BOHAI-009 物理落表（step2§三/§四） | PROP-BOHAI-021 | **accepted** | 裁 维持无源虚拟实体（劈分人工台账；新建源表归源系统侧建议；推导缺素材入问题清单）；commit `e3ab3d6` |
| A18 | 提取件二 8 条规则 §4 规则 13–20（step2§四） | PROP-BOHAI-023 | **accepted** | 8 条落 RULE-026..033（commit `0634435`）+装配接线 CORE-01 扩集（`adf254f`）；取样插补前置闭合 |
| A19 | 指标 8 措施有效率判据（fidelity§二/收官§6.9） | PROP-BOHAI-024 | **accepted** | 判据到齐关箱：RULE-034（90日累增油≥80t或有效期≥180日）；commit `3898cc9` |
| A20 | 指标 12 机采能效公式（fidelity§二/收官§6.9） | PROP-BOHAI-025 | **accepted** | 三级公式+单位（kN/A）到齐关箱：RULE-035+AGG-007 注记；commit `38bee60` |
| A21 | 指标 15 桶油成本投入字段（fidelity§二/收官§6.9） | PROP-BOHAI-026 | open（部分裁决） | 方向裁：本期不引入（ERP 扩源归源系统侧决策）；指标位池内预留；入问题清单 |
| A22 | 指标 2 开井日历支公式（fidelity§二/收官§6.9） | PROP-BOHAI-029 | open（缺公式） | 日历支公式未给全不猜；剔检支已全译可用；入问题清单 |
| A23 | 指标 3 年化拟合（fidelity§二/收官§6.9） | PROP-BOHAI-030 | **accepted** | 裁 实现层=对数线性回归+滚动 12 月窗口+扣减口径沿月度式（注记级可逆）；commit `d7f4e1d` |
| A24 | 指标 5 Q_w 换算口径（fidelity§二/收官§6.9） | PROP-BOHAI-031 | **accepted** | 裁决 B′ 默认推算+化验校正（>5pp 井月以化验重算）；RULE-BOHAI-010 条件式落定；commit `8e5e334`；A3 联动闭环 |
| A25 | 指标 10 基线拟合参数（fidelity§二/收官§6.9） | PROP-BOHAI-018 | open（部分裁决） | (a) 拟合参数缺素材待 Owner，入问题清单（同靶 A13 已部分裁决） |
| A26 | §4 规则 6 完井不在 8 表（step2§三/收官§6.10） | PROP-BOHAI-027 | **rejected** | 裁挂起（扩源=域面变更须 Owner 主动引入另立提案）；RULE-037 号位回收；commit 见本行翻转批次 |
| A27 | §4 规则 11 实时域（m3 头注/收官§6.10） | PROP-BOHAI-028 | **accepted** | 裁 批面近似（当日批内 current 全零即告警；实时面另案）；RULE-038 落地；commit `f930be8` |
| A28 | 区块/油田/平台/井筒/配注层未建（fidelity§一/收官§6.12） | PROP-BOHAI-013 | **accepted** | 区块建维形 AGG-BOHAI-010（族首）；油田/平台/井筒/配注层裁不建（无素材建即空壳，素材到另立提案）；commit `9d0b0c4` |
| A29 | 术语 水淹层 未建（fidelity§三） | PROP-BOHAI-001 | **accepted** | 票 10 落 GLS-BOHAI-006；commit `0474bc8`；残留扩域不随本提案闭合 |
| A30 | 术语 配注合格率 未建（fidelity§三） | PROP-BOHAI-002 | **accepted** | 票 10 落 GLS-BOHAI-009；commit `0474bc8`；指标化残留→PROP-BOHAI-014 |
| A31 | 术语 三多四难 未建（fidelity§三） | PROP-BOHAI-003 | **accepted** | 票 10 落 GLS-BOHAI-010；commit `0474bc8`；无残留 |
| A32 | 禁用词「老完成率」无强制拦截面（fidelity§三/收官§6.11） | PROP-BOHAI-004 | **accepted** | 票 16 banned-term 闸（真源=GLS-BOHAI-001.status）；commit `bad916c` |
| A33 | Golden Q 未加术语问句（review 批次一 P2/票 10 lessons 自认） | PROP-BOHAI-005 | **accepted** | 票 17 增 Q7（GLS-BOHAI-002）/Q8（GLS-BOHAI-001）+瀑布 GLS 步；commit `29f890b` |

## 二、清单外核验（B1–B8 · 不立提案+理由，不静默吞）

| # | 注记 | 出处 | 处置与理由 |
|---|---|---|---|
| B1 | affectedOutput 估算口径不一 | fidelity§一 AGG-004 行 | 不立提案：未进 L0 三真源清单；同型仲裁可循 PROP-BOHAI-008 先例另行受理 |
| B2 | 躺井「限语境」机器判定面 | fidelity§三 GLS-BOHAI-004 notes | 不立提案：术语位已建、无承载素材；语境标签属 GLS 字段演进面（schema 演进票），非业务裁决 |
| B3 | 存水率独立指标化（retentionDelta 无承载字段） | fidelity§三+RULE-BOHAI-008 inputParams | 不立提案：对账总口径未列；RULE-BOHAI-008 描述已注记，随物质平衡实现层一并裁 |
| B4 | 指标 6 折算开关 / 指标 7 累计起点 | fidelity§二 全译行内注记 | 不立提案：全译行内实现层注记，非独立裁决队列条目 |
| B5 | RULE-001 折算实现层 / RULE-002 配对实现层 / RULE-004 窗口起点 / RULE-007 迁移全表 | 各规则 description | 不立提案：元素描述内「实现层待 Owner」注记，未进三真源清单 |
| B6 | 低烈度注记 3 条（取样插补/well_type 改型/设备单位） | dirty-signs §低烈度 | 不立提案：dirty-signs 自判「不单列裁决项」（设备单位已随 PROP-BOHAI-025 联动点名） |
| B7 | wellRef vs wellId 双表示、引用 vs 依赖 | m1 头注+step2§三 | 不立提案：ID/键变更须过影响分析（m1 头注明文），非提案池单点裁决 |
| B8 | M2 行为颗粒度、M6 roleRef Owner 归位 | step2§三 | 不立提案：走查建模颗粒度/归位注记，无待裁业务口径 |

## 三、池现状速览（2026-09-19 · 票 19 落池后）

- 提案 31 份：**accepted 5**（PROP-001..005，已闭环回填）、**open 26**（PROP-006..031）、draft 0、rejected 0。
- 同靶冲突：无（26 份 open 靶元素两两不同；5 份 accepted 不参战）。`python3 tools/proposal_check.py docs/proposals` → 全过，exit 0。
- 预留号位（2026-09-21 A 线裁决后现值）：RULE-BOHAI-020/022/023/024/025 已建（accepted 落地）、021 回收可用（PROP-007 rejected 不建）、026..033（PROP-BOHAI-023 批次预留）、034..038（open 提案占用）；AGG-BOHAI-010 已建（区块维形，PROP-013）；SCR-BOHAI-001 保留可用（PROP-022 rejected 不建）。
- 裁决入口：Owner 按 status=open 逐份裁 accepted/rejected；裁决落痕=改 status+正文注记，不删档（proposal-format.md §4）。
