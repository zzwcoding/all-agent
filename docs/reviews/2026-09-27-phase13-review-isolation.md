# 第十三轮外部审查 · 三域隔离专项（2026-09-27，三子代理并行）

> 审查方式：三路只读子代理并行（A 语义闸层 / B 消费面层 / C weknora×pkb 边界），交叉验证后合并。
> 审查对象：ontology/ 三域（bohai 7 + pkb 4 + his 8 = 19 模型文件）、schema_check/审记/MCP/探针/L5 全消费出口、personal-weknora @ 2a9b26a。
> 整改路由：weknora 票 16（B 批工程错）已提前清偿 P1-1/P2-1..6；All-agent 票 76（schema_check L2/一致性对按域分桶 + T4 勘误）。

## 一、正面核实（审查确认成立）

| 面 | 结论 | 证据 |
|---|---|---|
| L4 禁用词三方向域内配对 | 探针 A/B/B2/C 全过 | 票 72 重建的三道域内闸完好 |
| L1 duplicate-id 跨域不判/同域红 | 探针 F/F2 | 票 38 设计如约 |
| L3 域内聚合基准 | 探针 G | bohai alias 变更即刻引发 L3 域内红 |
| 消费面 core 逐问跨域拒答 | bohai 问句→his refused_missing；his 问句→bohai refused_missing | 单域目录绑定=物理隔离 |
| graph_index 仓根跨域边数=0 | 306=128+155+23（三域和恰等） | 全量机判非抽样 |
| 审记旁档三域隔离 | pkb devkit verify 正确甄别到 pkb 记录（票 59 target 甄别） | 五件全过/pending 各归其位 |
| meta_probe 逐域 | 三域全 PASS，第 3/9 项冻结集零互串（票 64 机制实证） | /tmp/review-probe-* 三份 |
| weknora×三域语义零泄漏 | grep 全仓（排 .venv/node_modules/data）BOHAI/HIS/渤海/日产/医院 = 零命中（连白名单区都干净） | 三层实证（代码面/消费面/数据面） |
| weknora devkit 锚定 | review_gate verify pkb devkit = 已审且哈希一致（锚 5a44504） | 三项抽查（AGG-PKB-001/BH-PKB-CaptureItem/status 枚举）全对上 |
| weknora 数据零污染 | items 恰 4 件 Owner 素材；nodes 10557 集合=4 条目 id；跨域词面（渤海/医院/HIS）逐词验明为小说原词/英文片名 | 只读 sqlite 抽样 |

## 二、发现清单（合并去重：P1×2 / P2×7 / P3×12）

### P1×2（均在 schema_check 仓根跑法）

| # | 标题 | 根因 | 探针证据 |
|---|---|---|---|
| P1-1 | **L2 悬空引用判定集跨域共享**：his 借 bohai 真实 ID（AGG-BOHAI-002）仓根绿/单域红——判决随跑法漂移 | definitions 全域共享（schema_check.py:515/:711-713/:929-952） | 探针 D/E/H |
| P1-2 | **一致性对四桶全局收集**：跨域 M7↔M2 绑定既可静默也可把他域合法绑定拉红 | behaviors/permissions/query_reports/flows 四桶全域（:962-997） | 探针 I |

### P2×7

| # | 标题 | 来源 |
|---|---|---|
| P2-1 | MCP 仓根并集面跨域同形词混答无域标注（ask「结算」混列 4 BOHAI+2 HIS hits） | B F-1 |
| P2-2 | L5 评分请求域一致性无机判（his 候选硬套 Q1 rubric → PASS exit 0） | B F-2 |
| P2-3 | 第十轮 T4 结论失实：用全仓不存在 ID 验证跨域隔离属假阴性 | A F-3 |
| P2-4 | weknora reindex 守卫对真库失效（embed_dim 键未回填真库；真迁移在票 13 代码下，票 16 才加键）——裸 reindex 静默覆写 1536→64 | C F1 |
| P2-5 | AGENTS.md 第十一轮括注三处失真（P1 擦图系第十二轮内容误植/P3×13 系 ×11/18 项+幻觉率系第十二轮） | C F2 |
| P2-6 | AGENTS.md 锚点未记录 weknora webui 批（票 16-19 全 done + 81 测试 + CI 五门 + F7 转正） | C F3 |
| P2-7 | weknora linkify 回归测试不存在（票 11 AC6 勾选但未写） | B#3 |

### P3×12（摘要）

违规记录无显式 domain 字段（A F-4）；MCP server 不预检目录存在（B F-3）；smoke client 用例面 bohai 单域（B F-4）；交办面「3 域 445+ 节点」勘误（实为 195）；真 glm 问答原始输出无归档；L5 挂账未销账（同日第六批全量跑实质覆盖，缺一句回写）；weknora reindex 半迁移态静默偏斜+无断点续跑；embed_batched 末批多睡+usage 并发竞态+dim 死配置；skip 桶混装不可审计；图谱查询/汇入无 ns 归属+泛触发；reflux 标记永不可清；三测试文件 mid-file main 假绿；OCR 窄口+二进制裸崩；extract_library 无视 graph 开关+F4 spec 缺绑定；ResourceWarning 卫生；phase11 报告「票 72」指针无改号追注。

## 三、正面核实

三域隔离在**语义闸三道域内闸**（L4 禁用词/L1 重复 id/L3 聚合基准）与**消费面六出口**（core 逐问/图索引/审记/体检/L5 硬闸/smoke）两个层面均有机器实证——特别值得记录的是：**graph_index 仓根跨域边数=0 是全量机判铁证**（306=128+155+23 恰等），不是抽样推断。weknora×三域边界三层实证（代码面零词元/消费面单锚/数据面零污染）。

## 四、整改路由

- **All-agent 票 76**（schema_check P1×2 域分桶 + T4 勘误 + 违规记录 domain 字段 + 回归测试）：schema_check.py defs_by_domain + 一致性对逐域闭合 + CrossDomainIsolation 回归测试 + phase10 T4 勘误。
- **weknora 票 16 已提前清偿**：B 批 P2-4（linkify 回归测试）+ P2-7（空内容守卫）随票 16/61 落地；linkify 三断言+[[…]] 分段保护随票 16 落地。余下 reindex 守卫真库回填（P2-4）留后续票（真库回填 embed_dim 需 Owner 跑一次 reindex --real 或手工 set_meta）。
- **观察项**：his L5 评分面未建（挂残项查询面）；归档闸不设防未跟踪（挂残项查询面）；MCP 仓根并集域标注（待三域实际消费需求出现再开票）。
