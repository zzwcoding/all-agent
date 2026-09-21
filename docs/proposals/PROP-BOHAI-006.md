---
id: PROP-BOHAI-006
title: 新增吨方混写存量行检出规则（RULE-BOHAI-020）
status: accepted
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D1-吨方混写
target:
  model: M3
  element: RULE-BOHAI-020
change: add
rationale: "D1 吨方混写的增量检出面已落 RULE-BOHAI-001（折算密度值域）与 RULE-BOHAI-011 注记，但「存量误录行」的清点与处置无承载——dirty-signs D1 给 Owner 的原问是「单位语义收进属性定义还是立清洗规则」，进仓裁决语义层不吞存量修复，该项即悬置。提议新增 M3 存量批扫规则把「误录为方的吨值行」变成可检出对象；存量行的修复策略（修复/标注/搁置）与修复验收判据待 Owner 提供，本提案只立检出位与裁决点，表达式留待判据后落。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-020
  name: 吨方混写存量行检出
  ruleType: VALIDATION
  description: "D1 存量面（R5·A.2「oil_output DECIMAL(10,2) 吨（个别行误录为方）」）。按区块密度基准（渤南 0.86/渤中 0.89/渤西 0.91，R5·§2.2）折算后显著越出合理吨值域的行判为疑似误录，出清单不直改数据（语义层不吞存量修复——step2 §二 D1 裁决）。修复策略与验收判据待 Owner 裁决后补 enforcedAt 与 reusedBy。"
  expression: 待 Owner（修复判据提供后落表达式；检出算法=按区块密度折算越界批扫）
```

## 证据展开

- 信号原文：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D1——「单位混写（单位吨，个别行误录为方）……单位语义收进属性定义还是立清洗规则？」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D1 行——「仍待 Owner：存量误录行的数据修复（语义层不吞）」。
- A 级：`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-002`——oilOutput 属性注记「D1 吨方混写」；`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-001`——增量检出面已建，本提案补存量面。
- 靶 ID 核对：RULE-BOHAI-020 未占用（m3 现有 001–019，grep 核实）。

## 裁决记录（Owner，2026-09-21）

**裁决：判据两级 + 处置 A**——确诊=油>液（物理不可能，硬证据，expression 承载）；疑似=按区块密度基准（0.86/0.89/0.91）折算后越合理吨值域（软证据须人复核，narrative 承载）；处置=出清单交业务修复（守"语义层不吞存量修复"先例，不做查询层换算遮羞）。

落点：m3 RULE-BOHAI-020（VALIDATION，expression+narrative 两级，reusedBy 留空待批扫行为二期补）。
