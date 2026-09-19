---
id: PROP-BOHAI-007
title: 新增同井同日班次重复行校验规则（RULE-BOHAI-021）
status: open
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D2-班次重复行
target:
  model: M3
  element: RULE-BOHAI-021
change: add
rationale: "D2 同井同日 A/B 班重复行与复合主键 (wellId, prodDate) 声明冲突；进仓裁决保留 reportShift 枚举、主键声明照字典（班次行按业务事实暂保留），残留=去重规则与键约束是否强化待 Owner。提议新增 M3 唯一性校验规则作为该裁决的执行位：Owner 若裁「班次行是业务事实」则本提案 rejected 归档（现状即终态），若裁「须唯一/合并」则本规则承接键约束强化——两个方向都可落，裁决点明确。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-021
  name: 同井同日班次重复行校验
  ruleType: VALIDATION
  description: "D2（R5·A.2「班次手抄汇总：同井同日 A/B 两行」vs「一井一日；PK well_id+prod_date」）。校验同 (wellId, prodDate) 是否存在多行；命中即提示与复合主键声明冲突。处置方向待 Owner：班次行=业务事实（维持现状，本规则仅告警）/ 须唯一（强化键约束或合并策略）。"
  expression: count(rows by (wellId, prodDate)) == 1   # 处置策略待 Owner 后定 enforcedAt
```

## 证据展开

- 信号原文：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D2——「重复行（同井同日 A/B 两行）与主键声明冲突……班次行是业务事实还是应去重？」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D2 行——「仍待 Owner：去重规则与键约束是否强化」。
- A 级：`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-002`——description「A/B 班重复行与主键声明冲突（D2）」+ reportShift 注记「D2 班次手抄汇总」。
- 靶 ID 核对：RULE-BOHAI-021 未占用。
