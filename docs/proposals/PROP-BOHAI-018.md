---
id: PROP-BOHAI-018
title: 补齐递减增油基线拟合参数与统一前使用边界（RULE-BOHAI-018）
status: accepted
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#二-指标10-基线拟合参数未给
target:
  model: M3
  element: RULE-BOHAI-018
change: modify
rationale: "同靶两残留合一案：(a) 保真度对账指标 10 部分译——递减增油=(实际−基线)×劈分已译，但基线 q_0(1−d_a)^t 拟合参数未给，baselineOil 输入仍是占位；(b) D13——incrOilAnnual 两作业区算法不一致（事故 7），统一口径前的使用边界待 Owner。两项同属「这个口径现在能不能用、怎么才能用」的 Owner 裁决。提议 Owner 提供拟合参数/实现层选定后 modify 本规则：baselineOil 由占位落成可算式，description 补使用边界注记（联席裁决前限井组年尺度评估用，不进入对外报表口径）。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `RULE-BOHAI-018` 拟修改（裁决后落定）：

```yaml
  # 修改一：inputParams.baselineOil 的 sourceField 由「拟合基线 q_0(1−d_a)^t（拟合参数
  #         待 Owner）」落成 Owner 选定的实现层（拟合窗口/基期/递减率取值）
  # 修改二：description 补使用边界注记（D13 统一口径前：限井组年尺度评估，
  #         不入对外报表；联席裁决=采油工艺所+开发室）
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §二 指标 10 行——「增油=(实际−基线)×劈分 已译……基线 q_0(1−d_a)^t 拟合参数未给——未译待 Owner；事故 7 一数多源注记随描述」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D13 行——「RULE-BOHAI-018（递减增油）描述保留事故 7 注记；仍待 Owner：统一口径前的使用边界」；`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D13（两作业区算法不一致）。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-018`——description「基线 q_0(1−d_a)^t 的拟合参数与 d_a 取值待 Owner」；`ontology/bohai/glossary-model.yaml#GLS-BOHAI-007`（术语注记同源）。
- 影响面：单规则修改；劈分承载 AGG-BOHAI-009.splitCoefficient 不变（其落表裁决另见 PROP-BOHAI-021）。

## 裁决进展记录（Owner，2026-09-21，部分裁决——status 维持 open）

**(b) D13 使用边界已裁**：两作业区算法不一致未消前，递减增油限井组·年尺度内部评估使用，不入对外报表口径；对外发布须先完成联席口径统一（采油工艺所+开发室）。已落 RULE-BOHAI-018 description。

**(a) 基线拟合参数（q_0/d_a/拟合窗口/基期）缺素材待 Owner**——参数是工程事实不猜数（入问题清单）。素材到后 baselineOil 由占位落成可算式，本提案关箱。

**关箱（2026-09-21）**：参数到齐（Owner 素材 docs/proposals/evidence/owner-materials-2026-09-21.md §PROP-018，Owner 确认，与 PROP-024 阈值整体生效）——基期=措施前 6 个月；q₀=基期末 7 日均值；dₐ=1−(q末月均/q首月均)^(1/5)，采信域 [0,0.05] 越界转人工。已落 RULE-BOHAI-018 description 与 baselineOil sourceField。本提案关箱（使用边界见上一节 (b)）。
