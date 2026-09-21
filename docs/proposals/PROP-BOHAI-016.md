---
id: PROP-BOHAI-016
title: 新增补录窗口阈值校验规则（RULE-BOHAI-025）
status: accepted
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D11-迟到补录
target:
  model: M3
  element: RULE-BOHAI-025
change: modify
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

## 裁决进展记录（Owner，2026-09-21，部分裁决——status 维持 open）

**处置方向已裁：超窗不拒收（数据不丢是底线）、收单转问题单闭环（不静默——出清单走特批核实）**。已落 RULE-BOHAI-025 骨架（description/narrative 落定方向，expression 占位）。

**阈值数值（T-?）缺素材待 Owner**——**已到齐关箱（2026-09-21）**：Owner 素材（docs/proposals/evidence/owner-materials-2026-09-21.md §PROP-016，Owner 确认）——窗口=T-5 日（管理依据：次月 5 个工作日关账，关账前 5 日冻结预备期）。已落 RULE-BOHAI-025 expression `(today - businessDate) <= 5`、reusedBy 挂 BH-BOHAI-RecordOverhaul。本提案关箱。
