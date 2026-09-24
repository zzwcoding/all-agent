# 票 67：his 全八模型本体建模（M1/M2/M3/M5/M6/M7/MU/GLS+manifest）

Status: todo

> 本批核心票：八模型 schema 每条跑道第一个真实域内容（MU 为全仓首个真实文件）。素材=references/his-source/ 五件 + 票 66 细稿。定稿性质=**素材定稿**（非 Owner 签收定稿）——开放问题标「待 Owner 确认」。
Belongs to: docs/第六批第三域拆票方案.md；前置=票 66 done
Touches: ontology/his/（8 模型文件+manifest.json）

## What to build

1. **M1 对象**：8 源表对象（register 挂号/medical_record 病历/medical_record_disease 诊断关联/disease 疾病字典 ICD-10/prescription 处方/drug_info 药品/inspection_request 检验申请/medical_technology 医技项目/department 科室/employee 员工——按聚合归并，非一表一聚合，ID=AGG-HIS-xxx）+ 字段级属性（详细设计 §5.3 字段表为真源）；ADS 7 指标表归 M7 不归 M1（方案 §2 已裁）。
2. **M2 行为**：就诊链路 COMMAND（挂号/接诊/开处方/开检验申请/收费结算/退号退费）+ 报表平台 QUERY（按 6 模块 18 API 归并 6–8 个查询行为）；权限引用 M5 PERM。
3. **M3 规则**：硬规则候选=退号率>10% 告警阈值/收入占比合计=100% 校验/KPI 口径定义（退号率=退号数÷挂号人次等，素材 §4.3 六指标）——预期 3–5 条，不凑数；appliedRules 双向挂。
4. **M5 主体**：患者/医生/收费员/院长（报表消费者）/系统管理员；role 按素材面建（素材未给权限矩阵，开放问题挂账，权限面先按行为最小集）。
5. **M6 流程**：患者就诊全流程（PRD §1.3 流程图：挂号→候诊→接诊→诊断/开药/检查→收费→取药/检查→结束/退号退费）为全仓首个真实 M6 文件。
6. **M7 报表**：6 模块 18 API 归并承载对象（QR-HIS-xxx），口径字段对齐 ADS 表字段（§5.2 字段级）；objectRef 挂 M1。
7. **MU UI**：6 页面（Dashboard/Outpatient/Finance/Drug/Disease/Patient）+公共组件（KpiCard/FilterBar/App.vue 布局），交互需求（§6.3 表格）进 UI 元素——全仓首个真实 MU 文件。
8. **GLS 术语**：HIS/ICD-10/退号率/均次费用/复诊率/KPI 卡/ADS/DWS 分层等 ≥8 词，逐条注源（文档 file#节）。
9. **manifest**：domain=his、profile=v9-full、omittedModels 空（八模型全建）；描述注明素材定稿性质+开放问题挂账指针。
10. 实弹缝隙（尤其 MU 跑道 schema_check 检查面）按信号路由工程错道并入本票修。

## 验收（注源）

- [ ] AC1 ontology/his/ 九件齐（8 模型+manifest），ID 前缀 AGG/BH/RULE/ACTOR/ROLE/PERM/FLOW/QR/SCR/GLS-HIS 合规（schema_check L1 零）
- [ ] AC2 `python3 tools/schema_check.py ontology` 仓根 + `ontology/his` 单域双跑全绿 L1–L4 零
- [ ] AC3 引用完整性：M2 requiredPermissions→M5 PERM、M2/M7 appliedRules→M3、M7 objectRef→M1、M6 步骤引用行为/对象——grep 抽查零悬空（schema_check L2 在面）
- [ ] AC4 开放问题清单随定稿（本体头注或细稿节），每条「待 Owner 确认」零硬裁
- [ ] AC5 bohai/pkb 两域零扰动（语义闸全仓跑含旧域仍绿）
- [ ] AC6 `bash tools/ci.sh` 四闸全绿（最终树原样跑，协议⑩）

## 交接包（L0 自执行）

任务: 八模型全建+语义闸双绿。
产出: ontology/his/ 九件。
验收: AC1–6 全过后翻 done 一票一提交；commit 引方案路径。
