# 参照答案 Q2（AC2）· @AGG-BOHAI-001 有哪些行为？

- Golden Question: 「@AGG-BOHAI-001 有哪些行为？」
- 走到的瀑布级: 一级显式锚定（@ID 直达，未走名称模糊检索）→ 三级闭包装配（--impact 反向收集"谁引用了我"）
- A 线对照复核（2026-09-21，票 57 整改）：复核未涉及——本答断言面=问答本体最小域（A 线未触碰）；bohai 机判面 CORE-02 行为集亦未随 A 线增删（A 线 16 条规则均挂接既有行为 reusedBy，不新增行为），实跑复验一致。
- 断言面: 显式锚定直接命中 + 行为 ID 集 + 引用清单齐

## 答案（示范格式）

问题带 @AGG-BOHAI-001，**显式锚定直接命中**，未走名称模糊检索。检索面检查：AGG- 前缀 → 对象模型（M1），camp=business-core，在检索面内，进入装配。

锚定对象 `AGG-BOHAI-001`（井，AGGREGATE_ROOT，生命周期：钻进中/在产/停产/注销）名下行为（ownerEntity 反向收集，--impact 可复现）：

- `BH-BOHAI-UpdateWellStatus`（刷新井状态，COMMAND，SYSTEM 触发）：改 well.status；无前置条件、无附加规则、无权限要求。
- `BH-BOHAI-QueryWellDailyOutput`（查询单井日产量，QUERY，USER_ACTION）：需权限 `PERM-BOHAI-QueryWellDailyOutput`；其查询出口即 `QR-BOHAI-001`（behaviorRef 回指本行为）。

**关联说明（非本对象名下，单列防误答）**：`BH-BOHAI-RecordDailyOutput`（录入单井日产量）的 ownerEntity 是 `AGG-BOHAI-002`（单井日产量记录），经聚合关联 `ASSOC-BOHAI-001`（井 1..* 日产量记录）与流程 `FLOW-BOHAI-001` 间接触达本对象——它不属于"井的行为"，列为关联上下文。

## 本回答引用的元素 ID

- AGG-BOHAI-001（井——显式锚定对象，一级直达）
- BH-BOHAI-UpdateWellStatus（刷新井状态——锚定对象名下行为）
- BH-BOHAI-QueryWellDailyOutput（查询单井日产量——锚定对象名下行为）
- PERM-BOHAI-QueryWellDailyOutput（查询行为的所需权限）
- QR-BOHAI-001（查询行为的查询出口）
- BH-BOHAI-RecordDailyOutput（关联对象名下行为，非所问，单列防误答）
- AGG-BOHAI-002（单井日产量记录——上述关联行为的宿主）
- ASSOC-BOHAI-001（井与日产量记录的聚合关联）
- FLOW-BOHAI-001（触达两对象的录入流程）
