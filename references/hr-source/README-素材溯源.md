# hr 域素材溯源（R14）

## 上游

- 仓库：GitHub `datacharmer/test_db`（MySQL 官方示例数据库 employees 的社区维护版，
  schema 作者 Giuseppe Maxia；2007–2008 原始数据 Fusheng Wang / Carlo Zaniolo，
  XML→关系转换 Patrick Crews）。
- 抓取：2026-09-28，`raw.githubusercontent.com/datacharmer/test_db/master/employees.sql`
  （127 行，git raw 直取；上游无独立 README/changelog 可抓——溯源以本文件与
  employees.sql 头注为准）。

## License

employees.sql 头注明示：**Creative Commons Attribution-Share Alike 3.0 Unported**
（CC BY-SA 3.0）。署名条件由本文件 + R14 行 + 模型文件逐条 `[employees.sql …]`
证据注记满足；数据经上游声明为伪造（不对应真实个人）。只引用 schema 文本
（DDL+视图定义），不引入数据 dump（load_*.dump 未抓取、不入仓）。

## 本目录清单

| 文件 | 内容 | 用途 |
|---|---|---|
| `employees.sql` | 6 表 DDL（employees/departments/dept_manager/dept_emp/titles/salaries，含 PK/FK/ENUM/UNIQUE/ON DELETE CASCADE）+ 2 视图（dept_emp_latest_date/current_dept_emp） | hr 域建模唯一素材真源（R14） |

## 证据边界（db-reverse 纪律）

- 建模证据=**纯 DDL 文本**（表结构/约束/枚举/视图定义）；数据行、数据量级
  （~30 万员工）、`9999-01-01` 哨兵值等**数据层事实不在 DDL 内**，凡引用一律
  注记「数据惯例非 DDL 证据」（细稿 Q3）。
- AI 只做格式转换与结构映射，业务裁决按 Owner 2026-09-28 授权按推荐拍板
  （docs/meta/owner-delegation-2026-09-28.md），逐问留痕于
  `docs/requirements/hr-人力资本-细稿.md` §四。
