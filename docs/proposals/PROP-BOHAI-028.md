---
id: PROP-BOHAI-028
title: 受理 §4 规则 11 实时零值告警待实时面（RULE-BOHAI-038）
status: open
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step2-mr-adjudication.md#三-M3未建清单-规则11
target:
  model: M3
  element: RULE-BOHAI-038
change: add
rationale: "R5·§4 规则 11（设备电流零值告警）属实时域：数据侧 AGG-BOHAI-007.current 有承载（列在 8 表），但实时处理面未建（渤海 8 表是批表面，15 分钟级调度是 ETL 批闭环非流式）。判据的实时性归属待 Owner：二期实时域建设 / 降为批面近似校验（当日批内 current=0 连续 N 条）/ 不建。本提案预留 RULE-BOHAI-038 号位并登记裁决点；零值判据本身有素材（current==0），待裁决后落。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-038
  name: 设备电流零值告警（占位——实时面归属裁决后落定）
  ruleType: VALIDATION
  description: "R5·§4 规则 11：设备 current 零值告警。数据承载 AGG-BOHAI-007.current 现成；实时面归属待 Owner（实时域二期/批面近似/不建），归属落定后补 expression 与 reusedBy。"
  expression: 待 Owner（实时性归属裁决后落，形如 current == 0 持续窗口告警）
```

## 证据展开

- 信号原文：`docs/walkthrough/step2-mr-adjudication.md` §三 M3 行——「未建：……§4 规则 11（实时域）」。
- B 级：`docs/一期收官报告.md` §6 业务面 10；`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` 低烈度注记 3（load/current 单位待 Owner——关联裁决点）。
- A 级：`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-007`——current 注记「单位待 Owner；§4 规则 11 零值告警属实时域未建」。
- 靶 ID 核对：RULE-BOHAI-038 未占用。
