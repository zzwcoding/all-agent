---
id: PROP-BOHAI-015
title: 新增跨月检修归属期切割规则（RULE-BOHAI-024）
status: accepted
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D10-跨期切割
target:
  model: M3
  element: RULE-BOHAI-024
change: add
rationale: "D10 跨月作业（样本检泵 8-28→9-06）当月口径归属未定，目前只有 RULE-BOHAI-016（检泵周期）与 RULE-BOHAI-019（剔检口径）两处描述注记，无公共判据；归属期规则（按起算月/终止月/按天数劈分）待 Owner。提议新增 M3 归属期切割规则作为两处口径的公共判据位： Owner 给出规则后，两处注记升级为引用本规则执行；判据待 Owner 提供，rationale 照实登记。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-024
  name: 跨月检修归属期切割
  ruleType: CALCULATION
  description: "D10 跨期切割（R5·A.4「跨月 8-28→9-06：当月口径切割争议源」）。跨月检修对当月口径的归属规则待 Owner（起算月/终止月/按检修天数劈分）。落定后：检泵周期（RULE-BOHAI-016）与剔检口径（RULE-BOHAI-019）的跨月争议注记升级为引用本规则。"
  expression: 待 Owner（归属期判据提供后落表达式）
```

## 证据展开

- 信号原文：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D10——「跨期切割（跨月作业，当月口径切割争议源）……跨月作业的归属期规则（直接影响检泵周期/剔检口径）」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D10 行——「仍待 Owner：归属期规则」；`docs/一期收官报告.md` §6 业务面 13（跨月检修归属期规则未定）。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-016`（D10 注记）与 `#RULE-BOHAI-019`（「检泵跨月（8-28→9-06）时当月口径归属待 Owner」注记）。
- 靶 ID 核对：RULE-BOHAI-024 未占用。

## 裁决记录（Owner，2026-09-21）

**裁决：按日历天数劈分**——跨月检修按自然月劈开，当月只承担落在当月的天数（检泵 8-28→9-06：8 月 4 天、9 月 6 天）；否决起算月/终止月整记（长检修单月失真）。月度指标（时率/剔检）的口径正确性优先于计算简便。落点：新增 RULE-BOHAI-024（CALCULATION，overlapDays 劈分）；RULE-016/019 跨月注记升级为引用本规则。
