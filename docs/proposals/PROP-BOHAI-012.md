---
id: PROP-BOHAI-012
title: 为井 currentStatus 补状态时效责任方裁决注记（AGG-BOHAI-001）
status: open
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D7-状态滞后
target:
  model: M1
  element: AGG-BOHAI-001
change: modify
rationale: "D7 状态滞后（N-11 已停仍记「生产中」）的时效责任方未裁：谁负责及时更新状态（作业区/采集系统/治理面）无归属；字典无状态时间戳列，进仓裁决不增设属性（不发明）。该疑点非纯记录项：RULE-BOHAI-007（状态迁移校验）与 RULE-BOHAI-019（剔检口径）都以 currentStatus 为判定字段——状态不更新则剔检产量口径失真。提议 modify AGG-BOHAI-001 的 currentStatus 属性注记，补责任方与时效 SLA 裁决位；责任方归属待 Owner（裁决形式=二选一/指定角色，可裁决）。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `AGG-BOHAI-001` attributes.currentStatus 增补注记（裁决后落定）：

```yaml
      - name: currentStatus     # 既有属性，仅增补注记
        label: 当前状态
        type: Enum
        enumValues: [生产中, 停产, 检修, 待弃置]
        # 状态时效注记（待 Owner）：更新责任方（作业区录入/系统同步/治理稽核）+
        # 时效要求（如状态变更 T+1 内落库）；无时间戳列，责任面为流程约束非字段约束
```

## 证据展开

- 信号原文：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D7——「状态滞后（N-11 已停仍记『生产中』）……状态时效责任方；是否需要状态时间戳属性（字典无此列）」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D7 行——「仍待 Owner：状态时效责任方」。
- A 级：`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-001`——currentStatus 注记「状态滞后 D7；『检修』值是 RULE-BOHAI-019 剔检口径的判定字段」。
- 影响面：单属性注记级增补；下游 RULE-BOHAI-019 剔检口径的时效性随责任方裁决获得解释。
