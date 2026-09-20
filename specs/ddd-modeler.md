# spec · ddd-modeler（DDD 战术设计 skill）

触及: skill `ddd-modeler`（正文票 52 落盘；本票只立卡+格式真源+登记，见 tickets/50）

> 断言真源（2026-09-20 起）：tickets/51 票面 AC 表 + fixtures/ddd-modeler/assertions.json（票 51 落盘）、tickets/52 票面 AC 表 + skill 出厂集（票 52）；本表为骨架占位——只立表头与编号，断言随票 51/52 填充（照票 26 五 spec 真源指针先例）。格式真源=design/ddd/README.md；本 spec 与卡（specs/modules.md）不一致时以卡为准。
> 票 51 填充（2026-09-20）：下表 AC1a–AC4c 与 fixtures/ddd-modeler/assertions.json 断言一一对应（同标签同真源），并承接 tickets/51 票面 AC 表 AC1a–AC6；闸=tools/ddd_check.py 五查，负变体由绿灯副本单点变异生成。

## 出厂集断言表

| 断言 | 出厂集标签 | 给定 | 期望 |
|---|---|---|---|
| AC1a | DDD-AC1a | 聚合卡属性内嵌他聚合字段（`AGG-ORDER-003.amount` 点号路径，negative-variants/d1-cross-agg-embed） | 闸红，违规码 ddd-cross-agg-embed 且红因唯一 |
| AC1b | DDD-AC1b | 事件载荷词条 ID 悬空（GLS-ORDER-999，negative-variants/d2-term-ref） | 闸红，违规码 ddd-term-ref 且红因唯一 |
| AC1c | DDD-AC1c | 不变量清单空（订单卡）+ 三元组缺 expect_fail（支付卡），negative-variants/d3-invariant | 闸红，违规码 ddd-invariant 两处（同码两形态） |
| AC1d | DDD-AC1d | 映射列条目缺 column 键名（t_order_item，negative-variants/d4-mapping） | 闸红，违规码 ddd-mapping 且红因唯一 |
| AC1e | DDD-AC1e | 事件表两条 ORDER_SUBMITTED 重名（negative-variants/d5-naming） | 闸红，违规码 ddd-naming 且红因唯一（报双位置） |
| AC2 | DDD-AC2 | 最小订单域全套设计件（expected/，四类全齐） | 闸绿 exit 0；五查逐项 0 违规 |
| AC3a | DDD-AC3a | 含 ≥3 类错误样本（D1+D2+D3，negative-variants/ac3a-multi-error） | 一次报文收齐全部错误（failFast=false），exit 1 |
| AC3b | DDD-AC3b | 粒度异常样本（支付聚合零事件，negative-variants/ac3b-granularity） | 人审清单软节在场、exit 仍 0 |
| AC4 | DDD-AC4a/b/c | 正常（--json 绿）/违规/配置错（目标目录不存在）三路径 | exit 0/1/2（出厂集钉报文路径，精确退出码整数由 tools/test_ddd_check.py ExitCodes 断言） |
| AC7 | （票 52 填充：skill 出厂集——固定本体输入） | 断言产出四类设计件结构与工序中间件清单 |

## 行为约定

- 只产设计草案，进仓走 MR；status 仅 `草案`/`已审` 两值，翻转人=Owner（归档闸机判面）
- 无词条不建模：输入必须是本体模型产物（`ontology/<域>/`）；缺词条回 onto-modeler/提案池，不硬造词
- 不做代码生成（F9/sdd-flow 的事）；不预建事件运行时（Outbox/MQ 由被建项目按需建）
- 闸对设计件一次收集全部错误批量返回（failFast=false），不逐条打回
- 聚合粒度/不变量完备性不硬闸——出「待人审清单」交 Owner 裁决，机器不代业务判断
- 选配路由：只对交易型/状态机型项目路由（判据表真源 docs/ddd-modeler-建造交接包.md §5，卡触发面同步）
