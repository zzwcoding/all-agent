# 参照答案 Q1（AC1）· 日产量口径是什么？

- Golden Question: 「日产量口径是什么？」
- 走到的瀑布级: 二级 ID/名称解析（无 @ID，名称"日产量"命中两处落点）→ 三级闭包装配（口径四件套：字段/规则/行为/查询出口）
- A 线对照复核（2026-09-21，票 57 整改）：复核未涉及——本答断言面=问答本体 fixtures/graph_index/ontology-base（票 04 最小域，A 线未触碰，正文与断言零改动）；bohai 机判面的 CORE-01 扩集（RULE-027/030 装配接线）已在出厂集断言注记承载，不涉本答。
- 断言面: 命中 ID 集 + 引用清单齐（本文件同时是 answers 的格式示范）

## 答案（示范格式）

「日产量」在本问答本体有两个互相衔接的落点（二级名称解析命中，三级闭包装配口径证据）：

1. **井上属性 dailyOutput（标签「日产量」，Decimal）**：定义于 `AGG-BOHAI-001`（井）的 attributes；自带行级约束 refRules「产量非负」value >= 0（violationMessage：日产量不得为负）。
2. **录入载体 `AGG-BOHAI-002`（单井日产量记录）**：属性 outputVolume（标签「产液量」，Decimal，必填）；经 wellRef（targetAggregate → `AGG-BOHAI-001`）挂到井上，不变式「记录必须挂井」wellRef != null（ON_CREATE）。

**校验口径**：规则 `RULE-BOHAI-001`（日产量不得为负，VALIDATION）expression `outputVolume >= 0`，由行为 `BH-BOHAI-RecordDailyOutput`（录入单井日产量）以 appliedRules 引用执行——与井属性上的行级约束口径一致（均 >= 0，双层登记、语义一致）。

**查询出口**：`QR-BOHAI-001`（单井日产量查询）结果列 outputVolume（产液量）sourceExpression `w.dailyOutput`——报表列直接取井.dailyOutput，口径链闭合。

**属性级下钻说明**：属性引用类口径按 schema 约定走 dictionaryRef/dictionaryId 链（如井状态字段的 dictionaryRef 指向 `DICT-BOHAI-01`，typeCode WELL_STATUS）；dailyOutput 是 Decimal，无字典维度，本口径不含该项。

**一句话口径**：日产量 = 单井按日记录的产量数值，录入时经 `RULE-BOHAI-001` 校验非负，载体是 `AGG-BOHAI-002` 的 outputVolume（产液量），查询出口 `QR-BOHAI-001` 直接取 `AGG-BOHAI-001` 的 dailyOutput。

## 本回答引用的元素 ID

- AGG-BOHAI-001（井——dailyOutput 属性宿主，闭包起点）
- AGG-BOHAI-002（单井日产量记录——录入载体，wellRef 挂井）
- RULE-BOHAI-001（日产量不得为负——校验口径）
- BH-BOHAI-RecordDailyOutput（录入单井日产量——规则执行行为）
- QR-BOHAI-001（单井日产量查询——查询出口，报表列取 dailyOutput）
- DICT-BOHAI-01（井状态字典——dictionaryRef 下链示例，非本口径主链）
