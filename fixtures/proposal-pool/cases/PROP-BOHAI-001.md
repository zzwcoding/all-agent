---
id: PROP-BOHAI-001
title: 新增日产计量配产单值校验规则（RULE-BOHAI-099）
status: open
source-signal:
  kind: 对账缺口
  ref: evidence/prop1-d4-gap.md#缺口D4
target:
  model: M3
  element: RULE-BOHAI-099
change: add
rationale: AGG-BOHAI-002 描述里登记的疑点 D4（配产双值行与复合主键 (wellId, prodDate) 冲突）目前只有注记没有拦截；提议新增一条校验规则把「一井一生产日至多一行非空 planOutput」落成可执行判定，双值行如何取舍仍待 Owner 裁决，本提案只负责把缺口变成可裁决的草案。
---

## 草案内容（拟新增元素）

以下为拟新增到渤海域 M3 规则模型的元素草案（进仓走 MR，本提案不是已定稿本体）：

```yaml
- id: RULE-BOHAI-099
  name: 日产计量配产单值
  ruleType: VALIDATION
  description: "同一井（wellId）同一生产日（prodDate）至多一行非空 planOutput；违例即 D4 双值行（R5·A.2 复合主键声明 vs 实数据）。取舍策略（保留首行/最新行/报错阻断）待 Owner 确认，确认前建议 enforcedAt 仅告警。"
```

## 证据展开

- 信号：对账缺口——planOutput 在同一 (wellId, prodDate) 出现双值行，与模型声明的复合主键冲突（见 AGG-BOHAI-002 描述的 D4 注记）。
- 证据文件：`evidence/prop1-d4-gap.md`（缺口记录原文，#缺口D4 锚点）。
- 影响面：纯新增规则元素，不改任何既有元素；后续若 Owner 采纳，承接方为 AGG-BOHAI-002 的数据质量巡检。
