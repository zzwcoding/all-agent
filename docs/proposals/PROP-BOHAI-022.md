---
id: PROP-BOHAI-022
title: 裁决 MU 模型补建或维持不建（SCR-BOHAI-001 维形位）
status: open
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step2-mr-adjudication.md#一-MU-不建文件
target:
  model: MU
  element: SCR-BOHAI-001
change: add
rationale: "MU 全模型无素材：R5 全文无界面/屏幕/菜单/控件证据（§1 的「消费票」是 teach-petro-agent 的票号，非 UI 证据），进仓裁决 MU 不建文件（v9-full 下启用模型不出文件不违规）。裁决遗留=「MU 素材」仍待 Owner。提议把「MU 缺素材」变成可二选一裁决项：Owner 提供 UI 素材（转录落仓）则补建 mu-ui-model.yaml，本提案的 SCR-BOHAI-001 作首屏占位维形承接；Owner 明确产量域无界面面则裁决维持不建，本提案 rejected 归档留痕。占位元素不发明任何控件/布局/字段。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体；仅 Owner 给出素材后才有内容）

```yaml
- id: SCR-BOHAI-001
  name: 待定（占位维形——UI 素材提供后由 Owner 素材命名）
  description: "MU 素材面占位：R5 无 UI 证据（step2 §一 MU 不建文件裁决），本元素不发明任何控件/布局/数据源；Owner 提供 UI 素材（转录落仓，C 级证据先落盘）后按素材填实，或裁决维持不建并 rejected 归档。"
```

## 证据展开

- 信号原文：`docs/walkthrough/step2-mr-adjudication.md` §一——「MU 不建文件：R5 全文无界面/屏幕/菜单/控件证据……按『设定书没有的一律不建』不产 mu-ui-model.yaml」；§四 裁决遗留「MU 素材」。
- B 级：`docs/一期收官报告.md` §6 业务面 13（MU 全模型无素材）。
- 靶 ID 核对：SCR- 前缀已在 ontology/schema/model-deps.json idPrefixes 登记（SCR-→MU）；SCR-BOHAI-001 未占用（MU 无文件，grep 核实）。
- 影响面：若补建，mu-ui-model.yaml 为新文件（AC6 反向「启用却缺文件」已由票 13 落闸，omittedModels 机制可承接过渡态）。
