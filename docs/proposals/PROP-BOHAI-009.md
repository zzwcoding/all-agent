---
id: PROP-BOHAI-009
title: 新增配产单值校验规则承载双值行版本语义裁决（RULE-BOHAI-022）
status: accepted
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D4-配产双值行
target:
  model: M3
  element: RULE-BOHAI-022
change: add
rationale: "D4 配产版本切换日双值行目前只有 RULE-BOHAI-009（产量完成率）描述里的争议注记，无执行位；「双值行的版本语义」（两个都是事实/取最新版本/报错阻断）待 Owner。提议新增 M3 单值校验规则把缺口变成可裁决草案：一井一生产日至多一行非空 planOutput；取舍策略待 Owner 裁决，裁决前建议仅告警不阻断。产量完成率分母直接受双值行影响，裁决落定前该指标口径存在歧义。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-022
  name: 配产单值校验
  ruleType: VALIDATION
  description: "D4 双值行（R5·A.2「配产版本切换日双值行」，与复合主键 (wellId, prodDate) 冲突）。同一井同一生产日至多一行非空 planOutput。版本语义待 Owner：双值=版本事实（并列保留+口径取版）/脏行（取舍策略：保留首行/最新行/报错阻断）；确认前建议 enforcedAt 仅告警。"
  expression: count(non-null planOutput rows by (wellId, prodDate)) <= 1
```

## 证据展开

- 信号原文：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D4——「重复行（配产版本切换日双值行）……双值是版本事实还是脏行」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D4 行——「仍待 Owner：双值行的版本语义」。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-009`——description 争议注记「计划版本切换日双值行（AGG-BOHAI-002.planOutput，D4）」。
- 影响面：纯新增规则元素；裁决后承接方为产量完成率（RULE-BOHAI-009）口径净化。
- 靶 ID 核对：RULE-BOHAI-022 未占用。

## 裁决记录（Owner，2026-09-21）

**裁决：A 版本事实，日口径取切换后版本**——双值=配产版本切换的真实记录（承接 PROP-BOHAI-007=A 班次粒度：切换日早班旧版/晚班新版）；日配产口径=当日最后班次的非空 planOutput；全部双值行出清单供人复核（取版假设兜底，不阻断）。落点：新增 RULE-BOHAI-022（VALIDATION，检出+取版口径，reusedBy 挂产量完成率查询行为）；RULE-BOHAI-009 分母口径注记同步净化。
