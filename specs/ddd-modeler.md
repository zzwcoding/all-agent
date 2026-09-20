# spec · ddd-modeler（DDD 战术设计 skill）

触及: skill `ddd-modeler`（正文票 52 落盘；本票只立卡+格式真源+登记，见 tickets/50）

> 断言真源（2026-09-20 起）：tickets/51 票面 AC 表 + fixtures/ddd-modeler/assertions.json（票 51 落盘）、tickets/52 票面 AC 表 + skill 出厂集（票 52）；本表为骨架占位——只立表头与编号，断言随票 51/52 填充（照票 26 五 spec 真源指针先例）。格式真源=design/ddd/README.md；本 spec 与卡（specs/modules.md）不一致时以卡为准。

## 出厂集断言表

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | （票 51 填充：负变体——跨聚合内嵌对方属性） | 闸红，违规码 ddd-cross-agg-embed |
| AC2 | （票 51 填充：负变体——词条悬空） | 闸红，违规码 ddd-term-ref |
| AC3 | （票 51 填充：负变体——不变量清单空/三元组缺失） | 闸红，违规码 ddd-invariant |
| AC4 | （票 51 填充：负变体——表映射断链） | 闸红，违规码 ddd-mapping |
| AC5 | （票 51 填充：负变体——重名/前缀违规） | 闸红，违规码 ddd-naming |
| AC6 | （票 51 填充：最小订单域绿灯样本） | 闸绿 exit 0；批量报文一次收集全部错误（failFast=false） |
| AC7 | （票 52 填充：skill 出厂集——固定本体输入） | 断言产出四类设计件结构与工序中间件清单 |

## 行为约定

- 只产设计草案，进仓走 MR；status 仅 `草案`/`已审` 两值，翻转人=Owner（归档闸机判面）
- 无词条不建模：输入必须是本体模型产物（`ontology/<域>/`）；缺词条回 onto-modeler/提案池，不硬造词
- 不做代码生成（F9/sdd-flow 的事）；不预建事件运行时（Outbox/MQ 由被建项目按需建）
- 闸对设计件一次收集全部错误批量返回（failFast=false），不逐条打回
- 聚合粒度/不变量完备性不硬闸——出「待人审清单」交 Owner 裁决，机器不代业务判断
- 选配路由：只对交易型/状态机型项目路由（判据表真源 docs/ddd-modeler-建造交接包.md §5，卡触发面同步）
