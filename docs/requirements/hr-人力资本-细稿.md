# hr 域需求细稿 · 人力资本域（第四域 · db-reverse 实战批）

> **AI 只做格式转换与结构映射，业务裁决按授权拍板。** 素材=MySQL 官方示例库
> employees 的 DDL（R14·references/hr-source/，CC BY-SA 3.0），本细稿为
> db-reverse 纪律改写：逐属性注 `[employees.sql …]` 证据；DDL 无证据处标
> 「推荐档」并给依据。口径以本细稿为进仓真源。拍板性质=**Owner 2026-09-28
> 授权「按推荐拍板」**（docs/meta/owner-delegation-2026-09-28.md §二2），
> 逐问落定见 §四；跨批使用（如据此建真系统）须重新授权。
> 批次定位：db-reverse 通路首个实战域——三域此前全部走文档/口述素材，本域
> 首次以数据库 DDL 为源。建模面=人力资本只读消费面（报表/分析），非 OLTP
> 写入面。

## 一、域定位与选型依据（授权拍板 D1/D2，留痕）

- Owner 指令（2026-09-28 授权原文）：「没有问题就进行下一个域……需要拍板的
  按你推荐的拍板」。
- 选域：**hr 人力资本域**（employees 示例库）。依据三条：① db-reverse 通路
  三域从未实战，平台「多输入」中数据库输入是唯一零实弹面；② 素材稳定可采
  （上游十年未变，raw 直取，license 明确）；③ 与 bohai（油田生产）/pkb（个人
  知识库）/his（医院报表）零业务重叠，跨域隔离再添一组真负样本。
- 域 ID：`hr`；label：hr 人力资本域；profile：**v9-full**（M6 时态生命周期
  有结构证据；MU 按登记豁免，bohai 先例）。schemaVersion 1.2.0。

## 二、素材一句话

一张 MySQL 人力库：6 张表（员工/部门/部门任职/部门管理/职级/薪酬）以
`from_date/to_date` 时态区间组织员工全周期，复合主键保「一期一条」，两个
视图定义「现行部门」判定语义；无 UI、无流程文档、无角色说明——纯结构素材。

## 三、关键词三落点覆盖表（18 词全落，证据=employees.sql 行注）

| # | 关键词（DDL 原词） | 对象候选（M1） | 行为/规则候选（M2/M3） | 术语候选（GLS） | 落点备注 |
|---|---|---|---|---|---|
| 1 | employees 员工表 | 员工（聚合根） | 人司年限查询 | 员工 | `[CREATE TABLE employees]` |
| 2 | emp_no 员工编号 | 员工.empNo | — | — | PK，INT NOT NULL |
| 3 | birth_date 出生日期 | 员工.birthDate | — | — | DATE NOT NULL |
| 4 | first_name / last_name 姓名 | 员工.姓/名 | — | — | Q5 拆分与拼接落定 |
| 5 | gender ENUM('M','F') | 员工.gender | RULE 性别值域 | 性别字典 | DDL 内唯一枚举 |
| 6 | hire_date 入职日期 | 员工.hireDate | 人司年限口径 | 入职日期 | 生命周期起点 |
| 7 | departments 部门表 | 部门（聚合根） | — | 部门 | `[CREATE TABLE departments]` |
| 8 | dept_no 部门编号 | 部门.deptNo | — | — | CHAR(4) PK |
| 9 | dept_name 部门名称 | 部门.deptName | RULE 名称唯一 | — | UNIQUE KEY |
| 10 | dept_emp 部门任职 | 部门任职（关联聚合） | 在职人数口径 | 任职 | PK(emp_no,dept_no) |
| 11 | dept_manager 部门管理 | 管理任职（关联聚合） | 管理者查询 | — | PK(emp_no,dept_no) |
| 12 | titles 职级 | 职级记录 | 任职轨迹查询 | 职级 | PK(emp_no,title,from_date)，Q2 |
| 13 | salaries 薪酬 | 薪酬记录 | 薪酬查询/一期一条 | 薪酬记录 | PK(emp_no,from_date)，Q1 |
| 14 | from_date / to_date 时态区间 | 各轨迹表时间对 | RULE 区间有效性 | 时态区间 | 六表公共结构 |
| 15 | current_dept_emp 现行部门视图 | —（查询出口） | RULE 现行任职判定 | 现行任职 | `[CREATE OR REPLACE VIEW]` |
| 16 | dept_emp_latest_date 视图 | —（中间视图） | （并入现行判定） | — | MAX(from_date) 语义 |
| 17 | ON DELETE CASCADE 级联 | — | RULE 源库级联语义 | — | 六处 FK 声明，Q4 |
| 18 | FOREIGN KEY 外键 | 聚合关联（ASSOC×6） | — | — | 关联边全部有 DDL 证据 |

## 四、开放问题 Q1–Q8（按授权逐问落定：推荐+依据=拍板，跨批须 Owner 转正）

| # | 问题 | 推荐（已按授权生效） | 依据与边界 |
|---|---|---|---|
| Q1 | salary 语义：月薪/年薪/薪档？ | 登记为「**期间薪档**」——自 from_date 起生效的薪酬档，不标单位 | DDL 无单位/注释证据；标单位即发明。GLS 同口径 |
| Q2 | titles.title 值集要不要字典化？ | **不建职级字典**，职级为自由文本属性 | DDL 无 ENUM/CHECK；test_db 数据层的五个职级值是数据事实非 schema 证据。字典化待数据字典素材 |
| Q3 | 「在职/现行」判定：9999-01-01 哨兵？ | **规则登记以视图语义为准**（current_dept_emp 条件）；9999-01-01 采纳为数据惯例注记（GLS「现行任职」notes 注明「数据惯例非 DDL 证据」） | 哨兵值在数据不在 DDL；视图条件是唯一 schema 级证据 |
| Q4 | ON DELETE CASCADE 业务上允许物理删除吗？ | 登记**源库级联语义**为规则（如实）；业务面按**只读消费域**处理，不建 DELETE 行为 | hr 建模面=消费面；写路径属上游 HR 系统（素材外） |
| Q5 | 姓名 first/last 拆还是合？ | **照 DDL 拆双属性**；M7 出口提供「姓名」拼接列（lastName+firstName） | 结构证据优先；拼接属出口形态（建造面） |
| Q6 | 人司年限怎么算？ | hire_date 起算，天差 ÷365.25 取一位小数（CALCULATION 规则注记在 M3，表达式落 M7 出口） | 口径单源：规则给语义，出口给表达式（口径真源在 M3 纪律） |
| Q7 | 纯 DDL 推五个查询是否越权？ | **不越权**——五个查询出口逐一对应五个结构证据（salaries/dept_emp/视图/titles/dept_manager），不发明指标 | 每张轨迹表一个消费出口 + 视图自证查询语义；无「以后可能要」式发明 |
| Q8 | 主体面（M5）无 DDL 证据怎么办？ | 按**消费面推荐四主体**（人力分析师/部门管理者/高管/系统集成方），PERM 与 QUERY 行为一一对应；标注「推荐档待 Owner 转正」 | M5 面素材空白如实注记；不建空白文件，按 bohai「无证据不建模、消费面按需推荐」先例 |

## 五、明示不建模清单

- 数据行与量级（~30 万员工/260 万薪酬行——数据事实非结构）；
- 数据装载 dump（load_*.dump 未抓取不入仓）；
- MySQL 存储引擎/分区/物理索引实现面；
- 上游 HR 系统的写入流程（入职审批/调薪审批流程素材外——M6 只登记数据层
  时态生命周期，不发明审批流）；
- 薪酬加密/隐私合规（素材无、推荐面外——建真系统时须补）。

## 六、profile 建议与模型面

- profile **v9-full**：M1（二聚合根+四关联聚合+一字典+六关联）/ M2（QUERY×5，
  COMMAND×0 如实）/ M3（八规则）/ M5（四主体+四角色+五权限，推荐档）/
  M6（一时态生命周期流程）/ M7（五查询出口，与 M2 一对一）/ GLS（八术语）；
- **MU 豁免**（omittedModels 登记，bohai 先例）：素材纯 DDL 无界面证据；
- 建模文件 7 个（m1/m2/m3/m5/m6/m7/glossary）+ manifest。
