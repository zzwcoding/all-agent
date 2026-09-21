---
id: PROP-BOHAI-008
title: 为日产计量 waterCut 补权威源归属裁决注记（AGG-BOHAI-002）
status: accepted
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D3-化验折算打架
target:
  model: M1
  element: AGG-BOHAI-002
change: modify
rationale: "D3 化验含水（AGG-BOHAI-006.waterCutLab）与折算含水（AGG-BOHAI-002.waterCut）打架：一致性容差已由 RULE-BOHAI-002（偏差≤5pp）承载，但两属性谁是权威源未裁——直接决定综合含水率（RULE-BOHAI-010）等指标的取数方向。dirty-signs D3 原问「两属性并存还是其一为权威源」正待 Owner。提议 modify AGG-BOHAI-002.waterCut 属性注记，补权威源裁决位（裁决后注记权威方与另一属性的使用边界），口径仲裁走对应元素修改。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `AGG-BOHAI-002` attributes.waterCut 增补注记（裁决后落定）：

```yaml
      - name: waterCut          # 既有属性，仅增补注记
        label: 含水率（%）
        type: Decimal
        # 权威源裁决注记（待 Owner）：本属性 vs AGG-BOHAI-006.waterCutLab 谁为权威源；
        # 一致性容差（≤5pp）已由 RULE-BOHAI-002 承载，权威源裁决决定指标取数方向
        refRules: []            # 既有值域 refRules 保持不变（略）
```

## 证据展开

- 信号原文：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D3——「口径不一（化验折算与化验表打架）……两属性并存还是其一为权威源」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D3 行——「仍待 Owner：权威源归属」。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-002`——容差检测面；`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-006`——waterCutLab 注记「D3」。
- 影响面：单属性注记级增补，不改引用结构；RULE-BOHAI-010（综合含水率）取数方向随裁决更新（见 PROP-BOHAI-031，不同靶不相冲）。

## 裁决记录（Owner，2026-09-21）

**裁决：C 并存分场景**——日度监控用计量折算含水（AGG-BOHAI-002.waterCut）；月度/正式指标取数以化验实测（AGG-BOHAI-006.waterCutLab）为准；偏差 >5pp（RULE-BOHAI-002 容差）时以化验校正。

落点：m1-object-model.yaml 三处注记（AGG-BOHAI-002.waterCut / AGG-BOHAI-006 description / waterCutLab）。RULE-BOHAI-010 取数方向由 PROP-BOHAI-031 按本裁决落定（联动未闭，下一份过）。
