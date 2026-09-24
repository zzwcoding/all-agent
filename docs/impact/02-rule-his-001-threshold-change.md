# 变更影响分析 · his 域「退号率告警阈值由 10% 调整为 15%」（票 69 样本）

- 日期：2026-09-25
- 样本变更：`RULE-HIS-001.expression: refundRate <= 10` → `<= 15`（假想口径调整，未实施）
- 取证：`python3 tools/graph_index.py ontology/his --query RULE-HIS-001 --impact`（机械反向取证，零 LLM）

## 影响集（33 节点，按传播依据分组）

| 组 | 节点 | 传播依据 |
|---|---|---|
| 直达消费 | BH-HIS-QueryDashboard | appliedRules |
| 链式共享（经 RULE-HIS-003 退号率口径） | BH-HIS-QueryOutpatient、BH-HIS-CancelRegister、QR-HIS-001、QR-HIS-002、SCR-HIS-001、SCR-HIS-002、PERM-HIS-QueryDashboard/QueryOutpatient/CancelRegister、ROLE-HIS-002/003/004/005、ACTOR-HIS-002/003/004/005 | RULE-HIS-003 reusedBy=QueryDashboard/QueryOutpatient；CancelRegister appliedRules→RULE-HIS-003 |
| 链式共享（经 RULE-HIS-004 均次费用） | BH-HIS-QueryFinance、QR-HIS-003、SCR-HIS-003、PERM-HIS-QueryFinance、RULE-HIS-002 | RULE-HIS-004 reusedBy=QueryOutpatient/QueryFinance；RULE-HIS-002 与 QueryFinance 互挂 |
| 链式共享（经 RULE-HIS-005 处方退费率） | BH-HIS-QueryDrug、BH-HIS-RefundPrescription、QR-HIS-004、SCR-HIS-004、PERM-HIS-QueryDrug/RefundPrescription | RULE-HIS-005 reusedBy=QueryDrug/QueryDashboard |
| 深层（hops≥5） | ROLE-HIS-003、ACTOR-HIS-003、FLOW-HIS-001、PERM-HIS-Settle、BH-HIS-Settle | 主体/流程经权限-行为链挂到 QUERY 行为 |

## 建议落地顺序

1. 先改被依赖者：`RULE-HIS-001` 本体（走提案→MR→语义 CI）。
2. 再改依赖者：警告渲染面（SCR-HIS-001/002 的 refRules 注记、devkit/skillpkg 再生）——生成物由 --check 断言自动盯陈旧。
3. 验收点：Golden CORE-15/20 两问参照答案同步（阈值数字出现在口径叙述中），L5 评分面抽检。

## 备注

- 影响集不含 M1 属性层（visitStatus 挂 refRules=RULE-HIS-003 非 RULE-HIS-001）——阈值调整不动对象层，符合「规则-表现分离」设计。
- 33 节点是全消费面，实际重审面=2 QR + 2 SCR + 2 参照答案（其余为经共享 QUERY 行为的权限/主体链，随行为重审自然覆盖）。
