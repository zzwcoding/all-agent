---
id: PROP-BOHAI-001
title: 回填登记：新增术语「水淹层」进 GLS 术语模型（GLS-BOHAI-006）
status: accepted
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#三-术语-水淹层未建
target:
  model: GLS
  element: GLS-BOHAI-006
change: modify
rationale: "保真度对账登记术语「水淹层」未建（地质层段概念，8 表无承载对象、产量域素材无属性面）。票 10 已裁决补建 GLS 术语模型并把本条落仓为 GLS-BOHAI-006（commit 0474bc8），裁决已执行——本提案按票 19「裁决队列实弹落池」工序回填登记该闭环：靶元素已在真域，故以 modify 形态指向落点元素，正文留裁决落痕；术语已建即信号消解，残留的承载对象缺口（待 Owner 扩域）不随本提案闭合。"
---

## 裁决落痕（回填登记）

- 裁决日期：2026-09-19（票 10「术语模型 GLS 进 schema」）；commit：`0474bc8`。
- 裁决内容：GLS 术语模型进七模型（后八模型）体系，R5·§6 十条术语全量落仓，本条落为 `GLS-BOHAI-006`（ontology/bohai/glossary-model.yaml）。
- 落点元素已在真域（add 已执行完毕），故本提案以 modify 形态登记裁决注记，不作待执行草案。

## 草案内容（已进仓形态摘录，非新草案）

```yaml
- id: GLS-BOHAI-006
  term: 水淹层
  termType: 术语
  definition: 驱替前沿到达的高含水层段。
  relatedObjectRefs: []   # 待 Owner 扩域，不硬挂
  status: 有效
  owner: 地质研究所
  source: R5·设定书 §6
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §三——水淹层「未建：地质层段概念，8 表无承载对象、产量域素材无属性面——待 Owner 扩域时补」。
- A 级：`ontology/bohai/glossary-model.yaml#GLS-BOHAI-006`——术语位已在真域。
- 佐证：`docs/一期收官报告.md` §6 业务面 11（术语水淹层未建→票 10 后已闭环）。
- 残留（不在本提案闭合）：承载对象（层段实体）无属性素材，按「设定书没有的一律不建」不立 add 提案；Owner 扩域时另立。
