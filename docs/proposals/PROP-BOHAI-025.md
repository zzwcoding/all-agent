---
id: PROP-BOHAI-025
title: 新增机采系统能效指标位待公式（RULE-BOHAI-035）
status: open
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#二-指标12-机采能效未建
target:
  model: M3
  element: RULE-BOHAI-035
change: add
rationale: "§3 指标 12「机采系统能效」未建——三级（系统/单元/设备）公式设定书未给，仅优良/合格两个档名，公式缺不硬译。本提案预留 M3 指标位并登记裁决点：Owner 给出三级公式（或裁先行一级）后 modify 落表达式。关联裁决点：AGG-BOHAI-007.load/current 有承载线索但单位字典未声明——公式落定后单位口径一并裁。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-035
  name: 机采系统能效
  ruleType: CALCULATION
  description: "R5·§3 指标 12。三级（系统/单元/设备）公式设定书未给，仅优良/合格档名——公式由 Owner 提供后落 expression 与 inputParams；判据前不硬译。承载线索：AGG-BOHAI-007.load/current（单位字典未声明，随公式一并裁）。"
  expression: 待 Owner（三级公式提供后落表达式）
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §二 指标 12 行——「未建：三级（系统/单元/设备）公式设定书未给，仅优良/合格档名——公式缺不硬译」。
- B 级：`docs/一期收官报告.md` §6 业务面 9（指标 12 机采能效公式未给）。
- A 级：`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-007`——load/current 注记「单位待 Owner」。
- 靶 ID 核对：RULE-BOHAI-035 未占用。

## 裁决进展记录（Owner，2026-09-21，未裁——status 维持 open）

**缺公式，不可代裁**：三级（系统/单元/设备）公式设定书未给，仅优良/合格档名——公式是业务事实不硬译。关联缺口：AGG-BOHAI-007.load/current 单位字典未声明（单位判据随公式一并裁，同待素材）。指标位预留维持（RULE-BOHAI-035 池内登记），不落占位元素。入问题清单。
