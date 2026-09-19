---
id: PROP-BOHAI-003
title: 回填登记：新增术语「三多四难」进 GLS 术语模型（GLS-BOHAI-010）
status: accepted
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#三-术语-三多四难未建
target:
  model: GLS
  element: GLS-BOHAI-010
change: modify
rationale: "保真度对账登记术语「三多四难」未建（治理域热词，引马涛，非产量域业务对象/指标/规则）。票 10 已裁决以 GLS 术语位承载（termType=治理热词，owner=语义 Owner，commit 0474bc8），裁决已执行——本提案回填登记该闭环。与水淹层/配注合格率不同，本条无残留业务缺口：治理热词本就不入产量域对象/指标/规则面，术语位即全部闭环。"
---

## 裁决落痕（回填登记）

- 裁决日期：2026-09-19（票 10）；commit：`0474bc8`。
- 落点：`GLS-BOHAI-010`（ontology/bohai/glossary-model.yaml）。

## 草案内容（已进仓形态摘录，非新草案）

```yaml
- id: GLS-BOHAI-010
  term: 三多四难
  termType: 治理热词
  definition: 数据库多、平台多、孤立应用多；共享难、复用难、开发难、协同难（引马涛）。
  relatedObjectRefs: []   # 治理域热词，非产量域业务对象——不硬挂
  status: 有效（引用马涛）
  owner: 语义 Owner
  source: R5·设定书 §6
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §三——三多四难「未建：治理域热词（引马涛），非产量域业务对象/指标/规则——语义 Owner 域，一期域外」。
- A 级：`ontology/bohai/glossary-model.yaml#GLS-BOHAI-010`。
- 无残留：本条信号随术语位落仓完全消解。
