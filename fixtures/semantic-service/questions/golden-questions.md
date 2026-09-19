# Golden Question 集 · semantic-service（出厂集固定输入）

- 问答本体: `fixtures/graph_index/ontology-base`（票 04 最小域，两对象七模型各一文件 + UI 屏，只读，不改）。
- 前四问（Q1–Q4）各压检索瀑布一级，对应 specs/semantic-service.md AC1–4；术语两问（Q7/Q8，票 17）
  的解析证据取自 ontology/bohai 真域（GLS 术语条目在真域；票 04 最小域无 GLS 文件，且其图统计
  被 graph_index 出厂集锁定为精确数字，问答本体不扩文件）。断言在 ../assertions.json，
  参照答案在 ../expected-answers/（按 SKILL.md 工序对同一问答本体手工产出，示范瀑布走到哪一级，
  每份带「本回答引用的元素 ID」清单）。
- 问答本体含 MU 屏（camp=build-contract），是有意保留的：Q4 靠它实测"检索面外拒答"；
  图索引对它是全量索引，阵营裁剪是 skill 工序职责（见 skill 正文「检索面」节）。
- 术语两问（Q7/Q8，票 17）考「名称解析遇术语词先落 GLS」：术语条目本身是答案的一部分
  （定义/别名/状态；禁用词的处置=禁用说明+替代口径真实 ID 指路，不得把禁用词答成可用口径），
  并沿 relatedObjectRefs 指路实体（细则见 skill references/retrieval-waterfall.md §2）。

| # | Golden Question | 压的一级 | AC | 考什么 |
|---|---|---|---|---|
| Q1 | 日产量口径是什么？ | 二级名称解析 + 三级闭包装配 | AC1 | 口径四件套（字段/规则/行为/查询出口）配齐，ID 引用可追溯 |
| Q2 | @AGG-BOHAI-001 有哪些行为？ | 一级显式锚定 | AC2 | @ID 直达、不走模糊检索、反向收集行为 |
| Q3 | 月度产量汇总口径是什么？ | 四级可拒答（仓内没有） | AC3 | 拒答 + 缺件分层说明 + 近邻指路，未找到不猜、不编造 ID |
| Q4 | @SCR-BOHAI-01 的页面长什么样？有哪些按钮？ | 四级可拒答（检索面外） | AC4 | camp=build-contract 面外拒答，不返回任何 UI 元素细节 |
| Q7 | 剔检产量是什么口径？ | 二级名称解析（术语词先落 GLS）+ 三级闭包装配 | 票17 AC1 | GLS-BOHAI-002 命中（别名净产量），术语条目即答案一部分；沿 relatedObjectRefs 指路关联对象与承载规则 RULE-BOHAI-019 |
| Q8 | 老完成率还能用吗？ | 二级名称解析（GLS 禁用词）→ 禁用词处置 | 票17 AC2/AC3 | GLS-BOHAI-001 禁用词命中 → 回答=禁用说明+替代口径真实 ID 指路（RULE-BOHAI-009/QR-BOHAI-002），守卫正则断言禁用词不被答成可用口径 |

（问号 Q7/Q8 沿票 17 设计裁决定稿编号，不连排 Q5/Q6。）
