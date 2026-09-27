# lessons/64 · 第四域 db-reverse 实战（票 78–80 批）

## 做了什么
第四域 hr（人力资本域）端到端接入：MySQL 官方示例库 employees 的 DDL 为素材
（db-reverse 通路首实战），立项→细稿（Q1–Q8 按授权拍板）→七模型建模（逐属性
注 DDL 证据）→语义闸四域 26 文件全绿→devkit/skillpkg 导出→图索引/语义服务
问答/smoke 文案走查→四域体检+快照+锚点批收官。授权链=Owner 2026-09-28 会话
原文转正（owner-delegation-2026-09-28.md），审记 approve 不代审为 L0 自设边界。

## 坑
1. 布局表不认 .sql——`references/` 只许 md/json/py，employees.sql 入仓即归档闸
   红灯（pattern-mismatch）。db-reverse 通路开启后 SQL 素材是常客，布局表演进
   加 `*.sql` 是正当扩面，不是给红灯放水（登记表不加产物类，两表纪律不破）；
2. 实跑测试钉死域清单——票 77 自己写的三处测试 `["bohai","his","pkb"]` 字面量
   被第四域当场打红（meta_probe/onboard_check/report_numbers 各一）。防呆工具
   的测试自己犯了防呆要治的病；修法=测试期望动态对文件系统枚举互核+`>=4` 下限，
   而不是把字面量改成四域（第五域会再红一次）；
3. mcp capability-manifest 是全域再制件——加域必过期，`--check` 逐字节比对会
   红出「mcp-publisher 出厂集」而不是提示 manifest 过期，红灯点位与病灶隔了一层
   （fixture→命令→--check→副本），排障时别在 fixture 里找毛病；
4. L3-1 sourceField 解析按 id→alias→name→alias-tokens 逐层唯一命中——hr 的
   Department/DepartmentAssignment/DepartmentManager 同词根，用短段（`department`）
   会歧义，必须用聚合 alias 全名（`Department.deptName` 式）；同构命名域在
   db-reverse 场景是常态，建模时就该避开；
5. titles.to_date 可空是六表唯一可空列——DDL 大小写/NOT NULL 逐列读才能抓到
   「区间有效性规则对可空列要放行」这种细节；结构证据的精度=建模精度。

## 取舍
- 审记 approve 不代审（L0 自设边界）：review_gate 的 by= 字段机械取 git
  user.name，代审会留下「Owner 已审」假痕——闸完整性优先于进度，his×2+hr×2
  四件 pending 挂账过夜；
- COMMAND×0/MU 豁免/职级不字典化：DDL 无证据就不建，宁可 manifest 登记豁免
  与「推荐档待 Owner 转正」，不发明 UI 面/审批流/值集——db-reverse 的诚实度
  就是「结构给了多少建多少」；
- 级联删除规则走 narrative 形态：删批量行为不是行级可执行表达式，schema.md §6
  的两形态机判面正好承载；顺带成为 narrative 形态的首个实战用例。
