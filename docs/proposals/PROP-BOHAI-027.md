---
id: PROP-BOHAI-027
title: 受理 §4 规则 6 完井衔接校验待扩源（RULE-BOHAI-037）
status: open
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step2-mr-adjudication.md#三-M3未建清单-规则6
target:
  model: M3
  element: RULE-BOHAI-037
change: add
rationale: "R5·§4 规则 6 的判据挂在完井记录（well_completion）上，该表不在渤海域 8 表——数据源不在域，无法起草（无源不硬译）。本提案作受理登记与裁决点：Owner 裁决是否扩源（补 well_completion 进域→扩源属域面变更，与判据一起提供）或挂起本规则（rejected 归档，同信号再现先查池）。预留 RULE-BOHAI-037 号位；判据在 Owner 提供前不落。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-037
  name: 完井衔接校验（占位——源表与判据由 Owner 提供后命名落定）
  ruleType: 待定
  description: "R5·§4 规则 6 判据挂在完井记录（well_completion）上，该表不在 8 表——源不在域。本提案只登记号位与裁决点（扩源 or 挂起）；判据与源表证明材料由 Owner 提供，提供前不落表达式——不发明语义。"
```

## 证据展开

- 信号原文：`docs/walkthrough/step2-mr-adjudication.md` §三 M3 行——「未建：§4 规则 6（well_completion 不在 8 表）」。
- B 级：`docs/一期收官报告.md` §6 业务面 10（§4 规则 6 未建及原因）；`ontology/bohai/m3-rule-model.yaml` 头注（未建清单同源）。
- 靶 ID 核对：RULE-BOHAI-037 未占用。
- 影响面：占位不改既有元素；扩源若发生，属域面变更（新表→新对象），另走 onto-modeler 工序与 MR。
