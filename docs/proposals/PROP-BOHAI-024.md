---
id: PROP-BOHAI-024
title: 新增措施有效率指标位待判据（RULE-BOHAI-034）
status: open
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#二-指标8-措施有效率未建
target:
  model: M3
  element: RULE-BOHAI-034
change: add
rationale: "§3 指标 8「措施有效率 η」未建——「有效」判据设定书未定义（§3 争议注记原文即「『有效』判据」），不替 Owner 定判据（宁缺毋滥）。本提案预留 M3 指标位并登记裁决点：Owner 给出「有效」判据（如措施后累增油≥阈值 / 含水下降幅度≥门槛 / 有效期≥下限，均可）后 modify 落表达式。台账承载面已就绪（AGG-BOHAI-005 井措施记录），缺的只有判据。"
---

## 草案内容（拟新增元素，进仓走 MR，非已定稿本体）

```yaml
- id: RULE-BOHAI-034
  name: 措施有效率
  ruleType: CALCULATION
  description: "R5·§3 指标 8（Owner=采油工艺所）。「有效」判据设定书未定义——判据由 Owner 提供（阈值/口径均可），提供后落 expression 与 inputParams；判据前不硬译。承载面：AGG-BOHAI-005（措施台账，incrOilAnnual/effectiveFrom/To 现成）。"
  expression: 待 Owner（「有效」判据提供后落表达式，形如 有效措施次/总措施次×100）
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §二 指标 8 行——「未建：『有效』判据设定书未定义（§3 争议注记原文即『有效』判据）——不替 Owner 定判据」。
- B 级：`docs/一期收官报告.md` §6 业务面 9（指标 8 措施有效率判据未定义）。
- A 级：`ontology/bohai/m1-object-model.yaml#AGG-BOHAI-005`——措施台账承载面。
- 靶 ID 核对：RULE-BOHAI-034 未占用（020–025/026–033 已分别由本池其他提案与批次预留占用，见 pool-ledger）。

## 裁决进展记录（Owner，2026-09-21，未裁——status 维持 open）

**缺判据，不可代裁**：「有效」的业务判据设定书明文未定义（§3 争议注记原文即「有效」判据），措施后累增油阈值/含水下降门槛/有效期下限任一形态都是业务事实，发明判据=替业务定 KPI 定义，超代裁边界。**指标位预留维持**（RULE-BOHAI-034 号位池内登记），不落占位元素进本体（PROP-023 同判据：无判据空壳不建）。待 Owner 提供「有效」判据后落表达式即关箱。入问题清单。
