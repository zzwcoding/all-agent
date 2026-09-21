---
id: PROP-BOHAI-010
title: 新增停井日 openDays 与井状态联动校验规则（RULE-BOHAI-023）
status: accepted
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D5-停井矛盾行
target:
  model: M3
  element: RULE-BOHAI-023
change: add
rationale: "D5「停井日仍>0」矛盾行：openDays 值域 [0,24] 已下沉 M1 refRules（四层下沉第 2 层，只依赖当前属性值），但「停井」与 openDays>0 的矛盾是跨属性判定，refRules 承载不了——矛盾行的清洗规则（清洗/标注/保留）待 Owner。提议新增 M3 联动校验规则作为裁决执行位；该裁决直接影响抽油机时率（RULE-BOHAI-017）口径——其 description 已点名 D5。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-023
  name: 停井日 openDays 联动校验
  ruleType: VALIDATION
  description: "D5 矛盾行（R5·A.2「停井日仍>0 矛盾行」）。openDays>0 而井 currentStatus=停产/检修 的行判为矛盾行，出清单；处置策略（清洗为 0/标注待核/保留并注记）待 Owner。四层下沉说明：值域 [0,24] 已在 M1 refRules，本规则只做跨属性联动面。"
  expression: openDays > 0 implies well.currentStatus in [生产中]   # 处置策略待 Owner 后定 enforcedAt
```

## 证据展开

- 信号原文：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D5——「矛盾行（停井日仍>0）……矛盾行的取舍规则」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D5 行——「值域 [0,24] 下沉 M1 refRules……仍待 Owner：矛盾行清洗规则」。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-017`——description「openDays 值域 [0,24]（M1 refRules）与 D5 停井矛盾行直接影响本口径」。
- 靶 ID 核对：RULE-BOHAI-023 未占用。

## 裁决记录（Owner，2026-09-21）

**裁决：标注出清单交业务核实，不归零不直改**——矛盾归属未定（openDays 误录 or 状态滞后，D7/PROP-BOHAI-012 未裁），清洗为 0 会在状态滞后侧误杀；守 PROP-BOHAI-006 先例（语义层不吞存量修复）。落点：新增 RULE-BOHAI-023（跨属性联动校验，检出即入清单不阻断）；RULE-BOHAI-017 注记同步（矛盾行按原值计入+清单标注）。D7 裁决后本规则的处置可再细化。
