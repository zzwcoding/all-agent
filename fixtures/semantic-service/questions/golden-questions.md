# Golden Question 集 · semantic-service（出厂集固定输入）

- 问答本体: `fixtures/graph_index/ontology-base`（票 04 最小域，两对象七模型各一文件 + UI 屏，只读，不改）。
- 四问各压检索瀑布一级，对应 specs/semantic-service.md AC1–4；断言在 ../assertions.json，
  参照答案在 ../expected-answers/（按 SKILL.md 工序对同一问答本体手工产出，示范瀑布走到哪一级，
  每份带「本回答引用的元素 ID」清单）。
- 问答本体含 MU 屏（camp=build-contract），是有意保留的：Q4 靠它实测"检索面外拒答"；
  图索引对它是全量索引，阵营裁剪是 skill 工序职责（见 skill 正文「检索面」节）。

| # | Golden Question | 压的一级 | AC | 考什么 |
|---|---|---|---|---|
| Q1 | 日产量口径是什么？ | 二级名称解析 + 三级闭包装配 | AC1 | 口径四件套（字段/规则/行为/查询出口）配齐，ID 引用可追溯 |
| Q2 | @AGG-BOHAI-001 有哪些行为？ | 一级显式锚定 | AC2 | @ID 直达、不走模糊检索、反向收集行为 |
| Q3 | 月度产量汇总口径是什么？ | 四级可拒答（仓内没有） | AC3 | 拒答 + 缺件分层说明 + 近邻指路，未找到不猜、不编造 ID |
| Q4 | @SCR-BOHAI-01 的页面长什么样？有哪些按钮？ | 四级可拒答（检索面外） | AC4 | camp=build-contract 面外拒答，不返回任何 UI 元素细节 |
