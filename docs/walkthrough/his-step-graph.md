# his 域图索引实弹走查（票 69 · 第六批第三域）

> 问答对象：`ontology/his/`（票 67 进仓版，v9-full 八模型）。取证命令逐条实跑，输出摘录于 2026-09-25。
> 图统计：**节点=80 边=155**（三域合计 bohai 96/128 + pkb 19/23 + his 80/155）。

## 1. 建图与命中基线

- `python3 tools/graph_index.py ontology/his --query AGG-HIS-001` → 命中：AGG-HIS-001 (M1) 域=his 位置=m1-object-model.yaml:18，属性 10 个全列出（caseNumber…visitDay）。
- 未命中不猜：`--query RULE-HIS-999` → `未找到: RULE-HIS-999（图内共 80 节点；不做名称猜测）`（退出码 1）。

## 2. closure 两例（正向引用下游）

- **AGG-HIS-001（挂号记录）closure 1 → 0 个下游节点**——语义正确：全部引用边都指向它（处方/病历/诊断/检验的 caseRef），它自身无出向引用；枢纽对象的「重」在 impact 不在 closure。
- **QR-HIS-001（院长驾驶舱）closure 1 → 4 个下游**：BH-HIS-QueryDashboard（via behaviorRef）+ AGG-HIS-001/003/004（via objectRef）——M7→M2 单向依赖边 + M7→M1 出口承载，与 schema §9 依赖白名单一致。

## 3. impact 两例（ref 反向影响集）

- **RULE-HIS-001（退号率告警阈值）impact → 33 个受影响节点**：经 BH-HIS-QueryDashboard 直达，并经 RULE-HIS-003/004/005 共享 QUERY 行为链式扩散到全部 6 QR、6 SCR、13 PERM、5 ROLE、4 ACTOR、FLOW-HIS-001——改一条阈值，报表平台全消费面重审（最深 hops=6：FLOW-HIS-001 → ROLE-HIS-003 → PERM-HIS-CancelRegister → BH-HIS-CancelRegister → RULE-HIS-003 → BH-HIS-QueryDashboard → RULE-HIS-001）。
- **AGG-HIS-004（处方）impact → 经 ASSOC-HIS-001 反向收 1 跳就诊 + BH-HIS-Prescribe/RefundPrescription/QueryDrug + QR-HIS-004 + SCR-HIS-004**——药品字典漂移的落地顺序：先 DICT-HIS-002（被依赖者）后处方链。

## 4. 走查结论

- 八模型全部入图（M1 13 元素/M2 14/M3 7/M5 27/M6 1 流 11 活动/MU 6 屏 29 元素 7 动作/GLS 10），跨模型 ref 边 155 条零悬空（语义闸 L2 全零佐证）。
- MU 首入图：SCR→BH（actions behaviorRef）与 SCR→QR（elements dataSource）两条边型首跑即通，build-contract 阵营与 runtime 检索面划界正确（CORE-17 越面拒答实证）。
