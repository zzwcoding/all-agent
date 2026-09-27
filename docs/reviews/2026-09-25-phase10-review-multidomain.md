# 第十轮审查：多域可靠性专项 + 文档对齐盘点（sdd-flow2 审查窗）

- 日期：2026-09-25（第六批收官后，三域并存：bohai 7 + pkb 4 + his 8 = 19 模型文件）
- 重点：**多域隔离/可靠性/准确性**——所有跨域泄漏面实弹取证（注入-还原实验 + 跨域问句探针）
- verdict：**无 P1；P2 ×3（1 已实弹收编 e5b8849，2 拆票 72/73）；多域隔离主体验证通过**

## 一、多域隔离实弹取证（重点面）

| # | 实验 | 结果 | 判定 |
|---|---|---|---|
| T1 | his 域问 bohai 禁用词「老完成率还能用吗」 | refused_missing（不触发 bohai 禁用闸） | ✅ 运行时禁用词域内隔离 |
| T2 | pkb 域问 bohai 口径「日产量口径」 | refused_missing（零 bohai 泄漏） | ✅ |
| T3 | his 域问 pkb 业务词「知识条目暂存入册」 | refused_missing | ✅ |
| T4 | 注入 his 权限跨域借 ID（PERM-BOHAI-CaptureItem）→ 单域跑 + 仓根跑 | 单域 3×L2 红；**仓根同样 3×L2 红**（还原后复绿） | ✅ dangling-ref 判定域内有效，跨域借 ID 仓根照抓 |
| T5 | 图索引仓根跑（195 节点 306 边）closure/impact | AGG-HIS-001 closure 2 跳 0 个 BOHAI/PKB 节点 | ✅ 图边不跨域 |
| T6 | MCP manifest 三域块 | his 块含 MU/pkb 块缺 M3M7（与 omittedModels 一致），域块工具清单零互串 | ✅ |
| T7 | 审记旁档共享（bohai/pkb/his 同落 devkit-review.json） | verify 按 target 过滤，his=pending/bohai+pkb=已审各自正确 | ✅ 票 59 修复有效 |
| T4 勘误（票 76，2026-09-27）| T4 注入的 PERM-BOHAI-CaptureItem 全仓不存在（exit=1）——仓根抓红靠全局悬空而非域隔离；真实他域 ID 注入实证仓根不抓（defs_by_domain 修复后已可抓）。原 T4 行为假阴性验证 | ⚠️ 勘误 |
| T8 | **L4 禁用词并集实验**：his 词面造含「老完成率」元素 → 单域跑 vs 仓根跑 | **单域全过、仓根 1×L4 红**（还原后复绿） | ❌ **P2-1 缝隙实锤** |

**P2-1（唯一可靠性实锤）**：schema_check L4 禁用词面=仓根跑时的**全域 GLS 并集**（bohai 禁用词「老完成率」会命中 his/pkb 的正常词面），而运行时语义核心拒答是**域内**禁用词（T1 实证）——闸与运行时不一致，存在跨域误报面。当前无活实例（三域名/别名零重叠故全绿），属 Latent 缝隙：新域词面若与他域禁用词撞车，仓根 CI 必红而单域不红，误导排障方向。修=禁用词收集按域内配对（GLS 所在域的文件才匹配该域禁用词）。

**通过面备注**：L2 跨域借 ID 仓根照抓（T4）——票 38 的 id_index 按 manifest domain 值分桶 + definitions 域内判定，多域下无需修。

## 二、文档对齐发现（探索窗扫描 + 本窗复核）

| # | 位置 | 问题 | 级别 |
|---|---|---|---|
| D1 | references/his-source/ 五件 | **未跟踪未入仓**（票 66 落盘≠入仓，新 clone 丢素材真源，R13 登记失实） | **P2（已实弹收编 e5b8849）** |
| D2 | docs/三期收官报告.md §2 回归底线 | 9 条命令全写死 ontology/bohai，节标题却声明「后续批收官必跑」；第六批实际已跑双域探针，命令面滞后实践 | P2 |
| D3 | AGENTS.md 协议第 9 条 ①⑥ | 批收官探针/审记 verify 单域写死（①只跑 ontology/bohai、⑥只 verify bohai 两路径），三域下按条文执行漏 pkb/his | P2 |
| D4 | docs/prd.md 决策追认 | 缺第六批（2026-09-25 his 第三域 v9-full）登记——批次纪律「PRD 同步」未执行 | P2 |
| D5 | docs/二期收官报告.md §6 缺口清单（现行） | #1「L5 未建」被票 42–44 推翻、#5「open 提案 26 份」被 A 线清零推翻 | P2 |
| D6 | docs/三期收官报告.md §6 缺口（现行） | open 26/第二域接入两条已被 A 线清零+pkb+his 超越 | P3 |
| D7 | policies/README.md:20 + signal-routing.json:3 | 路由表维护纪律自检命令写死 ontology/bohai，改路由的自检不覆盖 pkb/his 域 | P3 |
| D8 | docs/prd.md:75 节标题 | 「首个业务域（建议，待拍板）」状态词过期（早已拍板进仓） | P3 |
| D9 | AGENTS.md:26 references 行 | 调研落盘清单缺 ddd-as-code/weknora-digest/his-source 等，入口文档不指素材真源 | P3 |

## 三、观察项（入账不拆票）

1. **his 域 L5 面未建**：L5 出厂 rubric/参照答案只覆盖 bohai 12 问；his 有 Golden 8 问机判冻结（CORE-15–22）但无评分面——挂残项查询面待 Owner 裁（建 his rubric 面 or 维持 bohai-only）。
2. **mcp_smoke_client 默认 ontology/bohai**（DEFAULT_ONTOLOGY）——缺省值合理，建议 help 文案补多域示例，随票 73 顺带。
3. **归档闸对未跟踪文件不设防**（D1 成因之一）——未跟踪文件不违归档闸；收编靠自觉。挂观察，改闸属扩张面待 Owner 裁。

## 四、整改票映射

| 票 | 内容 | 覆盖 |
|---|---|---|
| 72 | 多域可靠性缝隙：L4 禁用词域内化（+单测钉死 T8 两态）+ mcp_smoke 文案 + 观察项入账 | P2-1 |
| 73 | 文档对齐整改：D2–D9 七处 + AGENTS references 行补全 | D2–D9 |
