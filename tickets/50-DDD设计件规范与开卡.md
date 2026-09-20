# 票 50：DDD 设计件规范 + ddd-modeler 开卡（阶段 2/3 性质）

Status: todo

> 注（L0 拆票时点）：本票只定规范与卡，不写 skill 正文（票 52）、不建闸（票 51）。七个开放问题裁决已落 docs/prd.md 决策追认（2026-09-20）。
Belongs to: docs/第四期DDD线拆票方案.md 批次一；docs/ddd-modeler-建造交接包.md；references/ddd-as-code-digest.md；PRD F15
Touches: specs/modules.md、specs/ddd-modeler.md、design/ddd/README.md、references/repo-layout.json、specs/archive-registry.json、diagrams/all-agent.html、lessons/50

## What to build

1. **设计件格式真源** `design/ddd/README.md`：四类 YAML 设计件的字段 schema 与语义——
   - **聚合卡**：aggregateRoot 标记 / 属性用 `- 词条ID` 引用语法（引用即类型，抄 CML）/ 实体与值对象区分 / **不变量三元组（触发操作→期望失败→指向聚合方法）** / correctivePolicies / waysToAccess（抄 Codely Blueprint）；
   - **领域事件表**：事件名 / 载荷=词条 ID 表 / 生产聚合→消费聚合；
   - **聚合↔表映射**：聚合→表/列映射声明；
   - **仓储边界声明**：每聚合一个仓储，只返回本聚合。
2. **modules.md 开卡** `skill: ddd-modeler`（格式真源 = sdd-flow2 references/skill-module-format.md）：层 L1 工序；触发面=选配（交易型/状态机型项目，判据表引交接包 §5）；reads `ontology/<域>/**`+`ontology/schema/**`；writes `design/ddd/<域>/**` 草案（只产草案走 MR）；依赖 script schema_check（词条解析）；边界=不做代码生成、无词条不建模、不读生成器 skill 私件。
3. **边界规则增条**：design/ddd/ 只由 ddd-modeler 工序写入（草案制）；ddd-modeler 不读他 skill 非公开文件。
4. **布局与归档登记**：references/repo-layout.json 增 `design/ddd/` 目录条目；specs/archive-registry.json 增 design-card 产物类（必备字段含 status，合法值：草案/已审；进仓走 MR 人审，非派生物不走 --check）。
5. **specs/ddd-modeler.md 功能规格**（照 module-spec-format）：行为约定 + 出厂集断言表骨架（断言在票 51/52 填充，本票落表头与编号）。
6. **架构图**：diagrams/all-agent.html 插入 ddd-modeler 一格（流水线 onto-modeler → ddd-modeler（选配）→ F9），随票报 Owner 过目。

## 验收（注源）

- [ ] AC1 设计件格式真源在场，四类 YAML 各有最小合法样例（源：本票 AC 表）
- [ ] AC2 ddd-modeler 卡合规（skill-module-format 各槽齐；触发面写清选配路由）（源：实读）
- [ ] AC3 边界规则节增条且边界闸消费后仍绿（源：CI）
- [ ] AC4 repo-layout + archive-registry 登记在场，design/ddd/ 下样例文件过归档闸（源：CI）
- [ ] AC5 架构图插入 ddd-modeler 节点且 Owner 过目留痕（lessons/50）（源：本票 AC 表）
- [ ] AC6 `bash tools/ci.sh` 四闸绿（源：CI）

## 交接包（L2 自主档）

任务: 设计件规范+开卡+登记+图更新。
先读: docs/ddd-modeler-建造交接包.md §2/§3（共识与三件套）；references/ddd-as-code-digest.md §1/§4（字段骨架来源）；specs/modules.md（现有卡格式，如 onto-modeler 卡）；references/repo-layout.json 与 specs/archive-registry.json（登记先例：票 37/45 两类）；diagrams/all-agent.html（现有流水线结构）。
框架红线: 无点名框架。
边界红线: 只动 Touches 清单；不写 skill 正文不建闸（票 51/52 的活）；design/ddd/ 下只放格式真源 README 与最小样例。
产出: 五件规范与登记+架构图更新+lessons/50。
验收: AC1–6 全过；`bash tools/ci.sh` 四闸绿。
回报: 产物路径+六项 AC 实证+架构图 Owner 过目记录+ci.sh 摘要+偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | design/ddd/README.md | 四类设计件 schema+最小样例齐 |
| AC2 | modules.md ddd-modeler 卡 | 格式各槽齐、选配触发面明文 |
| AC3 | 边界规则节 | 新增条在场、skill_deps_check 绿 |
| AC4 | repo-layout.json + archive-registry.json | design/ddd/ 与 design-card 类登记、归档闸绿 |
| AC5 | diagrams/all-agent.html + lessons/50 | ddd-modeler 节点在场、过目留痕 |
| AC6 | CI | 四闸全绿 |
