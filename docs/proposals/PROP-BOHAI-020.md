---
id: PROP-BOHAI-020
title: 裁决商品量与井口口径仲裁注记（AGG-BOHAI-008）
status: open
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step2-mr-adjudication.md#二-D15-净重口径
target:
  model: M1
  element: AGG-BOHAI-008
change: modify
rationale: "D15：区块月度结算 netWeight（扣自用油与输差）与日产计量井口口径天然不等（事故 7 另一面；§8 事故 13 同源——A11 实时加和 vs E7 统计上报差 3.2%）。两个数并存必有一个被问倒，仲裁规则（披露双口径/指定权威源/定义折算关系）待 Owner。提议 modify AGG-BOHAI-008 description 补仲裁裁决位（与 QR-BOHAI-003 查询出口的口径提示联动）；同型权威源仲裁先例见 PROP-BOHAI-008（不同靶，不相冲）。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `AGG-BOHAI-008` description 拟增补（裁决后落定）：

```yaml
  # description 增补：「口径仲裁（Owner 裁决）：netWeight（商品量，扣自用油与输差）
  #   vs 井口口径（AGG-BOHAI-002.oilOutput 区块合计）——并存披露 / 指定权威 /
  #   定义折算关系（输差率口径），三选一落定后同步 QR-BOHAI-003 口径提示」
```

## 证据展开

- 信号原文：`docs/walkthrough/step2-mr-adjudication.md` §二 D15 行——「QR-BOHAI-003/AGG-BOHAI-008 描述保留『与井口口径天然不等』注记；仍待 Owner：商品量 vs 井口口径的仲裁（§8 事故 13 同源）」。
- B 级：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D15；`docs/一期收官报告.md` §6 业务面 13（商品量 vs 井口口径无仲裁规则）。
- A 级：`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-008`——description「netWeight 扣自用油与输差、与井口口径天然不等=事故 7 另一面（D15）；§8 事故 13 同源——口径仲裁待 Owner」。
- 影响面：单对象 description 注记；查询出口 QR-BOHAI-003 的口径提示随裁决同步（同向修改，另 MR 一并过）。
