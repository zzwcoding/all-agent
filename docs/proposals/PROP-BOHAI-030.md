---
id: PROP-BOHAI-030
title: 补全自然递减率年化指数拟合实现（RULE-BOHAI-013）
status: accepted
source-signal:
  kind: 对账缺口
  ref: docs/walkthrough/step5-fidelity.md#二-指标3-年化拟合未译
target:
  model: M3
  element: RULE-BOHAI-013
change: modify
rationale: "§3 指标 3「自然递减率 D_n」部分译：月度式 1−q_t/q_{t−1} 已译（本规则 expression），年化指数拟合 q(t)=q_i·e^(−Dt) 非闭式未译——实现层（拟合算法、拟合窗口、扣新井/扣措施口径在年化下的适用）待 Owner 选定。提议 Owner 选定实现层后 modify 本规则：补年化口径 narrative/表达式与实现层注记；月度式不动。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `RULE-BOHAI-013` 拟修改（裁决后落定）：

```yaml
  # description/narrative 补年化支注记：「年化指数拟合 q(t)=q_i·e^(−Dt)——实现层
  #   （算法/窗口/扣减口径年化适用性）Owner 选定后落定；月度式 expression 不变」
```

## 证据展开

- 信号：`docs/walkthrough/step5-fidelity.md` §二 指标 3 行——「月度式 1−q_t/q_{t−1} 全译（扣新井/扣措施在聚合口径说明）；年化指数拟合非闭式——未译待 Owner」。
- B 级：`docs/一期收官报告.md` §6 业务面 9（指标 3 一段未译）。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-013`——description「年化指数拟合 q(t)=q_i·e^(−Dt) 非闭式未译（待 Owner 选实现层）」。
- 影响面：单规则注记级修改；与 RULE-BOHAI-014（综合递减率）的「名近义不可互替」注记联动复核。

## 裁决记录（Owner，2026-09-21）

**裁决：实现层落定**——对数线性回归（ln q(t) 对 t 最小二乘，斜率=−D）+ 滚动 12 月窗口 + 扣新井/扣措施口径与月度式一致。性质：标准工程实现层（公式 q(t)=q_i·e^(−Dt) 已给定，拟合方法非业务事实），**注记级可逆**——业务若有既定拟合工具口径可推翻。与 RULE-BOHAI-014 联动复核：综合递减率「不扣措施」边界不受本裁决影响（名近义不可互替注记维持）。落点：RULE-BOHAI-013 description/expression 注记；年化支 expression 载体待消费面出现时补（当前无 M7 出口引用年化支，不落空表达式）。
