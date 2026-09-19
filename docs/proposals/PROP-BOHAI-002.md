---
id: PROP-BOHAI-002
title: 回填登记：新增术语「配注合格率」进 GLS 术语模型（GLS-BOHAI-009）
status: accepted
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#三-术语-配注合格率未建
target:
  model: GLS
  element: GLS-BOHAI-009
change: modify
rationale: "保真度对账登记术语「配注合格率」未建（定义=分层实注/配注 达标井次占比，但「配注目标」无承载字段）。票 10 已裁决把术语本体位落仓为 GLS-BOHAI-009（commit 0474bc8），裁决已执行——本提案回填登记该闭环（靶元素已在真域，以 modify 形态指向落点）。注意：术语位建成不等于指标化闭环，分母/目标双侧缺的残留缺口由 PROP-BOHAI-014 承接（同靶 AGG-BOHAI-003，另案 open）。"
---

## 裁决落痕（回填登记）

- 裁决日期：2026-09-19（票 10）；commit：`0474bc8`。
- 落点：`GLS-BOHAI-009`（ontology/bohai/glossary-model.yaml）。

## 草案内容（已进仓形态摘录，非新草案）

```yaml
- id: GLS-BOHAI-009
  term: 配注合格率
  termType: 术语
  definition: 分层实注/配注 达标井次占比。
  relatedObjectRefs: [AGG-BOHAI-003]   # 分子侧 layerSplit；分母配注目标无承载字段
  status: 有效
  owner: 采油工艺所
  source: R5·设定书 §6
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §三——配注合格率「未建：『配注目标』无承载字段（AGG-BOHAI-003.layerSplit 是实注且口径不一 D9）——分母/目标双侧缺」。
- A 级：`ontology/bohai/glossary-model.yaml#GLS-BOHAI-009`。
- 残留指向：指标化（新增达标判定规则+配注目标承载）→ 见 PROP-BOHAI-014（open，待 Owner 裁决格式规范与目标字段）。
