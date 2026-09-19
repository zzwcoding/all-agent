---
id: PROP-BOHAI-001
title: 负变体 · status 枚举值非法
status: published
source-signal:
  kind: 疑点
  ref: evidence/note.md#疑点
target:
  model: M3
  element: RULE-BOHAI-020
change: add
rationale: 本文件 status 取了枚举外的值 published（合法值只有 draft/open/accepted/rejected）——proposal-schema 枚举自检应红（AC4 后半）。
---

负变体：枚举值非法（status: published）。期望违规码 proposal-schema，报值非法并列出合法值。
