---
id: PROP-BOHAI-016
title: 新增补录窗口阈值校验规则（RULE-BOHAI-025）
status: open
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D11-迟到补录
target:
  model: M3
  element: RULE-BOHAI-025
change: add
rationale: "D11 补录：补录行为 BH-BOHAI-RecordOverhaul 前置条件已要求批次号带补录标记（样本 20260911-T3，T-3 案例），标记语义有承载；但「T-3 之外的迟到数据怎么办」无任何承载——补录窗口阈值与超窗处置（拒收/收单挂特批/收单转问题单闭环）待 Owner。提议新增 M3 补录窗口校验规则作为裁决执行位；阈值判据待 Owner 提供，rationale 照实登记。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-025
  name: 补录窗口阈值校验
  ruleType: VALIDATION
  description: "D11 迟到/补录（R5·A.4「补录：N-11 batch=20260911-T3」——T-3 案例）。校验补录行（batchId 带补录标记）的业务日期距当前日期是否在窗口阈值内；阈值（T-?）与超窗处置（拒收/特批收单/转问题单）待 Owner 裁决。落定后 reusedBy 挂 BH-BOHAI-RecordOverhaul。"
  expression: 待 Owner（阈值提供后落表达式，如 (today - businessDate) <= T-n）
```

## 证据展开

- 信号原文：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D11——「迟到/补录（样本 20260911-T3，T-3 案例）……迟到数据是否需要接收时间属性；补录窗口阈值」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D11 行——「仍待 Owner：补录窗口阈值（T-3 之外）」。
- A 级：`ontology/bohai/m2-behavior-model.yaml#BH-BOHAI-RecordOverhaul`——preconditions「批次号带补录标记……补录窗口阈值待 Owner 确认」。
- 靶 ID 核对：RULE-BOHAI-025 未占用。
