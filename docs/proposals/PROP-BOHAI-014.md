---
id: PROP-BOHAI-014
title: 为注水日计量 layerSplit 补格式规范与配注目标承载裁决（AGG-BOHAI-003）
status: open
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#三-术语-配注合格率-分母目标双侧缺
target:
  model: M1
  element: AGG-BOHAI-003
change: modify
rationale: "同一属性面上的两个待裁信号合靶：(a) D9——layerSplit 两层/三层口径不一、偶为累计值，格式规范待 Owner（结构化=发明格式，进仓裁决保持 String 不结构化）；(b) 术语「配注合格率」（GLS-BOHAI-009，票 10 已建术语位见 PROP-BOHAI-002）的指标化仍缺分母——「配注目标」无承载字段，layerSplit 是实注侧且口径不一。两项都等同一个 Owner 裁决：layerSplit 的格式与语义规范。提议 Owner 裁决后 modify 本属性（String→结构化或保持+规范注记），并裁决配注目标承载（本对象新增属性 or 作为 M3 达标判定规则的参数）；判据/格式待 Owner 提供，rationale 照实登记。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `AGG-BOHAI-003` attributes.layerSplit 拟修改（裁决后落定，二选一路径）：

```yaml
      # 路径 A（裁「结构化」）：
      - name: layerSplit
        label: 分层配注
        type: Struct   # 结构由 Owner 给出的格式规范定（层号/层段/配注目标/实注四元?）
      # 路径 B（裁「保持 String+规范注记」）：
      #   description 补格式规范与「偶为累计值」的甄别规则，另立 M3 达标判定规则承载配注合格率
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §三——配注合格率「『配注目标』无承载字段（AGG-BOHAI-003.layerSplit 是实注且口径不一 D9）——分母/目标双侧缺」；§一 AGG-BOHAI-003 行「layerSplit 覆盖但保持 String 未结构化——D9 格式规范未定，不发明」。
- A 级：`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-003`——layerSplit 注记「D9 不结构化；§6『配注合格率』缺配注目标承载字段」；`ontology/bohai/glossary-model.yaml#GLS-BOHAI-009`。
- B 级：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D9；`docs/walkthrough/step2-mr-adjudication.md` §二 D9 行（仍待 Owner：分层格式规范）。
- 影响面：单属性级裁决；配注合格率指标化（如有）另走 add M3 规则提案，不在本提案内私加。
