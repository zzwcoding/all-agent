# his 域语义核心实弹走查（票 69 · Golden 8 问冻结留痕）

> 问答对象：`ontology/his/`。逐问实跑 `python3 tools/semantic_service_core.py ontology/his --ask "<问>" --json`，status+hits 期望集冻结进 fixtures/semantic-service/assertions.json（CORE-15–22）与 meta_probe CORE_QUESTION_SETS["his"]（票 64 按域登记机制复用）。
> 五态覆盖：口径 answered×4 / 显式锚定 answered / 越面(MU) refused_out_of_surface / 缺件 refused_missing / 写意图 refused_out_of_surface。

| CORE | 问 | status | hits（排序后期望集=实际集） |
|---|---|---|---|
| CORE-15 | 退号率口径是什么？ | answered | BH-HIS-CancelRegister, GLS-HIS-003, RULE-HIS-001, RULE-HIS-003 |
| CORE-16 | @AGG-HIS-001 有哪些行为？ | answered | AGG-HIS-001 + 14×BH（8 COMMAND + 6 QUERY 全收） |
| CORE-17 | @SCR-HIS-001 的界面细节 | refused_out_of_surface | 空集（MU=build-contract 面外，与 bohai SCR-BOHAI 同款拒答） |
| CORE-18 | 医保报销比例口径是什么？ | refused_missing | 空集（素材未给，缺件分层说明+提案流程指路） |
| CORE-19 | 均次费用怎么算？ | answered | AGG-HIS-005*, GLS-HIS-004, RULE-HIS-004（*误配如实记：检验申请蹭均次费用词面，开单改口径时复核） |
| CORE-20 | 退号率告警阈值是多少？ | answered | BH-HIS-CancelRegister, GLS-HIS-003, RULE-HIS-001, RULE-HIS-003 |
| CORE-21 | 复诊率怎么算？ | answered | GLS-HIS-005, RULE-HIS-007 |
| CORE-22 | 把 @SCR-HIS-001 的查询按钮改成实时刷新要怎么改？ | refused_out_of_surface | 空集（写意图+面外双因，话术形态与 bohai Q14 互补实证） |

零编造自查：以上全部 ID 经 grep 于 ontology/his/ 八文件真实存在；拒答问 hits 为空、未生成任何幻觉 ID。

## 实弹发现（两条，入账不静默）

1. **CORE-19 误配**：AGG-HIS-005（检验申请）蹭入「均次费用」hits——fee/费用词面与检索词重叠。不构红灯（主命中 RULE-HIS-004/GLS-HIS-004 正确且含口径），如实留痕待 L5 评分面或后续 Golden 复跑时观察稳定性。
2. **写意图识别依赖问法**：「帮我改一下退号率阈值」裸问被判 answered（阈值词面锚定本体）；带 @MU 锚点+明确改造语（Q14 同款句式「把 @X 的 Y 改成 Z 要怎么改」）才稳定触发写意图拒答——与 bohai Q14 设计句式一致，非 his 域缝隙。
