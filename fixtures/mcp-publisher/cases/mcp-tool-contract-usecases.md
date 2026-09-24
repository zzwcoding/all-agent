# MCP 四工具行为一致性用例（票 23 出厂集 → 票 24 实弹对照单）

> 真源：本表与 fixtures/semantic-service 八问回归（CORE-01–08）同源（票 22 出厂集钉过 status 与关键 ID）。
> 用途：票 24 smoke client 的内置断言以此为准——经 MCP 协议实调四工具，逐条对 ID/status 一致性。
> 全部回答（含拒答）必含 ID token：「本回答引用的元素 ID」清单节或命中/指路 ID（票 24 AC3 的 grep 面）。

| # | 工具 | 入参 | 期望（对 ontology/bohai） |
|---|---|---|---|
| U1 | semantic_ask | `{"question": "日产量口径是什么？"}` | 骨架回答含「本回答引用的元素 ID」清单；ID 含 AGG-BOHAI-002（answered，ambiguous 列候选是合法形态） |
| U2 | semantic_ask | `{"question": "桶油增产成本的口径是什么？"}` | refused_missing：缺件三层「未建（仓内无承载，待 Owner 提案补建）」+提案流程指路；不硬凑近邻 |
| U3 | semantic_ask | `{"question": "老完成率还能用吗？"}` | refused_banned：GLS-BOHAI-001 命中；替代口径真实 ID 指路 RULE-BOHAI-009 / QR-BOHAI-002 |
| U4 | semantic_ask | `{"question": "@SCR-BOHAI-01 的界面细节"}` | refused_out_of_surface：前缀先判 MU camp=build-contract 即拒，不返回任何 UI 细节 |
| U5 | semantic_query | `{"element_id": "AGG-BOHAI-001"}` | 节点简报：ID、model=M1、域=bohai、文件位置；未找到不猜的镜像见 U6 |
| U6 | semantic_query | `{"element_id": "AGG-BOHAI-999"}` | 未找到明确报错（不做名称猜测、不给近似拼写建议） |
| U7 | semantic_closure | `{"element_id": "GLS-BOHAI-002", "hops": 1}` | 闭包含 AGG-BOHAI-001 / AGG-BOHAI-002（relatedObjectRefs 正向，hops=1） |
| U8 | semantic_impact | `{"element_id": "AGG-BOHAI-001"}` | 影响集非空且含 BH-BOHAI-* 名下行为（--impact 反向）；hops≤2 区分直挂/经子对象。量级随本体演进是活数不钉快照值（票 66：票 24 时点基线 56 已演进至 64） |
