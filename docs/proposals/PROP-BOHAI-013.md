---
id: PROP-BOHAI-013
title: 新增区块维形对象承载无源业务实体族裁决（AGG-BOHAI-010）
status: accepted
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#一-对象-无源表实体未建
target:
  model: M1
  element: AGG-BOHAI-010
change: add
rationale: "保真度对账：区块/油田/平台/井筒/配注层五业务实体 R5·§5 实体草案有名、但无源表且无属性级素材，按「字典没有、设定书属性面也没有的一律不建」未建，是否以维形对象补建待 Owner（收官报告 §6 业务面 12）；D8（field_name 冗余是否提升「油田」为独立对象）是同族裁决点，并入本提案一并裁。提议以素材最全的「区块」为族首建维形对象（blockName 在两表出现、密度基准按区块分区），其余四实体随裁决结果以 AGG-BOHAI-011 起顺延补建或明确不建；属性面不发明，留 Owner。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: AGG-BOHAI-010
  name: 区块
  alias: Block
  aggregateType: AGGREGATE_ROOT
  description: "R5·§5 实体草案「井—隶属→区块」。无源表（8 表之外），维形位：blockName 渤南/渤中/渤西（AGG-BOHAI-001.blockName 属性与 AGG-BOHAI-008.blockName 复合主键成分两处现值）；区块密度基准 0.86/0.89/0.91（R5·§2.2）的自然承载。属性面与引用方向（井/结算是否改引用 blockRef）待 Owner——维形提案不发明属性。"
```

同族待裁（不随本提案一次建）：油田（D8 提升裁决）/ 平台（§5「平台—承载→井」，现 platform 为 String 属性）/ 井筒 / 配注层——Owner 裁「补建」则各立 add 提案，裁「不建」则本提案正文登记关停理由。

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §一——「设定书有、仓内未建的业务实体：区块/油田/平台/井筒/配注层（R5·§5 实体草案）——均无源表、无属性级素材……待 Owner 确认是否以维形对象补建」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D8 行（油田提升裁决）+ §三「无源表」；`docs/一期收官报告.md` §6 业务面 12。
- A 级：`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-001`——blockName/platform 属性注记「未建对象（无源表，待 Owner）」；`#AGG-BOHAI-008`——blockName 复合主键成分。
- 靶 ID 核对：AGG-BOHAI-010 未占用（m1 现有 001–009，grep 核实）。

## 裁决记录（Owner，2026-09-21）

**裁决：区块建维形（族首），同族四实体裁不建**。区块有实质承载（blockName 两处现值+密度基准按区块分区），建维形对象 AGG-BOHAI-010（属性仅 blockName+densityBenchmark，全注源不发明）。油田（D8 不提升——无业务驱动拆对象，fieldName 保持行内冗余属性）/平台/井筒/配注层**不建**（无源表无属性素材，建即空壳；素材到时另立 add 提案，非永久关停）。井/结算的 blockName 改引用 blockRef 暂不动（引用改造走影响分析另提案）。落点：m1 新增 AGG-BOHAI-010。
