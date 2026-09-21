---
id: PROP-BOHAI-019
title: 补齐停机原因码新旧映射表全集（RULE-BOHAI-006）
status: open
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D14-新旧停机码
target:
  model: M3
  element: RULE-BOHAI-006
change: modify
rationale: "D14 新旧停机码并存：映射规则已建（TRANSFORMATION），但字典只示例一对映射（旧 R3=皮带断→新 BELT），映射表全集待 Owner——全集不明则「映射表全命中」的通过判据跑不全；且设备域质检行为二期补，本规则 reusedBy 现留空。提议 Owner 提供全集后 modify 本规则：narrative/expression 落显式映射全表，并把映射表来源注记进 description；属性侧 stopReasonCode 保持 String 不建枚举（进仓裁决不变）。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `RULE-BOHAI-006` 拟修改（裁决后落定）：

```yaml
  # 修改一：description 补「映射表全集：Owner 提供（来源注记）；命中不全即红」
  # 修改二：narrative 落显式映射集（已知一对：R3→BELT（皮带断）；全集待补）
  # 修改三：设备域质检行为落位后补 reusedBy（二期，另行 MR）
```

## 证据展开

- 信号原文：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D14——「新旧编码并存（旧 R3=皮带断，新 BELT）……映射表归属与全集（§4 规则 8 要求映射表全命中，字典只示例一对）」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D14 行——「仍待 Owner：映射表全集（字典只示例 R3↔BELT 一对）」。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-006`——description「映射表全集待 Owner 补齐后再挂接执行行为（设备域质检行为二期补，本期 reusedBy 留空）」；`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-007`——stopReasonCode 注记「D14 新旧编码并存，不建枚举」。

## 裁决进展记录（Owner，2026-09-21，无本体改动——status 维持 open）

**无新裁决面**：承载位（RULE-BOHAI-006）、属性侧不建枚举（进仓裁决）、reusedBy 二期补挂——方向均已定，唯一缺口是**映射表全集素材**（字典只示例 R3→BELT 一对，全集=业务事实，不可代裁不可发明）。与 PROP-011（井号归一表全集）同属"映射全集缺素材"族，入问题清单统一待 Owner 提供。素材到后 narrative/expression 落显式映射全表即关箱。
