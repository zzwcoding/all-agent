---
id: PROP-BOHAI-017
title: 裁决措施有效期缺失行统计分母口径（RULE-BOHAI-015）
status: accepted
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#二-指标9-缺失行是否计入分母
target:
  model: M3
  element: RULE-BOHAI-015
change: modify
rationale: "D12：约 30% 措施行 effective_from/to 缺失；进仓裁决两属性不设 required（30%<100% 意味着允许缺失行存在），但缺失行是否计入措施有效期统计分母未裁——直接决定该指标的分母口径（3 成行缺席时「平均有效期」可被显著拉偏）。提议 Owner 裁决后 modify RULE-BOHAI-015：description 补分母口径裁决注记，必要时表达式补缺失行计数说明；口径仲裁走对应元素修改。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `RULE-BOHAI-015` 拟修改（裁决后落定）：

```yaml
  # description 补注记：「缺失行分母口径（Owner 裁决：计入分母按缺失剔除 /
  #   不计入分母单列缺失率）/ 缺失行是否触发问题单闭环」
  # expression 视裁决补分母说明（现状 effectiveTo - effectiveFrom 仅对非缺失行可算）
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §二 指标 9 行——「t₂−t₁ 逐字；D12 30% 缺失行是否计入分母待 Owner」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D12 行——「effectiveFrom/To 不设 required……仍待 Owner：缺失行是否计入统计分母」。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-015`——description「D12：约 30% 行 effective_from/to 缺失——缺失行是否计入统计分母待 Owner」；`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-005`——effectiveFrom/To 注记「D12 约 30% 缺失，不设 required」。
- 影响面：单规则 description/表达式注记；措施有效期（§3 指标 9）口径随之定案。

## 裁决记录（Owner，2026-09-21）

**裁决：缺失行不计入分母 + 缺失率单列报告 + 缺失行入清单核实性质**——塞入分母会拉偏平均值且掩盖缺失问题；30% 缺失率本身作为数据质量指标单列可见；缺失属正常业务还是质量问题由清单核实结论回填（不预设）。落点：RULE-BOHAI-015 description/expression 注记。
