---
id: PROP-BOHAI-031
title: 裁决综合含水率产水量换算口径（RULE-BOHAI-010）
status: accepted
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#二-指标5-Qw换算口径待Owner
target:
  model: M3
  element: RULE-BOHAI-010
change: modify
rationale: "§3 指标 5「综合含水率 f_w」部分译：公式已译，但 Q_w 由 Q_液−Q_油 推算是转写选择——8 表无独立产水量列，推算口径（液量减油量 / 化验含水反推 / 引入水量源表）待 Owner。该口径与 D3 权威源归属（PROP-BOHAI-008）联动：化验若定为权威源，含水率可走 waterCut 直接聚合而非差值推算。提议 Owner 裁决换算口径后 modify 本规则 expression 与数据源注记；裁决前本规则维持推算式并在 description 保留待裁注记。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `RULE-BOHAI-010` 拟修改（裁决后落定，按裁决路径二选一）：

```yaml
  # 路径 A（维持差值推算）：description 注记升级为「推算口径经 Owner 确认」
  # 路径 B（改化验/水量源）：expression 改为按裁决口径（如 waterCut 加权聚合），
  #   inputParams 相应调整——以 Owner 裁决为准，不猜公式
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §二 指标 5 行——「公式已译，但 Q_w 由 Q_液−Q_油 推算是转写选择（8 表无水量列）——换算口径待 Owner；化验/计量打架（D3）经 RULE-BOHAI-002 容差承载」。
- B 级：`docs/一期收官报告.md` §6 业务面 9（指标 5 一支未译）；`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D3（关联裁决）。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-010`——description「Q_w=Q_液−Q_油 换算口径待 Owner 确认」。
- 影响面：单规则修改；与 PROP-BOHAI-008（权威源归属，靶 AGG-BOHAI-002）联动裁决，两案不同靶不相冲。

## 裁决记录（Owner，2026-09-21）

**裁决：B′ 默认推算+化验校正**——f_w 默认差值推算 Q_w=Q_液−Q_油；该井当月化验含水与计量折算偏差 >5pp（RULE-BOHAI-002 容差）时，该井当月以化验实测重算；无当月化验的井走差值推算。承接 PROP-BOHAI-008=C 的"月度化验权威"校正分支，井·月粒度一条确定性规则（一个归属+显式校正策略，不制造双口径）。

落点：m3-rule-model.yaml RULE-BOHAI-010（description 落定注记 + inputParams 改井·月粒度四参 + expression 条件式）。伴生效应：取样频次/插补规则争议（FluidTest 残留）由"疑点"升为指标正确性前置条件——该族提案优先级上调。
