---
id: PROP-BOHAI-026
title: 新增桶油增产成本指标位待投入字段（RULE-BOHAI-036）
status: open
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#二-指标15-桶油成本未建
target:
  model: M3
  element: RULE-BOHAI-036
change: add
rationale: "§3 指标 15「桶油增产成本」未建——分子「措施总投入」无承载字段（数据源 2.5+ERP，ERP 不在 8 表），分母侧 6.29 桶/m³ 换算系数已随 RULE-BOHAI-018 描述注记，增油量侧判据另见 PROP-BOHAI-018。本提案预留 M3 指标位并登记裁决点：Owner 裁决投入字段来源（ERP 扩源进域 / 2.5 台账加字段 / 不引入该指标）后落表达式；缺源不硬译。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-036
  name: 桶油增产成本
  ruleType: CALCULATION
  description: "R5·§3 指标 15。分子「措施总投入」无承载字段（数据源 2.5+ERP，ERP 不在 8 表）——投入来源由 Owner 裁决（扩源/加字段/不引入）后落 expression；换算系数 6.29 桶/m³（R5·§2.2）已随 RULE-BOHAI-018 注记，分母增油口径见 PROP-BOHAI-018。"
  expression: 待 Owner（措施总投入（元）/ 增油量（桶）×6.29 桶/m³ 换算——分子落定后成式）
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §二 指标 15 行——「未建：分子『措施总投入』无承载字段（数据源 2.5+ERP，ERP 不在 8 表）；6.29 桶/m³ 换算系数已随 RULE-BOHAI-018 描述注记」。
- B 级：`docs/一期收官报告.md` §6 业务面 9（指标 15 桶油成本投入字段缺源）。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-018`——description「换算系数 6.29 桶/m³（R5·§2.2，指标 15 桶油成本用）随本口径注记」。
- 靶 ID 核对：RULE-BOHAI-036 未占用。
