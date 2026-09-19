---
id: PROP-BOHAI-001
title: 负变体 · 缺必备字段 status
source-signal:
  kind: 疑点
  ref: evidence/note.md#疑点
target:
  model: M3
  element: RULE-BOHAI-020
change: add
rationale: 本文件故意缺 status 字段——proposal-schema 必备字段自检应红（AC4 前半），且 schema 红的文件不再进 target/conflict/evidence 检查（红因纯净）。
---

负变体：字段缺失（无 status 行）。期望违规码 proposal-schema，报「缺必备字段 `status`」。
