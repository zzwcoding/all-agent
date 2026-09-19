---
id: PROP-BOHAI-005
title: 回填登记：Golden Q 增术语两问（Q7/GLS-BOHAI-002、Q8/GLS-BOHAI-001）
status: accepted
source-signal:
  kind: 疑点
  ref: docs/reviews/2026-09-19-phase2-batch1-tickets10-12.md#P2-票10遗留两件
target:
  model: GLS
  element: GLS-BOHAI-002
change: modify
rationale: "票 10 落 GLS 术语模型后自认遗留「Golden Q 六问未加术语问句」（二期第一批审查 P2 点名：纪律落了地但没落消费面）。票 17 已裁决增术语两问：Q7「剔检产量是什么口径」考 GLS 命中指路（GLS-BOHAI-002 别名净产量命中，沿 relatedObjectRefs 指路 RULE-BOHAI-019），Q8「老完成率还能用吗」考禁用词处置守卫（GLS-BOHAI-001 禁用词不被答成可用口径），并给检索瀑布补 GLS 步（commit 29f890b），裁决已执行——本提案回填登记该闭环，以 Q7 主角术语 GLS-BOHAI-002 为 modify 靶登记落痕。"
---

## 裁决落痕（回填登记）

- 裁决日期：2026-09-19（票 17「Golden Q 增术语两问」）；commit：`29f890b`。
- 裁决内容：`fixtures/semantic-service/questions/golden-questions.md` 增 Q7/Q8（编号沿票 17 设计裁决定稿，不连排 Q5/Q6）；检索瀑布（skills/semantic-service references/retrieval-waterfall.md）补 GLS 步——名称解析遇术语词先落 GLS；check_citations 接线；Q8 带守卫正则断言禁用词不被答成可用口径。

## 草案内容（已进仓形态要点，非新草案）

- Q7（GLS 命中指路）：`GLS-BOHAI-002`（剔检产量，别名=净产量）术语条目即答案一部分，沿 relatedObjectRefs 指路 AGG-BOHAI-002 与 RULE-BOHAI-019。
- Q8（禁用词处置）：`GLS-BOHAI-001`（老完成率）命中禁用态 → 回答=禁用说明+替代口径真实 ID 指路（RULE-BOHAI-009 / QR-BOHAI-002）。

## 证据展开

- 信号：`docs/reviews/2026-09-19-phase2-batch1-tickets10-12.md` P2——「票 10 遗留两件：禁用词拦截面未建、Golden Q 六问未加术语问句（lessons 自认）」。
- A 级：`ontology/bohai/glossary-model.yaml#GLS-BOHAI-002`——Q7 解析落点术语。
- 佐证：`fixtures/semantic-service/questions/golden-questions.md`（Q7/Q8 行，票 17 后现状）；`docs/walkthrough/step5-fidelity.md` §三（剔检产量/老完成率条目）。
