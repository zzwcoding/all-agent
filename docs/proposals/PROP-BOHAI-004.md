---
id: PROP-BOHAI-004
title: 回填登记：为禁用词「老完成率」配强制拦截面（GLS-BOHAI-001）
status: accepted
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#三-术语-老完成率-禁用词拦截面未建
target:
  model: GLS
  element: GLS-BOHAI-001
change: modify
rationale: "保真度对账登记「老完成率」禁用词仅有描述注记、无强制拦截面（校验侧禁用未建）；票 10 lessons 亦自认此遗留。票 16 已裁决落 banned-term 禁用词闸（GLS status=禁用为真源，name/alias 子串匹配，description 豁免防误报，commit bad916c），裁决已执行——本提案回填登记该闭环：拦截面以 GLS-BOHAI-001 的禁用状态为机器真源，故以 modify 形态指向该元素，正文留裁决落痕。"
---

## 裁决落痕（回填登记）

- 裁决日期：2026-09-19（票 16「禁用词拦截面」）；commit：`bad916c`。
- 裁决内容：schema_check 增 banned-term 闸——扫描模型元素 name/alias 是否含 GLS 中 `status` 含「禁用」的术语子串，命中即红；description 引用豁免（防「禁用旧称……」注记自身误报）；防误报对照变体随票落 fixtures。
- 信号闭环：`GLS-BOHAI-001`（term=老完成率，status=禁用（替代：产量完成率））自此成为机器可执行真源。

## 草案内容（已进仓形态要点，非新草案）

- 闸的判定面（tools/schema_check.py banned-term 检查，票 16）：GLS 禁用词 × 元素 name/alias 子串匹配 → 违规；description 豁免。
- 本体侧落点：`GLS-BOHAI-001.status: 禁用（替代：产量完成率）`——闸读此字段，无需再改本体。

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §三——老完成率「禁用词的强制拦截面（校验侧禁用）未建——schema 无术语载体」。
- A 级：`ontology/bohai/glossary-model.yaml#GLS-BOHAI-001`——status=禁用为闸真源。
- 佐证：`docs/reviews/2026-09-19-phase2-batch1-tickets10-12.md` P2（票 10 遗留两件之一：禁用词拦截面未建）；`docs/一期收官报告.md` §6 业务面 11。
