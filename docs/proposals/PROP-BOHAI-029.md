---
id: PROP-BOHAI-029
title: 补全有效产量开井日历折算支公式（RULE-BOHAI-019）
status: open
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#二-指标2-开井日历支未译
target:
  model: M3
  element: RULE-BOHAI-019
change: modify
rationale: "§3 指标 2「有效产量」是两支口径并列：剔检支已全译（本规则 expression 与 narrative，票 09 影响分析的变更落点），开井日历折算支公式设定书未给全——narrative 只能占位「开井日历折算支公式待 Owner 补全后并列」。一支不全则「有效产量」术语（GLS-BOHAI-003 一词两译）的消歧永远缺一半。提议 Owner 提供开井日历折算支公式后 modify 本规则：补 (b) 支表达式、两支并列口径注记与使用场景说明。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `RULE-BOHAI-019` 拟修改（裁决后落定）：

```yaml
  # 修改一：expression 补开井日历折算支（公式由 Owner 提供，如
  #         Σ(oilOutput × openDays/24) 之类——以 Owner 原文为准，不猜）
  # 修改二：narrative 由「开井日历折算支公式待 Owner 补全后并列」改为两支并列
  #         口径与各自使用场景注记
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §二 指标 2 行——「剔检支全译（本票影响分析变更落点）；开井日历折算支公式设定书未给全——未译，narrative 占位待 Owner」。
- B 级：`docs/一期收官报告.md` §6 业务面 9（指标 2 一支未译）。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-019`——description「（a）开井日历折算——公式细节设定书未给全，待 Owner」；`ontology/bohai/glossary-model.yaml#GLS-BOHAI-003`——一词两译术语注记。
- 影响面：单规则修改；本规则是票 09 影响分析（docs/impact/01）的变更落点，再改须复核影响报告——交接给走 MR 的人。

## 裁决进展记录（Owner，2026-09-21，未裁——status 维持 open）

**缺公式，不可代裁**：开井日历折算支公式设定书未给全，补公式=发明业务算法（提案草案已明示「以 Owner 原文为准，不猜」）。剔检支已全译可用（PROP-015 跨月劈分已接入），GLS-BOHAI-003 一词两译的消歧注记维持「剔检支可用/日历支待补」现状。待 Owner 提供日历支公式后 modify 落 (b) 支即关箱。入问题清单。
