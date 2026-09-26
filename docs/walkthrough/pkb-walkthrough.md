# 走查留痕 · pkb 端到端实弹（All-agent 票 61，2026-09-25）

> 对象：personal-weknora 真系统（`/Users/divh/Downloads/personal-weknora/`，施工票 01–09 全 done，47 测试四门绿）。
> 执行方式：Owner 授权施工窗自主实弹（会话「后面的任务你自己控制，按 sdd-flow 完成所有任务」）；golden 题目由施工窗从素材实体词频起草（Owner 抽检校准留 All-agent 批收官⑤口径）。

## 实弹素材（真实资产，contentRef 指针制）

| 条目 | 类型 | 来源 | 入库规模 |
|---|---|---|---|
| 《故事》材质结构风格与银幕剧作原理 | 书籍 | Owner Documents/概念资产（OCR 优） | 父 149 / 子 728 |
| 月亮与六便士 | 书籍 | Owner Documents/书籍资产（全文） | 父 71 / 子 344 |
| gateway 设计要点 | 开发资料 | 仓样例（Owner 认可路径） | 1/1 |
| 三接入点开关哲学 | 技术感悟 | 仓样例 | 1/1 |

合计：chunk 1074（子块全嵌入，sqlite-vec vec0 索引）；四件 capture→promote 双链全通。

## 五段链路与对账

| # | 链路 | 结果 |
|---|---|---|
| ① | 入库（capture/promote） | ✅ 四件全通，flip→refresh 语义正确 |
| ② | **golden 对账（6 问，≥5 达标）** | ✅ **6/6**：斯特里克兰/毛姆/编剧/agent-key+Keychain/对号表+过闸+前哨/边界规则——要点全命中检索上下文、引用零悬空（golden-exit=0） |
| ③ | 检索问答带引用（CLI ask） | ✅ 引用编号编排层装配，[1] 即命中 gateway 设计要点块 |
| ④ | wiki 派生页 | ✅ 事实块（标题+原文要点，来自 chunk）+LLM 成文层；fake 档如实打 FAKE 桩标 |
| ⑤ | MCP 真起服往返 | ✅ stdio_client+ClientSession：list_tools={ask,graph,wiki}+ask 调用带引用结构 |
| ⑥ | **真实 LLM 问答（glm 档）** | ✅ 问「月亮与六便士主人公」→ 真智谱答「查尔斯·斯特里克兰德」带 [n] 引用意图（检索=确定性嵌入，成答=真 glm——混用口径见缺口②） |
| ⑦ | 图谱面外 | ✅ fake 档抽取为空图 → 查询「斯特里克兰」空返回（宁空不硬凑，闸在执法） |

复跑入口：personal-weknora 仓 `docs/walkthrough-dryrun.md` 固化命令。

## 缺口清单（逐条有去向）

1. **graph 抽取 fake 档=空图**（真实抽取需 LLM 逐块调用，千块成本）：遗留→下批开票「graph 真档抽取实弹」（对小样条目先行，非全库）；
2. **真实 embedding 未全库重嵌**（实弹问答用确定性嵌入检索+真 glm 成答的混用口径）：全库重嵌约 1074 次 embed 调用→下批开票「embedding 真档迁移」（批量+限流）；
3. **agent-key 供应商名不一致**（钥存 glm，代码默认 zhipu）：personal-weknora 仓小票修默认/加 env；
4. **烂 OCR 素材不入库**（《论艺术的精神》首页乱码）：素材质量前置检查票候选；
5. golden 题目为施工窗起草——**Owner 抽检校准待做**（批收官⑤口径：抽检证伪即推翻该问结论开票修）。

## 验收（注源票 61 AC 表）

- [x] AC1 实弹五步链路全通（入库/golden/问答/图 wiki/MCP——命令可复跑）
- [x] AC2 golden 6/6 全绿（≥5 达标，答案+引用对账）
- [x] AC3 走查留痕在场且缺口逐条有去向（本文件）
- [x] AC4 All-agent 仓 ci.sh 四闸全绿（本票提交前执行，提交 23cd860 可考）
