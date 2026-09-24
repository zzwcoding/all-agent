# Q4 candidate（2026-09-25 L5 评分面，成稿窗零上下文派发）

机判 status：`refused_out_of_surface`（`tools/semantic_service_core.py ontology/bohai --ask "@SCR-BOHAI-01 的页面长什么样？有哪些按钮？" --json`，waterfall_level=一级·显式锚定（检索面外），hits/citations 为空）

## 答案

问题带 `@SCR-BOHAI-01` 记法，属一级显式锚定。该锚定**检索面检查不通过，拒答，不返回任何页面/按钮细节**。

**为什么**：元素 ID 前缀 `SCR-` 经模型注册表解析为 MU（UI 模型），camp=build-contract——**不在检索面**（检索面 = camp=business-core）。本服务只答业务语义：对象、行为、规则、权限、查询口径。页面长什么样（布局、控件、按钮、菜单）属建造契约，由 build 侧消费方在建造链路消费，运行时语义服务不返回该类元素任何细节。

**该锚定 ID 在渤海域仓内也无元素实例**：`ontology/bohai/manifest.json` 登记豁免模型 MU 不建文件（R5 素材全文无界面/屏幕/菜单证据，裁决记录 docs/walkthrough/step2-mr-adjudication.md）——故「SCR-BOHAI-01 的页面」在本域本体中没有可描述的承载物，机判 `anchor_exists=false` 与此一致。

**如果你要的在业务面**（以下是与「录入/查询单井日产量」相关的服务面内概念直接引用——不是该页面的映射关系，页面↔业务的映射本身属面外模型，不代答）：

- 单井日产计量的录入行为是 `BH-BOHAI-RecordDailyOutput`（录入日产计量，COMMAND，用户动作，owner 对象 `AGG-BOHAI-002`）；执行需权限 `PERM-BOHAI-RecordDailyOutput`，行为挂接的规则是 `RULE-BOHAI-005`（井号归一化）；
- 该权限 `PERM-BOHAI-RecordDailyOutput` 的 targetRef 即上述行为，数据范围为 DEPT（作业区本部门数据）；
- 单井日产量的查询出口是 `QR-BOHAI-001`（单井日产量明细查询，按井号查明细行，含 reportShift 班次字段）。

**下一步**：页面契约问题请走建造链路（由 build 侧消费方处理）；若认为该页面背后缺业务概念（新行为/新口径/新对象），请走**提案流程**补定义——本服务只读，不改仓、不产文件。

## 本回答引用的元素 ID

- SCR-BOHAI-01（用户锚定 ID，仅复述并说明阵营归属与拒答理由，不展开任何细节；注：域内无元素实例，ID 依据=机判输出与 ontology/schema/model-deps.json 前缀表 SCR-→MU）
- BH-BOHAI-RecordDailyOutput（业务面近邻指路：单井日产计量录入行为，非所问）
- AGG-BOHAI-002（上述行为的 owner 对象，闭包轨迹 `BH-BOHAI-RecordDailyOutput` →(ownerEntity)→ `AGG-BOHAI-002`）
- PERM-BOHAI-RecordDailyOutput（上述行为的执行权限）
- RULE-BOHAI-005（上述行为 appliedRules 挂接的规则：井号归一化）
- QR-BOHAI-001（业务面近邻指路：单井日产量明细查询出口，非所问）
