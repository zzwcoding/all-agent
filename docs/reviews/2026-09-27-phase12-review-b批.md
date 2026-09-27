# 第十二轮外部审查 · personal-weknora B 批（2026-09-27，三子代理并行）

> 审查方式：三路只读子代理并行（A 网关与迁移面 / B 图谱抽取与入库面 / C 流程与文档对账），交叉验证后合并去重。整合人：L0 施工窗。整改路由：weknora 票 16（工程错）+ All-agent 票 75（文档对账）。

## 一、复跑式对账总表（C 路实测，18 项）

CI 双仓全绿（weknora 63 测试/All-agent 17/17 出厂集）｜golden --real 8/8｜vec_chunks float[1536] 1074 行｜nodes 10557 精确｜斯特里克兰家族网 CLI 复跑 1099 行｜麦基邻域 5 边｜关系问答带 chunk 级引用｜23+6 哈希零失真｜票 12–15 AC 逐条对得上｜lessons 三关键声称与 git 时间线相容｜票 10/11 整改回归复核全部在位｜两仓工作区净。**无 P1 级声称失实。**

## 二、合并发现清单（P1×1 / P2×7 / P3×13 摘要）

### P1

| # | 标题 | 证据 |
|---|---|---|
| P1-1 | **extract_library 失败路径静默擦除既有图谱**：worker 把非 429 GatewayError/其他异常/坏 JSON/合法空抽取四种结局折叠为同一 skip 桶，主循环对失败条目仍无条件 graph_replace（空集）——探针实证：先抽 1 节点、全失败重跑后 ns 节点 1→0，stats 仅 skip=1、rc0「正常完成」。一次网络故障的重跑可静默清空整图（重建成本 50 分钟） | src/graph/__init__.py:174-176,202 |

### P2

| # | 标题 | 来源 |
|---|---|---|
| P2-1 | MCP --real 网关漏传 embed_provider=minimax：查询侧 glm embedding-3（2048 维）对 1536 库静默零命中（维度守卫全跳过），ask 退化纯 BM25 无警告；根因=网关装配无单点工厂（CLI/golden/MCP 三处各构造） | A F1 |
| P2-2 | 裸 `reindex`（无 --real）静默覆写全库真档向量为假档（1536→64，探针实证 exit 0 无警告）——唯一对事实源做破坏性覆写的 fake 默认命令 | A F2 |
| P2-3 | vec0 KNN 读路径死亡：fresh 实例 `_vec_dim=None` 恒走 fallback cosine，vec 表只写不读（千行级+归一化无实害，但与模块卡承诺不符） | A F3 |
| P2-4 | 空文件 contentRef 绕过 promote 守卫：ratio=0 放行→入册+零块死条目（P2-7 旧账被绕） | B#2 |
| P2-5 | 票 11 AC6 勾选的 linkify 回归测试不存在（grep 零命中）；长短标题嵌套反例未被防护 | B#3 |
| P2-6 | 图谱边数口径混用：stats 数（去重前 11295）被当落库数写进四处文档（实库 11079，PK 去重差 216）；nodes 10557 精确恰证 stats≠库 | A F4/B#4/C P2-1 |
| P2-7 | AGENTS.md 锚点未推 B 批收官与第十一轮审查整改记录（协议「批收官推锚点」对账缺失） | C P2-2 |

### P3（摘要 13 条）

空钥缓存投毒（先缓存后校验）；embed_query 两链计量不一致+基类 isinstance 子类耦合+零测试；PW_EMBED_PROVIDER 未知值静默回落；reindex 半迁移态静默偏斜+无断点续跑；末批多睡+usage 并发竞态+self.dim 死配置；skip 桶混装四结局+43 块无台账；图谱查询/汇入无 ns 归属+context_for_question 泛触发（graph 开关开、普通问题必拉 10 条匿名跨书边）；reflux 标记永不可清；三测试文件 mid-file main 假绿（票 13 同款第三处残留）；OCR 窄口（逗号/连排变体+<200 短路）与二进制引用裸崩；extract_library 无视 graph 开关+F4 spec 缺 extract_library 绑定；ResourceWarning 卫生；phase11 报告「票 72」指针无改号追注。

## 三、正面核实

抽取质量全量对抗：**LLM 幻觉实体率仅 1.8–2.2%**（两书全 label 逐字对照）、悬空边 **0**、11 类白名单无绕过、跨书 ns 写侧隔离严格；OCR 守卫好文本零误伤（四样例 0.0000）、烂样 98.6% 拦截；第十一轮整改（幽灵倒排/边界闸/spec 绑定/CIT）全部在位且绿；钥面零泄漏复查通过；复跑式对账 18 项全绿。

## 四、整改路由

- **weknora 票 16**（工程错）：P1-1 失败路径保护（stats 拆桶+出错条目不写库）+ P2-1 网关工厂收口/装配断言 + P2-2 reindex 守卫 + P2-3 knn 维度回填 + P2-4 空内容拒入册 + P2-5 linkify 回归测试补齐 + P2-6 stats 口径根治 + P3 批（13 条内可顺手者）。
- **All-agent 票 75**（文档对账）：P2-7 锚点推 B 批收官+第十一轮记录（grep 断言）+ P3 phase11 报告改号追注 + 本报告落盘。
- golden 区分度类无新增；B 批验收面新增 F4 spec 绑定随票 16。
