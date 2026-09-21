---
id: PROP-BOHAI-021
title: 裁决受效关系实体物理落表方案（AGG-BOHAI-009）
status: accepted
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step2-mr-adjudication.md#三-AGG-BOHAI-009-物理落表待Owner
target:
  model: M1
  element: AGG-BOHAI-009
change: modify
rationale: "受效关系是 R5·§5 明文业务实体（注水井→受效油井多对多，属性=劈分系数 Σ=1、响应起始日），本体位已建且不可删——不建它则 Join 白名单「oil ⋈ water_injection 直连 ✗ 须经受效关系实体」无承载、递减增油劈分无落点。但 8 表无其源表：物理落表方案（新建源表/由现有表推导/维持无源虚拟实体）待 Owner 确认。提议 Owner 裁决后 modify AGG-BOHAI-009 description 登记落表方案与数据源注记；本体元素不动，裁决的是数据承载面。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `AGG-BOHAI-009` description 拟增补（裁决后落定）：

```yaml
  # description 增补：「物理落表方案（Owner 裁决）：新建受效关系表（源系统录入）/
  #   由注水动态+措施台账推导（推导规则待定义）/ 维持无源虚拟实体（仅语义层概念，
  #   劈分系数人工台账维护）。裁决落定后本对象数据承载面随之注记」
```

## 证据展开

- 信号原文：`docs/walkthrough/step2-mr-adjudication.md` §三——「AGG-BOHAI-009 受效关系……无源表（8 表之外的业务实体）：物理落表待 Owner 确认；不建它则 §5『oil ⋈ water_injection 直连 ✗ 须经受效关系实体』无承载」；§四 裁决遗留同点名。
- B 级：`docs/walkthrough/step5-fidelity.md` §一——「无源表实体：AGG-BOHAI-009 受效关系……物理落表待 Owner 确认」；`docs/一期收官报告.md` §6 业务面 12。
- A 级：`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-009`——description「8 表无源表，物理落表待 Owner 确认」。
- 影响面：数据承载面裁决；RULE-BOHAI-018 劈分系数（splitCoefficient）的实数来源随裁决获得解释（公式侧残留另见 PROP-BOHAI-018）。

## 裁决记录（Owner，2026-09-21）

**裁决：维持无源虚拟实体**——受效关系保持语义层概念位（Join 白名单与递减增油劈分的承载，本体位不可删），劈分系数暂由人工台账维护。新建源表属源系统工程决策（超语义平台裁决面，登记为源系统侧建议不代裁）；由现有表推导缺推导规则素材（待定义，入问题清单）。落点：AGG-BOHAI-009 description 落定注记。
