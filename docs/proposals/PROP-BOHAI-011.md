---
id: PROP-BOHAI-011
title: 补齐井号归一化映射表全集与归一位置裁决（RULE-BOHAI-005）
status: accepted
source-signal:
  kind: 疑点
  ref: docs/walkthrough/step1-db-reverse-draft/dirty-signs.md#D6-井号旧写法
target:
  model: M3
  element: RULE-BOHAI-005
change: modify
rationale: "井号归一化规则已建（TRANSFORMATION，N2/N-2→N-02 形态示例），残留两项待 Owner：(a) 归一表全集——字典只给一对形态示例，全集不明则归一化跑不全；(b) 归一化在源侧还是语义层执行（dirty-signs D6 原问，波及各表同名键列关联是否成立）。提议 Owner 提供全集与位置裁决后 modify 本规则：expression 由 normalizeWellId 占位落成显式映射表，description 登记执行层归属。靶为既有规则元素，走 modify。"
---

## 草案内容（拟修改点，进仓走 MR，非已定稿本体）

对 `RULE-BOHAI-005` 拟修改（裁决后落定）：

```yaml
  # 修改一：description 补两句——「归一表全集：R5·§4 规则 7 全表（Owner 提供）；
  #          执行层：源侧 ETL / 语义层（Owner 裁决）」
  # 修改二：expression 由 normalizeWellId(rawWellId) 占位落成显式映射集
  #          （如 {N2→N-02, N-2→N-02, ……全集}）
```

## 证据展开

- 信号原文：`docs/walkthrough/step1-db-reverse-draft/dirty-signs.md` D6——「新旧写法并存（N2/N-2 vs N-02）……归一化在源侧还是语义层；同名键列间的关联是否成立」。
- B 级：`docs/walkthrough/step2-mr-adjudication.md` §二 D6 行——「仍待 Owner：归一表全集」。
- A 级：`ontology/bohai/m3-rule-model.yaml#RULE-BOHAI-005`——description「归一化在源侧还是语义层待 Owner 确认；归一表全集待 Owner（字典只给 N2/N-2→N-02 形态示例）」。
- 影响面：单规则 description/expression 修改；关联脏特征检出（RULE-BOHAI-020 等批扫规则的键归一前置）。

## 裁决进展记录（Owner，2026-09-21，部分裁决——status 维持 open）

**(b) 归一化位置已裁**：映射表=语义资产（RULE-BOHAI-005 承载唯一真源）+ 执行归源侧 ETL + 语义层保留旧写法残留检出告警。已落 RULE-005 description。

**(a) 归一表全集：已到齐关箱（2026-09-21）**——Owner 素材（docs/proposals/evidence/owner-materials-2026-09-21.md §PROP-011，Owner 确认）：四类变体形态+幂等规范化算法+6 条代表性映射示例；匹配失败不猜测落问题单。已落 RULE-BOHAI-005 expression/description。本提案关箱。
