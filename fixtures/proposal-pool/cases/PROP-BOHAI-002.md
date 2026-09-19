---
id: PROP-BOHAI-002
title: 为日产计量 planOutput 补非负值域约束
status: open
source-signal:
  kind: 监督
  ref: evidence/prop2-monitor-note.md#告警-1
target:
  model: M1
  element: AGG-BOHAI-002
change: modify
rationale: 监督巡检发现 planOutput（配产量，吨）无值域约束，负值可入库；同元素 waterCut 已有 refRules 下沉先例，提议为 planOutput 按同构方式下沉非负值域，属结构性补齐而非口径变更。
---

## 草案内容（拟修改点）

对 `AGG-BOHAI-002`（日产计量）attributes 中 planOutput 增补 refRules（与既有 waterCut 值域同构）：

```yaml
- name: planOutput         # 既有属性，仅增补 refRules 子键
  label: 配产量（吨）
  type: Decimal
  refRules:
    - name: 配产量非负值域
      expression: value >= 0
      violationMessage: 配产量不得为负（吨）
      enforcedAt: ALWAYS
```

## 证据展开

- 信号：监督巡检告警——planOutput 出现负值样本（见证据文件 #告警-1）。
- 证据文件：`evidence/prop2-monitor-note.md`。
- 影响面：单元素属性级增补，不触引用结构；D4 双值行问题另见 PROP-BOHAI-001（不同靶，不冲突）。
