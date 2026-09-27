# 参照答案 Q1（AC1）· 日产量口径是什么？

- Golden Question: 「日产量口径是什么？」
- 走到的瀑布级: 二级名称解析（"日产量"命中日产计量族）→ 三级闭包装配（口径链：载体/校验规则/行为/查询出口）
- 再锚定注记（票 71，2026-09-27）：本答断言面从票 04 最小域迁至 **ontology/bohai 真域**（与机判 CORE-01 冻结集同源——第十一轮 L5 复跑前置）；`RULE-BOHAI-027/030` 为本体合法演进新增（Owner 素材 2026-09-21 提案采纳），一并纳入口径链。
- 断言面: 命中 ID 集（CORE-01 冻结七件）+ 引用清单齐（check_citations 正文↔清单一致）

## 答案（示范格式）

「日产量」在 bohai 真域的口径链（二级名称解析命中日产计量族，三级闭包装配证据）：

1. **录入载体 `AGG-BOHAI-002`（单井日产计量）**：日产量的承载数据面——产油/配产等计量属性按日挂井登记（wellRef 挂井），是本口径的事实源。
2. **质量校验规则四条（全部 VALIDATION）**：
   - `RULE-BOHAI-003` 日产油非空率校验；
   - `RULE-BOHAI-004` 日产恒值检测；
   - `RULE-BOHAI-027` 日产油突变告警（环比日降幅 >40% 且次日未恢复至降幅前 70% → 触发核实单，月度结算前须闭环）；
   - `RULE-BOHAI-030` 日产键完整性校验（(wellId, prodDate, reportShift) 三元组唯一，班次仅 A/B/C，缺失或重复行进问题单）。
3. **查询行为 `BH-BOHAI-QueryWellDailyOutput`（查询单井日产量，QUERY）**：ownerEntity=`AGG-BOHAI-001`（井）——产量口径以井为主体对外提供查询。
4. **查询出口 `QR-BOHAI-001`（单井日产量明细查询）**：口径链出口，闭环为「载体 → 校验 → 行为 → 出口」。

**一句话口径**：日产量 = 以 `AGG-BOHAI-002` 单井日产计量为载体、经 `RULE-BOHAI-003`/`RULE-BOHAI-004`/`RULE-BOHAI-027`/`RULE-BOHAI-030` 四条校验保质量、由 `BH-BOHAI-QueryWellDailyOutput` 查询行为经 `QR-BOHAI-001` 单井日产量明细查询对外提供的产量口径。

## 本回答引用的元素 ID

- AGG-BOHAI-001（井——查询行为宿主，闭包主体）
- AGG-BOHAI-002（单井日产计量——口径载体）
- RULE-BOHAI-003（日产油非空率校验）
- RULE-BOHAI-004（日产恒值检测）
- RULE-BOHAI-027（日产油突变告警）
- RULE-BOHAI-030（日产键完整性校验）
- BH-BOHAI-QueryWellDailyOutput（查询单井日产量——查询行为）
- QR-BOHAI-001（单井日产量明细查询——查询出口）
