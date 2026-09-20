# spec · semantic-service（运行时语义服务 skill）

触及: skill `semantic-service`

> 断言真源（2026-09-19 起）：tickets/07、17、22、25 票面 AC 表 + fixtures/semantic-service/assertions.json；本表为一期原始基线。

## 出厂集断言表

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | Golden Q："日产量口径是什么"（对最小域本体） | 命中正确指标/对象 ID |
| AC2 | Golden Q：显式 @对象ID 锚定 | 直接命中锚定对象，不走模糊检索 |
| AC3 | 仓内不存在的问题 | 拒答并说明缺什么，不编造 |
| AC4 | 查询涉及 build-contract 阵营模型 | 不在检索面内（不返回 MM/MU 类细节） |

## 行为约定

- 只读；写意图一律回"走提案流程"；回答必须带 ID 引用（可追溯）
