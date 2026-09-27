# hr 人力资本域（MySQL employees 示例库） 开发包（devkit · hr）

status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）

- 生成器: tools/app_pack_gen.py（确定性装配：YAML 机读 + 提案 frontmatter 扫描，零 LLM 零时间戳）
- 本体来源: ontology/hr（profile=v9-full）
- 声明模型: M1 对象模型 / M2 行为模型 / M3 规则模型 / M7 查询统计与报表模型
- 固定输入: fixtures/app-pack-gen/inputs/tech-constraints.md（出厂集固定输入（合成））、fixtures/app-pack-gen/inputs/dev-guide.md（出厂集固定输入（合成））
- 开放提案开关: 启用（docs/proposals）
- 防陈旧: python3 tools/app_pack_gen.py ontology/hr --check exports/devkit/hr/devkit.md

## 技术架构约束（固定输入，原样装配）

出厂集固定输入（合成）——中性示例文本，非任何真实项目规约；生成器按原样装配进开发包头部约束节，文件内容不参与判定。

## 技术架构约束

- 服务端形态：Python 服务端 + 关系库，三层架构（接入 / 领域 / 数据）。
- 数据访问：一切业务数据经语义层数据字典取数，禁直连物理表名。
- 集成边界：对外只暴露查询出口与行为接口，不出裸表。

（以上为合成中性约束，仅作开发包装配通路的固定输入。）

## 开发指导书（固定输入，原样装配）

出厂集固定输入（合成）——中性示例文本，非任何真实项目规约；生成器按原样装配进开发包头部约束节，文件内容不参与判定。

## 开发指导书

- 装配顺序：先数据字典后接口——数据字典是接口签名的唯一依据。
- 口径实现：统计口径以规则清单（M3）的 expression/narrative 为准，查询出口（M7）只是实现形态，两处不一致时以规则为准并回提案流程。
- 疑点处置：开发包第④节开放疑点逐条过目，命中疑点的实现先挂起待 Owner 裁决，不自行拍板。

（以上为合成中性指导，仅作开发包装配通路的固定输入。）

---

## 一、数据字典（M1 对象模型）

### AGG-HR-001 员工（Employee）

- AGGREGATE_ROOT；描述: 员工主档（R14·CREATE TABLE employees：emp_no PK，六列全 NOT NULL）。 生命周期自 hireDate 起；「在职/离职」不由本表字段承载，而由四张轨迹 表的时态区间表达（Q3 已裁以视图语义为准）。
- lifecycle: 在职/离职

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| empNo | 员工编号 | Integer | unique |
| birthDate | 出生日期 | Date |  |
| lastName | 姓 | String |  |
| firstName | 名 | String |  |
| gender | 性别 | Enum | 字典值集: M/F |
| hireDate | 入职日期 | Date |  |

### AGG-HR-002 部门（Department）

- AGGREGATE_ROOT；描述: 部门主档（R14·CREATE TABLE departments：dept_no CHAR(4) PK + dept_name UNIQUE KEY）。示例库共九行，但量级属数据事实不入本体。
- lifecycle: 设立/撤销

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| deptNo | 部门编号 | String | unique |
| deptName | 部门名称 | String | unique |

### AGG-HR-003 部门任职（DepartmentAssignment）

- AGGREGATE_ROOT；描述: 员工×部门的时态分配行（R14·CREATE TABLE dept_emp：PK(emp_no,dept_no)， 双 FK ON DELETE CASCADE）。from_date/to_date 区间承载「何时属何部门」； 「现行任职」判定=RULE-HR-003（current_dept_emp 视图条件，Q3 已裁）。
- lifecycle: 任职中/已调离

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| empNo | 员工编号 | Integer |  |
| deptNo | 部门编号 | String |  |
| fromDate | 起始日期 | Date |  |
| toDate | 截止日期 | Date |  |

### AGG-HR-004 管理任职（DepartmentManager）

- AGGREGATE_ROOT；描述: 员工×部门的管理角色时态行（R14·CREATE TABLE dept_manager： PK(emp_no,dept_no)，双 FK ON DELETE CASCADE）。结构上与部门任职同构， 语义=该员工在该时段管理该部门。
- lifecycle: 任期内/已卸任

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| empNo | 员工编号 | Integer |  |
| deptNo | 部门编号 | String |  |
| fromDate | 起始日期 | Date |  |
| toDate | 截止日期 | Date |  |

### AGG-HR-005 职级记录（TitleRecord）

- AGGREGATE_ROOT；描述: 员工职级的时态轨迹行（R14·CREATE TABLE titles：PK(emp_no,title, from_date)，单 FK）。title 为自由文本（Q2 已裁不字典化——DDL 无 枚举证据）；to_date 可空（DDL 唯一可空列，RULE-HR-005 如实注记）。
- lifecycle: 任职中/已变更

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| empNo | 员工编号 | Integer |  |
| title | 职级名称 | String |  |
| fromDate | 起始日期 | Date |  |
| toDate | 截止日期 | Date |  |

### AGG-HR-006 薪酬记录（SalaryRecord）

- AGGREGATE_ROOT；描述: 员工薪酬的时态轨迹行（R14·CREATE TABLE salaries：PK(emp_no,from_date)， 单 FK ON DELETE CASCADE）。salary 语义=期间薪档（Q1 已裁：自 fromDate 起生效的薪档，不标单位——DDL 无单位证据）。
- lifecycle: 生效中/已调整

| 属性 | 标签 | 类型 | 约束与字典 |
|---|---|---|---|
| empNo | 员工编号 | Integer |  |
| salary | 期间薪档 | Integer |  |
| fromDate | 起始日期 | Date |  |
| toDate | 截止日期 | Date |  |

聚合关联（aggregate_associations）:

| 关联 | 源 → 靶 | 类型 | 基数 | 引用字段 | 角色 |
|---|---|---|---|---|---|
| ASSOC-HR-001 | AGG-HR-001 → AGG-HR-003 | REFERENCE | ONE_TO_MANY | empNo | 员工→部门任职 |
| ASSOC-HR-002 | AGG-HR-002 → AGG-HR-003 | REFERENCE | ONE_TO_MANY | deptNo | 部门→部门任职 |
| ASSOC-HR-003 | AGG-HR-001 → AGG-HR-004 | REFERENCE | ONE_TO_MANY | empNo | 员工→管理任职 |
| ASSOC-HR-004 | AGG-HR-002 → AGG-HR-004 | REFERENCE | ONE_TO_MANY | deptNo | 部门→管理任职 |
| ASSOC-HR-005 | AGG-HR-001 → AGG-HR-005 | REFERENCE | ONE_TO_MANY | empNo | 员工→职级记录 |
| ASSOC-HR-006 | AGG-HR-001 → AGG-HR-006 | REFERENCE | ONE_TO_MANY | empNo | 员工→薪酬记录 |

## 二、口径四件套（M7 查询出口 × M2 行为 × M3 规则 × M1 承载）

### 口径 QR-HR-001 · 员工薪酬明细查询

- 问题样例: 员工薪酬明细查询
- 查询出口: QR-HR-001（STATISTICAL_QUERY）
- 行为: BH-HR-QuerySalary 查询员工薪酬（QUERY/，ownerEntity=AGG-HR-006）
- 承载对象: AGG-HR-006 薪酬记录（主）、AGG-HR-001 员工
- 参数: startDay（生效起始日，Date，必填）；endDay（生效截止日，Date，必填）
- 结果列: empNo=员工编号（e.empNo）；fullName=姓名（CONCAT(e.lastName, ' ', e.firstName)）；salary=期间薪档（s.salary）；fromDate=生效日期（s.fromDate）；toDate=截止日期（s.toDate）；isCurrent=是否现行（s.toDate == DATE '9999-01-01'）
- 命中 ID 集: QR-HR-001 BH-HR-QuerySalary AGG-HR-006 AGG-HR-001 RULE-HR-002 RULE-HR-003 RULE-HR-001 RULE-HR-008
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HR-002 薪酬一期一条（VALIDATION；via=behavior.appliedRules(BH-HR-QuerySalary)）: COUNT(*) == COUNT(DISTINCT (empNo, fromDate))
  - RULE-HR-003 现行任职判定（CALCULATION；via=behavior.appliedRules(BH-HR-QuerySalary)）: fromDate == MAX(fromDate) OVER (empNo) AND toDate == latestToDate
  - RULE-HR-001 性别代码值域（VALIDATION；via=ownerObjectBehaviors(AGG-HR-001)）: gender == 'M' or gender == 'F'
  - RULE-HR-008 人司年限口径（CALCULATION；via=ownerObjectBehaviors(AGG-HR-001)）: DATEDIFF(asOfDay, hireDate) / 365.25

### 口径 QR-HR-002 · 部门在职人数查询

- 问题样例: 部门在职人数查询
- 查询出口: QR-HR-002（STATISTICAL_QUERY）
- 行为: BH-HR-QueryHeadcount 查询部门在职人数（QUERY/，ownerEntity=AGG-HR-003）
- 承载对象: AGG-HR-003 部门任职（主）、AGG-HR-002 部门
- 参数: startDay（起始日，Date，必填）；endDay（截止日，Date，必填）
- 结果列: deptNo=部门编号（d.deptNo）；deptName=部门名称（d.deptName）；headcount=在职人数（COUNT(DISTINCT a.empNo)）
- 命中 ID 集: QR-HR-002 BH-HR-QueryHeadcount AGG-HR-003 AGG-HR-002 RULE-HR-003 RULE-HR-007 RULE-HR-004
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HR-003 现行任职判定（CALCULATION；via=behavior.appliedRules(BH-HR-QueryHeadcount)）: fromDate == MAX(fromDate) OVER (empNo) AND toDate == latestToDate
  - RULE-HR-007 部门在职人数口径（CALCULATION；via=behavior.appliedRules(BH-HR-QueryHeadcount)）: COUNT(DISTINCT empNo) WHERE 现行任职（RULE-HR-003 过滤）
  - RULE-HR-004 部门名称唯一（VALIDATION；via=reusedBy(BH-HR-QueryHeadcount)）: COUNT(*) == COUNT(DISTINCT deptName)

### 口径 QR-HR-003 · 员工任职轨迹查询

- 问题样例: 员工任职轨迹查询
- 查询出口: QR-HR-003（STATISTICAL_QUERY）
- 行为: BH-HR-QueryTitle 查询任职轨迹（QUERY/，ownerEntity=AGG-HR-005）
- 承载对象: AGG-HR-005 职级记录（主）、AGG-HR-001 员工
- 参数: startDay（起始日，Date，必填）；endDay（截止日，Date，必填）
- 结果列: empNo=员工编号（e.empNo）；fullName=姓名（CONCAT(e.lastName, ' ', e.firstName)）；title=职级（t.title）；fromDate=起始日期（t.fromDate）；toDate=截止日期（t.toDate）
- 命中 ID 集: QR-HR-003 BH-HR-QueryTitle AGG-HR-005 AGG-HR-001 RULE-HR-005 RULE-HR-001 RULE-HR-008
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HR-005 轨迹区间有效性（VALIDATION；via=behavior.appliedRules(BH-HR-QueryTitle)）: toDate IS NULL OR toDate >= fromDate
  - RULE-HR-001 性别代码值域（VALIDATION；via=ownerObjectBehaviors(AGG-HR-001)）: gender == 'M' or gender == 'F'
  - RULE-HR-008 人司年限口径（CALCULATION；via=ownerObjectBehaviors(AGG-HR-001)）: DATEDIFF(asOfDay, hireDate) / 365.25

### 口径 QR-HR-004 · 部门管理者查询

- 问题样例: 部门管理者查询
- 查询出口: QR-HR-004（STATISTICAL_QUERY）
- 行为: BH-HR-QueryManager 查询部门管理者（QUERY/，ownerEntity=AGG-HR-004）
- 承载对象: AGG-HR-004 管理任职（主）、AGG-HR-002 部门、AGG-HR-001 员工
- 参数: startDay（起始日，Date，必填）；endDay（截止日，Date，必填）
- 结果列: deptNo=部门编号（d.deptNo）；deptName=部门名称（d.deptName）；empNo=管理者编号（m.empNo）；managerName=管理者姓名（CONCAT(e.lastName, ' ', e.firstName)）；fromDate=任期起始（m.fromDate）；toDate=任期截止（m.toDate）
- 命中 ID 集: QR-HR-004 BH-HR-QueryManager AGG-HR-004 AGG-HR-002 AGG-HR-001 RULE-HR-003 RULE-HR-001 RULE-HR-008
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HR-003 现行任职判定（CALCULATION；via=behavior.appliedRules(BH-HR-QueryManager)）: fromDate == MAX(fromDate) OVER (empNo) AND toDate == latestToDate
  - RULE-HR-001 性别代码值域（VALIDATION；via=ownerObjectBehaviors(AGG-HR-001)）: gender == 'M' or gender == 'F'
  - RULE-HR-008 人司年限口径（CALCULATION；via=ownerObjectBehaviors(AGG-HR-001)）: DATEDIFF(asOfDay, hireDate) / 365.25

### 口径 QR-HR-005 · 员工人司年限查询

- 问题样例: 员工人司年限查询
- 查询出口: QR-HR-005（STATISTICAL_QUERY）
- 行为: BH-HR-QueryTenure 查询人司年限（QUERY/，ownerEntity=AGG-HR-001）
- 承载对象: AGG-HR-001 员工（主）
- 参数: asOfDay（统计日，Date，必填）
- 结果列: empNo=员工编号（e.empNo）；fullName=姓名（CONCAT(e.lastName, ' ', e.firstName)）；gender=性别（e.gender）；hireDate=入职日期（e.hireDate）；tenureYears=人司年限（年）（ROUND(DATEDIFF(asOfDay, e.hireDate) / 365.25, 1)）
- 命中 ID 集: QR-HR-005 BH-HR-QueryTenure AGG-HR-001 RULE-HR-001 RULE-HR-008
- 口径要点（关联规则 expression/narrative 摘录）:
  - RULE-HR-001 性别代码值域（VALIDATION；via=behavior.appliedRules(BH-HR-QueryTenure)）: gender == 'M' or gender == 'F'
  - RULE-HR-008 人司年限口径（CALCULATION；via=behavior.appliedRules(BH-HR-QueryTenure)）: DATEDIFF(asOfDay, hireDate) / 365.25

## 三、行为与规则清单（M2/M3 全量，注源=模型文件 [R<n>·…] 注释标签）

### 行为（M2 · 5 条）

- BH-HR-QuerySalary 查询员工薪酬 [QUERY/] ownerEntity=AGG-HR-006 appliedRules=RULE-HR-002,RULE-HR-003
- BH-HR-QueryHeadcount 查询部门在职人数 [QUERY/] ownerEntity=AGG-HR-003 appliedRules=RULE-HR-003,RULE-HR-007
- BH-HR-QueryTitle 查询任职轨迹 [QUERY/] ownerEntity=AGG-HR-005 appliedRules=RULE-HR-005
- BH-HR-QueryManager 查询部门管理者 [QUERY/] ownerEntity=AGG-HR-004 appliedRules=RULE-HR-003
- BH-HR-QueryTenure 查询人司年限 [QUERY/] ownerEntity=AGG-HR-001 appliedRules=RULE-HR-001,RULE-HR-008

### 规则（M3 · 8 条）

- RULE-HR-001 性别代码值域 [VALIDATION]  — gender == 'M' or gender == 'F'
- RULE-HR-002 薪酬一期一条 [VALIDATION]  — COUNT(*) == COUNT(DISTINCT (empNo, fromDate))
- RULE-HR-003 现行任职判定 [CALCULATION]  — fromDate == MAX(fromDate) OVER (empNo) AND toDate == latestToDate
- RULE-HR-004 部门名称唯一 [VALIDATION]  — COUNT(*) == COUNT(DISTINCT deptName)
- RULE-HR-005 轨迹区间有效性 [VALIDATION]  — toDate IS NULL OR toDate >= fromDate
- RULE-HR-006 源库级联删除语义 [VALIDATION]  — DELETE employees WHERE emp_no = :empNo 将级联删除该员工全部 部门任职/管理任职/职级/薪酬行（六处 ON DELETE CASCADE）。 消费域不得触发物理删除。
- RULE-HR-007 部门在职人数口径 [CALCULATION]  — COUNT(DISTINCT empNo) WHERE 现行任职（RULE-HR-003 过滤）
- RULE-HR-008 人司年限口径 [CALCULATION]  — DATEDIFF(asOfDay, hireDate) / 365.25

## 四、开放疑点（docs/proposals 扫描）

无开放提案。
